import hashlib
import re
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from functools import cache

from rapidfuzz import fuzz, process


class TextTools:
    """Утилиты для работы со строками."""

    @staticmethod
    @cache
    def to_clean(string: str) -> str:
        """
        Очищает строку от управляющих символов и лишних пробелов.

        Args:
            string (str): Строка.

        Returns:
            str: Очищенная строка.
        """
        c_str = re.sub(r'\n', ' ', string)
        c_str = re.sub(r'[\x00-\x09\x0B-\x1F\x7F-\x9F]', '', c_str)
        return re.sub(r'\s+', ' ', c_str).strip()

    @staticmethod
    @cache
    def to_trunc(string: str, max_length: int = 10) -> str:
        """
        Обрезает строку до заданной длины, добавляя '...' в конец. Итоговая длина строки учитывает '...'.

        Args:
            string (str): Строка.
            max_length (int): Максимальная длина строки.

        Returns:
            str: Обрезанная строка.
        """
        return string[: max(0, max_length - 3)] + '...' if len(string) > max_length else string

    @staticmethod
    @cache
    def is_empty(string: str) -> bool:
        """
        Проверяет, является ли строка пустой или содержит только специальные метки.

        Args:
            string (str): Строка.

        Returns:
            bool: True, если строка пустая, иначе False.
        """
        c_str = TextTools.to_clean(string)
        return not c_str or c_str.lower() in ('none', '-', 'n/a')

    @staticmethod
    @cache
    def get_hash(string: str) -> str:
        """
        Вычисляет SHA-256 хэш.

        Args:
            string (str): Строка.

        Returns:
            str: SHA-256 хэш.
        """
        return hashlib.sha256(string.encode('utf-8')).hexdigest()


class Parser:
    """Утилиты для парсинга строк."""

    @staticmethod
    @cache
    # TODO: Добавить docstring.
    def parse_number(string: str) -> float | None:
        # Очищаем строку и убираем пробелы.
        c_str = TextTools.to_clean(string)
        c_str = c_str.replace(' ', '')

        # Если строка пустая, возвращаем None.
        if not c_str:
            return None

        # Если разделитель - точка, но запятая служит для разделения классов, удаляем запятую.
        if ',' in c_str and '.' in c_str:
            c_str = c_str.replace(',', '')
        else:
            # Если разделитель - запятая, заменяем запятую на точку.
            # Дополнительно удаляем точку в конце строки (при наличии).
            c_str = c_str.replace(',', '.').removesuffix('.')

        try:
            return float(c_str)
        except ValueError:
            return None

    @staticmethod
    @cache
    # TODO: Добавить docstring.
    def parse_date(string: str) -> datetime | None:
        # Очищаем строку.
        c_str = TextTools.to_clean(string)

        # Если строка пустая, возвращаем None.
        if not c_str:
            return None

        # Форматы даты и даты-времени (YYYY-MM-DD).
        date_fmts_ymd = [
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%Y.%m.%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y.%m.%d',
        ]

        # Форматы даты и даты-времени (DD-MM-YYYY).
        date_fmts_dmy = [
            '%d-%m-%Y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
            '%d.%m.%Y %H:%M:%S',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%d.%m.%Y',
        ]

        # Пробуем cпарсить сначала форматы YYYY-MM-DD.
        for fmt in date_fmts_ymd:
            try:
                # Возвращаем datetime с временем 00:00:00.
                dt = datetime.strptime(c_str, fmt)
                return dt.replace(hour=0, minute=0, second=0, microsecond=0)
            except ValueError:
                continue

        # Затем пробуем cпарсить форматы DD-MM-YYYY.
        for fmt in date_fmts_dmy:
            try:
                # Возвращаем datetime с временем 00:00:00.
                dt = datetime.strptime(c_str, fmt)
                return dt.replace(hour=0, minute=0, second=0, microsecond=0)
            except ValueError:
                continue

        return None

    @staticmethod
    def parse_object(string: str, choices: dict[str, list[str]], threshold: int = 90) -> str | None:
        """
        Конвертирует строку в стандартизованное значение, используя нечеткое сравнение.

        Args:
            string (str): Входная строка, которую нужно стандартизировать.
            choices (dict[str, list[str]]): Словарь, где ключи — стандартизованные формы, а значения — варианты.
            threshold (int): Минимальное пороговое значение для нечеткого сравнения (от 0 до 100).

        Returns:
            str | None: Найденная стандартизованная форма или None, если подходящее значение не найдено.
        """
        c_str = TextTools.to_clean(string)

        if TextTools.is_empty(c_str):
            return None

        key = c_str.lower()

        # Flatten mapping: вариант или стандарт -> стандарт.
        mapping = {TextTools.to_clean(std).lower(): std for std in choices}
        mapping.update((TextTools.to_clean(var).lower(), std) for std, vars in choices.items() for var in vars)

        # Прямое совпадение.
        if std := mapping.get(key):
            return std

        # Нечеткое совпадение.
        candidates = list(mapping)

        for cut in range(100, threshold - 1, -1):
            for scorer in (fuzz.token_set_ratio, fuzz.WRatio):
                if match := process.extractOne(key, candidates, scorer=scorer, score_cutoff=cut):
                    return mapping[match[0]]

        return None

    @staticmethod
    @cache
    # TODO: Добавить docstring.
    def parse_timeslot(string: str) -> str | None:
        # Очищаем строку.
        c_str = TextTools.to_clean(string)

        # Если строка пустая, возвращаем None.
        if TextTools.is_empty(c_str):
            return None

        # Паттерн распознавания временного интервала.
        match = re.match(r'(\d{2}:\d{2}(?::\d{2})?)\s*[-–]\s*(\d{2}:\d{2}(?::\d{2})?)', c_str)

        # Если не удалось распознать временной интервал, возвращаем None.
        if not match:
            return None

        time_from = match.group(1)
        time_to = match.group(2)

        # Добавляем секунды, если они отсутствуют.
        if time_from.count(':') == 1:
            time_from += ':00'
        if time_to.count(':') == 1:
            time_to += ':00'

        return f'{time_from}-{time_to}'


def round_(value, ndigits=1):
    """Округление по математическим правилам."""
    exp = Decimal('1') if ndigits == 0 else Decimal(f'1e{-ndigits}')
    return float(Decimal(value).quantize(exp, rounding=ROUND_HALF_UP))
