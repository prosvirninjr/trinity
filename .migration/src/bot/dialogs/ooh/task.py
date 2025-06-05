from io import BytesIO

import polars as pl
from aiogram import Bot
from aiogram.types import BufferedInputFile, File

from app_settings import load_settings
from bot.utils.sync_executor import run_in_process
from core.ooh.analyzer import Analyzer
from core.ooh.guardian import Guardian
from core.ooh.guardian import validators as validators
from core.ooh.report import create_ooh_report
from core.ooh.schema import OOHColumn, Template
from core.utils.xlsx.xlsx_creator import create_workbook
from core.utils.xlsx.xlsx_loader import load_smart_table
from orm.databases import OOHDatabase
from orm.settings import ESettings, OOHSettings
from orm.sql_builder import get_engine
from orm.sql_queries import select_employee

engine = get_engine()

settings = load_settings()


def _load_template(file_io: BytesIO) -> pl.DataFrame:
    template = load_smart_table(file_io, worksheet='Стандартная закупка', smart_table='outdoor')

    return template


def _process_template(df: pl.DataFrame) -> pl.DataFrame:
    # Длительная операция, поэтому используем отдельный поток.
    df_table = Template(df)
    df_table.process_template()

    return df_table.df


def _get_db(panel: list[str], target_year: int) -> pl.DataFrame:
    odb = OOHDatabase()
    db = odb.get_database(panel=panel, target_year=target_year)

    return db


async def do_ooh_task(
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

    # NOTE: Чтение файла в отдельном процессе.
    template: pl.DataFrame = await run_in_process(_load_template, file_io)  # type: ignore

    guardian = Guardian(template=template, schema=OOHColumn, validators=validators)

    guardian.validate()

    if not guardian.is_valid():
        wb_errors = create_workbook(
            pl.DataFrame(guardian.get_report()), worksheet='Ошибки валидации', smart_table='Ошибки'
        )
        document = BufferedInputFile(wb_errors, filename='errors.xlsx')

        await bot.send_document(chat_id=chat_id, document=document, caption='Прежде чем продолжить, устраните ошибки.')
        return

    # NOTE: Обработка шаблона.
    template = guardian.get_valid_df()
    df: pl.DataFrame = await run_in_process(_process_template, df=template)

    # NOTE: Загрузка настроек пользователя и базы данных.
    employee = select_employee(engine, tg_id=user_id)  # type: ignore
    employee_settings = ESettings.model_validate(employee.settings)  # type: ignore

    # Получаем панель и удаляем из нее текущего рекламодателя для предотвращения расчета по себе же.
    current_advertiser: str = df.select(OOHColumn.advertiser.tech_name).to_series().first()  # type: ignore
    panel = employee_settings.ooh.panel

    try:
        panel.remove(current_advertiser)
    except ValueError:
        # Если текущий рекламодатель уже не в панели, то ничего не делаем.
        pass

    target_year = employee_settings.ooh.target_year

    db: pl.DataFrame = await run_in_process(_get_db, panel, target_year)

    # NOTE: Запуск задачи в отдельном процессе
    try:
        result: bytes = await run_in_process(create_ooh_task, df=df, db=db, ooh_settings=employee_settings.ooh)
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


def create_ooh_task(df: pl.DataFrame, db: pl.DataFrame, ooh_settings: OOHSettings) -> bytes:
    # NOTE: Запуск расчета.
    analyzer = Analyzer(df=df, db=db, ooh_settings=ooh_settings)
    analyzer.execute()

    # NOTE: Создание отчета .xlsx
    return create_ooh_report(df=analyzer.get_result(), db=db, ooh_settings=ooh_settings)
