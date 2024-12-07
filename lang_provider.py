from dataclasses import dataclass
from typing import Optional

from users_orm import UsersOrm


@dataclass
class Lang:
    start_command: str
    button_all: str
    lang_code: str

    next_quote: str

    days_short: str
    hours_short: str
    minutes_short: str



ru = Lang(
    start_command="Выберите категорию цитат",
    button_all="Любой тематики",
    lang_code="ru",

    next_quote="Следующая цитата через ",

    days_short = "д",
    hours_short = "ч",
    minutes_short = "м"
)


class LangProvider:

    @staticmethod
    def get_available_languages() -> dict[str, Lang]:
        return {
            ru.lang_code: ru,
        }

    @staticmethod
    def get_lang_by_code(lang_code: str) -> Lang:
        return LangProvider.get_available_languages()[lang_code]