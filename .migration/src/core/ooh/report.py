from datetime import datetime

import polars as pl

from core.ooh.schema import OOHColumn, OOHRecord
from core.utils.xlsx.xlsx_builder import FormatKey, XLSXBuilder
from orm.settings import OOHSettings


def create_ooh_report(df: pl.DataFrame, db: pl.DataFrame, ooh_settings: OOHSettings) -> bytes:
    """
    Создает отчет OOH в формате Excel.

    Скидки представлены в разрезе по оператору и формату.

    Args:
        df: Расчет.
        db: База данных.
        ooh_settings: Настройки расчета.

    Returns:
        bytes: Содержимое файла Excel в виде байтов.
    """
    wb_manager = XLSXBuilder()

    # Переименовываем столбцы DataFrame.
    def _get_ru_df(df: pl.DataFrame) -> pl.DataFrame:
        """
        Переименовывает столбцы DataFrame на русский язык.

        Args:
            df: Исходный DataFrame.

        Returns:
            DataFrame с переименованными столбцами.
        """
        # Переименовываем столбцы в соответствии с моделью pydantic.
        fields = OOHRecord.model_fields
        header: dict[str, str] = dict()

        for field in fields:
            header[field] = fields.get(field).title  # type: ignore

        header['subject_name'] = 'Субъект (Geo)'

        df = df.rename(header)

        return df

    def _create_total_sheet():
        # Создаем лист "Итоги".
        wb_manager.add_worksheet('Итоги')

        # Устанавливаем ширину столбцов.
        # (Ширина столбцов не зависит от строк, поэтому эта часть остается без изменений)
        wb_manager.set_column_width('Итоги', 'B:H', 20)
        wb_manager.set_column_width('Итоги', 'K:P', 20)  # Дублирование? Возможно K:Q было нужно? Оставил как есть.
        wb_manager.set_column_width('Итоги', 'S:Y', 20)
        wb_manager.set_column_width('Итоги', 'K:Q', 20)  # Эта строка перезаписывает K:P

        wb_manager.write_data(worksheet_name='Итоги', cell='B2', data='Оценено', format_key=FormatKey.TEXT_BG)
        wb_manager.write_data(worksheet_name='Итоги', cell='C2', data='Всего', format_key=FormatKey.TEXT)
        total_ws = wb_manager.get_worksheet(worksheet_name='Итоги')

        options = ['От скидки', 'От стоимости', 'Всего']
        total_ws.data_validation('C2', {'validate': 'list', 'source': options})  # type: ignore # noqa

        # --- Сдвиг на 2 строки вниз ---
        row_offset = 2

        # Записываем данные на лист "Итоги".

        # Секция №1. (Начало с B4)
        wb_manager.write_data('Итоги', f'B{2 + row_offset}', 'Размещение', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'C{2 + row_offset}', 'Позиций, ед.', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'D{2 + row_offset}', 'Доля, %', FormatKey.HEADER)

        wb_manager.write_data('Итоги', f'B{3 + row_offset}', 'Основное', FormatKey.TEXT)
        # Формула: =C7-C6 (было =C5-C4)
        wb_manager.write_formula(
            'Итоги', f'C{3 + row_offset}', f'=C{5 + row_offset}-C{4 + row_offset}', FormatKey.INTEGER
        )
        # Формула: =ЕСЛИОШИБКА(C5/СУММ(C5:C6);"-") (было =ЕСЛИОШИБКА(C3/СУММ(C3:C4);"-"))
        wb_manager.write_formula(
            'Итоги',
            f'D{3 + row_offset}',
            f'=ЕСЛИОШИБКА(C{3 + row_offset}/СУММ(C{3 + row_offset}:C{4 + row_offset});"-")',
            FormatKey.PERCENTAGE_1,
        )

        wb_manager.write_data('Итоги', f'B{4 + row_offset}', 'Бонусное', FormatKey.TEXT)
        # Формула не меняется, т.к. ссылается на 'Расчет', меняется только целевая ячейка
        wb_manager.write_formula(
            'Итоги', f'C{4 + row_offset}', '=СЧЁТЕСЛИМН(Расчет[Размещение со скидкой до НДС];0)', FormatKey.INTEGER
        )
        # Формула: =ЕСЛИОШИБКА(C6/СУММ(C5:C6);"-") (было =ЕСЛИОШИБКА(C4/СУММ(C3:C4);"-"))
        wb_manager.write_formula(
            'Итоги',
            f'D{4 + row_offset}',
            f'=ЕСЛИОШИБКА(C{4 + row_offset}/СУММ(C{3 + row_offset}:C{4 + row_offset});"-")',
            FormatKey.PERCENTAGE_1,
        )

        wb_manager.write_data('Итоги', f'B{5 + row_offset}', 'Всего', FormatKey.TEXT_BG)
        # Формула не меняется, меняется только целевая ячейка
        wb_manager.write_formula('Итоги', f'C{5 + row_offset}', '=СЧЁТЗ(Расчет[В расчет])', FormatKey.INTEGER_BG)

        wb_manager.write_data('Итоги', f'B{6 + row_offset}', 'Оценено', FormatKey.TEXT_BG)
        # Формула не меняется, меняется только целевая ячейка
        wb_manager.write_formula(
            'Итоги', f'C{6 + row_offset}', '=СЧЁТЕСЛИМН(Расчет[В расчет];"Да")', FormatKey.INTEGER_BG
        )
        # Формула: =ЕСЛИОШИБКА(C8/C7;"-") (было =ЕСЛИОШИБКА(C6/C5;"-"))
        wb_manager.write_formula(
            'Итоги',
            f'D{6 + row_offset}',
            f'=ЕСЛИОШИБКА(C{6 + row_offset}/C{5 + row_offset};"-")',
            FormatKey.PERCENTAGE_1_BG,
        )

        wb_manager.write_data('Итоги', f'B{7 + row_offset}', 'Не оценено', FormatKey.TEXT_BG)
        # Формула: =C7-C8 (было =C5-C6)
        wb_manager.write_formula(
            'Итоги', f'C{7 + row_offset}', f'=C{5 + row_offset}-C{6 + row_offset}', FormatKey.INTEGER_BG
        )
        # Формула: =ЕСЛИОШИБКА(100%-D8;"-") (было =ЕСЛИОШИБКА(100%-D6;"-"))
        wb_manager.write_formula(
            'Итоги', f'D{7 + row_offset}', f'=ЕСЛИОШИБКА(1-D{6 + row_offset};"-")', FormatKey.PERCENTAGE_1_BG
        )  # 100% = 1

        # Секция №2. (Начало с F4)
        wb_manager.write_data('Итоги', f'F{2 + row_offset}', 'Сторона', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'G{2 + row_offset}', 'Доля, %', FormatKey.HEADER)

        wb_manager.write_data('Итоги', f'F{3 + row_offset}', 'A', FormatKey.TEXT)
        # Формула: =СЧЁТЕСЛИМН(Расчет[Сторона];"A")/C7 (было =СЧЁТЕСЛИМН(Расчет[Сторона];"A")/C5)
        wb_manager.write_formula(
            'Итоги', f'G{3 + row_offset}', f'=СЧЁТЕСЛИМН(Расчет[Сторона];"A")/C{5 + row_offset}', FormatKey.PERCENTAGE_1
        )

        wb_manager.write_data('Итоги', f'F{4 + row_offset}', 'Остальные', FormatKey.TEXT)
        # Формула: =ЕСЛИОШИБКА(100%-G5;"-") (было =ЕСЛИОШИБКА(100%-G3;"-"))
        wb_manager.write_formula(
            'Итоги', f'G{4 + row_offset}', f'=ЕСЛИОШИБКА(1-G{3 + row_offset};"-")', FormatKey.PERCENTAGE_1
        )  # 100% = 1

        # Секция №3. (Начало с B12)
        wb_manager.write_data('Итоги', f'B{10 + row_offset}', 'Бюджет, руб.', FormatKey.TEXT_BG)
        # Формула не меняется, меняется только целевая ячейка
        wb_manager.write_formula(
            'Итоги', f'C{10 + row_offset}', '=СУММ(Расчет[Размещение со скидкой до НДС])', FormatKey.INTEGER
        )
        wb_manager.write_data('Итоги', f'D{10 + row_offset}', 'Отклонение, руб.', FormatKey.TEXT_BG)
        # Формула: =C12-C13 (было =C10-C11)
        wb_manager.write_formula(
            'Итоги', f'E{10 + row_offset}', f'=C{10 + row_offset}-C{11 + row_offset}', FormatKey.INTEGER
        )

        wb_manager.write_data('Итоги', f'B{11 + row_offset}', 'Оцененный бюджет, руб.', FormatKey.TEXT_BG)
        # Формула не меняется, меняется только целевая ячейка
        wb_manager.write_formula(
            'Итоги',
            f'C{11 + row_offset}',
            '=СУММЕСЛИМН(Расчет[Размещение со скидкой до НДС];Расчет[В расчет];"Да")',
            FormatKey.INTEGER,
        )

        wb_manager.write_data('Итоги', f'B{12 + row_offset}', 'Оцененный бюджет, %', FormatKey.TEXT_BG)
        # Формула: =ЕСЛИОШИБКА(C13/C12;"-") (было =ЕСЛИОШИБКА(C11/C10;"-"))
        wb_manager.write_formula(
            'Итоги',
            f'C{12 + row_offset}',
            f'=ЕСЛИОШИБКА(C{11 + row_offset}/C{10 + row_offset};"-")',
            FormatKey.PERCENTAGE_1,
        )

        # Секция №4. (Начало с B17, данные с B18)
        header_row_4 = 15 + row_offset
        wb_manager.write_data('Итоги', f'B{header_row_4}', 'Субъект', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'C{header_row_4}', 'Позиций, ед.', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'D{header_row_4}', 'Размещение, руб.', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'E{header_row_4}', 'Размещение панель, руб.', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'F{header_row_4}', 'Отклонение, руб.', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'G{header_row_4}', 'Отклонение, %', FormatKey.HEADER)

        # Записываем данные в таблицу "Итоги" (Секция №4).
        subjects = ['Москва', 'Московская область', 'Санкт-Петербург', 'Ленинградская область', 'Регионы']
        start_data_row_4 = 16 + row_offset

        for i, loc in enumerate(subjects):
            row = start_data_row_4 + i
            wb_manager.write_data('Итоги', f'B{row}', loc, FormatKey.TEXT)
            # Формула ссылается на B{row}, не меняется, т.к. row уже сдвинут
            wb_manager.write_formula(
                'Итоги',
                f'C{row}',
                f'=СЧЁТЕСЛИМН(Расчет[В расчет];"Да";Расчет[Субъект (Geo)];B{row})',
                FormatKey.INTEGER,
            )
            # Формула ссылается на B{row}, не меняется
            wb_manager.write_formula(
                'Итоги',
                f'D{row}',
                f'=СУММЕСЛИМН(Расчет[Размещение со скидкой до НДС];Расчет[В расчет];"Да";Расчет[Субъект (Geo)];B{row})',
                FormatKey.INTEGER,
            )
            # Формула ссылается на B{row}, не меняется
            wb_manager.write_formula(
                'Итоги',
                f'E{row}',
                f'=СУММЕСЛИМН(Расчет[Размещение панель];Расчет[В расчет];"Да";Расчет[Субъект (Geo)];B{row})',
                FormatKey.INTEGER,
            )
            # Формула ссылается на D{row} и E{row}, не меняется
            wb_manager.write_formula('Итоги', f'F{row}', f'=D{row}-E{row}', FormatKey.INTEGER)
            # Формула ссылается на D{row} и E{row}, не меняется
            wb_manager.write_formula('Итоги', f'G{row}', f'=ЕСЛИОШИБКА(D{row}/E{row}-1;"-")', FormatKey.PERCENTAGE_1)

        # Строка с итогами (Секция №4). (Начало с B23)
        total_row_4 = 21 + row_offset
        data_start_row_4 = 16 + row_offset
        data_end_row_4 = data_start_row_4 + len(subjects) - 1

        wb_manager.write_data('Итоги', f'B{total_row_4}', 'Итого', FormatKey.TEXT_BG)
        # Формула: =СУММ(C18:C22) (было =СУММ(C16:C20))
        wb_manager.write_formula(
            'Итоги', f'C{total_row_4}', f'=СУММ(C{data_start_row_4}:C{data_end_row_4})', FormatKey.INTEGER_BG
        )
        # Формула: =СУММ(D18:D22) (было =СУММ(D16:D20))
        wb_manager.write_formula(
            'Итоги', f'D{total_row_4}', f'=СУММ(D{data_start_row_4}:D{data_end_row_4})', FormatKey.INTEGER_BG
        )
        # Формула: =СУММ(E18:E22) (было =СУММ(E16:E20))
        wb_manager.write_formula(
            'Итоги', f'E{total_row_4}', f'=СУММ(E{data_start_row_4}:E{data_end_row_4})', FormatKey.INTEGER_BG
        )
        # Формула: =D23-E23 (было =D21-E21)
        wb_manager.write_formula('Итоги', f'F{total_row_4}', f'=D{total_row_4}-E{total_row_4}', FormatKey.INTEGER_BG)
        # Формула: =ЕСЛИОШИБКА(D23/E23-1;"-") (было =ЕСЛИОШИБКА(D21/E21-1;"-"))
        wb_manager.write_formula(
            'Итоги', f'G{total_row_4}', f'=ЕСЛИОШИБКА(D{total_row_4}/E{total_row_4}-1;"-")', FormatKey.PERCENTAGE_1_BG
        )

        # Секция №5. (Начало с B26, данные с B27)
        header_row_5 = 24 + row_offset
        wb_manager.write_data('Итоги', f'B{header_row_5}', 'Местоположение', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'C{header_row_5}', 'Формат', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'D{header_row_5}', 'Позиций, ед.', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'E{header_row_5}', 'Размещение, руб.', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'F{header_row_5}', 'Размещение панель, руб.', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'G{header_row_5}', 'Отклонение, руб.', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'H{header_row_5}', 'Отклонение, %', FormatKey.HEADER)

        # Записываем данные в таблицу "Детализация по местоположению и формату" (Секция №5).
        # Предполагается, что 'df' доступен в этой области видимости
        unique_entries_loc_fmt = df.select(['location', 'format_']).unique().to_numpy()

        start_data_row_5 = 25 + row_offset

        for i, (location, format_val) in enumerate(unique_entries_loc_fmt):
            row = start_data_row_5 + i
            wb_manager.write_data('Итоги', f'B{row}', location, FormatKey.TEXT)
            wb_manager.write_data('Итоги', f'C{row}', format_val, FormatKey.TEXT)
            # Формулы ссылаются на B{row} и C{row}, не меняются, т.к. row уже сдвинут
            wb_manager.write_formula(
                'Итоги',
                f'D{row}',
                f'=СЧЁТЕСЛИМН(Расчет[В расчет];"Да";Расчет[Местоположение];B{row};Расчет[Формат];C{row})',
                FormatKey.INTEGER,
            )
            wb_manager.write_formula(
                'Итоги',
                f'E{row}',
                f'=СУММЕСЛИМН(Расчет[Размещение со скидкой до НДС];Расчет[В расчет];"Да";Расчет[Местоположение];B{row};Расчет[Формат];C{row})',
                FormatKey.INTEGER,
            )
            wb_manager.write_formula(
                'Итоги',
                f'F{row}',
                f'=СУММЕСЛИМН(Расчет[Размещение панель];Расчет[В расчет];"Да";Расчет[Местоположение];B{row};Расчет[Формат];C{row})',
                FormatKey.INTEGER,
            )
            # Формула ссылается на E{row} и F{row}, не меняется
            wb_manager.write_formula('Итоги', f'G{row}', f'=E{row}-F{row}', FormatKey.INTEGER)
            # Формула ссылается на E{row} и F{row}, не меняется
            wb_manager.write_formula('Итоги', f'H{row}', f'=ЕСЛИОШИБКА(E{row}/F{row}-1;"-")', FormatKey.PERCENTAGE_1)

        # Секция №6. (Начало с K26, данные с K27)
        header_row_6 = 24 + row_offset  # Та же строка, что и у секции 5, но другие столбцы
        wb_manager.write_data('Итоги', f'K{header_row_6}', 'Местоположение', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'L{header_row_6}', 'Оператор | Поставщик', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'M{header_row_6}', 'Позиций, ед.', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'N{header_row_6}', 'Размещение, руб.', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'O{header_row_6}', 'Размещение панель, руб.', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'P{header_row_6}', 'Отклонение, руб.', FormatKey.HEADER)
        wb_manager.write_data('Итоги', f'Q{header_row_6}', 'Отклонение, %', FormatKey.HEADER)

        # Записываем данные в таблицу "Детализация по местоположению и оператору" (Секция №6).
        # Предполагается, что 'df' доступен в этой области видимости
        unique_entries_loc_op = df.select(['location', 'operator']).unique().to_numpy()

        start_data_row_6 = 25 + row_offset  # Та же стартовая строка данных, что и у секции 5

        for i, (location, operator) in enumerate(unique_entries_loc_op):
            row = start_data_row_6 + i
            wb_manager.write_data('Итоги', f'K{row}', location, FormatKey.TEXT)
            wb_manager.write_data('Итоги', f'L{row}', operator, FormatKey.TEXT)
            # Формулы ссылаются на K{row} и L{row}, не меняются, т.к. row уже сдвинут
            wb_manager.write_formula(
                'Итоги',
                f'M{row}',
                f'=СЧЁТЕСЛИМН(Расчет[В расчет];"Да";Расчет[Местоположение];K{row};Расчет[Оператор | Поставщик];L{row})',
                FormatKey.INTEGER,
            )
            wb_manager.write_formula(
                'Итоги',
                f'N{row}',
                f'=СУММЕСЛИМН(Расчет[Размещение со скидкой до НДС];Расчет[В расчет];"Да";Расчет[Местоположение];K{row};Расчет[Оператор | Поставщик];L{row})',
                FormatKey.INTEGER,
            )
            wb_manager.write_formula(
                'Итоги',
                f'O{row}',
                f'=СУММЕСЛИМН(Расчет[Размещение панель];Расчет[В расчет];"Да";Расчет[Местоположение];K{row};Расчет[Оператор | Поставщик];L{row})',
                FormatKey.INTEGER,
            )
            # Формула ссылается на N{row} и O{row}, не меняется
            wb_manager.write_formula('Итоги', f'P{row}', f'=N{row}-O{row}', FormatKey.INTEGER)
            # Формула ссылается на N{row} и O{row}, не меняется
            wb_manager.write_formula('Итоги', f'Q{row}', f'=ЕСЛИОШИБКА(N{row}/O{row}-1;"-")', FormatKey.PERCENTAGE_1)

    def _create_calculation_sheet(df: pl.DataFrame):
        # Создаем лист "Расчет".
        wb_manager.add_worksheet('Расчет')

        # Устанавливаем ширину столбцов.
        wb_manager.set_column_width('Расчет', 'B:BT', 20)

        # Записываем данные на лист "Расчет".
        formulas = {
            'Бонус': '=ЕСЛИ([@[Размещение со скидкой до НДС]]=0;"Да";"Нет")',
            'panel_discount': '=ПРОСМОТРX([@[subject_code]]&[@[Оператор | Поставщик]];Скидки[Субъект]&Скидки[Оператор];Скидки[Ср. скидка Панель];0;0)',
            'Размещение': '=[@[Размещение со скидкой до НДС]]',
            'Размещение панель': '=ЕСЛИОШИБКА(ЕСЛИ(И(ЕПУСТО([@[panel_base_price]]);ЕПУСТО([@[panel_discount]]));0;ЕСЛИ(ЕПУСТО([@[panel_base_price]]);[@[Размещение прайс-лист]] * (100% - [@[panel_discount]]);[@[panel_base_price]]*[@[rental_c]]*[@[digital_c]]*[@[side_c]]*[@[season_c]]*[@[user_c]]));0)',
            'Отклонение, руб.': '=[@Размещение]-[@[Размещение панель]]',
            'Отклонение, %': '=ЕСЛИОШИБКА([@Размещение]/[@[Размещение панель]]-1;"-")',
            'Расчет': '=ЕСЛИ(И(ЕПУСТО([@[panel_base_price]]);[@[panel_discount]] = 0);"";ЕСЛИ(ЕПУСТО([@[panel_base_price]]);"От скидки";"От стоимости"))',
            'В расчет': '=ЕСЛИ(ИЛИ(И([@[panel_base_price]]=0;[@[panel_discount]]=0);[@[Размещение со скидкой до НДС]]=0);"Нет";ЕСЛИ(ИЛИ(Итоги!$C$2="Всего";[@Расчет]=Итоги!$C$2);"Да";"Нет"))',
        }

        column_formats = {
            'Бонус': FormatKey.TEXT,
            'panel_discount': FormatKey.PERCENTAGE_1,
            'Размещение': FormatKey.INTEGER,
            'Размещение панель': FormatKey.INTEGER,
            'Отклонение, руб.': FormatKey.INTEGER,
            'Отклонение, %': FormatKey.PERCENTAGE_1,
            'Расчет': FormatKey.TEXT,
            'В расчет': FormatKey.TEXT,
        }

        wb_manager.write_smart_table(  # type: ignore
            worksheet_name='Расчет',
            cell='B2',
            df=df,
            smart_table_name='Расчет',
            autofilter=True,
            formulas=formulas,
            column_formats=column_formats,
        )

    def _create_bonus_sheet():
        # Создаем лист "Бонусы".
        wb_manager.add_worksheet('Бонусы')

        # Устанавливаем ширину столбцов.
        wb_manager.set_column_width('Бонусы', 'B:E', 27)
        wb_manager.set_column_width('Бонусы', 'H:K', 27)

        # Записываем данные на лист "Бонусы".
        wb_manager.write_data('Бонусы', 'B2', 'Доля бонусов, %', FormatKey.TEXT_BG)
        wb_manager.write_formula('Бонусы', 'C2', '=Итоги!D6', FormatKey.PERCENTAGE_1)

        wb_manager.write_data('Бонусы', 'B3', 'Оценено бонусов, %', FormatKey.TEXT_BG)
        wb_manager.write_formula(
            'Бонусы',
            'C3',
            '=ЕСЛИОШИБКА(СЧЁТЕСЛИМН(Расчет[Размещение со скидкой до НДС];0;Расчет[Размещение панель];"<>0") / СЧЁТЕСЛИМН(Расчет[Размещение со скидкой до НДС];0);"-")',
            FormatKey.PERCENTAGE_1,
        )

        wb_manager.write_data('Бонусы', 'B5', 'Местоположение', FormatKey.HEADER)
        wb_manager.write_data('Бонусы', 'C5', 'Формат', FormatKey.HEADER)
        wb_manager.write_data('Бонусы', 'D5', 'Позиций, ед.', FormatKey.HEADER)
        wb_manager.write_data('Бонусы', 'E5', 'Размещение панель, руб.', FormatKey.HEADER)

        # Записываем данные в таблицу "Бонусы".
        unique_entries = (
            df.filter(pl.col('placement_price_net') == 0).select(['location', 'format_']).unique().to_numpy()
        )

        start_row = 6

        for i, (location, format_val) in enumerate(unique_entries):
            row = start_row + i
            wb_manager.write_data('Бонусы', f'B{row}', location, FormatKey.TEXT)
            wb_manager.write_data('Бонусы', f'C{row}', format_val, FormatKey.TEXT)
            wb_manager.write_formula(
                'Бонусы',
                f'D{row}',
                f'=СЧЁТЕСЛИМН(Расчет[Местоположение];B{row};Расчет[Формат];C{row};Расчет[Размещение со скидкой до НДС];0;Расчет[Размещение панель];"<>0")',
                FormatKey.INTEGER,
            )
            wb_manager.write_formula(
                'Бонусы',
                f'E{row}',
                f'=СУММЕСЛИМН(Расчет[Размещение панель];Расчет[Местоположение];B{row};Расчет[Формат];C{row};Расчет[Размещение со скидкой до НДС];0;Расчет[Размещение панель];"<>0")',
                FormatKey.INTEGER,
            )

        # Секция №3.
        wb_manager.write_data('Бонусы', 'H5', 'Местоположение', FormatKey.HEADER)
        wb_manager.write_data('Бонусы', 'I5', 'Формат', FormatKey.HEADER)
        wb_manager.write_data('Бонусы', 'J5', 'Позиций, ед.', FormatKey.HEADER)
        wb_manager.write_data('Бонусы', 'K5', 'Размещение прайс-лист, руб.', FormatKey.HEADER)

        # Записываем данные в таблицу "Бонусы".
        unique_entries = (
            df.filter(pl.col('placement_price_net') == 0).select(['location', 'format_']).unique().to_numpy()
        )

        start_row = 6

        for i, (location, format_val) in enumerate(unique_entries):
            row = start_row + i
            wb_manager.write_data('Бонусы', f'H{row}', location, FormatKey.TEXT)
            wb_manager.write_data('Бонусы', f'I{row}', format_val, FormatKey.TEXT)
            wb_manager.write_formula(
                'Бонусы',
                f'J{row}',
                f'=СЧЁТЕСЛИМН(Расчет[Местоположение];H{row};Расчет[Формат];I{row};Расчет[Размещение со скидкой до НДС];0)',
                FormatKey.INTEGER,
            )
            wb_manager.write_formula(
                'Бонусы',
                f'K{row}',
                f'=СУММЕСЛИМН(Расчет[Размещение прайс-лист];Расчет[Местоположение];H{row};Расчет[Формат];I{row};Расчет[Размещение со скидкой до НДС];0)',
                FormatKey.INTEGER,
            )

    def _get_discounts() -> pl.DataFrame:
        """
        Получает данные о скидках из базы данных по тем операторам, что присутствуют в адресной программе.

        Returns:
            DataFrame со скидками.
        """
        agg_columns = ['subject_code', 'operator']

        agg_df = df.group_by(agg_columns).agg(
            pl.col(OOHColumn.placement_discount.tech_name).mean().alias('Ср. скидка'),
        )

        agg_db = db.group_by(agg_columns).agg(
            pl.col(OOHColumn.placement_discount.tech_name).mean().alias('Ср. скидка'),
        )

        discounts = agg_df.join(agg_db, on=agg_columns, how='left', suffix=' Панель')

        discounts = discounts.rename({'subject_code': 'Субъект', 'operator': 'Оператор'})

        return discounts

    def _create_panel_sheet():
        # Создаем лист "Панель"
        wb_manager.add_worksheet('Панель')

        # Устанавливаем ширину столбцов
        wb_manager.set_column_width('Панель', 'B:E', 20)
        wb_manager.set_column_width('Панель', 'H:M', 20)

        column_formats = {
            'Субъект': FormatKey.TEXT,
            'Оператор': FormatKey.TEXT,
            'Ср. скидка': FormatKey.PERCENTAGE_1,
            'Ср. скидка Панель': FormatKey.PERCENTAGE_1,
        }

        # Записываем данные на лист "Панель"
        wb_manager.write_smart_table(
            worksheet_name='Панель',
            cell='B2',
            df=_get_discounts(),
            smart_table_name='Скидки',
            autofilter=True,
            column_formats=column_formats,
        )

        # Добавляем ссылку на итоговую таблицу
        # Секция №4.
        wb_manager.write_data('Панель', 'H2', 'Субъект', FormatKey.HEADER)  # noqa
        wb_manager.write_data('Панель', 'I2', 'Позиций, ед.', FormatKey.HEADER)
        wb_manager.write_data('Панель', 'J2', 'Размещение, руб.', FormatKey.HEADER)
        wb_manager.write_data('Панель', 'K2', 'Размещение панель, руб.', FormatKey.HEADER)
        wb_manager.write_data('Панель', 'L2', 'Отклонение, руб.', FormatKey.HEADER)
        wb_manager.write_data('Панель', 'M2', 'Отклонение, %', FormatKey.HEADER)

        # Записываем данные в таблицу "Итоги" (Секция №4).
        subjects = ['Москва', 'Московская область', 'Санкт-Петербург', 'Ленинградская область', 'Регионы']

        for i, loc in enumerate(subjects):
            row = 3 + i
            wb_manager.write_data('Панель', f'H{row}', loc, FormatKey.TEXT)
            wb_manager.write_formula(
                'Панель',
                f'I{row}',
                f'=СЧЁТЕСЛИМН(Расчет[В расчет];"Да";Расчет[Субъект (Geo)];H{row})',
                FormatKey.INTEGER,
            )
            wb_manager.write_formula(
                'Панель',
                f'J{row}',
                f'=СУММЕСЛИМН(Расчет[Размещение со скидкой до НДС];Расчет[В расчет];"Да";Расчет[Субъект (Geo)];H{row})',
                FormatKey.INTEGER,
            )
            wb_manager.write_formula(
                'Панель',
                f'K{row}',
                f'=СУММЕСЛИМН(Расчет[Размещение панель];Расчет[В расчет];"Да";Расчет[Субъект (Geo)];H{row})',
                FormatKey.INTEGER,
            )
            wb_manager.write_formula('Панель', f'L{row}', f'=J{row}-K{row}', FormatKey.INTEGER)
            wb_manager.write_formula('Панель', f'M{row}', f'=ЕСЛИОШИБКА(J{row}/K{row}-1;"-")', FormatKey.PERCENTAGE_1)

        # Строка с итогами (Секция №4).
        wb_manager.write_data('Панель', 'H8', 'Итого', FormatKey.TEXT_BG)
        wb_manager.write_formula('Панель', 'I8', '=СУММ(I3:I7)', FormatKey.INTEGER_BG)
        wb_manager.write_formula('Панель', 'J8', '=СУММ(J3:J7)', FormatKey.INTEGER_BG)
        wb_manager.write_formula('Панель', 'K8', '=СУММ(K3:K7)', FormatKey.INTEGER_BG)
        wb_manager.write_formula('Панель', 'L8', '=J8-K8', FormatKey.INTEGER_BG)
        wb_manager.write_formula('Панель', 'M8', '=ЕСЛИОШИБКА(J8/K8-1;"-")', FormatKey.PERCENTAGE_1_BG)

    def _create_settings_sheet():
        # Создаем лист "Настройки".
        wb_manager.add_worksheet('Настройки')

        # Устанавливаем ширину столбцов.
        wb_manager.set_column_width('Настройки', 'B:C', 20)

        # Записываем данные на лист "Настройки".
        wb_manager.write_data('Настройки', 'B2', 'Дата', FormatKey.HEADER)
        wb_manager.write_data('Настройки', 'C2', f'{datetime.today().strftime("%Y-%m-%d")}', FormatKey.ISO_DATE)

        wb_manager.write_data('Настройки', 'B5', 'Ограничение', FormatKey.HEADER)
        wb_manager.write_data('Настройки', 'C5', 'Значение', FormatKey.HEADER)

        # TODO: Добавить автоматическое определение даты начала.
        wb_manager.write_data('Настройки', 'B6', 'Дата начала', FormatKey.TEXT)
        wb_manager.write_data('Настройки', 'C6', '', FormatKey.TEXT)

        # TODO: Добавить автоматическое определение даты окончания.
        wb_manager.write_data('Настройки', 'B7', 'Дата окончания', FormatKey.TEXT)
        wb_manager.write_data('Настройки', 'C7', '-', FormatKey.TEXT)

        wb_manager.write_data('Настройки', 'B8', 'Метод расчета', FormatKey.TEXT)
        wb_manager.write_data('Настройки', 'C8', f'{ooh_settings.c_method}', FormatKey.TEXT)

        wb_manager.write_data('Настройки', 'B9', 'Метод сглаживания', FormatKey.TEXT)
        wb_manager.write_data('Настройки', 'C9', f'{ooh_settings.s_method}', FormatKey.TEXT)

        wb_manager.write_data('Настройки', 'B10', 'Год инфляции', FormatKey.TEXT)
        wb_manager.write_data('Настройки', 'C10', ooh_settings.target_year, FormatKey.INTEGER)

        wb_manager.write_data('Настройки', 'B11', 'Размер панели', FormatKey.TEXT)
        wb_manager.write_data('Настройки', 'C11', len(ooh_settings.panel), FormatKey.INTEGER)

        if len(ooh_settings.panel):
            wb_manager.write_data('Настройки', 'B14', '№', FormatKey.HEADER)
            wb_manager.write_data('Настройки', 'C14', 'Рекламодатель', FormatKey.HEADER)

            start_row = 15

            for i, advertiser in enumerate(ooh_settings.panel):
                row = start_row + i
                wb_manager.write_data('Настройки', f'B{row}', i + 1, FormatKey.INTEGER)
                wb_manager.write_data('Настройки', f'C{row}', advertiser, FormatKey.TEXT)

    # Переименовываем столбцы на русский язык
    ru_df = _get_ru_df(df=df)

    # Создаем лист "Итоги".
    _create_total_sheet()

    # Создаем лист "Расчет".
    _create_calculation_sheet(df=ru_df)

    # Создаем лист "Бонусы", если есть бонусы
    if df.filter(pl.col('placement_price_net') == 0).shape[0] > 0:
        _create_bonus_sheet()

    # Создаем лист "Панель"
    _create_panel_sheet()

    # Создаем лист "Настройки"
    _create_settings_sheet()

    return wb_manager.get_workbook()
