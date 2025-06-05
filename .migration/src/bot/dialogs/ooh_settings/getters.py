from dataclasses import fields

from aiogram_dialog import DialogManager

from core.ooh.schema import CMethod, SMethod, Years
from orm.databases import OOHDatabase


async def settings_getter(dialog_manager: DialogManager, **kwargs: object) -> dict[str, object]:
    # Рекламодатели.
    db = OOHDatabase()
    advertisers = db.get_advertisers()
    panel: list[list[str]] = [[advertiser, advertiser] for advertiser in advertisers]

    # Методы расчета.
    c_methods: list[list[str]] = [[item.default, item.default] for item in fields(CMethod)]  # type: ignore

    # Методы сглаживания.
    s_methods: list[list[str]] = [[item.default, item.default] for item in fields(SMethod)]  # type: ignore

    # Годы инфляции.
    target_years: list[list[int]] = [[item.default, item.default] for item in fields(Years)]  # type: ignore

    return {
        'panel': panel,
        's_methods': s_methods,
        'c_methods': c_methods,
        'target_years': target_years,
    }
