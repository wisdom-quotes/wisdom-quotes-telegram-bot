from datetime import datetime
from typing import TypedDict, Optional
from zoneinfo import ZoneInfo

from lang_provider import LangProvider, Lang
from quotes_loader import QuotesLoader
from scheduler import Scheduler
from user_settings_manager import parse_user_settings, serialize_user_settings
from users_orm import UsersOrm


class Button(TypedDict):
    text: str
    data: Optional[str]
    url: Optional[str]

class Reply(TypedDict):
    to_chat_id: int
    message: str
    buttons: list[Button]
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
            ret.append(self._render_next_quote(user['user_id']))
        return ret

    def on_start_command(self, chat_id) -> Reply:
        user = self.user_orm.get_user_by_id(chat_id)
        settings = parse_user_settings(user['settings'])
        lang = LangProvider.get_lang_by_code(settings['lang_code'])
        ret = {
            'to_chat_id': chat_id,
            'message': lang.start_command,
            'buttons': [
                {
                    'text': category['name'],
                    'data': 'category:' + categoryKey,
                    'url': None
                } for categoryKey, category  in self.scheduler.quotes_loader.categories['subcategories'][lang.lang_code]['subcategories'].items()
            ],
            'menu_commands': [],
            'image': None
        }
        ret['buttons'] += [{
            'text': lang.button_all,
            'data': 'category:all',
            'url': None
        }]
        return ret

    def on_settings_command(self, chat_id) -> Reply:
        pass

    def on_data_provided(self, chat_id, data: str) -> Optional[Reply]:
        user = self.user_orm.get_user_by_id(chat_id)
        settings = parse_user_settings(user['settings'])
        lang = LangProvider.get_lang_by_code(settings['lang_code'])

        top_categories = self.scheduler.quotes_loader.categories['subcategories'][lang.lang_code]['subcategories']

        if data.startswith('category:'):
            category_key = data[len('category:'):]
            if category_key == 'all':
                settings['categories'] = list(top_categories.keys())
            else:
                settings['categories'] = [category_key]
            user['settings'] = serialize_user_settings(settings)
            self.user_orm.upsert_user(user)
            return self._render_next_quote(chat_id)

        return None

    def _render_next_quote(self, chat_id) -> Reply:
        user = self.user_orm.get_user_by_id(chat_id)
        settings = parse_user_settings(user['settings'])
        lang = LangProvider.get_lang_by_code(settings['lang_code'])

        quote, new_filter = self.scheduler.pick_next_quote([f'{lang.lang_code}_{cat_key}' for cat_key in settings['categories']],
                                                           settings['viewed_quotes_bloomfilter_base64'])
        settings['viewed_quotes_bloomfilter_base64'] = new_filter

        user['next_quote_time'] = self.scheduler.calculate_next_quote_time(settings['quote_times_mins'], ZoneInfo(settings['resolved_user_timezone']))
        user['settings'] = serialize_user_settings(settings)

        self.user_orm.upsert_user(user)

        secs_next_quote = int(user['next_quote_time'].timestamp() - datetime.now().timestamp())

        return {
            'to_chat_id': chat_id,
            'message': f"<blockquote>{quote['quote']['text']}</blockquote>" +
                       "\n\n" +
                       f"{quote['quote']['source']}, {quote['quote']['reference']}" +
                       "\n\n" +
                       f"{lang.next_quote}: {self._format_time_minutes(lang, secs_next_quote, True)}",
            'buttons': [],
            'menu_commands': [],
            'image': None
        }

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