from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Calendar, Cancel
from aiogram_dialog.widgets.text import Const, Format, List

from ... import filters

from .. import getters, states, tools

from . import handlers

# Диалог для обработки базовой выгрузки
nat_base_task_dialog = Dialog(
    Window(
        Const(text='Загрузите файл .txt'),
        MessageInput(
            content_types=ContentType.DOCUMENT,
            filter=filters.txt_filter,
            func=handlers.handle_base_task,
        ),
        MessageInput(
            content_types=ContentType.TEXT,
            func=handlers.handle_text,
        ),
        MessageInput(
            content_types=ContentType.ANY,
            func=handlers.handle_trash,
        ),
        state=states.NatBaseTaskSG.window_start,
    ),
)

# Диалог для выгрузки Affinity
nat_affinity_task_dialog = Dialog(
    Window(
        Const(text='Введите целевую аудиторию'),
        TextInput(
            id='_audience',
            type_factory=filters.is_valid_audience,
            on_success=handlers.handle_valid_audience,  # type: ignore
            on_error=handlers.handle_invalid_audience,  # type: ignore
        ),
        MessageInput(
            content_types=ContentType.ANY,
            func=handlers.handle_trash,
        ),
        state=states.NatAffinityTaskSG.window_audience,
    ),
    Window(
        Const(text='Выбрете дату начала'),
        Calendar(
            id='_start_date',
            on_click=handlers.handle_start_date,  # type: ignore
            config=tools.create_calendar_config(
                *tools.get_available_period(0),  # type: ignore
            ),
        ),
        Cancel(Const('✗ Отмена'), id='_cancel', on_click=handlers.handle_cancel),
        state=states.NatAffinityTaskSG.window_start_date,
    ),
    Window(
        Const(text='Выбрете дату окончания'),
        Calendar(
            id='_end_date',
            on_click=handlers.handle_end_date,  # type: ignore
            config=tools.create_calendar_config(
                *tools.get_available_period(0),  # type: ignore
            ),
        ),
        Cancel(Const('✗ Отмена'), id='_cancel', on_click=handlers.handle_cancel),
        state=states.NatAffinityTaskSG.window_end_date,
    ),
    Window(
        Const('Подтвердите выбор\n'),
        Const('Параметры задачи:'),
        List(
            Format('- {item[0]}: {item[1]}'),
            items='affinity_params',
        ),
        Button(
            Const('Отправить задачу'),
            id='_confirm',
            on_click=handlers.handle_confirm_affinity,
        ),
        Cancel(Const('✗ Отмена'), id='_cancel', on_click=handlers.handle_cancel),
        state=states.NatAffinityTaskSG.window_confirm,
        getter=getters.affinity_task,
    ),
)
