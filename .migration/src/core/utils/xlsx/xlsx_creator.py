import polars as pl
from xlsxwriter.utility import xl_col_to_name

from core.utils.xlsx.xlsx_builder import XLSXBuilder


def create_workbook(
    df: pl.DataFrame,
    worksheet: str,
    smart_table: str,
    autofilter: bool = True,
    column_width: int = 10,
    column_formats: dict = {},
) -> bytes:
    """
    Создает рабочую книгу из DataFrame с базовым форматированием.

    Args:
        df: DataFrame для создания рабочей книги.
        worksheet: Имя листа.
        smart_table: Имя smart-table.
        autofilter: Включить автофильтр.
        column_formats: Форматирование колонок.

    Returns:
        Байтовое представление рабочей книги .xlsx
    """
    xlsx_manager = XLSXBuilder()
    xlsx_manager.add_worksheet(worksheet)

    xlsx_manager.write_smart_table(  # type: ignore
        worksheet_name=worksheet,
        cell='A1',
        df=df,
        smart_table_name=smart_table,
        autofilter=autofilter,
        formulas=None,
        column_formats=column_formats,
    )

    xlsx_manager.set_column_width(worksheet, f'A:{xl_col_to_name(df.width)}', column_width)

    return xlsx_manager.get_workbook()
