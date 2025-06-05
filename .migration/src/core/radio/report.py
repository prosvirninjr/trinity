from datetime import datetime

import polars as pl

from core.utils.xlsx.xlsx_builder import FormatKey, XLSXBuilder
from orm.databases import RadioDatabase
from orm.settings import RadioSettings


def create_report(df: pl.DataFrame, radio_settings: RadioSettings):
    wb = XLSXBuilder()
    rdb = RadioDatabase()

    # Лист 'Итоги'.
    wb.add_worksheet('Итоги')
    wb.set_column_width('Итоги', 'B:G', 20)
    wb.set_column_width('Итоги', 'J:N', 20)

    wb.write_data('Итоги', 'B2', 'Расчет', FormatKey.TEXT_BG)

    total_ws = wb.get_worksheet('Итоги')
    options = ['От скидки', 'От таймслота']

    wb.write_data('Итоги', 'C2', 'От скидки', FormatKey.TEXT)
    total_ws.data_validation('C2', {'validate': 'list', 'source': options})  # type: ignore # noqa

    wb.write_data('Итоги', 'B5', 'Бюджет, руб.', FormatKey.TEXT_BG)
    wb.write_formula('Итоги', 'C5', '=СУММ(Расчет[price_net_final])', FormatKey.INTEGER)

    wb.write_data('Итоги', 'B6', 'Оцененный бюджет, руб.', FormatKey.TEXT_BG)
    wb.write_formula(
        'Итоги',
        'C6',
        '=ЕСЛИ($C$2="От таймслота";СУММЕСЛИМН(Расчет[price_net_final];Расчет[В расчет (таймслот)];"Да");СУММЕСЛИМН(Расчет[price_net_final];Расчет[В расчет (скидка)];"Да"))',
        FormatKey.INTEGER,
    )

    wb.write_data('Итоги', 'B7', 'Оцененный бюджет, %', FormatKey.TEXT_BG)
    wb.write_formula('Итоги', 'C7', '=ЕСЛИОШИБКА(C6/C5;"-")', FormatKey.PERCENTAGE_1)

    wb.write_data('Итоги', 'D5', 'Отклонение, руб.', FormatKey.TEXT_BG)
    wb.write_formula('Итоги', 'E5', '=C5-C6', FormatKey.INTEGER)

    wb.write_data('Итоги', 'B10', 'Радиостанция | Пакет', FormatKey.TEXT_BG)
    wb.write_data('Итоги', 'C10', 'Вещание', FormatKey.TEXT_BG)
    wb.write_data('Итоги', 'D10', 'Размещение, руб.', FormatKey.TEXT_BG)
    wb.write_data('Итоги', 'E10', 'Размещение панель, руб.', FormatKey.TEXT_BG)
    wb.write_data('Итоги', 'F10', 'Отклонение, руб.', FormatKey.TEXT_BG)
    wb.write_data('Итоги', 'G10', 'Отклонение, %', FormatKey.TEXT_BG)

    placement = df.select(('radiostation', 'broadcast')).unique()

    for row, (radiostation, broadcast) in enumerate(placement.iter_rows(), 11):
        wb.write_data('Итоги', f'B{row}', radiostation, FormatKey.TEXT)
        wb.write_data('Итоги', f'C{row}', broadcast, FormatKey.TEXT)
        wb.write_formula(
            'Итоги',
            f'D{row}',
            f'=ЕСЛИ($C$2="От таймслота";СУММЕСЛИМН(Расчет[price_net_final];Расчет[radiostation];B{row};Расчет[broadcast];C{row};Расчет[В расчет (таймслот)];"Да");СУММЕСЛИМН(Расчет[price_net_final];Расчет[radiostation];B{row};Расчет[broadcast];C{row};Расчет[В расчет (скидка)];"Да"))',
            FormatKey.INTEGER,
        )
        wb.write_formula(
            'Итоги',
            f'E{row}',
            f'=ЕСЛИ($C$2="От таймслота";СУММЕСЛИМН(Расчет[Итоговая стоимость (таймслот)];Расчет[radiostation];B{row};Расчет[broadcast];C{row};Расчет[В расчет (таймслот)];"Да");СУММЕСЛИМН(Расчет[Итоговая стоимость (скидка)];Расчет[radiostation];B{row};Расчет[broadcast];C{row};Расчет[В расчет (скидка)];"Да"))',
            FormatKey.INTEGER,
        )
        wb.write_formula('Итоги', f'F{row}', f'=D{row}-E{row}', FormatKey.INTEGER)
        wb.write_formula('Итоги', f'G{row}', f'=ЕСЛИОШИБКА(D{row}/E{row}-1;"-")', FormatKey.PERCENTAGE_1)

        wb.write_data('Итоги', 'J10', 'Вещание', FormatKey.TEXT_BG)
        wb.write_data('Итоги', 'K10', 'Размещение, руб.', FormatKey.TEXT_BG)
        wb.write_data('Итоги', 'L10', 'Размещение панель, руб.', FormatKey.TEXT_BG)
        wb.write_data('Итоги', 'M10', 'Отклонение, руб.', FormatKey.TEXT_BG)
        wb.write_data('Итоги', 'N10', 'Отклонение, %', FormatKey.TEXT_BG)

        broadcast = df.select(('broadcast')).to_series().unique().to_list()

        for row, broadcast_val in enumerate(broadcast, 11):
            wb.write_data('Итоги', f'J{row}', broadcast_val, FormatKey.TEXT)
            wb.write_formula(
                'Итоги',
                f'K{row}',
                f'=ЕСЛИ($C$2="От таймслота";СУММЕСЛИМН(Расчет[price_net_final];Расчет[broadcast];J{row};Расчет[В расчет (таймслот)];"Да");СУММЕСЛИМН(Расчет[price_net_final];Расчет[broadcast];J{row};Расчет[В расчет (скидка)];"Да"))',
                FormatKey.INTEGER,
            )
            wb.write_formula(
                'Итоги',
                f'L{row}',
                f'=ЕСЛИ($C$2="От таймслота";СУММЕСЛИМН(Расчет[Итоговая стоимость (таймслот)];Расчет[broadcast];J{row};Расчет[В расчет (таймслот)];"Да");СУММЕСЛИМН(Расчет[Итоговая стоимость (скидка)];Расчет[broadcast];J{row};Расчет[В расчет (скидка)];"Да"))',
                FormatKey.INTEGER,
            )
            wb.write_formula('Итоги', f'M{row}', f'=K{row}-L{row}', FormatKey.INTEGER)
            wb.write_formula('Итоги', f'N{row}', f'=ЕСЛИОШИБКА(K{row}/L{row}-1;"-")', FormatKey.PERCENTAGE_1)

    # Лист 'Расчет'.
    wb.add_worksheet('Расчет')
    wb.set_column_width('Расчет', 'B:BV', 15)

    formulas = {
        'Ср. стоимость таймслота (будни)': '=ПРОСМОТРX([@radiostation]&[@broadcast]&[@timeslot];panel_by_timeslots[radiostation]&panel_by_timeslots[broadcast]&panel_by_timeslots[timeslot];panel_by_timeslots[Ср. стоимость (будни)];0;0)',
        'Ср. стоимость таймслота (выходные)': '=ПРОСМОТРX([@radiostation]&[@broadcast]&[@timeslot];panel_by_timeslots[radiostation]&panel_by_timeslots[broadcast]&panel_by_timeslots[timeslot];panel_by_timeslots[Ср. стоимость (выходные)];0;0)',
        'Итоговая стоимость (будни)': '=[@[Ср. стоимость таймслота (будни)]]*СУММПРОИЗВ(Расчет[@[sec_5_c]:[sec_60_c]];Расчет[@[sec_5_wed]:[sec_60_wed]])',
        'Итоговая стоимость (выходные)': '=[@[Ср. стоимость таймслота (выходные)]]*СУММПРОИЗВ(Расчет[@[sec_5_c]:[sec_60_c]];Расчет[@[sec_5_wkd]:[sec_60_wkd]])',
        'Итоговая стоимость (таймслот)': '=СУММ(Расчет[@[Итоговая стоимость (будни)]:[Итоговая стоимость (выходные)]]) * [@[pos_surcharge]] * [@[extra_surcharge_1]] * [@[extra_surcharge_2]]',
        'Ср. скидка': '=ПРОСМОТРX([@radiostation]&[@broadcast];panel_by_discounts[radiostation]&panel_by_discounts[broadcast];panel_by_discounts[Ср. скидка];0;0)',
        'Итоговая стоимость (скидка)': '=[@[price_net_total]]*[@[season_c]] * (100% - [@[Ср. скидка]]) * [@[pos_surcharge]] * [@[extra_surcharge_1]] * [@[extra_surcharge_2]]',
        'Запись': '=ЕСЛИ(ЕПУСТО([@details]);"Радиостанция";ЕСЛИ([@[price_net_final]]=0;"Детализация по пакету";"Пакет"))',
        'В расчет (таймслот)': '=ЕСЛИ(ИЛИ([@Запись]="Детализация по пакету";[@[Итоговая стоимость (таймслот)]]=0;[@[price_net_final]]=0);"Нет";"Да")',
        'В расчет (скидка)': '=ЕСЛИ(ИЛИ([@Запись]="Детализация по пакету";[@[Итоговая стоимость (скидка)]]=0;[@[price_net_final]]=0);"Нет";"Да")',
    }

    column_formats = {
        'Ср. стоимость таймслота (будни)': FormatKey.INTEGER,
        'Ср. стоимость таймслота (выходные)': FormatKey.INTEGER,
        'Итоговая стоимость (будни)': FormatKey.INTEGER,
        'Итоговая стоимость (выходные)': FormatKey.INTEGER,
        'Итоговая стоимость (таймслот)': FormatKey.INTEGER,
        'Ср. скидка': FormatKey.PERCENTAGE_1,
        'Итоговая стоимость (скидка)': FormatKey.INTEGER,
        'Запись': FormatKey.TEXT,
        'В расчет (таймслот)': FormatKey.TEXT,
        'В расчет (скидка)': FormatKey.TEXT,
    }

    wb.write_smart_table(
        worksheet_name='Расчет',
        cell='B2',
        df=df,
        smart_table_name='Расчет',
        autofilter=True,
        formulas=formulas,
        column_formats=column_formats,
    )

    # Лист 'Панель'.
    wb.add_worksheet('Панель')
    wb.set_column_width('Панель', 'B:F', 15)
    wb.set_column_width('Панель', 'I:K', 15)

    panel_by_discounts = rdb.get_panel(by_discounts=True, panel=radio_settings.panel)
    panel_by_timeslots = rdb.get_panel(by_discounts=False, panel=radio_settings.panel)

    wb.write_smart_table(
        worksheet_name='Панель',
        cell='B2',
        df=panel_by_timeslots,
        smart_table_name='panel_by_timeslots',
        autofilter=True,
    )

    wb.write_smart_table(
        worksheet_name='Панель',
        cell='I2',
        df=panel_by_discounts,
        smart_table_name='panel_by_discounts',
        autofilter=True,
    )

    # Лист 'Настройки'.
    wb.add_worksheet('Настройки')

    # Устанавливаем ширину столбцов.
    wb.set_column_width('Настройки', 'B:C', 20)

    # Записываем данные на лист "Настройки".
    wb.write_data('Настройки', 'B2', 'Дата', FormatKey.HEADER)
    wb.write_data('Настройки', 'C2', f'{datetime.today().strftime("%Y-%m-%d")}', FormatKey.ISO_DATE)

    if len(radio_settings.panel):
        wb.write_data('Настройки', 'B5', '№', FormatKey.HEADER)
        wb.write_data('Настройки', 'C5', 'Рекламодатель', FormatKey.HEADER)

        start_row = 6

        for i, advertiser in enumerate(radio_settings.panel):
            row = start_row + i
            wb.write_data('Настройки', f'B{row}', i + 1, FormatKey.INTEGER)
            wb.write_data('Настройки', f'C{row}', advertiser, FormatKey.TEXT)

    return wb.get_workbook()
