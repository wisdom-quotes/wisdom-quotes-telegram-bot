import json
import zoneinfo
from datetime import datetime, timedelta
from typing import TypedDict, Optional
from zoneinfo import ZoneInfo

from lang_provider import LangProvider, Lang
from quotes_loader import Quote
from scheduler import Scheduler
from user_settings_manager import parse_user_settings, serialize_user_settings
from users_orm import UsersOrm
from fuzzywuzzy import fuzz

# Quite expensive operation, use only to sanitize user input
# utcoffset_secs is a positive offset (that is, Sydney's time is either +10*3600 or +11*3600)
def detect_timezone(tz_name: str, utcoffset_secs: int):
    try:
        return ZoneInfo(tz_name).key
    except:
        timezones = list(zoneinfo.available_timezones())
        timezones_by_offset_diff = {}
        min_diff = 10 * 3600
        for tz in timezones:
            offset = zoneinfo.ZoneInfo(tz).utcoffset(datetime.now()).total_seconds()
            offset_diff = abs(offset - utcoffset_secs)
            if offset_diff < min_diff:
                min_diff = offset_diff
            if timezones_by_offset_diff.get(offset_diff) is None:
                timezones_by_offset_diff[offset_diff] = [tz]
            else:
                timezones_by_offset_diff[offset_diff].append(tz)

        candidate_tzs = timezones_by_offset_diff[min_diff]
        found_tz = None
        found_tz_score = 0
        for tz in candidate_tzs:
            score = fuzz.ratio(tz, tz_name)
            if score > found_tz_score:
                found_tz = tz
                found_tz_score = score

        return found_tz


class Button(TypedDict):
    text: str
    data: Optional[str]
    url: Optional[str]

class Reply(TypedDict):
    to_chat_id: int
    message: str
    buttons: list[Button]
    protect_content: bool
    menu_commands: list[tuple[str, str]]
    image: Optional[str]

