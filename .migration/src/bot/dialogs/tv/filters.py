from aiogram.types import Message

from app_settings import AppSettings, load_settings
from core.tv.ru.tasks.mediascope.parser import parse_demo


async def xlsx_filter(message: Message) -> bool:
    """
    Проверяет документ на соответствие формату .xlsx и максимальному размеру файла.
    В случае успеха возвращает True, иначе False.

    Args:
        message: пользовательское сообщение.

    Returns:
        True, если документ соответствует формату .xlsx, иначе False.
    """
    file_name: str | None = message.document.file_name  # type: ignore

    app_settings: AppSettings = load_settings()

    if not app_settings.LOCALHOST:
        MAX_FILE_SIZE = 20 * 1024 * 1024  # 10 MB

        if message.document.file_size > MAX_FILE_SIZE:  # type: ignore
            return False

    if not file_name.lower().endswith('.xlsx'):  # type: ignore
        return False

    return True


async def txt_filter(message: Message) -> bool:
    """
    Проверяет документ на соответствие формату .txt и максимальному размеру файла.
    В случае успеха возвращает True, иначе False.

    Args:
        message: пользовательское сообщение.

    Returns:
        True, если документ соответствует формату .txt, иначе False.
    """
    if not message.document:
        return False

    file_name: str | None = message.document.file_name
    if not file_name:
        return False

    app_settings: AppSettings = load_settings()

    if not app_settings.LOCALHOST:
        MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

        if message.document.file_size > MAX_FILE_SIZE:  # type: ignore
            return False

    if not file_name.lower().endswith('.txt'):
        return False

    return True


def is_valid_audience(text: str) -> str:
    """
    Проверяет строку на соответствие формату демографической переменной.
    """
    audience = parse_demo(text)

    if audience is None:
        raise ValueError

    return text
