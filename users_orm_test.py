import datetime
import os
import unittest

from users_orm import UsersOrm


class TestHistory(unittest.IsolatedAsyncioTestCase):

    users_orm: UsersOrm

    def setUp(self):
        try:
            os.unlink('test.db')
        except FileNotFoundError:
            pass
        self.users_orm = UsersOrm('test.db')
        self.maxDiff = None

    def tearDown(self):
        self.users_orm.__del__()
        try:
            os.unlink('test.db')
        except FileNotFoundError:
            pass

    def test_get_user_no_data(self):
        self.assertEqual(self.users_orm.get_user_by_id(123), {'next_quote_time': None, 'settings': '', 'user_id': 123})

    def test_upsert_creates_user(self):
        self.users_orm.upsert_user({'next_quote_time': datetime.datetime(2021, 1, 2, 3, 4, 5), 'settings': 'blah', 'user_id': 123})
        self.assertEqual(self.users_orm.get_user_by_id(123), {
            'next_quote_time': datetime.datetime(2021, 1, 2, 3, 4, 5).astimezone(tz=datetime.timezone.utc),
            'settings': 'blah',
            'user_id': 123
        })

    def test_upsert_creates_user_no_quote_time(self):
        self.users_orm.upsert_user({'next_quote_time': None, 'settings': 'blah', 'user_id': 123})
        self.assertEqual(self.users_orm.get_user_by_id(123), {
            'next_quote_time': None,
            'settings': 'blah',
            'user_id': 123
        })

    def test_upsert_updates_user(self):
        self.users_orm.upsert_user({'next_quote_time': datetime.datetime(2021, 1, 2, 3, 4, 5), 'settings': 'blah', 'user_id': 123})
        user = self.users_orm.get_user_by_id(123)
        user['next_quote_time'] = datetime.datetime(2021, 1, 2, 3, 4, 6)
        user['settings'] = 'blahblah'
        self.users_orm.upsert_user(user)
        self.assertEqual(self.users_orm.get_user_by_id(123), {
            'next_quote_time': datetime.datetime(2021, 1, 2, 3, 4, 6).astimezone(tz=datetime.timezone.utc),
            'settings': 'blahblah',
            'user_id': 123
        })

    def test_get_some_users_for_quote_should_not_return_ineligible_users(self):
        self.users_orm.upsert_user({'next_quote_time': datetime.datetime(2040, 1, 2, 3, 4, 5), 'settings': 'blah', 'user_id': 123})
        self.users_orm.upsert_user({'next_quote_time': None, 'settings': 'blah', 'user_id': 124})

        self.assertEqual(self.users_orm.get_some_users_for_quote(1), [])

    def test_get_some_users_for_quote_should_return_ilegible_users(self):
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        self.users_orm.upsert_user({'next_quote_time': yesterday, 'settings': 'blah', 'user_id': 123})

        self.assertEqual(self.users_orm.get_some_users_for_quote(1), [
            {'next_quote_time': yesterday.astimezone(tz=datetime.timezone.utc), 'settings': 'blah', 'user_id': 123}])

