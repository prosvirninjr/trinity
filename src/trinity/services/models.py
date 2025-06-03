import io

import polars as pl
from pydantic import ValidationError

from trinity.schemas.outdoor import Metro
from trinity.services.exceptions import TemplateDataError, TemplateStructureError
from trinity.services.logics import Coefficient, Construction, MParser
from trinity.utils.xlsx.xlsx_loader import load_st


class MetroTemplate:
    def __init__(self, workbook: str | io.BytesIO):
        """
        Инициализация менеджера.

        Args:
            workbook (str | io.BytesIO): Путь к файлу или объект BytesIO с рабочей книгой .xlsx.

        Raises:
            TemplateStructureError: Если не удалось загрузить шаблон метро из рабочей книги.
            TemplateDataError: Если данные в шаблоне метро не прошли валидацию.
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
        try:
            r_template = load_st(workbook, ws_name='Метро & МЦК', st_name='metro')
        except KeyError as e:
            raise TemplateStructureError('Не удалось найти шаблон метро в рабочей книге.') from e

        r_template = self._set_header(r_template)
        v_template = self._build_template(r_template)

        return v_template

    def _create_is_digital_column(self, template: pl.DataFrame) -> pl.DataFrame:
        """
        Создает столбец с маркерами digital конструкций.

        Args:
            template (pl.DataFrame): Валидный шаблон метро в виде DataFrame.

        Returns:
            pl.DataFrame: Шаблон метро с добавленным столбцом is_digital.
        """
        template = template.with_columns(
            pl.col('spot_duration')
            .map_elements(lambda x: True if x else False, return_dtype=pl.Boolean)
            .alias('is_digital')
        )

        return template

    def _create_rental_c_column(self, template: pl.DataFrame) -> pl.DataFrame:
        """
        Создает столбец с коэффициентами длительности аренды.

        Args:
            template (pl.DataFrame): Валидный шаблон метро в виде DataFrame.

        Returns:
            pl.DataFrame: Шаблон метро с добавленным столбцом rental_c.
        """
        template = template.with_columns(
            pl.struct('date_from', 'date_to')
            .map_elements(lambda x: Coefficient.calc_rental_c(x['date_from'], x['date_to']), return_dtype=pl.Float64)
            .alias('rental_c')
        )

        return template

    def _create_digital_c_column(self, template: pl.DataFrame) -> pl.DataFrame:
        """
        Создает столбец с коэффициентами digital конструкций.

        Args:
            template (pl.DataFrame): Валидный шаблон метро в виде DataFrame.

        Returns:
            pl.DataFrame: Шаблон метро с добавленным столбцом digital_c.
        """
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

        template = template.with_columns(pl.Series(values=d_c, dtype=pl.Float64).alias('digital_c'))

        return template

    def _create_base_price_column(self, template: pl.DataFrame) -> pl.DataFrame:
        """
        Создает столбец с базовой ценой.

        Args:
            template (pl.DataFrame): Валидный шаблон метро в виде DataFrame.

        Returns:
            pl.DataFrame: Шаблон метро с добавленным столбцом base_price.
        """

        template = template.with_columns(
            (pl.col('placement_net') / (pl.col('digital_c') * pl.col('rental_c'))).round(4).alias('base_price')
        )

        return template

    def _create_tech_columns(self, template: pl.DataFrame) -> pl.DataFrame:
        """Создает вспомогательные столбцы для векторизованных вычислений."""
        sizes = [Construction.get_sizes(row['size']) for row in template.iter_rows(named=True)]

        template = template.with_columns(
            pl.Series(values=[size[0] for size in sizes], dtype=pl.Float64).alias('_width'),
            pl.Series(values=[size[1] for size in sizes], dtype=pl.Float64).alias('_height'),
        )

        return template

    def _parse_advertiser(self, template: pl.DataFrame) -> pl.DataFrame:
        """Парсит столбец advertiser. Стандартизирует названия рекламодателей."""
        template = template.with_columns(
            pl.col('advertiser')
            .map_elements(lambda x: MParser.parse_advertiser(x) or x, return_dtype=pl.String)
            .alias('advertiser')
        )

        return template

    def _parse_city(self, template: pl.DataFrame) -> pl.DataFrame:
        """Парсит столбец city. Стандартизирует названия городов."""
        template = template.with_columns(
            pl.col('city').map_elements(lambda x: MParser.parse_city(x) or x, return_dtype=pl.String).alias('city')
        )

        return template

    def _parse_line(self, template: pl.DataFrame) -> pl.DataFrame:
        """Парсит столбец line. Стандартизирует названия линий метро."""
        template = template.with_columns(
            pl.struct('city', 'line', 'station')
            .map_elements(
                lambda x: MParser.parse_line(x['city'], x['line'], x['station']) or x['line'],
                return_dtype=pl.String,
            )
            .alias('line')
        )

        return template

    def _parse_station(self, template: pl.DataFrame) -> pl.DataFrame:
        """Парсит столбец station. Стандартизирует названия станций метро."""
        template = template.with_columns(
            pl.struct('city', 'station')
            .map_elements(
                lambda x: MParser.parse_station(x['city'], x['station']) or x['station'],
                return_dtype=pl.String,
            )
            .alias('station')
        )

        return template

    def _parse_location(self, template: pl.DataFrame) -> pl.DataFrame:
        """Парсит столбец location. Стандартизирует названия локаций."""
        return template

    def _parse_format(self, template: pl.DataFrame) -> pl.DataFrame:
        """Парсит столбец format. Стандартизирует форматы поверхностей."""
        template = template.with_columns(
            pl.col('format_')
            .map_elements(lambda x: MParser.parse_format(x) or x, return_dtype=pl.String)
            .alias('format_')
        )

        return template

    def _parse_size(self, template: pl.DataFrame) -> pl.DataFrame:
        """Парсит столбец size. Стандартизирует размеры конструкций."""
        template = template.with_columns(
            pl.col('size').map_elements(lambda x: MParser.parse_size(x) or x, return_dtype=pl.String).alias('size')
        )

        return template

    def _process_template(self, template: pl.DataFrame) -> pl.DataFrame:
        """
        Обрабатывает шаблон метро.

        Добавляет вычисляемые столбцы и парсит данные.

        Требует наличия следующих столбцов:
            - advertiser
            - city
            - line
            - station
            - location
            - format_
            - size
            - spot_duration
            - spots_per_block
            - block_duration
            - date_from
            - date_to
            - placement_net

        Args:
            template (pl.DataFrame): Исходный шаблон метро.
        """
        # Создаем вычисляемые столбцы.
        template = self._create_is_digital_column(template)
        template = self._create_rental_c_column(template)
        template = self._create_digital_c_column(template)
        template = self._create_base_price_column(template)

        # Создаем вспомогательные столбцы для векторизованных вычислений.
        template = self._create_tech_columns(template)

        # Парсим данные.
        template = self._parse_advertiser(template)
        template = self._parse_city(template)
        template = self._parse_line(template)
        template = self._parse_station(template)
        template = self._parse_location(template)
        template = self._parse_format(template)
        template = self._parse_size(template)

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
