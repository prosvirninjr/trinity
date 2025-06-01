"""Pydantic-схемы шаблонов для наружной рекламы."""

from pydantic import BaseModel, Field
from typing_extensions import Annotated


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

    index: Annotated[int, Field()]
    advertiser: Annotated[str, Field()]
    campaign: Annotated[str, Field()]
    city: Annotated[str, Field()]
    line: Annotated[str, Field()]
    station: Annotated[str, Field()]
    location: Annotated[str, Field()]
    traffic: Annotated[int, Field()]
    type_: Annotated[str, Field()]
    size: Annotated[str, Field()]
    cars_count: Annotated[int, Field()]
    constructions_count: Annotated[int, Field()]

    # Период размещения.
    month: Annotated[str, Field()]
    date_from: Annotated[str, Field()]
    date_to: Annotated[str, Field()]

    # Digital параметры.
    spot_duration: Annotated[float, Field(gt=0)]
    spots_per_block: Annotated[float, Field(gt=0)]
    block_duration: Annotated[float, Field(gt=0)]
    spots_per_day: Annotated[float, Field(gt=0)]
    hours_per_day: Annotated[float, Field(gt=0)]

    # ID конструкций.
    gid_id: Annotated[str, Field()]
    client_id: Annotated[str, Field()]

    # Размещение.
    placement_price: Annotated[float, Field()]
    placement_discount: Annotated[float, Field()]
    placement_price_net: Annotated[float, Field()]
    placement_vat: Annotated[float, Field()]
    placement_final_price: Annotated[float, Field()]

    # Основной монтаж.
    installation_price: Annotated[float, Field()]
    installation_vat: Annotated[float, Field()]
    installation_final_price: Annotated[float, Field()]

    # Дополнительный монтаж.
    extra_installation_price: Annotated[float, Field()]
    extra_installation_vat: Annotated[float, Field()]
    extra_installation_final_price: Annotated[float, Field()]

    # Печать.
    print_price: Annotated[float, Field()]
    print_vat: Annotated[float, Field()]
    print_final_price: Annotated[float, Field()]

    # Итого.
    final_price: Annotated[float, Field()]
    final_price_net: Annotated[float, Field()]


class Transit(BaseModel):
    """Шаблон транспорта."""

    pass
