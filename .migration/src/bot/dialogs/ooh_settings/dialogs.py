import operator

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, CalendarConfig, Cancel, Group, Multiselect, Radio, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.ooh_settings import getters, handlers, states
from orm.databases import OOHDatabase

odb = OOHDatabase()

min_date, max_date = odb.get_available_period()

# --- Кастомная конфигурация календаря ---
ooh_calendar = CalendarConfig(
    min_date=min_date.date(),
    max_date=max_date.date(),
    firstweekday=0,  # Понедельник - первый день.
    month_columns=3,
)

ooh_settings_dialog = Dialog(
    Window(
        Const(text='Настройки OOH'),
        SwitchTo(
            Const('→ Панель'),
            id='_go_panel_window',
            state=states.OOHSettingsSG.window_panel,
        ),
        SwitchTo(
            Const('→ Метод расчета'),
            id='_go_c_method_window',
            state=states.OOHSettingsSG.window_c_method,
        ),
        SwitchTo(
            Const('→ Метод сглаживания'),
            id='_go_s_method_window',
            state=states.OOHSettingsSG.window_s_method,
        ),
        SwitchTo(
            Const('→ Год инфляции'),
            id='_go_inflation_window',
            state=states.OOHSettingsSG.window_target_year,
        ),
        Cancel(Const('✗ Закрыть окно'), id='_cancel'),
        state=states.OOHSettingsSG.window_start,
    ),
    Window(
        Const('Панель'),
        Group(
            Multiselect(
                Format('✓ {item[0]}'),
                Format(' {item[0]}'),
                id='_panel',
                items='panel',
                item_id_getter=operator.itemgetter(1),
                on_state_changed=handlers.update_panel,  # type: ignore
            ),
            width=3,
        ),
        Row(
            Button(Const('↻ Все'), id='_fill_panel', on_click=handlers.fill_panel),
        ),
        Row(
            Button(Const('↺ Сброс'), id='_drop_panel', on_click=handlers.drop_panel),
        ),
        SwitchTo(
            Const('← Назад'),
            id='_go_settings_window',
            state=states.OOHSettingsSG.window_start,
        ),
        state=states.OOHSettingsSG.window_panel,
    ),
    Window(
        Const('Метод расчета'),
        Group(
            Radio(
                checked_text=Format('✓ {item[0]}'),
                unchecked_text=Format(' {item[0]}'),
                id='_c_method',
                items='c_methods',
                item_id_getter=operator.itemgetter(1),
                on_state_changed=handlers.update_c_method,  # type: ignore
            ),
            width=1,
        ),
        SwitchTo(
            Const('← Назад'),
            id='_go_settings_window',
            state=states.OOHSettingsSG.window_start,
        ),
        state=states.OOHSettingsSG.window_c_method,
    ),
    Window(
        Const('Метод сглаживания'),
        Group(
            Radio(
                checked_text=Format('✓ {item[0]}'),
                unchecked_text=Format(' {item[0]}'),
                id='_s_method',
                items='s_methods',
                item_id_getter=operator.itemgetter(1),
                on_state_changed=handlers.update_s_method,  # type: ignore
            ),
            width=1,
        ),
        SwitchTo(
            Const('← Назад'),
            id='_go_settings_window',
            state=states.OOHSettingsSG.window_start,
        ),
        state=states.OOHSettingsSG.window_s_method,
    ),
    Window(
        Const('Год инфляции'),
        Group(
            Radio(
                checked_text=Format('✓ {item[0]}'),
                unchecked_text=Format(' {item[0]}'),
                id='_target_year',
                items='target_years',
                item_id_getter=operator.itemgetter(1),
                on_state_changed=handlers.update_target_year,  # type: ignore
            ),
            width=1,
        ),
        SwitchTo(
            Const('← Назад'),
            id='_go_settings_window',
            state=states.OOHSettingsSG.window_start,
        ),
        state=states.OOHSettingsSG.window_target_year,
    ),
    getter=getters.settings_getter,
)
