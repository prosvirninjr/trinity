from datetime import datetime
from typing import Any

from trinity.services.logics import MParser
from trinity.utils.tools import Parser, TextTools


# Базовые валидаторы.
def is_empty(value: Any, column: str) -> Any:
    """
    Before Pydantic валидатор. Проверяет, является ли входное значение пустым.
    Поднимает исключение, если значение является пустым.
    """
    if isinstance(value, str):
        if not TextTools.is_empty(value):
            return value

    if isinstance(value, (int, float)):
        return value

    raise ValueError(f'Значение в столбце "{column}" не может быть пустым.')


def is_number(value: Any, column: str) -> float:
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

    raise ValueError(f'Значение в столбце "{column}" не является числом.')


def is_date(value: Any, column: str) -> datetime:
    """
    Before Pydantic валидатор. Проверяет, является ли входное значение датой.
    Поднимает исключение, если значение не является датой.
    """
    if isinstance(value, str):
        result = Parser.parse_date(value)

        if result:
            return result

    raise ValueError(f'Значение в столбце "{column}" не является датой.')


def is_integer(value: int | float, column: str) -> int:
    """
    After Pydantic валидатор. Проверяет, является ли входное значение целым числом.
    Поднимает исключение, если значение не является целым числом.
    """
    result = isinstance(value, int) or (isinstance(value, float) and value.is_integer())

    if result:
        return int(value)

    raise ValueError(f'Значение в столбце "{column}" не является целым числом.')


def is_percentage(value: int | float, column: str) -> int | float:
    """
    After Pydantic валидатор. Проверяет, является ли входное значение процентом.
    Поднимает исключение, если значение не является процентом.
    """
    if isinstance(value, (int, float)):
        if 0 <= value <= 100:
            return value

    raise ValueError(f'Значение в столбце "{column}" не является процентом.')


def is_not_negative(value: int | float, column: str) -> int | float:
    """
    After Pydantic валидатор. Проверяет, является ли входное значение неотрицательным числом.
    Поднимает исключение, если значение является отрицательным.
    """
    if isinstance(value, (int, float)):
        if value >= 0:
            return value

    raise ValueError(f'Значение в столбце "{column}" должно быть неотрицательным числом.')


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


def set_value(value: str | int | float | None, column: str) -> int | float:
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
                raise ValueError(f'Значение в столбце "{column}" должно быть числом.')

    if value is None:
        return 0

    if isinstance(value, (int, float)):
        return value

    raise ValueError(f'Значение в столбце "{column}" должно быть числом.')


# Предметные валидаторы.
def valid_month(value: int, column: str) -> int:
    """
    After Pydantic валидатор. Проверяет, является ли входное значение валидным месяцем.
    Поднимает исключение, если значение не является месяцем.
    """
    if 1 <= value <= 12:
        return value

    raise ValueError(f'Значение в столбце "{column}" должно быть в диапазоне от 1 до 12.')


def valid_hours(value: int | float, column: str) -> int | float:
    """
    After Pydantic валидатор. Проверяет, является ли входное значение валидным количеством часов.
    Поднимает исключение, если значение не является валидным количеством часов.
    """
    if isinstance(value, (int, float)):
        if 0 <= value <= 24:
            return value

    raise ValueError(f'Количество часов в столбце "{column}" должно быть в диапазоне от 0 до 24.')


def valid_metro(value: str, column: str) -> str:
    """
    After Pydantic валидатор. Проверяет, что входное значение содержит один из городов, где есть метро.
    """
    city = MParser.parse_city(value)

    if city is None:
        raise ValueError('Не удалось определить город метро.')

    city = 'Москва' if city == 'Московская область' else city

    if city not in (
        'Москва',
        'Санкт-Петербург',
        'Екатеринбург',
        'Казань',
        'Новосибирск',
        'Нижний Новгород',
        'Самара',
        'Волгоград',
    ):
        raise ValueError('В указанном городе нет метро.')

    return city
