import asyncio
import logging
from datetime import datetime
from io import BytesIO

import polars as pl
from aiogram import Bot
from aiogram.types import BufferedInputFile, File

from bot.utils.sync_executor import run_in_process
from core.tv.ru.tasks.local.nat_tasks import nat_base_task
from core.tv.ru.tasks.mediascope.nat_tasks import nat_affinity_task
from core.utils.xlsx.xlsx_builder import FormatKey
from core.utils.xlsx.xlsx_creator import create_workbook

log = logging.getLogger(__name__)


async def run_nat_base_task(
    bot: Bot,
    chat_id: int,
    file_id: str,
    file_name: str,
    caption: str,
) -> None:
    """
    Выполняет задачу в отдельном процессе и отправляет результат в чат.

    Args:
        chat_id: Идентификатор чата.
        file_id: Идентификатор файла.
        file_name: Имя файла.
        caption: Подпись к файлу.
    """
    # Скачивание файла
    file_info: File = await bot.get_file(file_id=file_id)
    file_io: BytesIO = await bot.download_file(file_info.file_path)  # type: ignore

    try:
        df: pl.DataFrame = await run_in_process(
            pl.read_csv, file_io, separator='\t', has_header=False, quote_char=None, encoding='cp1251'
        )
    except Exception:
        log.exception('Не удалось открыть файл')
        await bot.send_message(
            chat_id=chat_id,
            text='Не удалось открыть файл',
        )
        return

    # Запуск задачи в отдельном процессе
    try:
        result: pl.DataFrame = await run_in_process(nat_base_task, df)
    except Exception:
        log.exception('Не удалось запустить задачу')
        await bot.send_message(
            chat_id=chat_id,
            text='Не удалось запустить задачу',
        )
        return

    # Завершение задачи и отправка результата
    try:
        workbook: bytes = await run_in_process(
            create_workbook, result, worksheet='Выгрузка', smart_table='Выгрузка', column_width=8
        )
    except Exception:
        log.exception('Не удалось обработать выгрузку')
        await bot.send_message(
            chat_id=chat_id,
            text='Не удалось обработать выгрузку',
        )
        return

    # Меняем расширение файла на .xlsx
    file_name = file_name.removesuffix('.txt') + '.xlsx'
    document = BufferedInputFile(workbook, filename=file_name)

    try:
        await bot.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption,
        )
    except Exception:
        log.exception('Не удалось отправить файл в чат')
        await bot.send_message(
            chat_id=chat_id,
            text='Не удалось отправить файл в чат. Ошибка на стороне сервера',
        )
        return


async def run_nat_affinity_task(
    bot: Bot,
    chat_id: int,
    caption: str,
    **kwargs,
) -> None:
    # Получаем параметры задачи
    start_date: datetime = kwargs.get('start_date')  # type: ignore
    end_date: datetime = kwargs.get('end_date')  # type: ignore
    audience: str = kwargs.get('audience')  # type: ignore

    # Запуск задачи в отдельном потоке
    try:
        result: pl.DataFrame = await asyncio.to_thread(nat_affinity_task, **kwargs)
    except Exception:
        log.exception('Не удалось рассчитать задачу')

        await bot.send_message(
            chat_id=chat_id,
            text='Не удалось рассчитать задачу',
        )

        return

    # Завершение задачи и отправка результата
    workbook: bytes = create_workbook(
        result,
        worksheet=f'{audience}',
        smart_table='affinity',
        column_width=8,
        column_formats={
            f'Affinity {audience}': FormatKey.PERCENTAGE_2,
        },
    )

    # Генерируем имя файла в формате: +Affinity {audience} [start_date-end_date].xlsx
    file_name = f'+Nat. Affinity {audience} [{start_date.strftime("%d.%m.%y")}-{end_date.strftime("%d.%m.%y")}].xlsx'

    document = BufferedInputFile(workbook, filename=file_name)

    await bot.send_document(
        chat_id=chat_id,
        document=document,
        caption=caption,
    )

    return
