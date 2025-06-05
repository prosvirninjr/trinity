import enum
import math
from dataclasses import dataclass
from datetime import datetime

import polars as pl
from polars import DataFrame
from pydantic import BaseModel, Field, field_validator

import app_assets
from core.ooh.logic import Coefficient, Construction, Geo
from core.ooh.ooh_parser import OOHParser as Parser
from core.utils.tools import TextTools
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
class OOHColumn:
    """Исходные столбцы в таблице."""

    index: Meta = Meta(
        orig_name='№',
        tech_name='index',
        output_name='Индекс',
        type_=int,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    advertiser: Meta = Meta(
        orig_name='Рекламодатель',
        tech_name='advertiser',
        output_name='Рекламодатель',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    campaign: Meta = Meta(
        orig_name='Наименование РК или Продукта',
        tech_name='campaign',
        output_name='Наименование РК или Продукта',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    subject: Meta = Meta(
        orig_name='Субъект',
        tech_name='subject',
        output_name='Субъект',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    location: Meta = Meta(
        orig_name='Город',
        tech_name='location',
        output_name='Местоположение',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    address: Meta = Meta(
        orig_name='Адрес',
        tech_name='address',
        output_name='Адрес',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    format_: Meta = Meta(
        orig_name='Тип конструкции Пример: BB, CB, CF…',
        tech_name='format_',
        output_name='Формат',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    size: Meta = Meta(
        orig_name='Размер конструкции, м. Пример: 1.2x1.8',
        tech_name='size',
        output_name='Размер',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    side: Meta = Meta(
        orig_name='Сторона A | B',
        tech_name='side',
        output_name='Сторона',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    month: Meta = Meta(
        orig_name='Месяц',
        tech_name='month',
        output_name='Месяц',
        type_=int,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    start_date: Meta = Meta(
        orig_name='Начало аренды В формате даты',
        tech_name='start_date',
        output_name='Начало аренды',
        type_=datetime,
        xlsx_format=FormatKey.ISO_DATE,
        nullable=False,
    )
    end_date: Meta = Meta(
        orig_name='Окончание аренды В формате даты',
        tech_name='end_date',
        output_name='Окончание аренды',
        type_=datetime,
        xlsx_format=FormatKey.ISO_DATE,
        nullable=False,
    )
    spot_duration: Meta = Meta(
        orig_name='Длительность ролика Не заполняется для статики',
        tech_name='spot_duration',
        output_name='Длительность ролика',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    spots_per_block: Meta = Meta(
        orig_name='Количество выходов в блоке Не заполняется для статики',
        tech_name='spots_per_block',
        output_name='Количество выходов в блоке',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    block_duration: Meta = Meta(
        orig_name='Длительность блока Не заполняется для статики',
        tech_name='block_duration',
        output_name='Длительность блока',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    spots_per_day: Meta = Meta(
        orig_name='Выходов в сутки Не заполняется для статики',
        tech_name='spots_per_day',
        output_name='Количество выходов в сутки',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    hours_per_day: Meta = Meta(
        orig_name='Время работы конструкции Стандартное значение, часов в сутки',
        tech_name='hours_per_day',
        output_name='Количество часов в сутки',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    gid: Meta = Meta(
        orig_name='GID | ID конструкции',
        tech_name='gid',
        output_name='GID',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    client_construction_id: Meta = Meta(
        orig_name='№ конструкции в программе клиента',
        tech_name='client_construction_id',
        output_name='№ конструкции в программе клиента',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    material: Meta = Meta(
        orig_name='Материал',
        tech_name='material',
        output_name='Материал',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    daily_grp: Meta = Meta(
        orig_name='Daily GRP',
        tech_name='daily_grp',
        output_name='Daily GRP',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    latitude: Meta = Meta(
        orig_name='Широта ° В десятичном формате',
        tech_name='latitude',
        output_name='Широта',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    longitude: Meta = Meta(
        orig_name='Долгота ° В десятичном формате',
        tech_name='longitude',
        output_name='Долгота',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    operator: Meta = Meta(
        orig_name='Оператор | Поставщик',
        tech_name='operator',
        output_name='Оператор | Поставщик',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    comment: Meta = Meta(
        orig_name='Комментарий',
        tech_name='comment',
        output_name='Комментарий',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=True,
    )
    placement_price_list: Meta = Meta(
        orig_name='Стоимость размещения Прайс-лист, руб. до НДС',
        tech_name='placement_price_list',
        output_name='Размещение прайс-лист',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    placement_discount: Meta = Meta(
        orig_name='Скидка от прайс-листа, %',
        tech_name='placement_discount',
        output_name='Скидка на размещение',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    placement_price_net: Meta = Meta(
        orig_name='Стоимость размещения со скидкой руб. до НДС',
        tech_name='placement_price_net',
        output_name='Размещение со скидкой до НДС',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    placement_vat: Meta = Meta(
        orig_name='НДС, % Размещение',
        tech_name='placement_vat',
        output_name='НДС на размещение',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    placement_price_with_vat: Meta = Meta(
        orig_name='Стоимость размещения со скидкой руб. с НДС',
        tech_name='placement_price_with_vat',
        output_name='Стоимость размещения с НДС',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    production_price_net: Meta = Meta(
        orig_name='Стоимость одного производства руб. до НДС',
        tech_name='production_price_net',
        output_name='Стоимость производства',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    production_quantity_format: Meta = Meta(
        orig_name='Количество, ед. Производство',
        tech_name='production_quantity_format',
        output_name='Количество форматов производства',
        type_=int,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    production_price_net_total: Meta = Meta(
        orig_name='Общая стоимость производства руб. до НДС',
        tech_name='production_price_net_total',
        output_name='Стоимость производства (без НДС) всего формата',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    production_vat: Meta = Meta(
        orig_name='НДС, % Производство',
        tech_name='production_vat',
        output_name='НДС на производство',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    production_price_total_with_vat: Meta = Meta(
        orig_name='Общая стоимость производства руб. с НДС',
        tech_name='production_price_total_with_vat',
        output_name='Стоимость производства (с НДС) всего формата',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    main_installation_price_net: Meta = Meta(
        orig_name='Стоимость основного монтажа руб. до НДС',
        tech_name='main_installation_price_net',
        output_name='Стоимость основного монтажа',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    main_installation_vat: Meta = Meta(
        orig_name='НДС, % Основной монтаж',
        tech_name='main_installation_vat',
        output_name='НДС на основной монтаж',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    main_installation_price_with_vat: Meta = Meta(
        orig_name='Стоимость основного монтажа руб. с НДС',
        tech_name='main_installation_price_with_vat',
        output_name='Стоимость основного монтажа (с НДС)',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    extra_installation_price_net: Meta = Meta(
        orig_name='Стоимость доп. монтажа руб. до НДС',
        tech_name='extra_installation_price_net',
        output_name='Стоимость доп. монтажа',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    extra_installation_quantity: Meta = Meta(
        orig_name='Количество, ед. Доп. монтаж',
        tech_name='extra_installation_quantity',
        output_name='Количество доп. монтажей',
        type_=int,
        xlsx_format=FormatKey.INTEGER,
        nullable=False,
    )
    extra_installation_price_net_total: Meta = Meta(
        orig_name='Общая стоимость доп. монтажей руб. до НДС',
        tech_name='extra_installation_price_net_total',
        output_name='Стоимость доп. монтажа (без НДС) итого',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    extra_installation_vat: Meta = Meta(
        orig_name='НДС, % Доп. монтаж',
        tech_name='extra_installation_vat',
        output_name='НДС на доп. монтаж',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    extra_installation_price_total_with_vat: Meta = Meta(
        orig_name='Общая стоимость доп. монтажей руб. с НДС',
        tech_name='extra_installation_price_total_with_vat',
        output_name='Стоимость доп. монтажа (с НДС) итого',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    delivery_price_net: Meta = Meta(
        orig_name='Стоимость доставки руб. до НДС',
        tech_name='delivery_price_net',
        output_name='Стоимость доставки',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    delivery_vat: Meta = Meta(
        orig_name='НДС, % Доставка',
        tech_name='delivery_vat',
        output_name='НДС на доставку',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    delivery_price_with_vat: Meta = Meta(
        orig_name='Стоимость доставки руб. с НДС',
        tech_name='delivery_price_with_vat',
        output_name='Стоимость доставки (с НДС)',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    price_net_total_format: Meta = Meta(
        orig_name='Полная стоимость руб. до НДС',
        tech_name='price_net_total_format',
        output_name='Итого стоимость формата (без НДС)',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    price_total_with_vat_format: Meta = Meta(
        orig_name='Полная стоимость руб. с НДС',
        tech_name='price_total_with_vat_format',
        output_name='Итого стоимость формата (с НДС)',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )


@dataclass
class EOOHColumn:
    """Дополнительные столбцы в таблице."""

    base_price: Meta = Meta(
        orig_name='Base Price',
        tech_name='base_price',
        output_name='Базовая цена',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    advertisers: Meta = Meta(
        orig_name='Advertisers',
        tech_name='advertisers',
        output_name='Рекламодатели',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    operators: Meta = Meta(
        orig_name='Operators',
        tech_name='operators',
        output_name='Операторы',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    constructions: Meta = Meta(
        orig_name='Constructions',
        tech_name='constructions',
        output_name='Конструкции',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    advertiser_shares: Meta = Meta(
        orig_name='Advertiser Shares',
        tech_name='advertiser_shares',
        output_name='Доли рекламодателей',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    operator_shares: Meta = Meta(
        orig_name='Operator Shares',
        tech_name='operator_shares',
        output_name='Доли операторов',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    subject_code: Meta = Meta(
        orig_name='Subject Code',
        tech_name='subject_code',
        output_name='Код субъекта',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    subject_name: Meta = Meta(
        orig_name='Subject Name',
        tech_name='subject_name',
        output_name='Название субъекта',
        type_=str,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    user_c: Meta = Meta(
        orig_name='User C',
        tech_name='user_c',
        output_name='Пользователь C',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    is_digital: Meta = Meta(
        orig_name='Is Digital',
        tech_name='is_digital',
        output_name='Цифровая конструкция',
        type_=bool,
        xlsx_format=FormatKey.TEXT,
        nullable=False,
    )
    rental_c: Meta = Meta(
        orig_name='Rental C',
        tech_name='rental_c',
        output_name='Аренда C',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    digital_c: Meta = Meta(
        orig_name='Digital C',
        tech_name='digital_c',
        output_name='Цифровая C',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    side_c: Meta = Meta(
        orig_name='Side C',
        tech_name='side_c',
        output_name='Сторона C',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    season_c: Meta = Meta(
        orig_name='Season C',
        tech_name='season_c',
        output_name='Сезон C',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )


@dataclass
class TOOHColumn:
    """Технические столбцы через Meta."""

    width: Meta = Meta(
        orig_name='_width',
        tech_name='_width',
        output_name='_width',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    height: Meta = Meta(
        orig_name='_height',
        tech_name='_height',
        output_name='_height',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    distance: Meta = Meta(
        orig_name='_distance',
        tech_name='_distance',
        output_name='_distance',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )
    weight: Meta = Meta(
        orig_name='_weight',
        tech_name='_weight',
        output_name='_weight',
        type_=float,
        xlsx_format=FormatKey.FLOAT_4,
        nullable=False,
    )


class OOHRecord(BaseModel):
    index: int | None = Field(default=None, title=OOHColumn.index.output_name)
    advertiser: str = Field(title=OOHColumn.advertiser.output_name)
    campaign: str | None = Field(default=None, title=OOHColumn.campaign.output_name)
    subject: str | None = Field(default=None, title=OOHColumn.subject.output_name)
    location: str | None = Field(default=None, title=OOHColumn.location.output_name)
    address: str | None = Field(default=None, title=OOHColumn.address.output_name)
    format_: str = Field(title=OOHColumn.format_.output_name)
    size: str | None = Field(default=None, title=OOHColumn.size.output_name)
    side: str = Field(title=OOHColumn.side.output_name)
    month: int = Field(title=OOHColumn.month.output_name)
    start_date: datetime = Field(title=OOHColumn.start_date.output_name)
    end_date: datetime = Field(title=OOHColumn.end_date.output_name)
    spot_duration: float | None = Field(default=None, title=OOHColumn.spot_duration.output_name)
    spots_per_block: float | None = Field(default=None, title=OOHColumn.spots_per_block.output_name)
    block_duration: float | None = Field(default=None, title=OOHColumn.block_duration.output_name)
    spots_per_day: float | None = Field(default=None, title=OOHColumn.spots_per_day.output_name)
    hours_per_day: float | None = Field(default=None, title=OOHColumn.hours_per_day.output_name)
    gid: str | None = Field(default=None, title=OOHColumn.gid.output_name)
    client_construction_id: str | None = Field(default=None, title=OOHColumn.client_construction_id.output_name)
    material: str | None = Field(default=None, title=OOHColumn.material.output_name)
    daily_grp: float | None = Field(default=None, title=OOHColumn.daily_grp.output_name)
    latitude: float = Field(title=OOHColumn.latitude.output_name)
    longitude: float = Field(title=OOHColumn.longitude.output_name)
    operator: str | None = Field(default=None, title=OOHColumn.operator.output_name)
    comment: str | None = Field(default=None, title=OOHColumn.comment.output_name)
    placement_price_list: float = Field(title=OOHColumn.placement_price_list.output_name)
    placement_discount: float = Field(title=OOHColumn.placement_discount.output_name)
    placement_price_net: float = Field(title=OOHColumn.placement_price_net.output_name)
    placement_vat: float = Field(default=0.0, title=OOHColumn.placement_vat.output_name)
    placement_price_with_vat: float = Field(title=OOHColumn.placement_price_with_vat.output_name)
    production_price_net: float = Field(default=0.0, title=OOHColumn.production_price_net.output_name)
    production_quantity_format: int = Field(default=0, title=OOHColumn.production_quantity_format.output_name)
    production_price_net_total: float = Field(title=OOHColumn.production_price_net_total.output_name)
    production_vat: float = Field(default=0.0, title=OOHColumn.production_vat.output_name)
    production_price_total_with_vat: float = Field(title=OOHColumn.production_price_total_with_vat.output_name)
    main_installation_price_net: float = Field(default=0.0, title=OOHColumn.main_installation_price_net.output_name)
    main_installation_vat: float = Field(default=0.0, title=OOHColumn.main_installation_vat.output_name)
    main_installation_price_with_vat: float = Field(title=OOHColumn.main_installation_price_with_vat.output_name)
    extra_installation_price_net: float = Field(default=0.0, title=OOHColumn.extra_installation_price_net.output_name)
    extra_installation_quantity: int = Field(default=0, title=OOHColumn.extra_installation_quantity.output_name)
    extra_installation_price_net_total: float = Field(title=OOHColumn.extra_installation_price_net_total.output_name)
    extra_installation_vat: float = Field(default=0.0, title=OOHColumn.extra_installation_vat.output_name)
    extra_installation_price_total_with_vat: float = Field(
        title=OOHColumn.extra_installation_price_total_with_vat.output_name
    )
    delivery_price_net: float = Field(default=0.0, title=OOHColumn.delivery_price_net.output_name)
    delivery_vat: float = Field(default=0.0, title=OOHColumn.delivery_vat.output_name)
    delivery_price_with_vat: float = Field(title=OOHColumn.delivery_price_with_vat.output_name)
    price_net_total_format: float = Field(title=OOHColumn.price_net_total_format.output_name)
    price_total_with_vat_format: float = Field(title=OOHColumn.price_total_with_vat_format.output_name)

    @field_validator('location', mode='before')
    def validate_location(cls, value: str) -> str | None:
        if TextTools.is_empty_string(value):
            return None

        return str(value).strip()

    @field_validator('format_', mode='before')
    def validate_format(cls, value: str) -> str:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        return str(value).strip()

    @field_validator('size', mode='before')
    def validate_size(cls, value: str) -> str | None:
        if TextTools.is_empty_string(value):
            return None
        return str(value).strip()

    @field_validator('side', mode='before')
    def validate_side(cls, value: str) -> str:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        return str(value).strip()

    @field_validator('month', mode='before')
    def validate_month(cls, value: str) -> int:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Не удалось распознать число в ячейке.')

        int_value = int(num_value)

        if not (1 <= int_value <= 12):
            raise ValueError('Логическая ошибка: значение в ячейке должно быть в диапазоне от 1 до 12 включительно.')
        return int_value

    @field_validator('start_date', mode='before')
    def validate_start_date(cls, value: str) -> datetime:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        dt_value = Parser.parse_date(value)
        if dt_value is None:
            raise ValueError('Не удалось распознать дату в ячейке.')
        return dt_value

    @field_validator('end_date', mode='before')
    def validate_end_date(cls, value: str) -> datetime:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        dt_value = Parser.parse_date(value)
        if dt_value is None:
            raise ValueError('Не удалось распознать дату в ячейке.')
        return dt_value

    @field_validator('spot_duration', mode='before')
    def validate_spot_duration(cls, value: str) -> float | None:
        if TextTools.is_empty_string(value):
            return None
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Не удалось распознать число в ячейке.')
        if num_value <= 0:
            raise ValueError(
                'Логическая ошибка: значение в ячейке не может быть отрицательным числом или равняться нулю.'
            )
        return num_value

    @field_validator('spots_per_block', mode='before')
    def validate_spots_per_block(cls, value: str) -> float | None:
        if TextTools.is_empty_string(value):
            return None
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Не удалось распознать число в ячейке.')
        if num_value <= 0:
            raise ValueError(
                'Логическая ошибка: значение в ячейке не может быть отрицательным числом или равняться нулю.'
            )
        return num_value

    @field_validator('block_duration', mode='before')
    def validate_block_duration(cls, value: str) -> float | None:
        if TextTools.is_empty_string(value):
            return None
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Не удалось распознать число в ячейке.')
        if num_value <= 0:
            raise ValueError(
                'Логическая ошибка: значение в ячейке не может быть отрицательным числом или равняться нулю.'
            )
        return num_value

    @field_validator('spots_per_day', mode='before')
    def validate_spots_per_day(cls, value: str) -> float | None:
        if TextTools.is_empty_string(value):
            return None
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Не удалось распознать число в ячейке.')
        if num_value <= 0:
            raise ValueError(
                'Логическая ошибка: значение в ячейке не может быть отрицательным числом или равняться нулю.'
            )
        return num_value

    @field_validator('hours_per_day', mode='before')
    def validate_hours_per_day(cls, value: str) -> float | None:
        if TextTools.is_empty_string(value):
            return None
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Не удалось распознать число в ячейке.')
        if not (0 < num_value <= 24):
            if num_value <= 0:
                raise ValueError('Логическая ошибка: значение в ячейке должно быть больше 0.')
            else:
                # Если значение близко к 24, то округляем до 24
                if not math.isclose(num_value, 24, abs_tol=0.1):
                    raise ValueError(
                        'Логическая ошибка: значение в ячейке должно быть в диапазоне (0, 24] включительно.'
                    )
                else:
                    return 24.0

        return num_value

    @field_validator('daily_grp', mode='before')
    def validate_daily_grp(cls, value: str) -> float | None:
        if TextTools.is_empty_string(value):
            return None
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Не удалось распознать число в ячейке.')
        if num_value <= 0:
            raise ValueError(
                'Логическая ошибка: значение в ячейке не может быть отрицательным числом или равняться нулю.'
            )
        return num_value

    @field_validator('latitude', mode='before')
    def validate_latitude(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        coord_value = Parser.parse_coord(value)
        if coord_value is None:
            raise ValueError('Не удалось распознать координату в ячейке.')
        if not (-90 <= coord_value <= 90):
            raise ValueError('Логическая ошибка: значение широты должно быть в диапазоне от -90 до 90 включительно.')
        return round(coord_value, 6)

    @field_validator('longitude', mode='before')
    def validate_longitude(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        coord_value = Parser.parse_coord(value)
        if coord_value is None:
            raise ValueError('Не удалось распознать координату в ячейке.')
        if not (-180 <= coord_value <= 180):
            raise ValueError('Логическая ошибка: значение долготы должно быть в диапазоне от -180 до 180 включительно.')
        return round(coord_value, 6)

    @field_validator('operator', mode='before')
    def validate_operator(cls, value: str) -> str | None:
        if TextTools.is_empty_string(value):
            return None

        return str(value).strip()

    @field_validator('placement_price_list', mode='before')
    def validate_placement_price_list(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('placement_discount', mode='before')
    def validate_placement_discount(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if not (0 <= num_value <= 1):
            if num_value < 0:
                raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
            else:
                raise ValueError('Логическая ошибка: значение скидки должно быть в диапазоне от 0 до 1 включительно.')
        return num_value

    @field_validator('placement_price_net', mode='before')
    def validate_placement_price_net(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('placement_vat', mode='before')
    def validate_placement_vat(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            return 0.0
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if not (0 <= num_value <= 1):
            if num_value < 0:
                raise ValueError('Логическая ошибка: значение НДС не может быть отрицательным числом.')
            else:
                raise ValueError('Логическая ошибка: значение НДС должно быть в диапазоне от 0 до 1 включительно.')
        return num_value

    @field_validator('placement_price_with_vat', mode='before')
    def validate_placement_price_with_vat(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('production_price_net', mode='before')
    def validate_production_price_net(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            return 0.0
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('production_quantity_format', mode='before')
    def validate_production_quantity_format(cls, value: str) -> int:
        if TextTools.is_empty_string(value):
            return 0
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')

        return int(num_value)

    @field_validator('production_price_net_total', mode='before')
    def validate_production_price_net_total(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('production_vat', mode='before')
    def validate_production_vat(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            return 0.0
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if not (0 <= num_value <= 1):
            if num_value < 0:
                raise ValueError('Логическая ошибка: значение НДС не может быть отрицательным числом.')
            else:
                raise ValueError('Логическая ошибка: значение НДС должно быть в диапазоне от 0 до 1 включительно.')
        return num_value

    @field_validator('production_price_total_with_vat', mode='before')
    def validate_production_price_total_with_vat(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('main_installation_price_net', mode='before')
    def validate_main_installation_price_net(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            return 0.0
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('main_installation_vat', mode='before')
    def validate_main_installation_vat(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            return 0.0
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if not (0 <= num_value <= 1):
            if num_value < 0:
                raise ValueError('Логическая ошибка: значение НДС не может быть отрицательным числом.')
            else:
                raise ValueError('Логическая ошибка: значение НДС должно быть в диапазоне от 0 до 1 включительно.')
        return num_value

    @field_validator('main_installation_price_with_vat', mode='before')
    def validate_main_installation_price_with_vat(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('extra_installation_price_net', mode='before')
    def validate_extra_installation_price_net(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            return 0.0
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('extra_installation_quantity', mode='before')
    def validate_extra_installation_quantity(cls, value: str) -> int:
        if TextTools.is_empty_string(value):
            return 0
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return int(num_value)

    @field_validator('extra_installation_price_net_total', mode='before')
    def validate_extra_installation_price_net_total(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('extra_installation_vat', mode='before')
    def validate_extra_installation_vat(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            return 0.0
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if not (0 <= num_value <= 1):
            if num_value < 0:
                raise ValueError('Логическая ошибка: значение НДС не может быть отрицательным числом.')
            else:
                raise ValueError('Логическая ошибка: значение НДС должно быть в диапазоне от 0 до 1 включительно.')
        return num_value

    @field_validator('extra_installation_price_total_with_vat', mode='before')
    def validate_extra_installation_price_total_with_vat(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('delivery_price_net', mode='before')
    def validate_delivery_price_net(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            return 0.0
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('delivery_vat', mode='before')
    def validate_delivery_vat(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            return 0.0
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if not (0 <= num_value <= 1):
            if num_value < 0:
                raise ValueError('Логическая ошибка: значение НДС не может быть отрицательным числом.')
            else:
                raise ValueError('Логическая ошибка: значение НДС должно быть в диапазоне от 0 до 1 включительно.')
        return num_value

    @field_validator('delivery_price_with_vat', mode='before')
    def validate_delivery_price_with_vat(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('price_net_total_format', mode='before')
    def validate_price_net_total_format(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value

    @field_validator('price_total_with_vat_format', mode='before')
    def validate_price_total_with_vat_format(cls, value: str) -> float:
        if TextTools.is_empty_string(value):
            raise ValueError('Отсутствует значение в ячейке.')
        num_value = Parser.parse_num(value)
        if num_value is None:
            raise ValueError('Значение в ячейке должно быть числом.')
        if num_value < 0:
            raise ValueError('Логическая ошибка: значение в ячейке не может быть отрицательным числом.')
        return num_value


@dataclass(frozen=True)
class CMethod:
    """Методы расчета."""

    default: str = 'По умолчанию'
    operator_plus: str = 'Оператор+'


@dataclass(frozen=True)
class SMethod:
    """Методы сглаживания."""

    mean: str = 'Среднее'
    weighted_mean: str = 'Взвешенное среднее'
    trimmed_mean: str = 'Усеченное среднее'
    median: str = 'Медиана'


@dataclass(frozen=True)
class Years:
    """Годы."""

    _2023: int = 2023
    _2024: int = 2024
    _2025: int = 2025


class AnalyzerParams(enum.Enum):
    """Параметры расчета."""

    RADIUS_MAX_MF = 0.1  # Максимальный радиус в км.
    RADIUS_MAX_DEFAULT = 5.0  # Максимальный радиус в км.
    RADIUS_MIN_MF = 0.0  # Минимальный радиус в км.
    RADIUS_MIN_DEFAULT = 0.0  # Минимальный радиус в км.
    RADIUS_STEP_MF = 0.01  # Шаг радиуса в км.
    RADIUS_STEP_DEFAULT = 0.5  # Шаг радиуса в км.
    REQUIRED_COUNT_MIN = 3  # Минимальное количество конструкций для формирования панели.
    REQUIRED_COUNT_DEFAULT = 10  # Количество конструкций по умолчанию.
    BASE_PRICE_TOLERANCE = 0.5  # Допуск для базовой цены (максимальное отличие в 50%).
    SIZE_TOLERANCE = 0.15  # Допуск для размера (максимальное отличие в 15%).

    @classmethod
    def get_values(cls) -> list[float]:
        """Возвращает отсортированный список значений."""
        return sorted(member.value for member in cls)


# --- Форматы конструкций ---
class Formats(enum.StrEnum):
    """Форматы конструкций."""

    MF = 'MF'
    DIGITAL = 'DIGITAL'
    NON_DIGITAL = 'NON_DIGITAL'

    @classmethod
    def get_values(cls) -> list[str]:
        """Возвращает отсортированный список значений."""
        return sorted(member.value for member in cls)


# --- Конфигурация OOH ---
class OOHConfig(enum.StrEnum):
    """Конфигурация OOH."""

    TOP_OPERATORS = 'TOP_OPERATORS'

    @classmethod
    def get_values(cls) -> list[str]:
        """Возвращает отсортированный список значений."""
        return sorted(member.value for member in cls)


class Template:
    """Шаблон OOH."""

    def __init__(self, df: DataFrame):
        self.df = df

    def _create_tech_columns(self) -> None:
        """Создает вспомогательные столбцы для векторизованных вычислений."""
        sizes = [Construction.get_sizes(row[OOHColumn.size.tech_name]) for row in self.df.iter_rows(named=True)]

        self.df = self.df.with_columns(
            pl.Series([size[0] for size in sizes]).alias(TOOHColumn.width.tech_name),
            pl.Series([size[1] for size in sizes]).alias(TOOHColumn.height.tech_name),
        )

    def _create_is_digital_column(self) -> None:
        """Создает столбец с маркерами digital конструкций."""
        self.df = self.df.with_columns(
            pl.col(OOHColumn.hours_per_day.tech_name)
            .map_elements(lambda x: True if x else False, return_dtype=pl.Boolean, skip_nulls=False)
            .alias(EOOHColumn.is_digital.tech_name)
        )

    def _create_rental_c_column(self) -> None:
        """Создает столбец с коэффициентами длительности аренды."""
        self.df = self.df.with_columns(
            pl.struct(OOHColumn.start_date.tech_name, OOHColumn.end_date.tech_name)
            .map_elements(
                lambda x: Coefficient.calc_rental_c(x[OOHColumn.start_date.tech_name], x[OOHColumn.end_date.tech_name]),
                return_dtype=pl.Float64,
                skip_nulls=False,
            )
            .alias(EOOHColumn.rental_c.tech_name)
        )

    def _create_digital_c_column(self) -> None:
        # Если digital параметры конструкции - None, задаем коэффициент равный 1.0, для исключения влияния на расчет.
        coefficients = [
            1.0
            if (
                row[OOHColumn.format_.tech_name] is None
                or row[OOHColumn.spot_duration.tech_name] is None
                or row[OOHColumn.spots_per_block.tech_name] is None
                or row[OOHColumn.block_duration.tech_name] is None
            )
            else Coefficient.calc_digital_c(
                row[OOHColumn.format_.tech_name],
                row[OOHColumn.spot_duration.tech_name],
                row[OOHColumn.spots_per_block.tech_name],
                row[OOHColumn.block_duration.tech_name],
            )
            for row in self.df.iter_rows(named=True)
        ]
        self.df = self.df.with_columns(pl.Series(coefficients).alias(EOOHColumn.digital_c.tech_name))

    def _create_side_c_column(self) -> None:
        coefficients = [
            Coefficient.calc_side_c(row[OOHColumn.side.tech_name], strict=False)
            for row in self.df.iter_rows(named=True)
        ]
        self.df = self.df.with_columns(pl.Series(coefficients).alias(EOOHColumn.side_c.tech_name))

    def _create_season_c_column(self) -> None:
        coefficients = [
            Coefficient.calc_season_c(row[OOHColumn.month.tech_name], strict=False)
            for row in self.df.iter_rows(named=True)
        ]
        self.df = self.df.with_columns(pl.Series(coefficients).alias(EOOHColumn.season_c.tech_name))

    def _create_subject_code_column(self) -> None:
        subject_codes = [
            Geo.locate_point(row[OOHColumn.latitude.tech_name], row[OOHColumn.longitude.tech_name])
            for row in self.df.iter_rows(named=True)
        ]
        self.df = self.df.with_columns(pl.Series(subject_codes).alias(EOOHColumn.subject_code.tech_name))

    def _create_base_price_column(self) -> None:
        base_prices = [
            row[OOHColumn.placement_price_net.tech_name]
            / (
                row[EOOHColumn.digital_c.tech_name]
                * row[EOOHColumn.rental_c.tech_name]
                * row[EOOHColumn.side_c.tech_name]
                * row[EOOHColumn.season_c.tech_name]
            )
            for row in self.df.iter_rows(named=True)
        ]
        self.df = self.df.with_columns(pl.Series(base_prices, dtype=pl.Float64).alias(EOOHColumn.base_price.tech_name))

    def _create_user_c_column(self) -> None:
        self.df = self.df.with_columns(pl.lit(1).alias(EOOHColumn.user_c.tech_name))

    def _parse_advertiser_column(self) -> None:
        advertisers = app_assets.load_advertisers()

        self.df = self.df.with_columns(
            pl.col(OOHColumn.advertiser.tech_name)
            .map_elements(
                lambda x: Parser.parse_object(x, choices=advertisers) or x,
                return_dtype=pl.String,
                skip_nulls=True,
            )
            .alias(OOHColumn.advertiser.tech_name)
        )

    def _get_current_data(
        self, data: dict[str, dict[str, dict[str, object]]], subject_code: str
    ) -> dict[str, list[str]]:
        current_data = data.get(subject_code, {})
        return {location: info.get('options', []) for location, info in current_data.items()}  # type: ignore

    def _parse_location_column(self) -> None:
        subject_codes = self.df[EOOHColumn.subject_code.tech_name]
        original_locs = self.df[OOHColumn.location.tech_name]
        parsed = []
        for subj, loc in zip(subject_codes, original_locs):
            out = Parser.parse_location(subj, loc)
            parsed.append(out if out is not None else loc)
        self.df = self.df.with_columns(pl.Series(parsed).alias(OOHColumn.location.tech_name))

    def _parse_format_column(self) -> None:
        self.df = self.df.with_columns(
            pl.col(OOHColumn.format_.tech_name)
            .map_elements(
                lambda x: Parser.parse_format(x) or x,
                return_dtype=pl.String,
                skip_nulls=True,
            )
            .alias(OOHColumn.format_.tech_name)
        )

    def _parse_size_column(self) -> None:
        self.df = self.df.with_columns(
            pl.col(OOHColumn.size.tech_name)
            .map_elements(
                lambda x: Parser.parse_size(x) or x,
                return_dtype=pl.String,
                skip_nulls=True,
            )
            .alias(OOHColumn.size.tech_name)
        )

    def _parse_side_column(self) -> None:
        self.df = self.df.with_columns(
            pl.col(OOHColumn.side.tech_name)
            .map_elements(
                lambda x: Parser.parse_side(x) or x,
                return_dtype=pl.String,
                skip_nulls=True,
            )
            .alias(OOHColumn.side.tech_name)
        )

    def _parse_operator_column(self) -> None:
        self.df = self.df.with_columns(
            pl.col(OOHColumn.operator.tech_name)
            .map_elements(
                lambda x: Parser.parse_operator(x) or x,
                return_dtype=pl.String,
                skip_nulls=True,
            )
            .alias(OOHColumn.operator.tech_name)
        )

    def create_extra_columns(self) -> None:
        """Создает дополнительные столбцы для векторизованных вычислений."""
        self._create_tech_columns()
        self._create_is_digital_column()
        self._create_rental_c_column()
        self._create_digital_c_column()
        self._create_side_c_column()
        self._create_season_c_column()
        self._create_subject_code_column()
        self._create_base_price_column()
        self._create_user_c_column()

    def parse_columns(self) -> None:
        self._parse_advertiser_column()
        self._parse_location_column()
        self._parse_operator_column()
        self._parse_format_column()
        self._parse_size_column()
        self._parse_side_column()

    def process_template(self) -> None:
        """Обрабатывает шаблон OOH."""
        self.create_extra_columns()
        self.parse_columns()

    def get_df(self) -> DataFrame:
        """Возвращает обработанный DataFrame."""
        self.process_template()
        return self.df
