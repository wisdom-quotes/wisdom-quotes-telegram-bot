import json
import unittest

import time_machine

from settings_manager import parse_user_settings, serialize_user_settings


class TestHistory(unittest.IsolatedAsyncioTestCase):

    @time_machine.travel("2021-01-01 1:01:00Z")
    def test_deserialize_empty(self):
        self.assertEqual(parse_user_settings(""), {'lang_code': 'ru',
                                                   'categories': [],
                                                   'quote_times_mins': [61],
                                                   'resolved_timezone': 'UTC',
                                                   'user_offset_mins': 0,
                                                   'user_timezone': 'UTC',
                                                   'viewed_quotes': []})

    def test_deserialize(self):
        self.assertEqual(parse_user_settings('{"lang_code": "en", "categories": ["cat1", "cat2"], "viewed_quotes": ["quote1", "quote2"], '
                                            '"user_timezone": "Europe/Moscow", "user_offset_mins": 180, "quote_times_mins": [0, 1, 2], '
                                            '"resolved_timezone": "Europe/Moscow"}'), {'lang_code': 'en', 'categories': ['cat1', 'cat2'],
                                                                                  'quote_times_mins': [0, 1, 2],
                                                                                  'resolved_timezone': 'Europe/Moscow',
                                                                                  'user_offset_mins': 180,
                                                                                  'user_timezone': 'Europe/Moscow',
                                                                                  'viewed_quotes': ['quote1', 'quote2']})

    def test_serialize(self):
        settings = {'lang_code': 'en', 'categories': ['cat1', 'cat2'],
         'quote_times_mins': [61],
         'resolved_timezone': 'UTC',
         'user_offset_mins': 0,
         'user_timezone': 'UTC',
         'viewed_quotes': ['quote1', 'quote2']}

        self.assertEqual(parse_user_settings(serialize_user_settings(settings)), settings)