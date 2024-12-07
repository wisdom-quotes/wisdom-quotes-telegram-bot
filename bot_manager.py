from typing import TypedDict, Optional
from zoneinfo import ZoneInfo

from lang_provider import LangProvider
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
        return []

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

            quote, new_filter = self.scheduler.pick_next_quote([f'{lang.lang_code}_{cat_key}' for cat_key in settings['categories']],
                                                               settings['viewed_quotes_bloomfilter_base64'])
            settings['viewed_quotes_bloomfilter_base64'] = new_filter

            user['next_quote_time'] = self.scheduler.calculate_next_quote_time(settings['quote_times_mins'], ZoneInfo(settings['resolved_user_timezone']))
            user['settings'] = serialize_user_settings(settings)

            print(settings)

            self.user_orm.upsert_user(user)

            return {
                'to_chat_id': chat_id,
                'message': f"<blockquote>{quote['quote']['text']}</blockquote>" +
                           "\n\n" +
                           f"{quote['quote']['source']}, {quote['quote']['reference']}",
                'buttons': [],
                'menu_commands': [],
                'image': None
            }