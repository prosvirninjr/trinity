"""Pydantic-схемы шаблонов для наружной рекламы."""

from pydantic import BaseModel, BeforeValidator, Field
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
        Field(title='Индекс'),
        # Порядок выполнения BeforeValidator-ов снизу вверх.
        BeforeValidator(validators.is_integer),  # Значение должно быть целым числом.
        BeforeValidator(validators.is_number),  # Значение должно быть числом.
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    advertiser: Annotated[
        str,
        Field(title='Рекламодатель'),
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    campaign: Annotated[
        str,
        Field(title='Кампания'),
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    city: Annotated[
        str,
        Field(title='Город'),
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    line: Annotated[
        str,
        Field(title='Линия'),
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    station: Annotated[
        str,
        Field(title='Станция'),
    ]
    location: Annotated[
        str,
        Field(title='Локация'),
    ]
    traffic: Annotated[
        int,
        Field(title='Пассажиропоток'),
    ]
    format_: Annotated[
        str,
        Field(title='Формат поверхности'),
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    size: Annotated[
        str,
        Field(title='Размер поверхности'),
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    cars_count: Annotated[
        int,
        Field(title='Количество вагонов'),
    ]
    constructions_count: Annotated[
        int,
        Field(title='Количество поверхностей'),
    ]

    # Период размещения.
    month: Annotated[
        str,
        Field(title='Месяц'),
        BeforeValidator(validators.is_number),  # Значение должно быть числом.
    ]
    date_from: Annotated[
        str,
        Field(title='Дата начала'),
        BeforeValidator(validators.is_date),  # Значение не должно быть пустым.
    ]
    date_to: Annotated[
        str,
        Field(title='Дата окончания'),
        BeforeValidator(validators.is_date),  # Значение не должно быть пустым.
    ]

    # Digital параметры.
    spot_duration: Annotated[
        float,
        Field(title='Длительность ролика'),
    ]
    spots_per_block: Annotated[
        float,
        Field(title='Выходов в блоке'),
    ]
    block_duration: Annotated[
        float,
        Field(title='Длительность блока'),
    ]
    spots_per_day: Annotated[
        float,
        Field(title='Выходов в сутки'),
    ]
    hours_per_day: Annotated[
        float,
        Field(title='Время работы поверхности'),
    ]

    # ID конструкций.
    gid_id: Annotated[
        str,
        Field(title='GID / ID поверхности'),
    ]
    client_id: Annotated[
        str,
        Field(title='ID поверхности (клиент)'),
    ]

    # Размещение.
    placement_price: Annotated[
        float,
        Field(title='Размещение PRICE'),
    ]
    placement_discount: Annotated[
        float,
        Field(title='Размещение DISCOUNT'),
    ]
    placement_price_net: Annotated[
        float,
        Field(title='Размещение NET'),
        BeforeValidator(validators.is_number),  # Значение должно быть числом.
    ]
    placement_vat: Annotated[
        float,
        Field(title='Размещение VAT'),
    ]
    placement_final_price: Annotated[
        float,
        Field(title='Размещение NET + VAT'),
        BeforeValidator(validators.is_number),  # Значение должно быть числом.
    ]

    # Основной монтаж.
    installation_price: Annotated[
        float,
        Field(title='Монтаж NET'),
    ]
    installation_vat: Annotated[
        float,
        Field(title='Монтаж VAT'),
    ]
    installation_final_price: Annotated[
        float,
        Field(title='Монтаж NET + VAT'),
    ]

    # Дополнительный монтаж.
    extra_installation_price: Annotated[
        float,
        Field(title='Доп. монтаж NET'),
    ]
    extra_installation_vat: Annotated[
        float,
        Field(title='Доп. монтаж VAT'),
    ]
    extra_installation_final_price: Annotated[
        float,
        Field(title='Доп. монтаж NET + VAT'),
    ]

    # Печать.
    print_price: Annotated[
        float,
        Field(title='Печать NET'),
    ]
    print_vat: Annotated[
        float,
        Field(title='Печать VAT'),
    ]
    print_final_price: Annotated[
        float,
        Field(title='Печать NET + VAT'),
    ]

    # Итого.
    final_price: Annotated[
        float,
        Field(title='Итого NET'),
    ]
    final_price_vat: Annotated[
        float,
        Field(title='Итого NET + VAT'),
    ]


class Transit(BaseModel):
    """Шаблон транспорта."""

    pass
