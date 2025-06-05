import re
from datetime import datetime

from rapidfuzz import fuzz, process

from core.utils.tools import TextTools


class Parser:
    @staticmethod
    def parse_num(string: str) -> float | None:
        """
        Парсит число с плавающей точкой.

        Args:
            string: Входная строка.

        Returns:
            Вещественное число или None, если преобразование не удалось.
        """
        # Удаляем пробелы и специальные символы, заменяем запятые на точки.
        cleaned_string = TextTools.to_clean_string(string).replace(' ', '')

        if ',' in cleaned_string and '.' in cleaned_string:
            cleaned_string = cleaned_string.replace(',', '')
        else:
            cleaned_string = cleaned_string.replace(',', '.').removesuffix('.')

        # Если строка пустая, возвращаем None.
        if not cleaned_string:
            return None

        try:
            num = float(cleaned_string)
        except ValueError:
            return None

        return num

    @staticmethod
    def parse_date(string: str) -> datetime | None:
        """
        Парсит объект datetime.

        Args:
            string: Входная строка.

        Returns:
            Объект datetime или None, если преобразование не удалось.
        """
        # Удаляем пробелы и специальные символы.
        cleaned_string = TextTools.to_clean_string(string)

        # Если строка пустая, возвращаем None.
        if not cleaned_string:
            return None

        # Форматы даты и даты-времени (YYYY-MM-DD).
        date_formats_ymd = [
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',
            '%Y.%m.%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y.%m.%d',
        ]

        # Форматы даты и даты-времени (DD-MM-YYYY).
        date_formats_dmy = [
            '%d-%m-%Y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
            '%d.%m.%Y %H:%M:%S',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%d.%m.%Y',
        ]

        # Пробуем cпарсить сначала форматы YYYY-MM-DD.
        for fmt in date_formats_ymd:
            try:
                # Возвращаем datetime с временем 00:00:00.
                dt = datetime.strptime(cleaned_string, fmt)
                return dt.replace(hour=0, minute=0, second=0, microsecond=0)
            except ValueError:
                continue

        # Затем пробуем cпарсить форматы DD-MM-YYYY.
        for fmt in date_formats_dmy:
            try:
                # Возвращаем datetime с временем 00:00:00.
                dt = datetime.strptime(cleaned_string, fmt)
                return dt.replace(hour=0, minute=0, second=0, microsecond=0)
            except ValueError:
                continue

        return None

    @staticmethod
    def parse_timeslot(string: str) -> str | None:
        """
        Парсит временной интервал.

        Args:
            string: Входная строка.

        Returns:
            Временной интервал в формате HH:MM:SS-HH:MM:SS.
        """
        # Удаляем пробелы и специальные символы.
        cleaned_string = TextTools.to_clean_string(string)

        # Если строка пустая, возвращаем None.
        if TextTools.is_empty_string(cleaned_string):
            return None

        match = re.match(r'(\d{2}:\d{2}(?::\d{2})?)\s*[-–]\s*(\d{2}:\d{2}(?::\d{2})?)', cleaned_string)

        # Если не удалось распознать временной интервал, возвращаем None.
        if not match:
            return None

        start_time = match.group(1)
        end_time = match.group(2)

        # Добавляем секунды, если они отсутствуют.
        if start_time.count(':') == 1:
            start_time += ':00'
        if end_time.count(':') == 1:
            end_time += ':00'

        return f'{start_time}-{end_time}'

    @staticmethod
    def _dms_to_dd(degrees: int, minutes: int, seconds: float, hemisphere: str) -> float:
        """
        Конвертирует координаты из формата DMS (градусы, минуты, секунды) в десятичные градусы.

        Args:
            degrees: Градусы.
            minutes: Минуты.
            seconds: Секунды.
            hemisphere: Полушарие ('N', 'S', 'E', 'W').

        Returns:
            Координаты в десятичных градусах.
        """
        # Преобразуем градусы, минуты и секунды в десятичные градусы.
        dd = degrees + minutes / 60 + seconds / 3600

        # Если полушарие южное или западное, меняем знак.
        if hemisphere in ('S', 'W'):
            dd = -dd

        return dd

    @staticmethod
    def parse_coord(string: str) -> float | None:
        """
        Парсит координаты (десятичные градусы или формат DMS).

        Args:
            string: Входная строка.

        Returns:
            Координаты в десятичных градусах или None, если преобразование не удалось.
        """
        # Пробуем преобразовать строку в число.
        num = Parser.parse_num(string)

        # Если преобразование прошло успешно, возвращаем число.
        if num is not None:
            return num

        # Удаляем пробелы и специальные символы.
        cleaned_string = TextTools.to_clean_string(string)

        # Пробуем распознать координаты в формате DMS.
        match = re.match(
            r"(\d{1,3})\s*°\s*(\d{1,2})\s*'\s*([\d.]+)\s*[\"″']?\s*([NSWE])", cleaned_string, re.IGNORECASE
        )

        # Если не удалось распознать координаты, возвращаем None.
        if not match:
            return None

        degrees = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))
        hemisphere = match.group(4).upper()

        # Переводим в десятичные градусы.
        return Parser._dms_to_dd(degrees, minutes, seconds, hemisphere)

    @staticmethod
    def parse_object(string: str, choices: dict[str, list[str]], threshold: int = 90) -> str | None:
        """
        Конвертирует строку в стандартизованное значение, используя нечеткое сравнение.

        Args:
            string: Входная строка, которую нужно стандартизировать.
            choices: Словарь, где ключи - это стандартизованные формы, а значения - списки вариантов.
            threshold: Минимальное пороговое значение для нечеткого сравнения (от 0 до 100).
        Returns:
            Стандартизованная форма или None, если не удалось найти подходящее значение.
        """
        cleaned = TextTools.to_clean_string(string)

        if TextTools.is_empty_string(cleaned):
            return None

        key = cleaned.lower()

        # Flatten mapping: вариант или стандарт -> стандарт.
        mapping = {TextTools.to_clean_string(std).lower(): std for std in choices}
        mapping.update((TextTools.to_clean_string(var).lower(), std) for std, vars in choices.items() for var in vars)

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
