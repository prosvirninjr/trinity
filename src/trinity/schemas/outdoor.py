"""Pydantic-схемы шаблонов для наружной рекламы."""

from pydantic import AfterValidator, BaseModel, BeforeValidator, Field
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
        # Порядок выполнения BeforeValidator-ов снизу вверх, AfterValidator-ов сверху вниз.
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
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    location: Annotated[
        str,
        Field(title='Локация'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    traffic: Annotated[
        int,
        Field(title='Пассажиропоток'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
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
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    constructions_count: Annotated[
        int,
        Field(title='Количество поверхностей'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]

    # Период размещения.
    month: Annotated[
        str,
        Field(title='Месяц'),
        BeforeValidator(validators.is_number),  # Значение должно быть числом.
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
        AfterValidator(validators.is_month),  # Проверка месяца.
    ]
    date_from: Annotated[
        str,
        Field(title='Дата начала'),
        BeforeValidator(validators.is_date),  # Значение должно быть датой.
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    date_to: Annotated[
        str,
        Field(title='Дата окончания'),
        BeforeValidator(validators.is_date),  # Значение должно быть датой.
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]

    # Digital параметры.
    spot_duration: Annotated[
        float,
        Field(title='Длительность ролика'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    spots_per_block: Annotated[
        float,
        Field(title='Выходов в блоке'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    block_duration: Annotated[
        float,
        Field(title='Длительность блока'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    spots_per_day: Annotated[
        float,
        Field(title='Выходов в сутки'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    hours_per_day: Annotated[
        float,
        Field(title='Время работы поверхности'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]

    # ID конструкций.
    gid_id: Annotated[
        str,
        Field(title='GID / ID поверхности'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    client_id: Annotated[
        str,
        Field(title='ID поверхности (клиент)'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]

    # Размещение.
    placement_price: Annotated[
        float,
        Field(title='Размещение PRICE'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    placement_discount: Annotated[
        float,
        Field(title='Размещение DISCOUNT'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    placement_price_net: Annotated[
        float,
        Field(title='Размещение NET'),
        BeforeValidator(validators.is_number),  # Значение должно быть числом.
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    placement_vat: Annotated[
        float,
        Field(title='Размещение VAT'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    placement_final_price: Annotated[
        float,
        Field(title='Размещение NET + VAT'),
        BeforeValidator(validators.is_number),  # Значение должно быть числом.
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]

    # Основной монтаж.
    installation_price: Annotated[
        float,
        Field(title='Монтаж NET'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    installation_vat: Annotated[
        float,
        Field(title='Монтаж VAT'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    installation_final_price: Annotated[
        float,
        Field(title='Монтаж NET + VAT'),
    ]

    # Дополнительный монтаж.
    extra_installation_price: Annotated[
        float,
        Field(title='Доп. монтаж NET'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    extra_installation_vat: Annotated[
        float,
        Field(title='Доп. монтаж VAT'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    extra_installation_final_price: Annotated[
        float,
        Field(title='Доп. монтаж NET + VAT'),
    ]

    # Печать.
    print_price: Annotated[
        float,
        Field(title='Печать NET'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    print_vat: Annotated[
        float,
        Field(title='Печать VAT'),
        AfterValidator(validators.set_empty),  # Значение может быть пустым. Заменяем пустое значение на None.
    ]
    print_final_price: Annotated[
        float,
        Field(title='Печать NET + VAT'),
    ]

    # Итого.
    final_price: Annotated[
        float,
        Field(title='Итого NET'),
        BeforeValidator(validators.is_number),  # Значение должно быть числом.
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]
    final_price_vat: Annotated[
        float,
        Field(title='Итого NET + VAT'),
        BeforeValidator(validators.is_number),  # Значение должно быть числом.
        BeforeValidator(validators.is_empty),  # Значение не должно быть пустым.
    ]


class Transit(BaseModel):
    """Шаблон транспорта."""

    pass
