from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Const

from bot.dialogs.radio import handlers
from bot.dialogs.radio.filters import xlsx_filter
from bot.dialogs.radio.states import RadioTaskSG

radio_dialog = Dialog(
    Window(
        Const(text='Загрузите файл .xlsx.'),
        MessageInput(content_types=ContentType.DOCUMENT, filter=xlsx_filter, func=handlers.handle_radio_task),
        MessageInput(content_types=ContentType.TEXT, func=handlers.handle_text),
        MessageInput(content_types=ContentType.ANY, func=handlers.handle_trash),
        state=RadioTaskSG.window_start,
    ),
)
