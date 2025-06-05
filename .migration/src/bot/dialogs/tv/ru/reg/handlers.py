import asyncio
import logging
from datetime import date, datetime
from textwrap import dedent

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Button

from bot.utils.actions import send_action

from .reg_tasks import run_reg_affinity_task, run_reg_base_task

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def handle_base_task(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    """
    Хендлер обработки основной выгрузки национального ТВ.

    При успешной загрузке файла закрывает диалог и возвращает результат в виде словаря с id файла.
    """
    bot: Bot = message.bot  # type: ignore
    chat_id: int = message.chat.id

    file_id: str = message.document.file_id  # type: ignore
    result_file_name: str = message.document.file_name  # type: ignore

    # Сообщение к результату
    caption: str = 'Задача завершена'

    # Запуск задачи
    task = asyncio.create_task(
        run_reg_base_task(
            bot,
            chat_id,
            file_id,
            result_file_name,
            caption,
        )
    )

    # Запуск анимации
    asyncio.create_task(send_action(message.bot, message.from_user.id, task))  # type: ignore

    await message.answer('Ожидайте завершения задачи')
    await dialog_manager.done()
    return


async def handle_text(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    """
    Хендлер обработки текста.

    При загрузке текста просто игнорирует его.
    """
    text = dedent(
        """
        Получен текст, ожидается файл.
        
        Пожалуйста, загрузите файл.
        """
    )

    # Устанавливаем режим отображения диалога, чтобы избежать повторного отправления сообщения
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
        Документ не соответствует ожидаемому формату или его размер превышает допустимый.

        Пожалуйста, загрузите файл повторно.
        """
    )

    # Устанавливаем режим отображения диалога, чтобы избежать повторного отправления сообщения
    dialog_manager.show_mode = ShowMode.NO_UPDATE

    await message.answer(text)
    return


async def handle_valid_audience(message: Message, widget: TextInput, dialog_manager: DialogManager, text: str) -> None:
    dialog_manager.dialog_data['audience'] = text
    await dialog_manager.next()


async def handle_invalid_audience(
    message: Message, widget: TextInput, dialog_manager: DialogManager, error: ValueError
) -> None:
    # Устанавливаем режим отображения диалога, чтобы избежать повторного отправления сообщения
    dialog_manager.show_mode = ShowMode.NO_UPDATE

    text = dedent(
        """
        Целевая аудитория не распознана.

        Целевая аудитория должна содержать:
        - Пол (M, W или All)
        - Возраст
            - Нижняя граница
            - Верхняя граница (опционально)
        - Группа дохода (опционально)
        - Уровень дохода (опционально)

        Примеры:
        - All 18+ (Все 18+)
        - W 18+ (Женщины от 18 лет)
        - M 18-35 (Мужчины от 18 до 35 лет)
        - All 18-54 BC (Все от 18 до 54 лет, группа дохода B и C)
        - W 18-54 IL 3-5 (Женщины от 18 до 54 лет, уровень дохода 3-5)

        Пожалуйста, попробуйте еще раз.
        """
    )

    await message.answer(text)
    return


async def handle_start_date(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager, chosen_date: date
) -> None:
    start_date = chosen_date.strftime('%Y-%m-%d')

    # WARNING: Данные в диалоге хранятся как JSON, поэтому сохранять объекты напрямую нельзя
    dialog_manager.dialog_data['start_date'] = start_date

    await callback.answer(f'Выбрана дата начала: {start_date}')

    await dialog_manager.next()


async def handle_end_date(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager, chosen_date: date
) -> None:
    end_date = chosen_date.strftime('%Y-%m-%d')

    # WARNING: Данные в диалоге хранятся как JSON, поэтому сохранять объекты напрямую нельзя
    dialog_manager.dialog_data['end_date'] = end_date

    await callback.answer(f'Выбрана дата окончания: {end_date}')
    await dialog_manager.next()


async def handle_confirm_affinity(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    bot: Bot = callback.bot  # type: ignore
    chat_id: int = callback.message.chat.id  # type: ignore

    caption = 'Задача завершена'
    audience = dialog_manager.dialog_data['audience']
    start_date = datetime.fromisoformat(dialog_manager.dialog_data['start_date'])
    end_date = datetime.fromisoformat(dialog_manager.dialog_data['end_date'])

    # Расчет задачи
    task = asyncio.create_task(
        run_reg_affinity_task(
            bot,
            chat_id,
            caption,
            start_date=start_date,
            end_date=end_date,
            audience=audience,
        )
    )

    # Запуск анимации
    asyncio.create_task(send_action(callback.bot, callback.from_user.id, task))  # type: ignore

    # Редактируем сообщение и завершаем диалог.
    text = dedent(
        f"""
        Задача отправлена на расчет:

        Параметры задачи:
        - Целевая аудитория: {audience}
        - Дата начала: {start_date.strftime('%Y-%m-%d')}
        - Дата окончания: {end_date.strftime('%Y-%m-%d')}

        Пожалуйста, ожидайте завершения.
        """
    )

    await callback.message.edit_text(text)  # type: ignore

    await dialog_manager.done()


async def handle_cancel(callback: CallbackQuery, button: Button, dialog_manager: DialogManager) -> None:
    """
    Хендлер обработки отмены диалога.
    """
    await callback.message.edit_text('Задача отменена.')  # type: ignore
