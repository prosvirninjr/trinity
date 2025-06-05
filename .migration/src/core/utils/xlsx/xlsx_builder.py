import enum
import io
import re

import polars as pl
import xlsxwriter
from xlsxwriter.utility import xl_cell_to_rowcol

from app_assets import load_xlsx_formulas

FORMULAS = load_xlsx_formulas()


class Color(enum.Enum):
    HEADER_BG = '#5B4A73'
    HEADER_FONT = '#FFFFFF'
    DEFAULT_FONT = '#000000'
    BORDER = '#FFFFFF'


class Align(enum.Enum):
    CENTER = 'center'
    LEFT = 'left'


class Valign(enum.Enum):
    VCENTER = 'vcenter'


class NumberFormat(enum.Enum):
    INTEGER = '# ### ##0'
    FLOAT_2 = '# ### ##0.00'
    FLOAT_4 = '# ### ##0.0000'
    PERCENTAGE_1 = '0.0%'
    PERCENTAGE_2 = '0.00%'
    ISO_DATE = 'yyyy-mm-dd'


class BorderStyle(enum.Enum):
    THIN = 1


class FormatKey(enum.Enum):
    HEADER = 'header'
    TEXT = 'text'
    TEXT_BG = 'text_bg'
    INTEGER = 'integer'
    INTEGER_BG = 'integer_bg'
    FLOAT_2 = 'float_2'
    FLOAT_4 = 'float_4'
    PERCENTAGE_1 = 'percentage_1'
    PERCENTAGE_1_BG = 'percentage_1_bg'
    PERCENTAGE_2 = 'percentage_2'
    PERCENTAGE_2_BG = 'percentage_2_bg'
    ISO_DATE = 'iso_date'


