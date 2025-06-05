"""Pydantic-схемы шаблонов для наружной рекламы."""

import math
from datetime import datetime
from functools import partial

import polars as pl
from pydantic import AfterValidator, BaseModel, BeforeValidator, Field, model_validator
from typing_extensions import Annotated

from trinity.schemas import validators


class Outdoor(BaseModel):
    """Шаблон стандартной закупки."""

    pass


class OTS(BaseModel):
    """Шаблон OTS."""

    pass


class Indoor(BaseModel):
    """Шаблон индор."""

    index: Annotated[
        int,
        Field(title='Индекс', pl_dtype=pl.Int64),
        BeforeValidator(partial(validators.is_integer, column='Индекс')),
        BeforeValidator(partial(validators.is_number, column='Индекс')),
        BeforeValidator(partial(validators.is_empty, column='Индекс')),
    ]
    advertiser: Annotated[
        str,
        Field(title='Рекламодатель', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Рекламодатель')),
    ]
    campaign: Annotated[
        str,
        Field(title='Кампания', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Кампания')),
    ]
    subject: Annotated[
        str,
        Field(title='Субъект', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Субъект')),
    ]
    city: Annotated[
        str,
        Field(title='Город', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Город')),
    ]
    location_type: Annotated[
        str,
        Field(title='Тип локации', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Тип локации')),
    ]
    location_name: Annotated[
        str,
        Field(title='Название локации', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Название локации')),
    ]
    format_: Annotated[
        str,
        Field(title='Формат поверхности', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Формат поверхности')),
    ]
    size: Annotated[
        str,
        Field(title='Размер поверхности', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Размер поверхности')),
    ]
    constructions_count: Annotated[
        int,
        Field(title='Количество поверхностей', pl_dtype=pl.Int64),
        BeforeValidator(partial(validators.is_integer, column='Количество поверхностей')),
        BeforeValidator(partial(validators.set_value, column='Количество поверхностей')),
        AfterValidator(partial(validators.is_not_negative, column='Количество поверхностей')),
    ]
    placement_per_unit: Annotated[
        float,
        Field(title='Стоимость за единицу размещения', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Стоимость за единицу размещения')),
        AfterValidator(partial(validators.is_not_negative, column='Стоимость за единицу размещения')),
    ]
    month: Annotated[
        int,
        Field(title='Месяц', pl_dtype=pl.Int64),
        BeforeValidator(partial(validators.is_number, column='Месяц')),
        BeforeValidator(partial(validators.is_empty, column='Месяц')),
        AfterValidator(partial(validators.valid_month, column='Месяц')),
    ]
    date_from: Annotated[
        datetime,
        Field(title='Начало аренды', pl_dtype=pl.Datetime),
        BeforeValidator(partial(validators.is_date, column='Начало аренды')),
        BeforeValidator(partial(validators.is_empty, column='Начало аренды')),
    ]
    date_to: Annotated[
        datetime,
        Field(title='Окончание аренды', pl_dtype=pl.Datetime),
        BeforeValidator(partial(validators.is_date, column='Окончание аренды')),
        BeforeValidator(partial(validators.is_empty, column='Окончание аренды')),
    ]
    spot_duration: Annotated[
        float,
        Field(title='Длительность ролика', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Длительность ролика')),
        AfterValidator(partial(validators.is_not_negative, column='Длительность ролика')),
    ]
    spots_per_block: Annotated[
        float,
        Field(title='Количество выходов в блоке', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Количество выходов в блоке')),
        AfterValidator(partial(validators.is_not_negative, column='Количество выходов в блоке')),
    ]
    block_duration: Annotated[
        float,
        Field(title='Длительность блока', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Длительность блока')),
        AfterValidator(partial(validators.is_not_negative, column='Длительность блока')),
    ]
    spots_per_day: Annotated[
        float,
        Field(title='Выходов в сутки', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Выходов в сутки')),
        AfterValidator(partial(validators.is_not_negative, column='Выходов в сутки')),
    ]
    hours_per_day: Annotated[
        float,
        Field(title='Время работы конструкции', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Время работы конструкции')),
        AfterValidator(partial(validators.is_not_negative, column='Время работы конструкции')),
        AfterValidator(partial(validators.valid_hours, column='Время работы конструкции')),
    ]
    gid_id: Annotated[
        str | None,
        Field(title='GID | ID конструкции', pl_dtype=pl.String),
        AfterValidator(validators.set_empty),
    ]
    client_id: Annotated[
        str | None,
        Field(title='№ конструкции в программе клиента', pl_dtype=pl.String),
        AfterValidator(validators.set_empty),
    ]
    material: Annotated[
        str,
        Field(title='Материал', pl_dtype=pl.String),
        AfterValidator(partial(validators.set_empty)),
    ]
    daily_grp: Annotated[
        float,
        Field(title='Daily GRP', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Daily GRP')),
        AfterValidator(partial(validators.is_not_negative, column='Daily GRP')),
    ]
    latitude: Annotated[
        float,
        Field(title='Широта', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Широта')),
        AfterValidator(partial(validators.is_not_negative, column='Широта')),
    ]
    longitude: Annotated[
        float,
        Field(title='Долгота', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Долгота')),
        AfterValidator(partial(validators.is_not_negative, column='Долгота')),
    ]
    operator: Annotated[
        str,
        Field(title='Оператор', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Оператор')),
    ]
    comment: Annotated[
        str | None,
        Field(title='Комментарий', pl_dtype=pl.String),
        AfterValidator(validators.set_empty),
    ]
    placement_price: Annotated[
        float,
        Field(title='Размещение PRICE', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Размещение PRICE')),
        AfterValidator(partial(validators.is_not_negative, column='Размещение PRICE')),
    ]
    placement_discount: Annotated[
        float,
        Field(title='Размещение DISCOUNT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Размещение DISCOUNT')),
        AfterValidator(partial(validators.is_percentage, column='Размещение DISCOUNT')),
    ]
    placement_net: Annotated[
        float,
        Field(title='Размещение NET', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Размещение NET')),
        AfterValidator(partial(validators.is_not_negative, column='Размещение NET')),
    ]
    placement_vat: Annotated[
        float,
        Field(title='Размещение VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Размещение VAT')),
        AfterValidator(partial(validators.is_percentage, column='Размещение VAT')),
    ]
    placement_final: Annotated[
        float,
        Field(title='Размещение NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Размещение NET + VAT')),
        AfterValidator(partial(validators.is_not_negative, column='Размещение NET + VAT')),
    ]
    production_net: Annotated[
        float,
        Field(title='Производство NET', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Производство NET')),
        AfterValidator(partial(validators.is_not_negative, column='Производство NET')),
    ]
    production_count: Annotated[
        int,
        Field(title='Производство COUNT', pl_dtype=pl.Int64),
        BeforeValidator(partial(validators.is_integer, column='Производство COUNT')),
        BeforeValidator(partial(validators.set_value, column='Производство COUNT')),
        AfterValidator(partial(validators.is_not_negative, column='Производство COUNT')),
    ]
    production_total: Annotated[
        float,
        Field(title='Производство NET TOTAL', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Производство NET TOTAL')),
        AfterValidator(partial(validators.is_not_negative, column='Производство NET TOTAL')),
    ]
    production_vat: Annotated[
        float,
        Field(title='Производство VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Производство VAT')),
        AfterValidator(partial(validators.is_percentage, column='Производство VAT')),
    ]
    production_final: Annotated[
        float,
        Field(title='Производство NET TOTAL + VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Производство NET TOTAL + VAT')),
        AfterValidator(partial(validators.is_not_negative, column='Производство NET TOTAL + VAT')),
    ]
    installation_net: Annotated[
        float,
        Field(title='Монтаж NET', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Монтаж NET')),
        AfterValidator(partial(validators.is_not_negative, column='Монтаж NET')),
    ]
    installation_vat: Annotated[
        float,
        Field(title='Монтаж VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Монтаж VAT')),
        AfterValidator(partial(validators.is_percentage, column='Монтаж VAT')),
    ]
    installation_final: Annotated[
        float,
        Field(title='Монтаж NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Монтаж NET + VAT')),
        AfterValidator(partial(validators.is_not_negative, column='Монтаж NET + VAT')),
    ]
    e_installation_net: Annotated[
        float,
        Field(title='Доп. монтаж NET', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Доп. монтаж NET')),
        AfterValidator(partial(validators.is_not_negative, column='Доп. монтаж NET')),
    ]
    e_installation_count: Annotated[
        int,
        Field(title='Доп. монтаж COUNT', pl_dtype=pl.Int64),
        BeforeValidator(partial(validators.is_integer, column='Доп. монтаж COUNT')),
        BeforeValidator(partial(validators.set_value, column='Доп. монтаж COUNT')),
        AfterValidator(partial(validators.is_not_negative, column='Доп. монтаж COUNT')),
    ]
    e_installation_total: Annotated[
        float,
        Field(title='Доп. монтаж NET TOTAL', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Доп. монтаж NET TOTAL')),
        AfterValidator(partial(validators.is_not_negative, column='Доп. монтаж NET TOTAL')),
    ]
    e_installation_vat: Annotated[
        float,
        Field(title='Доп. монтаж VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Доп. монтаж VAT')),
        AfterValidator(partial(validators.is_percentage, column='Доп. монтаж VAT')),
    ]
    e_installation_final: Annotated[
        float,
        Field(title='Доп. монтаж NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Доп. монтаж NET + VAT')),
        AfterValidator(partial(validators.is_not_negative, column='Доп. монтаж NET + VAT')),
    ]
    delivery_net: Annotated[
        float,
        Field(title='Доставка NET', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Доставка NET')),
        AfterValidator(partial(validators.is_not_negative, column='Доставка NET')),
    ]
    delivery_vat: Annotated[
        float,
        Field(title='Доставка VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Доставка VAT')),
        AfterValidator(partial(validators.is_percentage, column='Доставка VAT')),
    ]
    delivery_final: Annotated[
        float,
        Field(title='Доставка NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Доставка NET + VAT')),
        AfterValidator(partial(validators.is_not_negative, column='Доставка NET + VAT')),
    ]
    full_net: Annotated[
        float,
        Field(title='Итого NET', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Итого NET')),
        AfterValidator(partial(validators.is_not_negative, column='Итого NET')),
    ]
    full_vat: Annotated[
        float,
        Field(title='Итого VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Итого VAT')),
        AfterValidator(partial(validators.is_not_negative, column='Итого VAT')),
    ]

    @model_validator(mode='after')
    def valid_month(self) -> 'Indoor':
        if self.date_from.month != self.month or self.date_to.month != self.month:
            raise ValueError('Месяц аренды не соответствует дате.')
        return self

    @model_validator(mode='after')
    def valid_period(self) -> 'Indoor':
        if self.date_from > self.date_to:
            raise ValueError('Дата начала не может быть позже окончания.')
        return self

    @classmethod
    def get_polars_schema(cls) -> dict[str, pl.DataType]:
        schema: dict[str, pl.DataType] = {}
        for field, info in Indoor.model_fields.items():
            schema[field] = info.json_schema_extra.get('pl_dtype')
        return schema


class Metro(BaseModel):
    """Шаблон метро."""

    index: Annotated[
        int,
        Field(title='Индекс', pl_dtype=pl.Int64),
        # Порядок выполнения BeforeValidator-ов снизу вверх, AfterValidator-ов сверху вниз.
        BeforeValidator(partial(validators.is_integer, column='Индекс')),
        BeforeValidator(partial(validators.is_number, column='Индекс')),
        BeforeValidator(partial(validators.is_empty, column='Индекс')),
    ]
    advertiser: Annotated[
        str,
        Field(title='Рекламодатель', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Рекламодатель')),
    ]
    campaign: Annotated[
        str,
        Field(title='Кампания', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Кампания')),
    ]
    city: Annotated[
        str,
        Field(title='Город', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Город')),
        AfterValidator(partial(validators.valid_metro, column='Город')),
    ]
    line: Annotated[
        str,
        Field(title='Линия', pl_dtype=pl.String),
        AfterValidator(validators.set_empty),  # Может быть пустым в случае закупки рекламы на всех станциях метро.
    ]
    station: Annotated[
        str | None,
        Field(title='Станция', pl_dtype=pl.String),
        AfterValidator(validators.set_empty),  # Может быть пустым в случае закупки рекламы в вагоне метро.
    ]
    location: Annotated[
        str | None,
        Field(title='Локация', pl_dtype=pl.String),
        AfterValidator(partial(validators.is_empty, column='Локация')),
    ]
    traffic: Annotated[
        float,
        Field(title='Пассажиропоток', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Пассажиропоток')),
        AfterValidator(partial(validators.is_not_negative, column='Пассажиропоток')),
    ]
    format_: Annotated[
        str,
        Field(title='Формат поверхности', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Формат поверхности')),
    ]
    size: Annotated[
        str,
        Field(title='Размер поверхности', pl_dtype=pl.String),
        BeforeValidator(partial(validators.is_empty, column='Размер поверхности')),
    ]
    cars_count: Annotated[
        int,
        Field(title='Количество вагонов', pl_dtype=pl.Int64),
        BeforeValidator(partial(validators.is_integer, column='Количество вагонов')),
        BeforeValidator(partial(validators.set_value, column='Количество вагонов')),
        AfterValidator(partial(validators.is_not_negative, column='Количество вагонов')),
    ]
    constructions_count: Annotated[
        int,
        Field(title='Количество поверхностей', pl_dtype=pl.Int64),
        BeforeValidator(partial(validators.is_integer, column='Количество поверхностей')),
        BeforeValidator(partial(validators.set_value, column='Количество поверхностей')),
        AfterValidator(partial(validators.is_not_negative, column='Количество поверхностей')),
    ]

    # Период размещения.
    month: Annotated[
        int,
        Field(title='Месяц', pl_dtype=pl.Int64),
        BeforeValidator(partial(validators.is_number, column='Месяц')),
        BeforeValidator(partial(validators.is_empty, column='Месяц')),
        AfterValidator(partial(validators.valid_month, column='Месяц')),
    ]
    date_from: Annotated[
        datetime,
        Field(title='Дата начала', pl_dtype=pl.Datetime),
        BeforeValidator(partial(validators.is_date, column='Дата начала')),
        BeforeValidator(partial(validators.is_empty, column='Дата начала')),
    ]
    date_to: Annotated[
        datetime,
        Field(title='Дата окончания', pl_dtype=pl.Datetime),
        BeforeValidator(partial(validators.is_date, column='Дата окончания')),
        BeforeValidator(partial(validators.is_empty, column='Дата окончания')),
    ]

    # Digital параметры.
    spot_duration: Annotated[
        float,
        Field(title='Длительность ролика', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Длительность ролика')),
        AfterValidator(partial(validators.is_not_negative, column='Длительность ролика')),
    ]
    spots_per_block: Annotated[
        float,
        Field(title='Выходов в блоке', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Выходов в блоке')),
        AfterValidator(partial(validators.is_not_negative, column='Выходов в блоке')),
    ]
    block_duration: Annotated[
        float,
        Field(title='Длительность блока', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Длительность блока')),
        AfterValidator(partial(validators.is_not_negative, column='Длительность блока')),
    ]
    spots_per_day: Annotated[
        float,
        Field(title='Выходов в сутки', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Выходов в сутки')),
        AfterValidator(partial(validators.is_not_negative, column='Выходов в сутки')),
    ]
    hours_per_day: Annotated[
        float,
        Field(title='Время работы поверхности', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Время работы поверхности')),
        AfterValidator(partial(validators.is_not_negative, column='Время работы поверхности')),
        AfterValidator(partial(validators.valid_hours, column='Время работы поверхности')),
    ]

    # ID конструкций.
    gid_id: Annotated[
        str | None,
        Field(title='GID / ID поверхности', pl_dtype=pl.String),
        AfterValidator(validators.set_empty),
    ]
    client_id: Annotated[
        str | None,
        Field(title='ID поверхности (клиент)', pl_dtype=pl.String),
        AfterValidator(validators.set_empty),
    ]

    # Размещение.
    placement_price: Annotated[
        float,
        Field(title='Размещение PRICE', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Размещение PRICE')),
        AfterValidator(partial(validators.is_not_negative, column='Размещение PRICE')),
    ]
    placement_discount: Annotated[
        float,
        Field(title='Размещение DISCOUNT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Размещение DISCOUNT')),
        AfterValidator(partial(validators.is_percentage, column='Размещение DISCOUNT')),
    ]
    placement_net: Annotated[
        float,
        Field(title='Размещение NET', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Размещение NET')),
        AfterValidator(partial(validators.is_not_negative, column='Размещение NET')),
    ]
    placement_vat: Annotated[
        float,
        Field(title='Размещение VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Размещение VAT')),
        AfterValidator(partial(validators.is_percentage, column='Размещение VAT')),
    ]
    placement_final: Annotated[
        float,
        Field(title='Размещение NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Размещение NET + VAT')),
        AfterValidator(partial(validators.is_not_negative, column='Размещение NET + VAT')),
    ]

    # Основной монтаж.
    installation_total: Annotated[
        float,
        Field(title='Монтаж NET', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Монтаж NET')),
        AfterValidator(partial(validators.is_not_negative, column='Монтаж NET')),
    ]
    installation_vat: Annotated[
        float,
        Field(title='Монтаж VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Монтаж VAT')),
        AfterValidator(partial(validators.is_percentage, column='Монтаж VAT')),
    ]
    installation_final: Annotated[
        float,
        Field(title='Монтаж NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Монтаж NET + VAT')),
        AfterValidator(partial(validators.is_not_negative, column='Монтаж NET + VAT')),
    ]

    # Дополнительный монтаж.
    e_installation_total: Annotated[
        float,
        Field(title='Доп. монтаж NET', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Доп. монтаж NET')),
        AfterValidator(partial(validators.is_not_negative, column='Доп. монтаж NET')),
    ]
    e_installation_vat: Annotated[
        float,
        Field(title='Доп. монтаж VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Доп. монтаж VAT')),
        AfterValidator(partial(validators.is_percentage, column='Доп. монтаж VAT')),
    ]
    e_installation_final: Annotated[
        float,
        Field(title='Доп. монтаж NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Доп. монтаж NET + VAT')),
        AfterValidator(partial(validators.is_not_negative, column='Доп. монтаж NET + VAT')),
    ]

    # Печать.
    print_total: Annotated[
        float,
        Field(title='Печать NET', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Печать NET')),
        AfterValidator(partial(validators.is_not_negative, column='Печать NET')),
    ]
    print_vat: Annotated[
        float,
        Field(title='Печать VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Печать VAT')),
        AfterValidator(partial(validators.is_percentage, column='Печать VAT')),
    ]
    print_final: Annotated[
        float,
        Field(title='Печать NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Печать NET + VAT')),
        AfterValidator(partial(validators.is_not_negative, column='Печать NET + VAT')),
    ]

    # Итого.
    full_net: Annotated[
        float,
        Field(title='Итого NET', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Итого NET')),
        AfterValidator(partial(validators.is_not_negative, column='Итого NET')),
    ]
    full_vat: Annotated[
        float,
        Field(title='Итого NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(partial(validators.set_value, column='Итого NET + VAT')),
        AfterValidator(partial(validators.is_not_negative, column='Итого NET + VAT')),
    ]

    @model_validator(mode='after')
    def valid_line(self) -> 'Metro':
        """Проверка корректности линии метро."""
        if self.station is not None:
            if self.line is None:
                raise ValueError('Линия метро должна быть указана, если указана станция.')

        return self

    @model_validator(mode='after')
    def valid_month(self) -> 'Metro':
        """Проверка корректности месяца размещения."""
        if self.date_from.month != self.month:
            raise ValueError('Месяц размещения не соответствует месяцу даты начала размещения.')
        if self.date_to.month != self.month:
            raise ValueError('Месяц размещения не соответствует месяцу даты окончания размещения.')

        return self

    @model_validator(mode='after')
    def valid_period(self) -> 'Metro':
        """Проверка корректности периода размещения."""
        if self.date_from > self.date_to:
            raise ValueError('Дата начала размещения не может быть позже даты окончания размещения.')

        return self

    @model_validator(mode='after')
    def valid_digital_params(self) -> 'Metro':
        """Проверка корректности цифровых параметров."""

        params = [
            self.spot_duration,
            self.spots_per_block,
            self.block_duration,
            self.spots_per_day,
            self.hours_per_day,
        ]

        if sum(params) != 0 and any(param == 0 for param in params):
            raise ValueError('Необходимо указать все digital параметры.')

        if self.spot_duration > self.block_duration:
            raise ValueError('Длительность ролика не может быть больше длительности блока.')

        if (self.spot_duration * self.spots_per_block) > self.block_duration:
            raise ValueError('Общий хронометраж роликов не может превышать длительность блока.')

        return self

    @model_validator(mode='after')
    def valid_placement(self) -> 'Metro':
        """Проверка размещения."""
        if not math.isclose(self.placement_price * (1 - self.placement_discount), self.placement_net, abs_tol=1.0):
            raise ValueError('Размещение PRICE не соответствует Размещению NET с учетом скидки.')

        if not math.isclose(self.placement_net * (1 + self.placement_vat), self.placement_final, abs_tol=1.0):
            raise ValueError('Размещение NET не соответствует Размещению NET с НДС.')

        return self

    @model_validator(mode='after')
    def valid_installation(self) -> 'Metro':
        """Проверка монтажа."""
        if not math.isclose(
            self.installation_total * (1 + self.installation_vat), self.installation_final, abs_tol=1.0
        ):
            raise ValueError('Монтаж NET не соответствует Монтажу NET с НДС.')

        return self

    @model_validator(mode='after')
    def valid_extra_installation(self) -> 'Metro':
        """Проверка дополнительного монтажа."""
        if not math.isclose(
            self.e_installation_total * (1 + self.e_installation_vat),
            self.e_installation_final,
            abs_tol=1.0,
        ):
            raise ValueError('Дополнительный монтаж NET не соответствует Дополнительному монтажу NET с НДС.')

        return self

    @model_validator(mode='after')
    def valid_print(self) -> 'Metro':
        """Проверка печати."""
        if not math.isclose(self.print_total * (1 + self.print_vat), self.print_final, abs_tol=1.0):
            raise ValueError('Печать NET не соответствует Печати NET с НДС.')

        return self

    @model_validator(mode='after')
    def valid_final_prices(self) -> 'Metro':
        """Проверка итоговых цен."""
        if not math.isclose(
            self.placement_net + self.installation_total + self.e_installation_total + self.print_total,
            self.full_net,
            abs_tol=1.0,
        ):
            raise ValueError('Итоговая цена NET не соответствует сумме всех компонентов.')

        if not math.isclose(
            self.placement_final + self.installation_final + self.e_installation_final + self.print_final,
            self.full_vat,
            abs_tol=1.0,
        ):
            raise ValueError('Итоговая цена с НДС не соответствует сумме всех компонентов.')

        return self

    @classmethod
    def get_polars_schema(self) -> dict:
        """Возвращает схему polars DataFrame."""
        schema: dict[str, pl.DataType] = {}

        for field, field_info in Metro.model_fields.items():
            schema[field] = field_info.json_schema_extra.get('pl_dtype')

        return schema


class Transit(BaseModel):
    """Шаблон транспорта."""

    pass
