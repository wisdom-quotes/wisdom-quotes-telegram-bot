import os
import unittest

from bot_manager import BotManager
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
        self.assertEqual(reply, {'buttons': [{'data': 'buddhist', 'text': 'Философия Буддизма', 'url': None},
                                             {'data': 'stoic', 'text': 'Философия стоицизма', 'url': None}],
                                 'image': None,
                                 'menu_commands': [],
                                 'message': 'Выберите категорию цитат',
                                 'to_chat_id': 123})