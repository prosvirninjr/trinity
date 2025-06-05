import hashlib
import io
import json
import math
import re
from decimal import ROUND_HALF_UP, Decimal


class TextTools:
    """
    Утилиты для работы со строками: очистка, усечение и хеширование.
    """

    @staticmethod
    def to_clean_string(string: str) -> str:
        """
        Очищает строку от управляющих символов и лишних пробелов.

        Args:
            string: Исходная строка.

        Returns:
            Очищенная строка.
        """
        cleaned = re.sub(r'\n', ' ', string)
        cleaned = re.sub(r'[\x00-\x09\x0B-\x1F\x7F-\x9F]', '', cleaned)
        return re.sub(r'\s+', ' ', cleaned).strip()

    @staticmethod
    def is_empty_string(string: str) -> bool:
        """
        Проверяет, является ли строка пустой или содержит только специальные метки.

        Args:
            string: Исходная строка.

        Returns:
            True, если строка пустая или содержит только пробелы/None, '-', 'n/a'.
        """
        cleaned = TextTools.to_clean_string(string)
        return not cleaned or cleaned.lower() in ('none', '-', 'n/a')

    @staticmethod
    def to_trunc_string(string: str, max_length: int = 10) -> str:
        """
        Обрезает строку до заданной длины, добавляя "..." в конце, если она была длиннее.

        Args:
            string: Исходная строка.
            max_length: Максимальная длина результата.

        Returns:
            Обрезанная строка.
        """
        return string[: max(0, max_length - 3)] + '...' if len(string) > max_length else string

    @staticmethod
    def get_hash(string: str) -> str:
        """
        Вычисляет SHA-256 хэш от строки.

        Args:
            string: Исходная строка.

        Returns:
            SHA-256 хэш строки.
        """
        return hashlib.sha256(string.encode('utf-8')).hexdigest()


class FileTools:
    """
    Утилиты для работы с файлами.
    """

    @staticmethod
    def load_json(file: str | io.BytesIO) -> dict:
        """
        Загружает JSON из файла или BytesIO.
        """
        if isinstance(file, str):
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        if isinstance(file, io.BytesIO):
            content = file.getvalue().decode('utf-8')
            return json.loads(content)
        raise TypeError('Не удалось загрузить JSON файл. Ожидался путь или BytesIO.')

    @staticmethod
    def save_json(file: str | io.BytesIO, data: dict | list[dict]) -> None:
        """
        Сохраняет словарь или список словарей в JSON файл или BytesIO.

        Args:
            file: Путь к файлу или BytesIO.
            data: Словарь или список словарей для сохранения.
        """
        if isinstance(file, str):
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        elif isinstance(file, io.BytesIO):
            s = json.dumps(data, ensure_ascii=False, indent=4)
            file.write(s.encode('utf-8'))
            file.seek(0)
        else:
            raise TypeError('Не удалось сохранить JSON файл. Ожидался путь или BytesIO.')

    @staticmethod
    def save_bytes(file: str | io.BytesIO, data: bytes) -> None:
        """
        Сохраняет байты в файл или BytesIO.
        """
        if isinstance(file, str):
            with open(file, 'wb') as f:
                f.write(data)
        elif isinstance(file, io.BytesIO):
            file.write(data)
            file.seek(0)
        else:
            raise TypeError('Не удалось сохранить байтовые данные. Ожидался путь или BytesIO.')


def singleton(class_):
    """
    Декоратор для реализации паттерна Singleton.

    Args:
        class_: Класс.
    """
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


def round_(value, ndigits=1):
    """Округление по математическим правилам."""
    exp = Decimal('1') if ndigits == 0 else Decimal(f'1e{-ndigits}')
    return float(Decimal(value).quantize(exp, rounding=ROUND_HALF_UP))


def is_integer(number: float, tol: float = 0.01) -> bool:
    """
    Проверяет, является ли число целым с заданной точностью.

    Args:
        number (float): Исходное число.
        tol (float): Допустимая погрешность.

    Returns:
        bool: True, если число целое с заданной точностью, иначе False.
    """
    rounded_number = round(number)

    return math.isclose(number, rounded_number, abs_tol=tol)
