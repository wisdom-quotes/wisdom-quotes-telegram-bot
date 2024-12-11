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

    menu_settings: str

    settings_command: str
    button_categories: str
    button_time: str

    time_updated: str

    categories_updated: str
    no_categories: str

ru = Lang(
    start_command="Выберите категорию цитат",
    button_all="Любой тематики",
    lang_code="ru",

    next_quote="Следующая цитата через ",

    days_short = "д",
    hours_short = "ч",
    minutes_short = "м",

    menu_settings = "Настройки",

    settings_command =('Настройки\n'
                       '\n'
                       'Выбранные категории: {categories}\n'
                       'Время отправки цитат: {time}'),
    button_categories = 'Изменить категории',
    button_time = 'Изменить время',

    time_updated="Время цитат обновлено: {time}",

    categories_updated="Категории цитат обновлены: {categories}",
    no_categories = "вы не выбрали ни одной категории",
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
