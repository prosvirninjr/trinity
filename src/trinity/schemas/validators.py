from typing import Any

from trinity.utils.tools import Parser, TextTools


# Базовые валидаторы.
def is_empty(value: Any) -> Any:
    """
    Before Pydantic валидатор. Проверяет, является ли входное значение пустым.
    Поднимает исключение, если значение является пустым.
    """
    if isinstance(value, str):
        if c_str := TextTools.is_empty(value):
            return c_str

    if isinstance(value, (int, float)):
        return value

    raise ValueError('Значение не может быть пустым.', value)


def is_number(value: Any) -> float:
    """
    Before Pydantic валидатор. Проверяет, является ли входное значение числом.
    Поднимает исключение, если значение не является числом.
    """
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        result = Parser.parse_number(value)

        if result:
            return result

    raise ValueError('Значение не является числом.', value)


def is_date(value: Any) -> float:
    """
    Before Pydantic валидатор. Проверяет, является ли входное значение датой.
    Поднимает исключение, если значение не является датой.
    """
    if isinstance(value, str):
        result = Parser.parse_date(value)

        if result:
            return result

    raise ValueError('Значение не является датой.', value)


def is_integer(value: int | float) -> int:
    """
    After Pydantic валидатор. Проверяет, является ли входное значение целым числом.
    Поднимает исключение, если значение не является целым числом.
    """
    result = isinstance(value, int) or (isinstance(value, float) and value.is_integer())

    if result:
        return int(value)

    raise ValueError('Значение не является целым числом.', value)


def is_percentage(value: int | float) -> float:
    """
    After Pydantic валидатор. Проверяет, является ли входное значение процентом.
    Поднимает исключение, если значение не является процентом.
    """
    if isinstance(value, (int, float)):
        if 0 <= value <= 100:
            return float(value)

    raise ValueError('Значение не является процентом.', value)


# Специальные валидаторы.
def set_empty(value: Any) -> Any:
    """
    After Pydantic валидатор. Если входное значение является пустым (пустая строка или None), возвращает None.
    """

    if not value:
        return None

    if isinstance(value, str):
        if TextTools.is_empty(value):
            return None

    return value


# Предметные валидаторы.
def is_month(value: int) -> int:
    """
    After Pydantic валидатор. Проверяет, является ли входное значение валидным месяцем.
    Поднимает исключение, если значение не является месяцем.
    """
    if 1 <= value <= 12:
        return value

    raise ValueError('Месяц должен быть в диапазоне от 1 до 12.', value)
