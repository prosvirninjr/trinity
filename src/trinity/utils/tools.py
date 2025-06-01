import hashlib
import re
from functools import cache


class TextTools:
    """Утилиты для работы со строками."""

    @staticmethod
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
    def to_trunc(string: str, max_length: int = 10) -> str:
        """
        Обрезает строку до заданной длины, добавляя '...' в конец. Итоговая длина строки учитывает '...'.

        Args:
            string (str): Строка.
            max_length (int): Максимальная длина результата.

        Returns:
            str: Обрезанная строка.
        """
        return string[: max(0, max_length - 3)] + '...' if len(string) > max_length else string

    @staticmethod
    def is_empty(string: str) -> bool:
        """
        Проверяет, является ли строка пустой или содержит только специальные метки.

        Args:
            string (str): Строка.

        Returns:
            bool: True, если строка пустая или содержит только пробелы, 'None', '-', 'n/a'.
        """
        c_str = TextTools.to_clean(string)
        return not c_str or c_str.lower() in ('none', '-', 'n/a')

    @staticmethod
    @cache
    def get_hash(string: str) -> str:
        """
        Вычисляет SHA-256 хэш строки.

        Args:
            string (str): Строка.

        Returns:
            str: SHA-256 хэш строки.
        """
        return hashlib.sha256(string.encode('utf-8')).hexdigest()
