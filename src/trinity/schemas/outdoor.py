"""Pydantic-схемы шаблонов для наружной рекламы."""

from datetime import datetime

import polars as pl
from pydantic import AfterValidator, BaseModel, BeforeValidator, Field, model_validator
from typing_extensions import Annotated

from trinity.schemas import validators


class Outdoor(BaseModel):
    """Шаблон стандартной закупки."""

    pass


class Ots(BaseModel):
    """Шаблон OTS."""

    pass


class Indoor(BaseModel):
    """Шаблон индор."""

    pass


class Metro(BaseModel):
    """Шаблон метро."""

    index: Annotated[
        int,
        Field(title='Индекс', pl_dtype=pl.Int64),
        # Порядок выполнения BeforeValidator-ов снизу вверх, AfterValidator-ов сверху вниз.
        BeforeValidator(validators.is_integer),  # Значение должно быть целым числом.
        BeforeValidator(validators.is_number),  # Значение должно быть числом.
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    advertiser: Annotated[
        str,
        Field(title='Рекламодатель', pl_dtype=pl.String),
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    campaign: Annotated[
        str,
        Field(title='Кампания', pl_dtype=pl.String),
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    city: Annotated[
        str,
        Field(title='Город', pl_dtype=pl.String),
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    line: Annotated[
        str,
        Field(title='Линия', pl_dtype=pl.String),
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    station: Annotated[
        str | None,
        Field(title='Станция', pl_dtype=pl.String),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    location: Annotated[
        str | None,
        Field(title='Локация', pl_dtype=pl.String),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    traffic: Annotated[
        int,
        Field(title='Пассажиропоток', pl_dtype=pl.Int64),
        BeforeValidator(validators.set_value),  # Значение может быть пустым. Заменяем пустое значение на None.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
        AfterValidator(validators.is_integer),  # Значение должно быть целым числом.
    ]
    format_: Annotated[
        str,
        Field(title='Формат поверхности', pl_dtype=pl.String),
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    size: Annotated[
        str,
        Field(title='Размер поверхности', pl_dtype=pl.String),
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    cars_count: Annotated[
        int,
        Field(title='Количество вагонов', pl_dtype=pl.Int64),
        BeforeValidator(validators.set_value),  # Значение может быть пустым. Заменяем пустое значение на None.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
        AfterValidator(validators.is_integer),  # Значение должно быть целым числом.
    ]
    constructions_count: Annotated[
        int,
        Field(title='Количество поверхностей', pl_dtype=pl.Int64),
        BeforeValidator(validators.set_value),  # Значение может быть пустым. Заменяем пустое значение на None.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
        AfterValidator(validators.is_integer),  # Значение должно быть целым числом.
    ]

    # Период размещения.
    month: Annotated[
        int,
        Field(title='Месяц', pl_dtype=pl.Int64),
        BeforeValidator(validators.is_number),  # Значение должно быть числом.
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
        AfterValidator(validators.valid_month),  # Проверка месяца.
    ]
    date_from: Annotated[
        datetime,
        Field(title='Дата начала', pl_dtype=pl.Datetime),
        BeforeValidator(validators.is_date),  # Значение должно быть датой.
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    date_to: Annotated[
        datetime,
        Field(title='Дата окончания', pl_dtype=pl.Datetime),
        BeforeValidator(validators.is_date),  # Значение должно быть датой.
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]

    # Digital параметры.
    spot_duration: Annotated[
        float,
        Field(title='Длительность ролика', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]
    spots_per_block: Annotated[
        float,
        Field(title='Выходов в блоке', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]
    block_duration: Annotated[
        float,
        Field(title='Длительность блока', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]
    spots_per_day: Annotated[
        float,
        Field(title='Выходов в сутки', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]
    hours_per_day: Annotated[
        float,
        Field(title='Время работы поверхности', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
        AfterValidator(validators.valid_hours),  # Значение должно быть корректным количеством часов.
    ]

    # ID конструкций.
    gid_id: Annotated[
        str | None,
        Field(title='GID / ID поверхности', pl_dtype=pl.String),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    client_id: Annotated[
        str | None,
        Field(title='ID поверхности (клиент)', pl_dtype=pl.String),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]

    # Размещение.
    placement_price: Annotated[
        float,
        Field(title='Размещение PRICE', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]
    placement_discount: Annotated[
        float,
        Field(title='Размещение DISCOUNT', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_percentage),  # Значение должно быть процентом.
    ]
    placement_price_net: Annotated[
        float,
        Field(title='Размещение NET', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]
    placement_vat: Annotated[
        float,
        Field(title='Размещение VAT', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_percentage),  # Значение должно быть процентом.
    ]
    placement_final_price: Annotated[
        float,
        Field(title='Размещение NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]

    # Основной монтаж.
    installation_price: Annotated[
        float,
        Field(title='Монтаж NET', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]
    installation_vat: Annotated[
        float,
        Field(title='Монтаж VAT', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_percentage),  # Значение должно быть процентом.
    ]
    installation_final_price: Annotated[
        float,
        Field(title='Монтаж NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]

    # Дополнительный монтаж.
    extra_installation_price: Annotated[
        float,
        Field(title='Доп. монтаж NET', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]
    extra_installation_vat: Annotated[
        float,
        Field(title='Доп. монтаж VAT', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_percentage),  # Значение должно быть процентом.
    ]
    extra_installation_final_price: Annotated[
        float,
        Field(title='Доп. монтаж NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]

    # Печать.
    print_price: Annotated[
        float,
        Field(title='Печать NET', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]
    print_vat: Annotated[
        float,
        Field(title='Печать VAT', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_percentage),  # Значение должно быть процентом.
    ]
    print_final_price: Annotated[
        float,
        Field(title='Печать NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]

    # Итого.
    final_price: Annotated[
        float,
        Field(title='Итого NET', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]
    final_price_vat: Annotated[
        float,
        Field(title='Итого NET + VAT', pl_dtype=pl.Float64),
        BeforeValidator(validators.set_value),  # # Значение может быть пустым. Заменяем пустое значение на 0.
        AfterValidator(validators.is_not_negative),  # Значение не должно быть отрицательным.
    ]

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

        if self.spot_duration * self.spots_per_block > self.block_duration:
            raise ValueError('Общий хронометраж роликов не может превышать длительность блока.')

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
