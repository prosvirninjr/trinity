from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Const

from bot.dialogs.ooh import handlers
from bot.dialogs.ooh.filters import xlsx_filter
from bot.dialogs.ooh.states import OOHTaskSG

ooh_task_dialog = Dialog(
    Window(
        Const(text='Загрузите файл .xlsx.'),
        MessageInput(content_types=ContentType.DOCUMENT, filter=xlsx_filter, func=handlers.handle_ooh_task),
        MessageInput(content_types=ContentType.TEXT, func=handlers.handle_text),
        MessageInput(content_types=ContentType.ANY, func=handlers.handle_trash),
        state=OOHTaskSG.window_start,
    ),
)
