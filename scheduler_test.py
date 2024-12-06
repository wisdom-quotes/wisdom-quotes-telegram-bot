import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

import time_machine

from scheduler import Scheduler


class TestHistory(unittest.IsolatedAsyncioTestCase):

    @time_machine.travel("2021-01-01 13:10:00Z", tick=False)
    def test_scheduler_should_calculate_next_quote_time(self):
        self.assertEqual(datetime.now(ZoneInfo("Australia/Sydney")), datetime(2021, 1, 2, 0, 10, tzinfo=ZoneInfo(key='Australia/Sydney')))

        next_time = Scheduler("quotes-test").calculate_next_quote_time([15*60 + 30, 16 * 60 + 30], ZoneInfo("Australia/Sydney"))
        self.assertEqual(next_time,
                         datetime(2021, 1, 2, 15, 30, tzinfo=ZoneInfo(key='Australia/Sydney'))
                         )

        with time_machine.travel("2021-01-02 04:40:00Z", tick=False):
            self.assertEqual(datetime.now(ZoneInfo("Australia/Sydney")), datetime(2021, 1, 2, 15, 40, tzinfo=ZoneInfo(key='Australia/Sydney')))

            next_time = Scheduler("quotes-test").calculate_next_quote_time([15*60 + 30, 16 * 60 + 30], ZoneInfo("Australia/Sydney"))
            self.assertEqual(next_time,
                             datetime(2021, 1, 2, 16, 30, tzinfo=ZoneInfo(key='Australia/Sydney'))
                             )

        with time_machine.travel("2021-01-02 05:40:00Z", tick=False):
            self.assertEqual(datetime.now(ZoneInfo("Australia/Sydney")), datetime(2021, 1, 2, 16, 40, tzinfo=ZoneInfo(key='Australia/Sydney')))

            next_time = Scheduler("quotes-test").calculate_next_quote_time([15*60 + 30, 16 * 60 + 30], ZoneInfo("Australia/Sydney"))
            self.assertEqual(next_time,
                             datetime(2021, 1, 3, 15, 30, tzinfo=ZoneInfo(key='Australia/Sydney'))
                             )