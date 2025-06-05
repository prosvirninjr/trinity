from dataclasses import fields
from datetime import date, datetime
from io import BytesIO
from typing import Any

import polars as pl
from pydantic import ValidationError

from core.ooh.exceptions import OOHDataError
from core.ooh.ooh_shield import check_ooh_template
from core.ooh.schema import OOHColumn, OOHRecord
from core.utils.xlsx.xlsx_loader import load_smart_table


def load_ooh_template(
    file_path: str | BytesIO, worksheet: str = 'Стандартная закупка', smart_table: str = 'outdoor'
) -> pl.DataFrame:
    """
    Загружает smart-table из Excel файла.

    Args:
        file_path (str | BytesIO): Путь к файлу или объект BytesIO.
        worksheet (str): Название листа в Excel файле.
        smart_table (str): Название smart-table в Excel файле.

    Returns:
        pl.DataFrame: DataFrame с загруженными данными.

    Raises:
        ValueError: Если данные не соответствуют модели OOHRecord.
    """
    template = load_smart_table(workbook=file_path, worksheet=worksheet, smart_table=smart_table)

    template.columns = list(OOHRecord.model_fields.keys())

    ooh_rows: list[dict[str, Any]] = []
    exceptions: list[dict[str, Any]] = []

    for i, r in enumerate(template.iter_rows(named=True), start=1):
        try:
            row: dict[str, Any] = OOHRecord(**r).model_dump()
        except ValidationError as e:
            exceptions.append(
                {
                    'row': i,
                    'exception': e,
                }
            )
        else:
            ooh_rows.append(row)

    if exceptions:
        raise OOHDataError('Ошибки валидации данных', exceptions)

    # Собираем схему из типов полей Pydantic-модели
    TYPE_MAPPING = {
        int: pl.Int64,
        float: pl.Float64,
        str: pl.String,
        bool: pl.Boolean,
        date: pl.Date,
        datetime: pl.Datetime,
    }

    schema = {item.name: TYPE_MAPPING[getattr(OOHColumn, item.name).type_] for item in fields(OOHColumn)}
    df = pl.DataFrame(ooh_rows, schema=schema)

    # Проверка логики.
    check_ooh_template(df)

    return df
