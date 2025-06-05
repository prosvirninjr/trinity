from aiogram_dialog import DialogManager

from orm.databases import RadioDatabase


async def settings_getter(dialog_manager: DialogManager, **kwargs: object) -> dict[str, object]:
    # Рекламодатели.
    rdb = RadioDatabase()
    advertisers = rdb.get_advertisers()
    panel: list[list[str]] = [[advertiser, advertiser] for advertiser in advertisers]

    return {
        'panel': panel,
    }
