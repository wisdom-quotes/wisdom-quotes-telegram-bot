import datetime
import random
from typing import Optional
from zoneinfo import ZoneInfo

from bloomfilter import BloomFilter

from quotes_loader import QuotesLoader, FlatQuote


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


    def pick_next_quote(self, top_level_categories: list[str], viewed_quotes_bloomfilter_hex: Optional[str]) -> (FlatQuote, str):
        suitable_quotes: list[FlatQuote] = []

        viewed_filter = BloomFilter(self._get_max_estimate(self._get_max_estimate(len(self.quotes_loader.flat_quotes))), 0.1)
        if viewed_quotes_bloomfilter_hex is not None:
            viewed_filter = viewed_filter.loads_from_hex(viewed_quotes_bloomfilter_hex)

        category_quotes = self.quotes_loader.filter_by_top_category(top_level_categories)
        for flat_quote in category_quotes:
            if not viewed_filter.might_contain(flat_quote['quote']['id']):
                suitable_quotes.append(flat_quote)

        if len(suitable_quotes) == 0 and viewed_quotes_bloomfilter_hex is not None:
            return self.pick_next_quote(top_level_categories, None)

        if len(suitable_quotes) == 0:
            return None, viewed_filter.dumps_to_hex()

        picked_quote = random.choice(suitable_quotes)
        viewed_filter.put(picked_quote['quote']['id'])
        return picked_quote, viewed_filter.dumps_to_hex()

    def _get_max_estimate(self, n: int):
        approx = 10
        for iter in range(0, 1000):
            if n < approx:
                return approx
            approx = approx * 10