class XLSXBuilder:
    """Менеджер для создания и работы с файлом .xlsx в памяти."""

    def __init__(self) -> None:
        self.formula_translations: dict = FORMULAS
        self.buffer: io.BytesIO = io.BytesIO()
        self.workbook: xlsxwriter.Workbook = xlsxwriter.Workbook(self.buffer, {'in_memory': True})
        self.formats: dict = {}
        self.worksheets: dict = {}
        self._create_default_formats()

    def _create_default_formats(self) -> None:
        """Создает стандартные форматы ячеек."""

        # Базовые свойства для всех форматов
        base_props: dict = {
            'align': Align.CENTER.value,
            'valign': Valign.VCENTER.value,
            'text_wrap': False,
        }

        # Свойства для форматов с фоном и границей
        base_border_bg_props: dict = {
            **base_props,
            'bg_color': Color.HEADER_BG.value,
            'font_color': Color.HEADER_FONT.value,
            'border': BorderStyle.THIN.value,
            'border_color': Color.BORDER.value,
        }

        # Свойства для форматов с дефолтным шрифтом
        base_default_font_props: dict = {
            **base_props,
            'font_color': Color.DEFAULT_FONT.value,
        }

        # Формат заголовка
        self.formats[FormatKey.HEADER] = self.workbook.add_format(
            {**base_border_bg_props},
        )

        # Формат текста
        self.formats[FormatKey.TEXT] = self.workbook.add_format(
            base_default_font_props,
        )

        # Формат текста с фоном
        self.formats[FormatKey.TEXT_BG] = self.workbook.add_format(
            base_border_bg_props,
        )

        # Форматы для чисел: выравнивание вправо
        self.formats[FormatKey.INTEGER] = self.workbook.add_format(
            {**base_default_font_props, 'num_format': NumberFormat.INTEGER.value, 'align': Align.CENTER.value},
        )
        self.formats[FormatKey.INTEGER_BG] = self.workbook.add_format(
            {**base_border_bg_props, 'num_format': NumberFormat.INTEGER.value, 'align': Align.CENTER.value},
        )
        self.formats[FormatKey.FLOAT_2] = self.workbook.add_format(
            {**base_default_font_props, 'num_format': NumberFormat.FLOAT_2.value, 'align': Align.CENTER.value},
        )
        self.formats[FormatKey.FLOAT_4] = self.workbook.add_format(
            {**base_default_font_props, 'num_format': NumberFormat.FLOAT_4.value, 'align': Align.CENTER.value},
        )
        self.formats[FormatKey.PERCENTAGE_1] = self.workbook.add_format(
            {**base_default_font_props, 'num_format': NumberFormat.PERCENTAGE_1.value, 'align': Align.CENTER.value},
        )
        self.formats[FormatKey.PERCENTAGE_1_BG] = self.workbook.add_format(
            {**base_border_bg_props, 'num_format': NumberFormat.PERCENTAGE_1.value, 'align': Align.CENTER.value},
        )
        self.formats[FormatKey.PERCENTAGE_2] = self.workbook.add_format(
            {**base_default_font_props, 'num_format': NumberFormat.PERCENTAGE_2.value, 'align': Align.CENTER.value},
        )
        self.formats[FormatKey.PERCENTAGE_2_BG] = self.workbook.add_format(
            {**base_border_bg_props, 'num_format': NumberFormat.PERCENTAGE_2.value, 'align': Align.CENTER.value},
        )

        # Формат для даты в формате ISO
        self.formats[FormatKey.ISO_DATE] = self.workbook.add_format(
            {**base_props, 'num_format': NumberFormat.ISO_DATE.value, 'align': Align.CENTER.value},
        )

    def _translate_formula(self, ru_formula: str) -> str:
        """Переводит формулу с русского на английский (регистрозависимо), используя self.formula_translations."""
        translations: dict = self.formula_translations
        en_formula: str = ru_formula.replace(';', ',')

        for ru, en in translations.items():
            pattern = re.compile(r'\b' + re.escape(ru) + r'\b')
            en_formula = pattern.sub(en, en_formula)

        return en_formula

    def add_worksheet(self, name: str) -> object:
        """Добавляет лист в книгу."""
        worksheet = self.workbook.add_worksheet(name)
        self.worksheets[name] = worksheet

        return worksheet

    def get_worksheet(self, worksheet_name: str) -> object:
        """Возвращает лист по имени."""
        return self.worksheets[worksheet_name]

    def write_data(self, worksheet_name: str, cell: str, data, format_key: FormatKey) -> None:
        """Записывает данные в ячейку."""
        worksheet = self.worksheets[worksheet_name]

        cell_format = self.formats[format_key]
        row_col_tuple: tuple = xl_cell_to_rowcol(cell)

        row: int = row_col_tuple[0]
        col: int = row_col_tuple[1]

        worksheet.write(row, col, data, cell_format)

    def write_formula(self, worksheet_name: str, cell: str, formula: str, format_key: FormatKey) -> None:
        """Записывает формулу в ячейку."""
        worksheet = self.worksheets[worksheet_name]

        cell_format = self.formats[format_key]
        row_col_tuple: tuple = xl_cell_to_rowcol(cell)

        row: int = row_col_tuple[0]
        col: int = row_col_tuple[1]

        translated_formula: str = self._translate_formula(formula)

        worksheet.write_formula(row, col, translated_formula, cell_format)

    def set_column_width(self, worksheet_name: str, column_range: str, width: float) -> None:
        """Устанавливает ширину колонок."""
        worksheet = self.worksheets[worksheet_name]
        worksheet.set_column(column_range, width)

        return

    def write_smart_table(
        self,
        worksheet_name: str,
        cell: str,
        df: pl.DataFrame,
        smart_table_name: str,
        autofilter: bool = True,
        formulas: dict | None = None,
        column_formats: dict | None = None,
    ) -> None:
        """Записывает polars DataFrame как 'умную' таблицу Excel."""

        _column_formats: dict = (
            {column_name: self.formats[format_key] for column_name, format_key in column_formats.items()}
            if column_formats
            else {}
        )

        _formulas: dict = (
            {column_name: self._translate_formula(formula_str) for column_name, formula_str in formulas.items()}
            if formulas
            else {}
        )

        header_fmt = self.formats.get(FormatKey.HEADER)

        df.write_excel(
            workbook=self.workbook,
            worksheet=self.worksheets[worksheet_name],
            position=cell,
            table_name=smart_table_name,
            header_format=header_fmt,
            autofilter=autofilter,
            formulas=_formulas,
            column_formats=_column_formats,
        )

    def get_workbook(self) -> bytes:
        """Закрывает книгу и возвращает байты файла Excel."""
        if self.workbook:
            self.workbook.close()

        self.buffer.seek(0)

        workbook_bytes: bytes = self.buffer.getvalue()

        self.buffer.close()

        return workbook_bytes
