import datetime
import os
import unittest
from unittest import mock
from zoneinfo import ZoneInfo

import time_machine

from bot_manager import BotManager
from user_settings_manager import parse_user_settings, serialize_user_settings
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
                                              'text': 'Философия Стоицизма',
                                              'url': None},
                                             {'data': 'category:all', 'text': 'Любой тематики', 'url': None}],
                                 'image': None,
                                 'menu_commands': [('settings', 'Настройки')],
                                 'message': 'Выберите категорию цитат',
                                 'to_chat_id': 123})

    @time_machine.travel('2022-04-21T01:00:01Z', tick=False)
    def test_on_settings_command_for_non_existing_user(self):
        reply = self.bot_manager.on_settings_command(123)
        self.assertEqual(reply, {'buttons': [{'data': 'command:start',
                                              'text': 'Изменить категории',
                                              'url': None},
                                             {'text': 'Изменить время',
                                              'url': 'http://sample?mins=60&is_mins_tz=true&lang=ru&env=test'}],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'Настройки\n'
                                            '\n'
                                            'Выбранные категории: \n'
                                            'Время отправки цитат: 01:00 (+0)',
                                 'to_chat_id': 123})

    @time_machine.travel('2022-04-21T01:00:01Z', tick=False)
    def test_on_settings_command_for_existing_users(self):
        self.bot_manager.on_data_provided(123, 'category:buddhist')
        user = self.users_orm.get_user_by_id(123)
        settings = parse_user_settings(user['settings'])
        settings['quote_times_mins']  = [120, 240];
        settings['user_timezone'] = 'Asia/Novosibirsk'
        user['settings'] = serialize_user_settings(settings)
        self.users_orm.upsert_user(user)

        reply = self.bot_manager.on_settings_command(123)
        self.assertEqual(reply, {'buttons': [{'data': 'command:start',
                                              'text': 'Изменить категории',
                                              'url': None},
                                             {'text': 'Изменить время',
                                              'url': 'http://sample?mins=120,240&is_mins_tz=true&lang=ru&env=test'}],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'Настройки\n'
                                            '\n'
                                            'Выбранные категории: Философия Буддизма\n'
                                            'Время отправки цитат: 02:00, 04:00',
                                 'to_chat_id': 123})


    @time_machine.travel('2022-04-21T00:00:01Z', tick=False)
    def test_selection_of_category_renders_quote_from_that_category(self):
        with mock.patch('random.choice', lambda x: self.bot_manager.scheduler.quotes_loader.flat_quotes[0]):
            reply = self.bot_manager.on_data_provided(123, 'category:buddhist')
            self.assertEqual(reply, {'buttons': [],
                                     'image': None,
                                     'menu_commands': [],
                                     'message': '<b>Существа – владельцы своих поступков, наследники своих '
                                                'поступков. Они происходят из своих поступков, связаны со своими '
                                                'поступками, имеют свои поступки своим прибежищем. Именно поступок '
                                                'разделяет людей на низших и высших</b>\n'
                                                '\n'
                                                ' – <i>Чулакаммавибханга-сутта. МН 135</i>',
                                     'to_chat_id': 123})
        user = self.users_orm.get_user_by_id(123)
        settings = parse_user_settings(user['settings'])
        self.assertEqual(settings['categories'], ['buddhist'])
        self.assertEqual(user['next_quote_time'], datetime.datetime(2022, 4, 22, 0, 0, 0, tzinfo=ZoneInfo('UTC')))

    def test_on_start_command_renders_start(self):
        reply = self.bot_manager.on_data_provided(123, 'command:start')
        self.assertEqual(reply, {'buttons': [{'data': 'category:buddhist',
                                              'text': 'Философия Буддизма',
                                              'url': None},
                                             {'data': 'category:stoic',
                                              'text': 'Философия Стоицизма',
                                              'url': None},
                                             {'data': 'category:all', 'text': 'Любой тематики', 'url': None}],
                                 'image': None,
                                 'menu_commands': [('settings', 'Настройки')],
                                 'message': 'Выберите категорию цитат',
                                 'to_chat_id': 123})

    @time_machine.travel('2022-04-21T00:00:01Z', tick=False)
    def test_process_tick_sends_quote(self):
        with mock.patch('random.choice', lambda x: self.bot_manager.scheduler.quotes_loader.flat_quotes[0]):
            self.bot_manager.on_data_provided(123, 'category:buddhist')

            self.assertEqual(self.bot_manager.process_tick(), [])

            with time_machine.travel('2022-04-21T23:59:01Z'):
                self.assertEqual(self.bot_manager.process_tick(), [])

            with time_machine.travel('2022-04-22T00:59:01Z'):
                self.assertEqual(self.bot_manager.process_tick(), [{'buttons': [],
                                                                    'image': None,
                                                                    'menu_commands': [],
                                                                    'message': '<b>Существа – владельцы своих поступков, наследники своих '
                                                                               'поступков. Они происходят из своих поступков, связаны со своими '
                                                                               'поступками, имеют свои поступки своим прибежищем. Именно '
                                                                               'поступок разделяет людей на низших и высших</b>\n'
                                                                               '\n'
                                                                               ' – <i>Чулакаммавибханга-сутта. МН 135</i>',
                                                                    'to_chat_id': 123}])

            user = self.users_orm.get_user_by_id(123)
            self.assertEqual(user['next_quote_time'], datetime.datetime(2022, 4, 23, 0, 0, tzinfo=ZoneInfo('utc')))

    @time_machine.travel('2022-04-21T00:00:01Z', tick=False)
    def test_can_select_empty_categories(self):
        res = self.bot_manager.on_data_provided(123, 'categories:')
        self.assertEqual(res, {'buttons': [],
                               'image': None,
                               'menu_commands': [],
                               'message': 'Категории цитат обновлены: вы не выбрали ни одной категории',
                               'to_chat_id': 123})

        res = self.bot_manager.on_settings_command(123)
        self.assertEqual(res, {'buttons': [{'data': None,
                                            'text': 'Изменить категории',
                                            'url': 'http://sample?selected_categories=&lang=ru&env=test'},
                                           {'data': None,
                                            'text': 'Изменить время',
                                            'url': 'http://sample?mins=0&is_mins_tz=true&lang=ru&env=test'}],
                               'image': None,
                               'menu_commands': [],
                               'message': 'Настройки\n'
                                          '\n'
                                          'Выбранные категории: вы не выбрали ни одной категории\n'
                                          'Время отправки цитат: 00:00 (+0)',
                               'to_chat_id': 123})

    @time_machine.travel('2022-04-21T00:00:01Z', tick=False)
    def test_process_tick_updates_next_quote_if_no_categories(self):
        with mock.patch('random.choice', lambda x: self.bot_manager.scheduler.quotes_loader.flat_quotes[0]):
            self.bot_manager.on_data_provided(123, 'category:buddhist')
            user = self.users_orm.get_user_by_id(123)
            settings = parse_user_settings(user['settings'])
            settings['categories'] = []
            user['settings'] = serialize_user_settings(settings)
            self.users_orm.upsert_user(user)

            with time_machine.travel('2022-04-22T00:59:01Z'):
                self.assertEqual(self.bot_manager.process_tick(), [])

            user = self.users_orm.get_user_by_id(123)
            self.assertEqual(user['next_quote_time'], datetime.datetime(2022, 4, 23, 0, 0, tzinfo=ZoneInfo('utc')))

    @time_machine.travel('2022-04-21T00:00:01Z', tick=False)
    def test_time_updated(self):
        ret = self.bot_manager.on_data_provided(123, 'Sending ...{"times":"810,300","timeZone":"Australia/Sydney","offsetSecs":39600}')
        self.assertEqual(ret, {'buttons': [],
                               'image': None,
                               'menu_commands': [],
                               'message': 'Время цитат обновлено: 05:00, 13:30',
                               'to_chat_id': 123})
        user = self.users_orm.get_user_by_id(123)
        settings = parse_user_settings(user['settings'])
        self.assertEqual(settings['quote_times_mins'], [300, 810])
        self.assertEqual(settings['user_timezone'], 'Australia/Sydney')
        self.assertEqual(settings['resolved_user_timezone'], 'Australia/Sydney')
        self.assertEqual(user['next_quote_time'], datetime.datetime(2022, 4, 21, 13, 30, tzinfo=ZoneInfo('Australia/Sydney')))
