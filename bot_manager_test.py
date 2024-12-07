import datetime
import os
import unittest
from unittest import mock
from zoneinfo import ZoneInfo

import time_machine

from bot_manager import BotManager
from user_settings_manager import parse_user_settings
from users_orm import UsersOrm


class TestHistory(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        try:
            os.unlink('test.db')
        except FileNotFoundError:
            pass
        self.users_orm = UsersOrm('test.db')
        self.bot_manager = BotManager('test.db', 'quotes', 'test', 'http://sample')
        self.maxDiff = None

    def tearDown(self):
        self.users_orm.__del__()
        try:
            os.unlink('test.db')
        except FileNotFoundError:
            pass

    def test_on_start_for_new_user(self):
        reply = self.bot_manager.on_start_command(123)
        self.assertEqual(reply, {'buttons': [{'data': 'category:buddhist',
                                              'text': 'Философия Буддизма',
                                              'url': None},
                                             {'data': 'category:stoic',
                                              'text': 'Философия стоицизма',
                                              'url': None},
                                             {'data': 'category:all', 'text': 'Все', 'url': None}],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'Выберите категорию цитат',
                                 'to_chat_id': 123})

    @time_machine.travel('2022-04-21T00:00:01Z', tick=False)
    def test_selection_of_category_renders_quote_from_that_category(self):
        with mock.patch('random.choice', lambda x: self.bot_manager.scheduler.quotes_loader.flat_quotes[0]):
            reply = self.bot_manager.on_data_provided(123, 'category:buddhist')
            self.assertEqual(reply, {'buttons': [],
                                     'image': None,
                                     'menu_commands': [],
                                     'message': '<blockquote>Существа – владельцы своих поступков, наследники '
                                                'своих поступков. Они происходят из своих поступков, связаны со '
                                                'своими поступками, имеют свои поступки своим прибежищем. Именно '
                                                'поступок разделяет людей на низших и высших</blockquote>\n'
                                                '\n'
                                                'Чулакаммавибханга-сутта, МН 135\n'
                                                '\n'
                                                'Следующая цитата через : 23ч 59м',
                                     'to_chat_id': 123})
        user = self.users_orm.get_user_by_id(123)
        settings = parse_user_settings(user['settings'])
        self.assertEqual(settings['categories'], ['buddhist'])
        self.assertEqual(user['next_quote_time'], datetime.datetime(2022, 4, 22, 0, 0, 0, tzinfo=ZoneInfo('UTC')))


