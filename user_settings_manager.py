import datetime
import json
from typing import TypedDict, Optional


class UserSettings(TypedDict):
    lang_code: str
    categories: list[str]
    viewed_quotes_bloomfilter_base64: Optional[str]
    user_timezone: str
    resolved_user_timezone: str
    user_timezone_offset_mins: int
    quote_times_mins: list[int]

def parse_user_settings(settings_json_str: str) -> UserSettings:
    now_utc = datetime.datetime.now().astimezone(tz=datetime.timezone.utc)
    minutes = now_utc.hour * 60 + now_utc.minute

    settings = json.loads(settings_json_str) if len(settings_json_str) > 0 else {}
    return UserSettings(
        lang_code=settings.get('lang_code', "ru"),
        categories=settings.get('categories', []),
        viewed_quotes_bloomfilter_base64=settings.get('viewed_quotes_bloomfilter_base64', None),
        user_timezone=settings.get('user_timezone', 'UTC'),
        resolved_user_timezone=settings.get('resolved_user_timezone', 'UTC'),
        user_timezone_offset_mins=settings.get('user_timezone_offset_mins', 0),
        quote_times_mins=settings.get('quote_times_mins', [(minutes // 30) * 30]),
    )

def serialize_user_settings(user_settings: UserSettings) -> str:
    return json.dumps(user_settings)