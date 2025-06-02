import io

import polars as pl
from pydantic import ValidationError

from trinity.schemas.outdoor import Metro
from trinity.services.exceptions import TemplateDataError, TemplateStructureError
from trinity.utils.xlsx.xlsx_loader import load_st


class MetroTemplate:
    def __init__(self, workbook: str | io.BytesIO):
        """
        Инициализация менеджера.

        Args:
            workbook (str | io.BytesIO): Путь к файлу или объект BytesIO с рабочей книгой .xlsx.
        """
        self.template: pl.DataFrame = self._load_template(workbook)

    # TODO: Добавить документацию.
    def _set_header(self, r_template: pl.DataFrame) -> None:
        try:
            fields = list(Metro.model_fields.keys())
            r_template.columns = fields
        except Exception as e:
            raise TemplateStructureError('Не удалось установить заголовок DataFrame.') from e

        return r_template

    # TODO: Добавить документацию.
    def _build_template(self, r_template: pl.DataFrame) -> pl.DataFrame:
        data: list[dict] = []
        details: list[tuple[int, list[dict]]] = []

        # Перебираем строки исходного DataFrame.
        for idx, row in enumerate(r_template.iter_rows(named=True), start=1):
            try:
                # Валидируем каждую строку через Pydantic.
                data.append(Metro(**row).model_dump())
            except ValidationError as e:
                details.append((idx, e.errors(include_url=False, include_context=False)))

        # Если нет ни одной ошибки — собираем итоговый DataFrame.
        if not details:
            return pl.DataFrame(data, schema=Metro.get_polars_schema())

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

        raise TemplateDataError('Данные не прошли валидацию.', v_info)

    # TODO: Добавить документацию.
    def _load_template(self, workbook: str | io.BytesIO) -> None:
        r_template = load_st(workbook, ws_name='Метро & МЦК', st_name='metro')
        r_template = self._set_header(r_template)
        v_template = self._build_template(r_template)

        self.template = v_template

    # TODO: Добавить документацию.
    def _process_template(self, template: pl.DataFrame) -> pl.DataFrame:
        """
        Обрабатывает шаблон метро.

        Добавляет вычисляемые столбцы и парсит данные.

        Args:
            template (pl.DataFrame): Исходный шаблон метро.
        """
        return template

    # TODO: Добавить документацию.
    def get_template(self, original: bool = False) -> pl.DataFrame:
        """
        Возвращает шаблон метро.

        Args:
            original (bool): Если True, возвращает оригинальный шаблон без обработки.

        Returns:
            pl.DataFrame: Шаблон метро в виде DataFrame.
        """
        if original:
            return self.template

        return self._process_template(self.template.clone())


class MetroAnalyzer:
    def __init__(self, template: pl.DataFrame):
        self.template = template
