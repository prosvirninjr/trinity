from typing import Any

from trinity.utils.tools import Parser, TextTools


def is_empty(value: Any) -> Any:
    """Before Pydantic валидатор. Проверяет, является ли входное значение пустым."""
    if isinstance(value, str):
        if c_str := TextTools.is_empty(value):
            return c_str

    if isinstance(value, (int, float)):
        return value

    raise ValueError('Значение не может быть пустым.', value)


def is_number(value: Any) -> float:
    """Before Pydantic валидатор. Проверяет, является ли входное значение числом."""
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        result = Parser.parse_number(value)

        if result:
            return result

    raise ValueError('Значение не является числом.', value)


def is_integer(value: int | float) -> int:
    """After Pydantic валидатор. Проверяет, является ли входное значение целым числом."""
    result = isinstance(value, int) or (isinstance(value, float) and value.is_integer())

    if result:
        return int(value)

    raise ValueError('Значение не является целым числом.', value)


def is_percentage(value: int | float) -> float:
    """After Pydantic валидатор. Проверяет, является ли входное значение процентом."""
    if isinstance(value, (int, float)):
        if 0 <= value <= 100:
            return float(value)

    raise ValueError('Значение не является процентом.', value)
