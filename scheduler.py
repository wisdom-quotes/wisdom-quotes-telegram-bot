import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from quotes_loader import QuotesLoader


class Scheduler:
    def __init__(self, quotes_dir: str):
        self.quotes_loader = QuotesLoader(quotes_dir)

    def calculate_next_quote_time(self, quote_times_mins: list[int], time_zone: ZoneInfo) -> Optional[datetime.datetime]:
        quote_times_mins.sort()
        cursor = datetime.datetime.now(tz=time_zone) - datetime.timedelta(days=1)
        cursor = cursor.replace(second=0, microsecond=0)
        now = datetime.datetime.now(tz=time_zone)
        for dayNo in range(0, 3):
            for maybe_mins in quote_times_mins:
                maybe_time = cursor.replace(hour=maybe_mins // 60, minute=maybe_mins % 60)
                if now.timestamp() < maybe_time.timestamp():
                    return maybe_time
            cursor = cursor + datetime.timedelta(days=1)
        return None

