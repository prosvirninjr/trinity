import operator

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, Multiselect, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from bot.dialogs.radio_settings import getters, handlers, states

radio_settings_dialog = Dialog(
    Window(
        Const(text='Настройки Радио'),
        SwitchTo(
            Const('→ Панель'),
            id='_go_panel_window',
            state=states.RadioSettingsSG.window_panel,
        ),
        Cancel(Const('✗ Закрыть окно'), id='_cancel'),
        state=states.RadioSettingsSG.window_start,
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
            state=states.RadioSettingsSG.window_start,
        ),
        state=states.RadioSettingsSG.window_panel,
    ),
    getter=getters.settings_getter,
)
