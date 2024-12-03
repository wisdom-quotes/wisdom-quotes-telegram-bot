import datetime
import json
from typing import TypedDict, Optional


class UserSettings(TypedDict):
    lang_code: str
    categories: list[str]
    viewed_quotes: list[str]
    user_timezone: str
    user_offset_mins: int
    quote_times_mins: list[int]
    resolved_timezone: str

def parse_user_settings(settings_json_str: str):
    if len(settings_json_str) == 0:
        now_utc = datetime.datetime.now().astimezone(tz=datetime.timezone.utc)
        minutes = now_utc.hour * 60 + now_utc.minute
        return UserSettings(lang_code='ru', categories=[], viewed_quotes=[], user_timezone='UTC', user_offset_mins=0, quote_times_mins=[minutes], resolved_timezone='UTC')

    settings = json.loads(settings_json_str)
    return UserSettings(
        lang_code=settings.get('lang_code', None),
        categories=settings.get('categories', []),
        viewed_quotes=settings.get('viewed_quotes', []),
        user_timezone=settings.get('user_timezone', 'UTC'),
        user_offset_mins=settings.get('user_offset_mins', 0),
        quote_times_mins=settings.get('quote_times_mins', []),
        resolved_timezone=settings.get('resolved_timezone', 'UTC')
    )

def serialize_user_settings(user_settings: UserSettings) -> str:
    return json.dumps(user_settings)