import json
import unittest

import time_machine

from settings_manager import parse_user_settings, serialize_user_settings


class TestHistory(unittest.IsolatedAsyncioTestCase):

    @time_machine.travel("2021-01-01 1:01:00Z")
    def test_deserialize_empty(self):
        self.assertEqual(parse_user_settings(""), {'categories': [],
                                                   'lang_code': 'ru',
                                                   'quote_times_mins': [60],
                                                   'resolved_user_timezone': 'UTC',
                                                   'user_timezone': 'UTC',
                                                   'user_timezone_offset_mins': 0,
                                                   'viewed_quotes_bloomfilter_base64': None})

    def test_deserialise_serialise(self):
        settings = {'categories': ['cat1', 'cat2'],
                    'lang_code': 'en',
                    'quote_times_mins': [61],
                    'resolved_user_timezone': 'UTC',
                    'user_timezone': 'UTC',
                    'user_timezone_offset_mins': 0,
                    'viewed_quotes_bloomfilter_base64': None}

        self.assertEqual(parse_user_settings(serialize_user_settings(settings)), settings)