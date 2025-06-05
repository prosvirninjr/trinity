from io import BytesIO

import polars as pl
from aiogram import Bot
from aiogram.types import BufferedInputFile, File

from app_settings import load_settings
from bot.utils.sync_executor import run_in_process
from core.radio.exceptions import RadioDataError
from core.radio.models import RadioTable
from core.radio.radio_loader import load_radio_template
from core.radio.report import create_report
from orm.settings import ESettings
from orm.sql_builder import get_engine
from orm.sql_queries import select_employee

engine = get_engine()


settings = load_settings()


def _process_template(df: pl.DataFrame) -> pl.DataFrame:
    # Длительная операция, поэтому используем отдельный поток.
    df_table = RadioTable(df)
    df_table.process_template()

    return df_table.get_df()


async def do_radio_task(
    bot: Bot,
    user_id: int,
    chat_id: int,
    file_id: str,
    output_name: str,
    caption: str,
) -> None:
    """
    Выполняет шаги подготовки и запуска основной задачи обработки выгрузки.

    1. Асинхронно получает информацию о файле и скачивает его.
    2. Запускает чтение Excel в отдельном процессе.
    3. Запускает основную обработку в отдельном процессе и отправляет результат.
    """

    # NOTE: Скачивание файла.
    file_info: File = await bot.get_file(file_id=file_id)
    file_io: BytesIO = await bot.download_file(file_info.file_path)  # type: ignore
    file_io.seek(0)

    try:
        # NOTE: Чтение файла в отдельном процессе.
        template: pl.DataFrame = await run_in_process(load_radio_template, file_io)  # type: ignore
    except RadioDataError:
        # Нельзя использовать пробелы в имени smart-table.
        await bot.send_message(chat_id=chat_id, text='Ошибки в данных. Проверьте файл.')
        return

    # NOTE: Обработка шаблона.
    template: pl.DataFrame = await run_in_process(_process_template, template)

    # NOTE: Загрузка настроек пользователя и базы данных.
    employee = select_employee(engine, tg_id=user_id)  # type: ignore
    employee_settings = ESettings.model_validate(employee.settings)  # type: ignore

    # NOTE: Запуск задачи в отдельном процессе
    try:
        result: bytes = await run_in_process(create_report, df=template, radio_settings=employee_settings.radio)
    except Exception:
        await bot.send_message(chat_id=chat_id, text='Не удалось запустить задачу.')
        return

    # NOTE: Отправляем результат выполнения задачи.
    document = BufferedInputFile(result, filename=f'+{output_name}.xlsx')

    try:
        await bot.send_document(chat_id=chat_id, document=document, caption=caption)
    except Exception:
        await bot.send_message(chat_id=chat_id, text='Не удалось отправить файл.')
        return
