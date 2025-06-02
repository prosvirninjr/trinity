import io

import polars as pl
from pydantic import ValidationError

from trinity.schemas.outdoor import Metro
from trinity.services.exceptions import TemplateDataError, TemplateStructureError
from trinity.services.logics import Coefficient
from trinity.utils.xlsx.xlsx_loader import load_st


class MetroTemplate:
    def __init__(self, workbook: str | io.BytesIO):
        """
        Инициализация менеджера.

        Args:
            workbook (str | io.BytesIO): Путь к файлу или объект BytesIO с рабочей книгой .xlsx.
        """
        self.template: pl.DataFrame = self._load_template(workbook)

    def _set_header(self, r_template: pl.DataFrame) -> None:
        """
        Устанавливает заголовок DataFrame на основе полей модели Metro.

        Args:
            r_template (pl.DataFrame): Исходный шаблон метро в виде DataFrame.

        Returns:
            pl.DataFrame: DataFrame с установленным заголовком.

        Raises:
            TemplateStructureError: Если не удалось установить заголовок DataFrame.
        """
        try:
            fields = list(Metro.model_fields.keys())
            r_template.columns = fields
        except Exception as e:
            raise TemplateStructureError('Не удалось установить заголовок DataFrame.') from e

        return r_template

    def _build_template(self, r_template: pl.DataFrame) -> pl.DataFrame:
        """
        Создает DataFrame из шаблона метро, валидируя каждую строку.

        Args:
            r_template (pl.DataFrame): Исходный шаблон метро в виде DataFrame.

        Returns:
            pl.DataFrame: Валидированный шаблон метро в виде DataFrame.

        Raises:
            TemplateDataError: Если данные не прошли валидацию.
        """
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

    def _load_template(self, workbook: str | io.BytesIO) -> pl.DataFrame:
        """
        Загружает шаблон метро из файла Excel.

        Args:
            workbook (str | io.BytesIO): Путь к файлу или объект BytesIO с рабочей книгой .xlsx.

        Returns:
            pl.DataFrame: Шаблон метро в виде DataFrame.
        """
        r_template = load_st(workbook, ws_name='Метро & МЦК', st_name='metro')
        r_template = self._set_header(r_template)
        v_template = self._build_template(r_template)

        return v_template

    def _create_is_digital_column(self, template: pl.DataFrame) -> pl.DataFrame:
        """Создает столбец с маркерами digital конструкций."""
        template = template.with_columns(
            pl.col('spot_duration')
            .map_elements(lambda x: True if x else False, return_dtype=pl.Boolean)
            .alias('is_digital')
        )

        return template

    def _create_rental_c_column(self, template: pl.DataFrame) -> pl.DataFrame:
        """Создает столбец с коэффициентами длительности аренды."""
        template = template.with_columns(
            pl.struct('date_from', 'date_to')
            .map_elements(lambda x: Coefficient.calc_rental_c(x['date_from'], x['date_to']), return_dtype=pl.Float64)
            .alias('rental_c')
        )

        return template

    def _create_digital_c_column(self, template: pl.DataFrame) -> pl.DataFrame:
        # Если digital отсутствуют, задаем коэффициент равный 1.0, для исключения влияния на расчет.
        d_c = [
            1.0
            if row['spot_duration'] == 0
            else Coefficient.calc_digital_c(
                row['format_'],
                row['spot_duration'],
                row['spots_per_block'],
                row['block_duration'],
            )
            for row in template.iter_rows(named=True)
        ]

        template = template.with_columns(pl.Series(d_c).alias('digital_c'))

        return template

    def _process_template(self, template: pl.DataFrame) -> pl.DataFrame:
        """
        Обрабатывает шаблон метро.

        Добавляет вычисляемые столбцы и парсит данные.

        Args:
            template (pl.DataFrame): Исходный шаблон метро.
        """
        # Создаем вычисляемые столбцы.
        template = self._create_is_digital_column(template)
        template = self._create_rental_c_column(template)
        template = self._create_digital_c_column(template)

        return template

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
