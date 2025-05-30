"""Pydantic-схемы шаблонов для наружной рекламы."""

from pydantic import BaseModel


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

    pass


class Transit(BaseModel):
    """Шаблон транспорта."""

    pass
