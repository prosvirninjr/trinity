from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, ManagedMultiselect

from orm.databases import RadioDatabase
from orm.settings import ESettings
from orm.sql_builder import get_engine
from orm.sql_queries import select_employee, update_employee
from orm.sql_tables import Employee

engine = get_engine()


async def drop_panel(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    """Хендлер сброса панели."""
    try:
        # Получаем объект виджета.
        _panel: ManagedMultiselect = dialog_manager.find('_panel')  # type: ignore

        # Сбрасываем все выбранные элементы виджета.
        await _panel.reset_checked()

        employee: Employee = select_employee(engine=engine, tg_id=callback.from_user.id)  # type: ignore
        e_settings = ESettings.model_validate(employee.settings)

        e_settings.radio.panel = []

        # Сбрасываем панель в базе данных.
        update_employee(engine=engine, tg_id=callback.from_user.id, settings=e_settings.model_dump())
    except Exception:
        await callback.answer('Не удалось сбросить панель. Внутреняя ошибка.')
    finally:
        return


async def fill_panel(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    """Хендлер заполнения панели."""
    try:
        # Получаем объект виджета.
        _panel: ManagedMultiselect = dialog_manager.find('_panel')  # type: ignore

        rdb = RadioDatabase()

        advertisers = rdb.get_advertisers()

        for advertiser in advertisers:
            await _panel.set_checked(advertiser, checked=True)  # type: ignore

        employee: Employee = select_employee(engine=engine, tg_id=callback.from_user.id)  # type: ignore
        e_settings = ESettings.model_validate(employee.settings)

        e_settings.radio.panel = advertisers

        # Сбрасываем панель в базе данных.
        update_employee(engine=engine, tg_id=callback.from_user.id, settings=e_settings.model_dump())
    except Exception:
        await callback.answer('Не удалось сбросить панель. Внутреняя ошибка.')
    finally:
        return


async def update_panel(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item_id: str) -> None:
    """Хендлер обновления панели."""
    try:
        # Получаем объект виджета.
        _panel: ManagedMultiselect = dialog_manager.find('_panel')  # type: ignore

        # Получаем все выбранные элементы виджета.
        panel: list[str] = _panel.get_checked()

        employee: Employee = select_employee(engine=engine, tg_id=callback.from_user.id)  # type: ignore
        e_settings = ESettings.model_validate(employee.settings)

        e_settings.radio.panel = panel

        # Обновляем панель в базе данных.
        update_employee(engine=engine, tg_id=callback.from_user.id, settings=e_settings.model_dump())
    except Exception:
        await callback.answer('Не удалось обновить панель. Внутреняя ошибка.')
    finally:
        return
