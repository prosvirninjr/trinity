from typing import Any

from trinity.utils.tools import Parser, TextTools


# Базовые валидаторы.
def is_empty(value: Any) -> Any:
    """
    Before Pydantic валидатор. Проверяет, является ли входное значение пустым.
    Поднимает исключение, если значение является пустым.
    """
    if isinstance(value, str):
        if not TextTools.is_empty(value):
            return value

    if isinstance(value, (int, float)):
        return value

    raise ValueError('Значение не может быть пустым.')


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

    raise ValueError('Значение не является числом.')


def is_date(value: Any) -> float:
    """
    Before Pydantic валидатор. Проверяет, является ли входное значение датой.
    Поднимает исключение, если значение не является датой.
    """
    if isinstance(value, str):
        result = Parser.parse_date(value)

        if result:
            return result

    raise ValueError('Значение не является датой.')


def is_integer(value: int | float) -> int:
    """
    After Pydantic валидатор. Проверяет, является ли входное значение целым числом.
    Поднимает исключение, если значение не является целым числом.
    """
    result = isinstance(value, int) or (isinstance(value, float) and value.is_integer())

    if result:
        return int(value)

    raise ValueError('Значение не является целым числом.')


def is_percentage(value: int | float) -> int | float:
    """
    After Pydantic валидатор. Проверяет, является ли входное значение процентом.
    Поднимает исключение, если значение не является процентом.
    """
    if isinstance(value, (int, float)):
        if 0 <= value <= 100:
            return value

    raise ValueError('Значение не является процентом.')


def is_not_negative(value: int | float) -> int | float:
    """
    After Pydantic валидатор. Проверяет, является ли входное значение неотрицательным числом.
    Поднимает исключение, если значение является отрицательным.
    """
    if isinstance(value, (int, float)):
        if value >= 0:
            return value

    raise ValueError('Значение должно быть неотрицательным числом.')


# Специальные валидаторы.
def set_empty(value: Any) -> Any:
    """
    After Pydantic валидатор. Если входное значение является пустым (пустая строка или None), возвращает None.
    """

    if isinstance(value, str):
        if TextTools.is_empty(value):
            return None

    if not value:
        return None

    return value


def set_value(value: str | int | float | None) -> int | float:
    """
    Before | After Pydantic валидатор. Если входное значение является пустым (пустая строка или None), возвращает 0,
    Иначе возвращает само значение.
    """
    if isinstance(value, str):
        if TextTools.is_empty(value):
            return 0
        else:
            value = Parser.parse_number(value)
            if value is None:
                raise ValueError('Значение должно быть числом.')

    if value is None:
        return 0

    if isinstance(value, (int, float)):
        return value

    raise ValueError('Значение должно быть числом.')


# Предметные валидаторы.
def is_month(value: int) -> int:
    """
    After Pydantic валидатор. Проверяет, является ли входное значение валидным месяцем.
    Поднимает исключение, если значение не является месяцем.
    """
    if 1 <= value <= 12:
        return value

    raise ValueError('Месяц должен быть в диапазоне от 1 до 12.')