class BotManager:
    def __init__(self, db_name, quotes_dir, env, frontend_base_url):
        self.user_orm = UsersOrm(db_name)
        self.env = env
        self.frontend_base_url = frontend_base_url
        self.scheduler = Scheduler(quotes_dir)

    def process_tick(self) -> list[Reply]:
        users_eligible_quotes = self.user_orm.get_some_users_for_quote(20)
        ret = []
        for user in users_eligible_quotes:
            reply = self._render_next_quote(user['user_id'])
            if reply is not None:
                ret.append(reply)
        return ret

    def on_start_command(self, chat_id) -> Reply:
        user = self.user_orm.get_user_by_id(chat_id)
        settings = parse_user_settings(user['settings'])
        lang = LangProvider.get_lang_by_code(settings['lang_code'])
        ret = {
            'to_chat_id': chat_id,
            'message': lang.start_command,
            'protect_content': False,
            'buttons': [
                {
                    'text': category['name'],
                    'data': 'category:' + categoryKey,
                    'url': None
                } for categoryKey, category  in self.scheduler.quotes_loader.categories['subcategories'][lang.lang_code]['subcategories'].items()
            ],
            'menu_commands': [
                ('settings', lang.menu_settings)
            ],
            'image': None
        }
        ret['buttons'] += [{
            'text': lang.button_all,
            'data': 'category:all',
            'url': None
        }]
        return ret

    def on_settings_command(self, chat_id) -> Reply:
        user = self.user_orm.get_user_by_id(chat_id)
        settings = parse_user_settings(user['settings'])
        lang = LangProvider.get_lang_by_code(settings['lang_code'])

        categories = ", ".join([self.scheduler.quotes_loader.categories['subcategories'][lang.lang_code]['subcategories'][cat_key]['name'] for cat_key in settings['categories']])
        if len(categories) == 0:
            categories = lang.no_categories

        return {
            'to_chat_id': chat_id,
            'protect_content': False,
            'message': lang.settings_command.format(
                categories=categories,
                time=(
                    ", ".join([self._minutes_to_clock_time(mins) for mins in settings['quote_times_mins']])
                    + (" (+0)" if settings['user_timezone'] == 'UTC' else '')
                )
            ),
            'buttons': [
                {
                    'text': lang.button_categories,
                    'url': self.frontend_base_url + "?selected_categories=" + ','.join(settings['categories']) +
                           '&lang=' + settings['lang_code'] +
                           '&env=' + self.env,
                    'data': None
                },
                {
                    'text': lang.button_time,
                    'url': self.frontend_base_url + "?mins=" + str(','.join(map(str, settings['quote_times_mins']))) +
                           ('&is_mins_tz=true' if settings['resolved_user_timezone'] == 'UTC' else '') +
                            '&lang=' + settings['lang_code'] +
                            '&env=' + self.env,
                    'data': None
                }
            ],
            'menu_commands': [],
            'image': None
        }

    def _minutes_to_clock_time(self, time_mins: int) -> str:
        hours = time_mins // 60
        minutes = time_mins % 60
        return f"{hours:02}:{minutes:02}"

    def on_data_provided(self, chat_id, data: str) -> Optional[list[Reply]]:
        user = self.user_orm.get_user_by_id(chat_id)
        settings = parse_user_settings(user['settings'])
        lang = LangProvider.get_lang_by_code(settings['lang_code'])

        top_categories = self.scheduler.quotes_loader.categories['subcategories'][lang.lang_code]['subcategories']

        if data.startswith('command:'):
            command = data[len('command:'):]
            if command == 'start':
                return [self.on_start_command(chat_id)]
            if command == 'settings':
                return [self.on_settings_command(chat_id)]

        if data.startswith('share:'):
            quote_id = data[len('share:'):]
            quote = self.scheduler.quotes_loader.quote_id_to_quote.get(quote_id)
            if quote is not None:
                ret = self._render_quote(lang, chat_id, quote)
                ret['protect_content'] = False
                ret['message'] += "\n\n" + lang.share_command
                ret['buttons'] = []
                return [
                    {
                        'to_chat_id': chat_id,
                        'protect_content': True,
                        'message': lang.share_instruction,
                        'buttons': [],
                        'menu_commands': [],
                        'image': None
                    },
                    ret
                ]
            return [{
                'to_chat_id': chat_id,
                'protect_content': False,
                'message': 'Invalid content',
                'buttons': [],
                'menu_commands': [],
                'image': None
            }]

        if data.startswith('category:'):
            category_key = data[len('category:'):]
            if category_key == 'all':
                settings['categories'] = list(top_categories.keys())
            else:
                settings['categories'] = [category_key]
            user['settings'] = serialize_user_settings(settings)
            self.user_orm.upsert_user(user)
            ret = self._render_next_quote(chat_id)
            if ret is not None:
                return [ret]
            return []

        if 'categories:' in data:
            categories = data.split('categories:')[1]
            settings['categories'] = categories.split(',') if len(categories) > 0 else []
            user['settings'] = serialize_user_settings(settings)
            self.user_orm.upsert_user(user)
            if len(settings['categories']) == 0:
                return [{
                    'to_chat_id': chat_id,
                    'protect_content': False,
                    'message': lang.categories_updated.format(
                        categories=lang.no_categories
                    ),
                    'buttons': [],
                    'menu_commands': [],
                    'image': None
                }]
            return [{
                'to_chat_id': chat_id,
                'protect_content': False,
                'message': lang.categories_updated.format(
                    categories=", ".join([top_categories[cat_key]['name'] for cat_key in settings['categories']])
                ),
                'buttons': [],
                'menu_commands': [],
                'image': None
            }]

        if data.startswith('move:'):
            move_time_hrs = int(data[len('move:'):])
            user['next_quote_time'] = user['next_quote_time'] - timedelta(hours=move_time_hrs)
            self.user_orm.upsert_user(user)
            return [{
                'to_chat_id': chat_id,
                'protect_content': False,
                'message': f"Next quote time: {user['next_quote_time']}",
                'buttons': [],
                'menu_commands': [],
                'image': None
            }]

        if data.startswith('quote:'):
            quote_id = data[len('quote:'):]
            quote = self.scheduler.quotes_loader.quote_id_to_quote.get(quote_id)
            if quote is not None:
                return [self._render_quote(lang, chat_id, quote)]
            return [{
                'to_chat_id': chat_id,
                'protect_content': False,
                'message': "Quote not found",
                'buttons': [],
                'menu_commands': [],
                'image': None
            }]

        if "times" in data and "timeZone" in data and "offsetSecs" in data:
            try:
                data = json.loads('{' + data.split('{')[1])
                settings['quote_times_mins'] = list(dict.fromkeys(list(map(int, data['times'].split(',')))))
                settings['quote_times_mins'].sort()
                settings['user_timezone'] = data['timeZone']
                settings['user_timezone_offset_mins'] = data['offsetSecs'] // 60
                settings['resolved_user_timezone'] = detect_timezone(data['timeZone'], data['offsetSecs'])
                user['settings'] = serialize_user_settings(settings)
                user['next_quote_time'] = self.scheduler.calculate_next_quote_time(settings['quote_times_mins'], ZoneInfo(settings['resolved_user_timezone']))
                self.user_orm.upsert_user(user)

                return [{
                    'to_chat_id': chat_id,
                    'protect_content': False,
                    'message': lang.time_updated.format(
                        time=(
                                ", ".join([self._minutes_to_clock_time(mins) for mins in settings['quote_times_mins']])
                                + (" (+0)" if settings['user_timezone'] == 'UTC' else '')
                        )
                    ),
                    'buttons': [],
                    'menu_commands': [],
                    'image': None
                }]
            except Exception as e:
                print("Error handling payload", e)
                return [{
                    'to_chat_id': chat_id,
                    'protect_content': False,
                    'message': f"Error",
                    'buttons': [],
                    'menu_commands': [],
                    'image': None
                }]

        return [{
            'to_chat_id': chat_id,
            'protect_content': False,
            'message': "Unknown command",
            'buttons': [],
            'menu_commands': [],
            'image': None
        }]

    def _render_quote(self, lang: Lang, chat_id, quote: Quote) -> Reply:
        return {
            'to_chat_id': chat_id,
            'protect_content': True,
            'message': f"<b>{quote['text']}</b>" +
                       "\n\n" +
                       f" – <i>{quote['reference']}</i>",
            'buttons': [{
                'text': lang.share_button,
                'data': "share:" + quote['id'],
                'url': None
            }],
            'menu_commands': [],
            'image': None
        }

    def _render_next_quote(self, chat_id) -> Optional[Reply]:
        user = self.user_orm.get_user_by_id(chat_id)
        settings = parse_user_settings(user['settings'])
        lang = LangProvider.get_lang_by_code(settings['lang_code'])

        user['next_quote_time'] = self.scheduler.calculate_next_quote_time(settings['quote_times_mins'], ZoneInfo(settings['resolved_user_timezone']))

        selected_cat_keys = [f'{lang.lang_code}_{cat_key}' for cat_key in settings['categories']]
        if len(selected_cat_keys) > 0:
            quote, new_filter = self.scheduler.pick_next_quote(selected_cat_keys,
                                                               settings['viewed_quotes_bloomfilter_base64'])
            settings['viewed_quotes_bloomfilter_base64'] = new_filter
            user['settings'] = serialize_user_settings(settings)

            self.user_orm.upsert_user(user)

            return self._render_quote(lang, chat_id, quote['quote'])
        else:
            self.user_orm.upsert_user(user)
            return None


    def _format_time_minutes(self, lang: Lang, time_secs: int, skip_zeros = False) -> str:
        days = int(time_secs // 86400)
        hours = int((time_secs % 86400) // 3600)
        minutes = int((time_secs % 3600) // 60)

        ret = []
        if days > 0 or not skip_zeros:
            ret.append(f"{days}{lang.days_short}")
        if hours > 0 or not skip_zeros:
            ret.append(f"{hours}{lang.hours_short}")

        if len(ret) == 0 or minutes > 0:
            ret.append(f"{minutes}{lang.minutes_short}")

        return " ".join(ret)
