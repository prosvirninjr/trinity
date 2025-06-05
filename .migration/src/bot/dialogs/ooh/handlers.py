import asyncio
import logging
from textwrap import dedent

from aiogram import Bot
from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput

from bot.dialogs.ooh.task import do_ooh_task
from bot.utils.actions import send_action

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def handle_ooh_task(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    """
    Хендлер обработки файла.

    При успешной загрузке файла закрывает диалог и возвращает результат в виде словаря с id файла.
    """
    bot: Bot = message.bot  # type: ignore

    user_id: int = message.from_user.id  # type: ignore
    chat_id: int = message.chat.id  # type: ignore
    file_id: str = message.document.file_id  # type: ignore
    file_name: str = message.document.file_name  # type: ignore

    caption: str = 'Расчет завершен.'

    task = asyncio.create_task(
        do_ooh_task(
            bot=bot,
            user_id=user_id,
            chat_id=chat_id,
            file_id=file_id,
            output_name=file_name.removesuffix('.xlsx'),
            caption=caption,
        )
    )

    asyncio.create_task(send_action(message.bot, chat_id=message.from_user.id, task=task))  # type: ignore

    await message.answer('Расчет начат. Ожидайте завершения.')

    await dialog_manager.done()
    return


async def handle_text(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    """
    Хендлер обработки текста.

    При загрузке текста просто игнорирует его.
    """
    text = dedent(
        """
        Получен текст, в то время как ожидается файл.
        
        Загрузите файл .xlsx.
        """
    )
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.answer(text)
    return


async def handle_trash(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    """
    Хендлер обработки мусора.

    При загрузке мусора просто игнорирует его.
    """
    text = dedent(
        """
        Документ не соответствует формату .xlsx или его размер превышает допустимый. 
        
        Загрузите файл .xlsx.
        """
    )
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.answer(text)
    return
