from dataclasses import dataclass
from datetime import date
from typing import Annotated

import polars as pl
from pydantic import BaseModel, Field, field_validator

from core.radio.radio_parser import RadioParser as Parser
from core.utils.tools import TextTools, is_integer
from core.utils.xlsx.xlsx_builder import FormatKey


class Meta(BaseModel, frozen=True):
    """Метаданные для столбца."""

    orig_name: str
    tech_name: str
    output_name: str
    type_: object
    xlsx_format: object
    nullable: bool


@dataclass
class RadioColumn:
    campaign: Meta = Meta(
        output_name='Кампания',
        tech_name='campaign',
        orig_name='Кампания',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )
    status: Meta = Meta(
        output_name='Статус',
        tech_name='status',
        orig_name='Статус',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )
    radiostation: Meta = Meta(
        output_name='Радиостанция | Пакет',
        tech_name='radiostation',
        orig_name='Радиостанция | Пакет',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )
    details: Meta = Meta(
        output_name='Станции внутри пакета',
        tech_name='details',
        orig_name='Станции внутри пакета',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )
    broadcast: Meta = Meta(
        output_name='Вещание',
        tech_name='broadcast',
        orig_name='Вещание',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )
    placement: Meta = Meta(
        output_name='Размещение',
        tech_name='placement',
        orig_name='Размещение',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )
    month: Meta = Meta(
        output_name='Месяц',
        tech_name='month',
        orig_name='Месяц',
        type_=date,
        xlsx_format=FormatKey.ISO_DATE,
        nullable=True,
    )
    timeslot: Meta = Meta(
        output_name='Таймслот',
        tech_name='timeslot',
        orig_name='Таймслот',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )
    drivetime: Meta = Meta(
        output_name='DriveTime',
        tech_name='drivetime',
        orig_name='DriveTime',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )
    price_net_30_wed: Meta = Meta(
        output_name='Прайс-лист 30 сек. (будни)',
        tech_name='price_net_30_wed',
        orig_name='Прайс-лист 30 сек. (будни)',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    price_net_30_wkd: Meta = Meta(
        output_name='Прайс-лист 30 сек. (выходные)',
        tech_name='price_net_30_wkd',
        orig_name='Прайс-лист 30 сек. (выходные)',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_5_c: Meta = Meta(
        output_name='Коэффициент за 5 сек.',
        tech_name='sec_5_c',
        orig_name='Коэффициент за 5 сек.',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_10_c: Meta = Meta(
        output_name='Коэффициент за 10 сек.',
        tech_name='sec_10_c',
        orig_name='Коэффициент за 10 сек.',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_15_c: Meta = Meta(
        output_name='Коэффициент за 15 сек.',
        tech_name='sec_15_c',
        orig_name='Коэффициент за 15 сек.',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_20_c: Meta = Meta(
        output_name='Коэффициент за 20 сек.',
        tech_name='sec_20_c',
        orig_name='Коэффициент за 20 сек.',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_25_c: Meta = Meta(
        output_name='Коэффициент за 25 сек.',
        tech_name='sec_25_c',
        orig_name='Коэффициент за 25 сек.',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_30_c: Meta = Meta(
        output_name='Коэффициент за 30 сек.',
        tech_name='sec_30_c',
        orig_name='Коэффициент за 30 сек.',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_35_c: Meta = Meta(
        output_name='Коэффициент за 35 сек.',
        tech_name='sec_35_c',
        orig_name='Коэффициент за 35 сек.',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_40_c: Meta = Meta(
        output_name='Коэффициент за 40 сек.',
        tech_name='sec_40_c',
        orig_name='Коэффициент за 40 сек.',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_45_c: Meta = Meta(
        output_name='Коэффициент за 45 сек.',
        tech_name='sec_45_c',
        orig_name='Коэффициент за 45 сек.',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_50_c: Meta = Meta(
        output_name='Коэффициент за 50 сек.',
        tech_name='sec_50_c',
        orig_name='Коэффициент за 50 сек.',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_55_c: Meta = Meta(
        output_name='Коэффициент за 55 сек.',
        tech_name='sec_55_c',
        orig_name='Коэффициент за 55 сек.',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_60_c: Meta = Meta(
        output_name='Коэффициент за 60 сек.',
        tech_name='sec_60_c',
        orig_name='Коэффициент за 60 сек.',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_5_wed: Meta = Meta(
        output_name='Кол-во роликов с хроно 5 сек. (будни)',
        tech_name='sec_5_wed',
        orig_name='Кол-во роликов с хроно 5 сек. (будни)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_10_wed: Meta = Meta(
        output_name='Кол-во роликов с хроно 10 сек. (будни)',
        tech_name='sec_10_wed',
        orig_name='Кол-во роликов с хроно 10 сек. (будни)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_15_wed: Meta = Meta(
        output_name='Кол-во роликов с хроно 15 сек. (будни)',
        tech_name='sec_15_wed',
        orig_name='Кол-во роликов с хроно 15 сек. (будни)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_20_wed: Meta = Meta(
        output_name='Кол-во роликов с хроно 20 сек. (будни)',
        tech_name='sec_20_wed',
        orig_name='Кол-во роликов с хроно 20 сек. (будни)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_25_wed: Meta = Meta(
        output_name='Кол-во роликов с хроно 25 сек. (будни)',
        tech_name='sec_25_wed',
        orig_name='Кол-во роликов с хроно 25 сек. (будни)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_30_wed: Meta = Meta(
        output_name='Кол-во роликов с хроно 30 сек. (будни)',
        tech_name='sec_30_wed',
        orig_name='Кол-во роликов с хроно 30 сек. (будни)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_35_wed: Meta = Meta(
        output_name='Кол-во роликов с хроно 35 сек. (будни)',
        tech_name='sec_35_wed',
        orig_name='Кол-во роликов с хроно 35 сек. (будни)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_40_wed: Meta = Meta(
        output_name='Кол-во роликов с хроно 40 сек. (будни)',
        tech_name='sec_40_wed',
        orig_name='Кол-во роликов с хроно 40 сек. (будни)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_45_wed: Meta = Meta(
        output_name='Кол-во роликов с хроно 45 сек. (будни)',
        tech_name='sec_45_wed',
        orig_name='Кол-во роликов с хроно 45 сек. (будни)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_50_wed: Meta = Meta(
        output_name='Кол-во роликов с хроно 50 сек. (будни)',
        tech_name='sec_50_wed',
        orig_name='Кол-во роликов с хроно 50 сек. (будни)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_55_wed: Meta = Meta(
        output_name='Кол-во роликов с хроно 55 сек. (будни)',
        tech_name='sec_55_wed',
        orig_name='Кол-во роликов с хроно 55 сек. (будни)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_60_wed: Meta = Meta(
        output_name='Кол-во роликов с хроно 60 сек. (будни)',
        tech_name='sec_60_wed',
        orig_name='Кол-во роликов с хроно 60 сек. (будни)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_5_wkd: Meta = Meta(
        output_name='Кол-во роликов с хроно 5 сек. (выходные)',
        tech_name='sec_5_wkd',
        orig_name='Кол-во роликов с хроно 5 сек. (выходные)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_10_wkd: Meta = Meta(
        output_name='Кол-во роликов с хроно 10 сек. (выходные)',
        tech_name='sec_10_wkd',
        orig_name='Кол-во роликов с хроно 10 сек. (выходные)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_15_wkd: Meta = Meta(
        output_name='Кол-во роликов с хроно 15 сек. (выходные)',
        tech_name='sec_15_wkd',
        orig_name='Кол-во роликов с хроно 15 сек. (выходные)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_20_wkd: Meta = Meta(
        output_name='Кол-во роликов с хроно 20 сек. (выходные)',
        tech_name='sec_20_wkd',
        orig_name='Кол-во роликов с хроно 20 сек. (выходные)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_25_wkd: Meta = Meta(
        output_name='Кол-во роликов с хроно 25 сек. (выходные)',
        tech_name='sec_25_wkd',
        orig_name='Кол-во роликов с хроно 25 сек. (выходные)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_30_wkd: Meta = Meta(
        output_name='Кол-во роликов с хроно 30 сек. (выходные)',
        tech_name='sec_30_wkd',
        orig_name='Кол-во роликов с хроно 30 сек. (выходные)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_35_wkd: Meta = Meta(
        output_name='Кол-во роликов с хроно 35 сек. (выходные)',
        tech_name='sec_35_wkd',
        orig_name='Кол-во роликов с хроно 35 сек. (выходные)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_40_wkd: Meta = Meta(
        output_name='Кол-во роликов с хроно 40 сек. (выходные)',
        tech_name='sec_40_wkd',
        orig_name='Кол-во роликов с хроно 40 сек. (выходные)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_45_wkd: Meta = Meta(
        output_name='Кол-во роликов с хроно 45 сек. (выходные)',
        tech_name='sec_45_wkd',
        orig_name='Кол-во роликов с хроно 45 сек. (выходные)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_50_wkd: Meta = Meta(
        output_name='Кол-во роликов с хроно 50 сек. (выходные)',
        tech_name='sec_50_wkd',
        orig_name='Кол-во роликов с хроно 50 сек. (выходные)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_55_wkd: Meta = Meta(
        output_name='Кол-во роликов с хроно 55 сек. (выходные)',
        tech_name='sec_55_wkd',
        orig_name='Кол-во роликов с хроно 55 сек. (выходные)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    sec_60_wkd: Meta = Meta(
        output_name='Кол-во роликов с хроно 60 сек. (выходные)',
        tech_name='sec_60_wkd',
        orig_name='Кол-во роликов с хроно 60 сек. (выходные)',
        type_=int,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    spots: Meta = Meta(
        output_name='Суммарное кол-во роликов',
        tech_name='spots',
        orig_name='Суммарное кол-во роликов',
        type_=int,
        xlsx_format=FormatKey.INTEGER,
        nullable=True,
    )
    price_net_wed_total: Meta = Meta(
        output_name='Стоимость роликов в будни',
        tech_name='price_net_wed_total',
        orig_name='Стоимость роликов в будни',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    price_net_wkd_total: Meta = Meta(
        output_name='Стоимость роликов в выходные',
        tech_name='price_net_wkd_total',
        orig_name='Стоимость роликов в выходные',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    price_net_total: Meta = Meta(
        output_name='Стоимость итого',
        tech_name='price_net_total',
        orig_name='Стоимость итого',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    season_c: Meta = Meta(
        output_name='Сезонный коэффициент',
        tech_name='season_c',
        orig_name='Сезонный коэффициент',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    price_net_total_1: Meta = Meta(
        output_name='Стоимость итого с учетом сезонного коэффициента',
        tech_name='price_net_total_1',
        orig_name='Стоимость итого с учетом сезонного коэффициента',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    discount: Meta = Meta(
        output_name='Скидка',
        tech_name='discount',
        orig_name='Скидка',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    price_net_total_2: Meta = Meta(
        output_name='Стоимость итого с учетом сезонного коэффициента и скидки',
        tech_name='price_net_total_2',
        orig_name='Стоимость итого с учетом сезонного коэффициента и скидки',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    pos_surcharge: Meta = Meta(
        output_name='Наценка за позиционирование',
        tech_name='pos_surcharge',
        orig_name='Наценка за позиционирование',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    extra_surcharge_1: Meta = Meta(
        output_name='Доп. наценка 1',
        tech_name='extra_surcharge_1',
        orig_name='Доп. наценка 1',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    extra_surcharge_2: Meta = Meta(
        output_name='Доп. наценка 2',
        tech_name='extra_surcharge_2',
        orig_name='Доп. наценка 2',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    price_net_final: Meta = Meta(
        output_name='Стоимость итого с учетом всех наценок и скидок',
        tech_name='price_net_final',
        orig_name='Стоимость итого с учетом всех наценок и скидок',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    target_audience: Meta = Meta(
        output_name='Целевая аудитория',
        tech_name='target_audience',
        orig_name='Целевая аудитория',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )
    aqh: Meta = Meta(
        output_name='AQH',
        tech_name='aqh',
        orig_name='AQH',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    ots: Meta = Meta(
        output_name='OTS',
        tech_name='ots',
        orig_name='OTS',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=True,
    )
    comment: Meta = Meta(
        output_name='Комментарий',
        tech_name='comment',
        orig_name='Комментарий',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )


class RadioRecord(BaseModel):
    campaign: Annotated[str | None, Field(title=RadioColumn.campaign.output_name)]
    status: Annotated[str, Field(title=RadioColumn.status.output_name)]
    radiostation: Annotated[str, Field(title=RadioColumn.radiostation.output_name)]
    details: Annotated[str | None, Field(title=RadioColumn.details.output_name)]
    broadcast: Annotated[str, Field(title=RadioColumn.broadcast.output_name)]
    placement: Annotated[str, Field(title=RadioColumn.placement.output_name)]
    month: Annotated[date, Field(title=RadioColumn.month.output_name)]
    timeslot: Annotated[str, Field(title=RadioColumn.timeslot.output_name)]
    drivetime: Annotated[str | None, Field(title=RadioColumn.drivetime.output_name)]

    price_net_30_wed: Annotated[float, Field(title=RadioColumn.price_net_30_wed.output_name)]
    price_net_30_wkd: Annotated[float, Field(title=RadioColumn.price_net_30_wkd.output_name)]

    sec_5_c: Annotated[float, Field(title=RadioColumn.sec_5_c.output_name)]
    sec_10_c: Annotated[float, Field(title=RadioColumn.sec_10_c.output_name)]
    sec_15_c: Annotated[float, Field(title=RadioColumn.sec_15_c.output_name)]
    sec_20_c: Annotated[float, Field(title=RadioColumn.sec_20_c.output_name)]
    sec_25_c: Annotated[float, Field(title=RadioColumn.sec_25_c.output_name)]
    sec_30_c: Annotated[float, Field(title=RadioColumn.sec_30_c.output_name)]
    sec_35_c: Annotated[float, Field(title=RadioColumn.sec_35_c.output_name)]
    sec_40_c: Annotated[float, Field(title=RadioColumn.sec_40_c.output_name)]
    sec_45_c: Annotated[float, Field(title=RadioColumn.sec_45_c.output_name)]
    sec_50_c: Annotated[float, Field(title=RadioColumn.sec_50_c.output_name)]
    sec_55_c: Annotated[float, Field(title=RadioColumn.sec_55_c.output_name)]
    sec_60_c: Annotated[float, Field(title=RadioColumn.sec_60_c.output_name)]

    sec_5_wed: Annotated[int, Field(title=RadioColumn.sec_5_wed.output_name)]
    sec_10_wed: Annotated[int, Field(title=RadioColumn.sec_10_wed.output_name)]
    sec_15_wed: Annotated[int, Field(title=RadioColumn.sec_15_wed.output_name)]
    sec_20_wed: Annotated[int, Field(title=RadioColumn.sec_20_wed.output_name)]
    sec_25_wed: Annotated[int, Field(title=RadioColumn.sec_25_wed.output_name)]
    sec_30_wed: Annotated[int, Field(title=RadioColumn.sec_30_wed.output_name)]
    sec_35_wed: Annotated[int, Field(title=RadioColumn.sec_35_wed.output_name)]
    sec_40_wed: Annotated[int, Field(title=RadioColumn.sec_40_wed.output_name)]
    sec_45_wed: Annotated[int, Field(title=RadioColumn.sec_45_wed.output_name)]
    sec_50_wed: Annotated[int, Field(title=RadioColumn.sec_50_wed.output_name)]
    sec_55_wed: Annotated[int, Field(title=RadioColumn.sec_55_wed.output_name)]
    sec_60_wed: Annotated[int, Field(title=RadioColumn.sec_60_wed.output_name)]

    sec_5_wkd: Annotated[int, Field(title=RadioColumn.sec_5_wkd.output_name)]
    sec_10_wkd: Annotated[int, Field(title=RadioColumn.sec_10_wkd.output_name)]
    sec_15_wkd: Annotated[int, Field(title=RadioColumn.sec_15_wkd.output_name)]
    sec_20_wkd: Annotated[int, Field(title=RadioColumn.sec_20_wkd.output_name)]
    sec_25_wkd: Annotated[int, Field(title=RadioColumn.sec_25_wkd.output_name)]
    sec_30_wkd: Annotated[int, Field(title=RadioColumn.sec_30_wkd.output_name)]
    sec_35_wkd: Annotated[int, Field(title=RadioColumn.sec_35_wkd.output_name)]
    sec_40_wkd: Annotated[int, Field(title=RadioColumn.sec_40_wkd.output_name)]
    sec_45_wkd: Annotated[int, Field(title=RadioColumn.sec_45_wkd.output_name)]
    sec_50_wkd: Annotated[int, Field(title=RadioColumn.sec_50_wkd.output_name)]
    sec_55_wkd: Annotated[int, Field(title=RadioColumn.sec_55_wkd.output_name)]
    sec_60_wkd: Annotated[int, Field(title=RadioColumn.sec_60_wkd.output_name)]

    spots: Annotated[int, Field(title=RadioColumn.spots.output_name)]

    price_net_wed_total: Annotated[float, Field(title=RadioColumn.price_net_wed_total.output_name)]
    price_net_wkd_total: Annotated[float, Field(title=RadioColumn.price_net_wkd_total.output_name)]
    price_net_total: Annotated[float, Field(title=RadioColumn.price_net_total.output_name)]

    season_c: Annotated[float, Field(title=RadioColumn.season_c.output_name)]

    price_net_total_1: Annotated[float, Field(title=RadioColumn.price_net_total_1.output_name)]

    discount: Annotated[float, Field(title=RadioColumn.discount.output_name)]

    price_net_total_2: Annotated[float, Field(title=RadioColumn.price_net_total_2.output_name)]

    pos_surcharge: Annotated[float, Field(title=RadioColumn.pos_surcharge.output_name)]
    extra_surcharge_1: Annotated[float, Field(title=RadioColumn.extra_surcharge_1.output_name)]
    extra_surcharge_2: Annotated[float, Field(title=RadioColumn.extra_surcharge_2.output_name)]

    price_net_final: Annotated[float, Field(title=RadioColumn.price_net_final.output_name)]

    target_audience: Annotated[str | None, Field(title=RadioColumn.target_audience.output_name)]
    aqh: Annotated[float, Field(title=RadioColumn.aqh.output_name)]
    ots: Annotated[float, Field(title=RadioColumn.ots.output_name)]

    comment: Annotated[str | None, Field(title=RadioColumn.comment.output_name)]

    @field_validator('campaign', mode='before')
    def validate_campaign(cls, value: str | None) -> str | None:
        if value is None or TextTools.is_empty_string(value):
            return None

        return value

    @field_validator('status', mode='before')
    def validate_status(cls, value: str | None) -> str:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        return value

    @field_validator('radiostation', mode='before')
    def validate_radiostation(cls, value: str | None) -> str:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        return value

    @field_validator('details', mode='before')
    def validate_details(cls, value: str | None) -> str | None:
        if value is None or TextTools.is_empty_string(value):
            return None

        return value

    @field_validator('broadcast', mode='before')
    def validate_broadcast(cls, value: str | None) -> str:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        return value

    @field_validator('placement', mode='before')
    def validate_placement(cls, value: str | None) -> str:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        return value

    @field_validator('month', mode='before')
    def validate_month(cls, value: str | None) -> date:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        date_ = Parser.parse_date(value)

        if date_ is None:
            raise ValueError('Отсутствует значение в ячейке.')

        return date_

    @field_validator('timeslot', mode='before')
    def validate_timeslot(cls, value: str | None) -> str:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        return value

    @field_validator('drivetime', mode='before')
    def validate_drivetime(cls, value: str | None) -> str | None:
        if value is None or TextTools.is_empty_string(value):
            return None

        return value

    @field_validator('price_net_30_wed', mode='before')
    def validate_price_net_30_wed(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('price_net_30_wkd', mode='before')
    def validate_price_net_30_wkd(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('sec_5_c', mode='before')
    def validate_sec_5_c(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('sec_10_c', mode='before')
    def validate_sec_10_c(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('sec_15_c', mode='before')
    def validate_sec_15_c(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('sec_20_c', mode='before')
    def validate_sec_20_c(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('sec_25_c', mode='before')
    def validate_sec_25_c(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('sec_30_c', mode='before')
    def validate_sec_30_c(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('sec_35_c', mode='before')
    def validate_sec_35_c(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('sec_40_c', mode='before')
    def validate_sec_40_c(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('sec_45_c', mode='before')
    def validate_sec_45_c(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('sec_50_c', mode='before')
    def validate_sec_50_c(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('sec_55_c', mode='before')
    def validate_sec_55_c(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0.0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('sec_60_c', mode='before')
    def validate_sec_60_c(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0.0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('sec_5_wed', mode='before')
    def validate_sec_5_wed(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_10_wed', mode='before')
    def validate_sec_10_wed(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_15_wed', mode='before')
    def validate_sec_15_wed(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_20_wed', mode='before')
    def validate_sec_20_wed(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_25_wed', mode='before')
    def validate_sec_25_wed(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_30_wed', mode='before')
    def validate_sec_30_wed(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_35_wed', mode='before')
    def validate_sec_35_wed(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_40_wed', mode='before')
    def validate_sec_40_wed(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_45_wed', mode='before')
    def validate_sec_45_wed(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_50_wed', mode='before')
    def validate_sec_50_wed(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_55_wed', mode='before')
    def validate_sec_55_wed(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_60_wed', mode='before')
    def validate_sec_60_wed(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_5_wkd', mode='before')
    def validate_sec_5_wkd(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_10_wkd', mode='before')
    def validate_sec_10_wkd(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_15_wkd', mode='before')
    def validate_sec_15_wkd(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_20_wkd', mode='before')
    def validate_sec_20_wkd(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_25_wkd', mode='before')
    def validate_sec_25_wkd(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_30_wkd', mode='before')
    def validate_sec_30_wkd(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_35_wkd', mode='before')
    def validate_sec_35_wkd(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_40_wkd', mode='before')
    def validate_sec_40_wkd(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_45_wkd', mode='before')
    def validate_sec_45_wkd(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_50_wkd', mode='before')
    def validate_sec_50_wkd(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_55_wkd', mode='before')
    def validate_sec_55_wkd(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('sec_60_wkd', mode='before')
    def validate_sec_60_wkd(cls, value: str | None) -> int:
        if value is None or TextTools.is_empty_string(value):
            return 0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('spots', mode='before')
    def validate_sec_spots(cls, value: str | None) -> int:
        # Кол-во роликов может быть равно 0, но отсутствие значения означает ошибку в шаблоне.
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        if not is_integer(num):
            raise ValueError('Логическая ошибка: значение должно быть целым числом.')

        return int(num)

    @field_validator('price_net_wed_total', mode='before')
    def validate_price_net_wed_total(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('price_net_wkd_total', mode='before')
    def validate_price_net_wkd_total(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('price_net_total', mode='before')
    def validate_price_net_total(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('season_c', mode='before')
    def validate_season_c(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('price_net_total_1', mode='before')
    def validate_price_net_total_1(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('discount', mode='before')
    def validate_discount(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if not 0 <= num <= 1:
            raise ValueError('Логическая ошибка: значение должно быть в диапазоне от 0 до 1.')

        return num

    @field_validator('price_net_total_2', mode='before')
    def validate_price_net_total_2(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('pos_surcharge', mode='before')
    def validate_pos_surcharge(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 1.0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('extra_surcharge_1', mode='before')
    def validate_extra_surcharge_1(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 1.0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('extra_surcharge_2', mode='before')
    def validate_extra_surcharge_2(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 1.0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('price_net_final', mode='before')
    def validate_price_net_final(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 1.0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('target_audience', mode='before')
    def validate_target_audience(cls, value: str | None) -> str | None:
        if value is None or TextTools.is_empty_string(value):
            return None

        return value

    @field_validator('aqh', mode='before')
    def validate_aqh(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            return 0.0

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('ots', mode='before')
    def validate_ots(cls, value: str | None) -> float:
        if value is None or TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')

        num = Parser.parse_num(value)

        if num is None:
            raise ValueError('Значение должно быть числом.')

        if num < 0:
            raise ValueError('Логическая ошибка: значение не может быть отрицательным числом.')

        return num

    @field_validator('comment', mode='before')
    def validate_comment(cls, value: str | None) -> str | None:
        if value is None or TextTools.is_empty_string(value):
            return None

        return value


class RadioTable:
    def __init__(self, df: pl.DataFrame) -> None:
        self.df = df

    def standardize_status_column(self) -> None:
        self.df = self.df.with_columns(
            pl.col(RadioColumn.status.tech_name).map_elements(
                lambda x: Parser.parse_status(x) or x, return_dtype=pl.String, skip_nulls=True
            )
        )

    def standardize_radiostation_column(self) -> None:
        self.df = self.df.with_columns(
            pl.col(RadioColumn.radiostation.tech_name).map_elements(
                lambda x: Parser.parse_radiostation(x) or x, return_dtype=pl.String, skip_nulls=True
            )
        )

    def standardize_broadcast_column(self) -> None:
        self.df = self.df.with_columns(
            pl.col(RadioColumn.broadcast.tech_name).map_elements(
                lambda x: Parser.parse_broadcast(x) or x, return_dtype=pl.String, skip_nulls=True
            )
        )

    def standardize_placement_column(self) -> None:
        self.df = self.df.with_columns(
            pl.col(RadioColumn.placement.tech_name).map_elements(
                lambda x: Parser.parse_placement(x) or x, return_dtype=pl.String, skip_nulls=True
            )
        )

    def standardize_timeslot_column(self) -> None:
        self.df = self.df.with_columns(
            pl.col(RadioColumn.timeslot.tech_name).map_elements(
                lambda x: Parser.parse_timeslot(x) or x, return_dtype=pl.String, skip_nulls=True
            )
        )

    def standardize_drivetime_column(self) -> None:
        self.df = self.df.with_columns(
            pl.col(RadioColumn.drivetime.tech_name).map_elements(
                lambda x: Parser.parse_drivetime(x) or x, return_dtype=pl.String, skip_nulls=True
            )
        )

    def process_template(self) -> None:
        self.standardize_status_column()
        self.standardize_radiostation_column()
        self.standardize_broadcast_column()
        self.standardize_placement_column()
        self.standardize_timeslot_column()
        self.standardize_drivetime_column()

    def get_df(self) -> pl.DataFrame:
        return self.df
