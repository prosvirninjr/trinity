import enum

import polars as pl
from pydantic import BaseModel

from core.utils.xlsx.xlsx_builder import FormatKey


class Meta(BaseModel):
    """Метаданные для столбца."""

    name: str
    type_: object
    xlsx_format: object
    nullable: bool


class NatOColumn(BaseModel):
    """Исходные столбцы в таблице."""

    spot_id_out: Meta = Meta(
        name='Ролик ID выхода',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    date_: Meta = Meta(
        name='Дата',
        type_=pl.Date,
        xlsx_format=FormatKey.ISO_DATE,
        nullable=False,
    )
    spot_time_start: Meta = Meta(
        name='Ролик время начала',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    advertisers_list: Meta = Meta(
        name='Список рекламодателей',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    brands_list: Meta = Meta(
        name='Список брендов',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    sub_brands_list: Meta = Meta(
        name='Список суббрендов',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    products_list: Meta = Meta(
        name='Список продуктов',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    spot_distribution: Meta = Meta(
        name='Ролик распространение',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    spot_type: Meta = Meta(
        name='Ролик тип',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    spot_expected_duration: Meta = Meta(
        name='Ролик ожидаемая длительность',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    spot_positioning: Meta = Meta(
        name='Ролик позиционирование',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    spot_id: Meta = Meta(
        name='Ролик ID',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    spot: Meta = Meta(
        name='Ролик',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    spot_description: Meta = Meta(
        name='Ролик описание',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    program: Meta = Meta(
        name='Программа',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    spot_id_out_original: Meta = Meta(
        name='Ролик ID выхода оригинала',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    tv_company: Meta = Meta(
        name='Телекомпания',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    block_id_out: Meta = Meta(
        name='Блок ID выхода',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )


class NatEColumn(BaseModel):
    """Дополнительные столбцы, созданные в процессе обработки."""

    year: Meta = Meta(
        name='Год',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    month: Meta = Meta(
        name='Месяц',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    week: Meta = Meta(
        name='Неделя',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    weekday: Meta = Meta(
        name='День недели',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    weekday_name: Meta = Meta(
        name='День недели [название]',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    time_start_standard: Meta = Meta(
        name='Время начала [24-часовой формат]',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    hour_start_standard: Meta = Meta(
        name='Час начала',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    time_interval_standard: Meta = Meta(
        name='Временной интервал',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    day: Meta = Meta(
        name='Время суток',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    prime_time: Meta = Meta(
        name='Prime Time',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    original_platform: Meta = Meta(
        name='Платформа оригинала',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    positioning: Meta = Meta(
        name='Позиционирование',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    channel_type: Meta = Meta(
        name='Тип канала',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    buying_audience: Meta = Meta(
        name='Баинговая аудитория',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    channel_number: Meta = Meta(
        name='Номер телеканала',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    channel: Meta = Meta(
        name='Телеканал',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    daytype: Meta = Meta(
        name='Тип дня',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    sales_tvr_tv: Meta = Meta(
        name='Sales TVR TV',
        type_=pl.Float64,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    sales_tvr_desktop: Meta = Meta(
        name='Sales TVR Desktop',
        type_=pl.Float64,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    sales_tvr_mobile: Meta = Meta(
        name='Sales TVR Mobile',
        type_=pl.Float64,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    sales_std_tvr_tv: Meta = Meta(
        name='Sales Std. TVR TV',
        type_=pl.Float64,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    sales_std_tvr_desktop: Meta = Meta(
        name='Sales Std. TVR Desktop',
        type_=pl.Float64,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    sales_std_tvr_mobile: Meta = Meta(
        name='Sales Std. TVR Mobile',
        type_=pl.Float64,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    big_sales_tvr: Meta = Meta(
        name='Big Sales TVR',
        type_=pl.Float64,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    big_sales_std_tvr: Meta = Meta(
        name='Big Sales Std. TVR',
        type_=pl.Float64,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    rounding: Meta = Meta(
        name='Округление',
        type_=pl.Float64,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    grp_rounding: Meta = Meta(
        name='GRP [округл.]',
        type_=pl.Float64,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    grp20_rounding: Meta = Meta(
        name='GRP20 [округл.]',
        type_=pl.Float64,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    grp20_min: Meta = Meta(
        name='GRP20 [min.]',
        type_=pl.Float64,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    campaign: Meta = Meta(
        name='Кампания',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )
    placement: Meta = Meta(
        name='Размещение',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )


class RegOColumn(BaseModel):
    region: Meta = Meta(
        name='Регион',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    date_: Meta = Meta(
        name='Дата',
        type_=pl.Date,
        xlsx_format=FormatKey.ISO_DATE,
        nullable=False,
    )
    spot_time_start: Meta = Meta(
        name='Ролик время начала',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    advertisers_list: Meta = Meta(
        name='Список рекламодателей',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    brands_list: Meta = Meta(
        name='Список брендов',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    sub_brands_list: Meta = Meta(
        name='Список суббрендов',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    products_list: Meta = Meta(
        name='Список продуктов',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    spot_distribution: Meta = Meta(
        name='Ролик распространение',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    spot_type: Meta = Meta(
        name='Ролик тип',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    spot_expected_duration: Meta = Meta(
        name='Ролик ожидаемая длительность',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    spot_positioning: Meta = Meta(
        name='Ролик позиционирование',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    spot_id: Meta = Meta(
        name='Ролик ID',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    spot_description: Meta = Meta(
        name='Ролик описание',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    program: Meta = Meta(
        name='Программа',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    spot_id_out: Meta = Meta(
        name='Ролик ID выхода',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    block_id_out: Meta = Meta(
        name='Блок ID выхода',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    national_company: Meta = Meta(
        name='Национальная телекомпания',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    original_company: Meta = Meta(
        name='Телекомпания оригинала',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )


class RegEColumn(BaseModel):
    year: Meta = Meta(
        name='Год',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    month: Meta = Meta(
        name='Месяц',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    week: Meta = Meta(
        name='Неделя',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    weekday: Meta = Meta(
        name='День недели',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    weekday_name: Meta = Meta(
        name='День недели [название]',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    time_start_standard: Meta = Meta(
        name='Время начала [24-часовой формат]',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    hour_start_standard: Meta = Meta(
        name='Час начала',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    time_interval_standard: Meta = Meta(
        name='Временной интервал',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    day: Meta = Meta(
        name='Время суток',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    prime_time: Meta = Meta(
        name='Prime Time',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    buying_audience: Meta = Meta(
        name='Баинговая аудитория',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    channel_number: Meta = Meta(
        name='Номер телеканала',
        type_=pl.Int64,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    channel: Meta = Meta(
        name='Телеканал',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    rounding: Meta = Meta(
        name='Округление',
        type_=pl.Float64,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    campaign: Meta = Meta(
        name='Кампания',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )
    placement: Meta = Meta(
        name='Размещение',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )
    daytype: Meta = Meta(
        name='Тип дня',
        type_=pl.String,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )


class Day(enum.StrEnum):
    """Время суток"""

    DAY = 'День'
    NIGHT = 'Ночь'


class Platform(enum.StrEnum):
    """Платформа"""

    TV = 'ТВ'
    INTERNET = 'Интернет'


class Distribution(enum.StrEnum):
    """Блок распространение"""

    NETWORK = 'Сетевой'
    ORBITAL = 'Орбитальный'


class PrimeTime(enum.StrEnum):
    """Prime Time"""

    PT = 'Prime'
    OP = 'Off Prime'


class Position(enum.StrEnum):
    """Ролик позиционирование"""

    MIDDLE = 'Средний'
    PREMIUM = 'Премиальный'


class Sale(enum.StrEnum):
    """Тип продажи"""

    MIN = 'минуты'
    GRP = 'GRP'


class SpotType(enum.StrEnum):
    """Ролик тип"""

    CLIP = 'Ролик'
