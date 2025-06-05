import re

from core.tv.kz.enums import SpotPosition


def is_prime_time(start_hour: int, end_hour: int, lower_bound: int = 18, upper_bound: int = 24) -> bool:
    """
    Проверяет, попадает ли временной диапазон в границы prime time.

    Args:
        start_hour (int): час начала временного диапазона.
        end_hour (int): час окончания временного диапазона.
        lower_bound (int, optional): нижняя граница prime time. По умолчанию 18.
        upper_bound (int, optional): верхняя граница prime time. По умолчанию 24.

    Returns:
        bool: True, если временной диапазон попадает в prime time, иначе False.
    """
    return (start_hour >= lower_bound) and (end_hour < upper_bound)


def get_spot_position(spot_position: int, spots_count: int) -> str:
    """
    Получает строковое представление позиции ролика в рекламном блоке.

    Args:
        spot_position (int): позиция ролика в блоке.
        spots_count (int): количество роликов в блоке.

    Returns:
        str: строковое представление позиции ролика.
    """
    if spot_position == 1:
        return SpotPosition.FIRST.value
    elif spot_position == 2:
        return SpotPosition.SECOND.value
    elif spot_position == (spots_count - 1):
        return SpotPosition.PENULTIMATE.value
    elif spot_position == spots_count:
        return SpotPosition.LAST.value

    return SpotPosition.MIDDLE.value


def get_time_parts(string: str) -> list[int]:
    """
    Извлекает часы, минуты и секунды из строки "ЧЧ:ММ:СС".

    Args:
        string (str): Строка времени в формате "ЧЧ:ММ:СС".

    Returns:
        list[int]: Список из трех целых чисел (часы, минуты, секунды).
    """
    return list(map(int, string.split(':')))


def get_date_parts(string: str) -> list[int]:
    """
    Извлекает год, месяц и день из строки даты.

    Args:
        string (str): Строка даты в одном из поддерживаемых форматов.

    Returns:
        list[int]: Список из трех целых чисел [год, месяц, день].
    """
    n1, n2, n3 = map(int, re.split(r'[-/.]', string))

    if len(str(n1)) == 4:
        return [n1, n2, n3]

    return [n3, n2, n1]
