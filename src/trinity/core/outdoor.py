import io

import polars as pl
from pydantic import ValidationError

from trinity.schemas.outdoor import Metro
from trinity.services.exceptions import TemplateDataError
from trinity.utils.xlsx.xlsx_loader import load_st


class MetroController:
    def __init__(self):
        self.df: pl.DataFrame = pl.DataFrame()
        self.v_info: list[dict] = []

    # TODO: Добавить документацию.
    def _set_header(self, df: pl.DataFrame) -> None:
        try:
            fields = list(Metro.model_fields.keys())
            df.columns = fields
        except Exception as e:
            raise ValueError('Ошибка при установке заголовка DataFrame.') from e

        return df

    # TODO: Добавить документацию.
    def _build_df(self, df: pl.DataFrame):
        data: list[dict] = []
        details: list[tuple[int, list[dict]]] = []

        # Перебираем строки исходного DataFrame.
        for idx, row in enumerate(df.iter_rows(named=True), start=1):
            try:
                # Валидируем каждую строку через Pydantic.
                data.append(Metro(**row).model_dump())
            except ValidationError as e:
                details.append((idx, e.errors(include_url=False, include_context=False)))

        # Если нет ни одной ошибки — собираем итоговый DataFrame.
        if not details:
            return pl.DataFrame(data, schema=Metro.get_schema())

        # Если есть, генерируем отчет об ошибках.
        v_info: list[dict] = []

        for idx, errors in details:
            for error in errors:
                v_info.append(
                    {
                        'Строка': idx,
                        'Ошибка': error['msg'].removeprefix('Value error, '),
                    }
                )

        raise TemplateDataError('Ошибка валидации.', v_info)

    # TODO: Добавить документацию.
    def load_template(self, workbook: str | io.BytesIO) -> bool:
        r_df = load_st(workbook, ws_name='Метро & МЦК', st_name='metro')
        r_df = self._set_header(r_df)

        try:
            v_df = self._build_df(r_df)
        except TemplateDataError as e:
            self.v_info = e.field
            return False
        else:
            self.df = v_df

        return True

    def get_v_info(self) -> list[dict]:
        """Возвращает результат валидации."""
        return self.v_info
