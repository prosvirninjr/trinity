import logging

from aiogram.types import Message

from app_settings import load_settings
from core.utils.tools import TextTools

settings = load_settings()

log = logging.getLogger(__name__)


async def xlsx_filter(message: Message) -> bool:
    """
    Проверяет документ на соответствие формату .xlsx.
    В случае успеха возвращает True, иначе False.

    Args:
        message: пользовательское сообщение.

    Returns:
        True, если документ соответствует формату .xlsx, иначе False.
    """
    user_id = message.chat.id  # type: ignore
    file_id = message.document.file_id  # type: ignore

    file_name: str | None = message.document.file_name  # type: ignore

    log.debug(f'Получен документ. [user_id:{user_id}] [file_id:{TextTools.to_trunc_string(file_id, max_length=10)}]')

    if not settings.LOCALHOST:
        MAX_FILE_SIZE = 20 * 1024 * 1024  # 10 MB

        if message.document.file_size > MAX_FILE_SIZE:  # type: ignore
            log.debug(
                f'Получен документ с превышающим лимит размером. Фильтр не пройден. [user_id:{user_id}] [file_id:{TextTools.to_trunc_string(file_id, max_length=10)}]'
            )
            return False

    if not file_name.lower().endswith('.xlsx'):  # type: ignore
        log.warning(
            f'Получен документ с неподдерживаемым форматом. Фильтр не пройден. [user_id:{user_id}] [file_id:{TextTools.to_trunc_string(file_id, max_length=10)}]'
        )
        return False

    log.debug(
        f'Документ соответствует формату .xlsx. Фильтр успешно пройден. [user_id:{user_id}] [file_id:{TextTools.to_trunc_string(file_id, max_length=10)}]'
    )
    return True
