import logging
import os
import re
from functools import cache

from app_assets import (
    load_advertisers,
    load_formats,
    load_locations,
    load_operators,
    load_sides,
    load_sizes,
    load_specific_locs,
)
from app_settings import PROJECT_ROOT
from core.utils.parser import Parser
from core.utils.tools import TextTools, round_


class DuplicateFilter(logging.Filter):
    """
    Фильтр, который не пропускает повторяющиеся сообщения.
    """

    def __init__(self):
        super().__init__()
        self._seen: set[str] = set()

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        if msg in self._seen:
            return False
        self._seen.add(msg)
        return True


log_path = PROJECT_ROOT / '.logs' / 'parser.log'

# Проверяем наличие папки и создаем ее при необходимости.
if not os.path.exists(log_path.parent):
    os.makedirs(log_path.parent)

file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
file_handler.addFilter(DuplicateFilter())

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.propagate = False  # Отключаем передачу сообщений родительским логгерам.
log.addHandler(file_handler)


class OOHParser(Parser):
    @staticmethod
    @cache
    def _extract_size(string: str) -> str | None:
        cleaned_string = TextTools.to_clean_string(string)

        # Ищем числа с разделителями (x, х, X, Х, *, ×).
        match = re.search(r'(\d+[,.]?\d*)\s*([xхXХ*×])\s*(\d+[,.]?\d*)', cleaned_string)

        # Если не найдено совпадений, возвращаем None
        if not match:
            return None

        # Иначе извлекаем числа из регулярного выражения
        try:
            width = float(match.group(1).replace(',', '.'))
            height = float(match.group(3).replace(',', '.'))

            width, height = sorted((width, height))

            width, height = round_(width, 1), round_(height, 1)
        except ValueError:
            # Если произошла ошибка при преобразовании, возвращаем None
            return None
        else:
            return f'{width}x{height}'

    @staticmethod
    @cache
    def parse_size(string: str | None, threshold: int = 100) -> str | None:
        """
        Сначала пробуем по справочнику размеров, затем экстрактор чисел.
        """
        if string is None:
            log.warning('Не удалось распарсить размер: строка пустая')
            return None

        sizes = load_sizes()

        if parsed := Parser.parse_object(string, sizes, threshold):
            log.debug(f'Размер успешно распознан: [{string}] -> [{parsed}]')
            return parsed

        result = OOHParser._extract_size(string)

        if result:
            log.debug(f'Размер успешно распознан: [{string}] -> [{result}]')
        else:
            log.warning(f'Не удалось распарсить размер: [{string}] -> None')

        return result

    @staticmethod
    @cache
    def parse_location(subject_code: str | None, string: str | None, threshold: int = 90) -> str | None:
        """
        Парсинг местоположения: сначала по специфичным локациям,
        затем по справочнику с учётом subject_code.
        """
        if subject_code is None or string is None:
            log.warning('Не удалось распарсить локацию: строка пустая')
            return None

        text = string.strip()

        if not text:
            log.warning('Не удалось распарсить локацию: строка пустая')
            return None

        # Специальные соответствия
        specific = load_specific_locs()

        if mapped := specific.get(text):
            log.debug(f'Локация успешно распознана: [{subject_code}][{string}] -> [{mapped}]')
            return mapped

        # Общий справочник локаций
        all_locs = load_locations()
        subject_data = all_locs.get(subject_code, {})  # type: ignore

        # Собираем варианты для парсинга
        choices: dict[str, list[str]] = {}
        for loc_name, info in subject_data.items():
            if isinstance(info, dict):
                opts = info.get('options', [])
                if isinstance(opts, list):
                    choices[loc_name] = [str(o) for o in opts if isinstance(o, (str, int, float))]

        if not choices:
            log.warning('Не удалось распарсить локацию: нет доступных вариантов')
            return None

        result = Parser.parse_object(text, choices, threshold)
        if result:
            log.debug(f'Локация успешно распознана: [{subject_code}][{string}] -> [{result}]')
        else:
            log.warning(f'Не удалось распарсить локацию: [{subject_code}][{string}] -> None')
        return result

    @staticmethod
    @cache
    def parse_advertiser(string: str | None, threshold: int = 90) -> str | None:
        """
        Парсинг рекламодателя по справочнику.
        """
        if string is None:
            log.warning('Не удалось распарсить рекламодателя: строка пустая')
            return None
        advertisers = load_advertisers()
        result = Parser.parse_object(string, advertisers, threshold)
        if result:
            log.debug(f'Рекламодатель успешно распознан: [{string}] -> [{result}]')
        else:
            log.warning(f'Не удалось распарсить рекламодателя: [{string}] -> None')
        return result

    @staticmethod
    @cache
    def parse_format(string: str | None, threshold: int = 90) -> str | None:
        """
        Парсинг формата конструкции по справочнику.
        """
        if string is None:
            log.warning('Не удалось распарсить формат: строка пустая')
            return None
        formats = load_formats()
        result = Parser.parse_object(string, formats, threshold)
        if result:
            log.debug(f'Формат успешно распознан: [{string}] -> [{result}]')
        else:
            log.warning(f'Не удалось распарсить формат: [{string}] -> None')
        return result

    @staticmethod
    @cache
    def parse_side(string: str | None, threshold: int = 90) -> str | None:
        """
        Парсинг стороны (A|B) по справочнику.
        """
        if string is None:
            log.warning('Не удалось распарсить сторону: строка пустая')
            return None
        sides = load_sides()
        result = Parser.parse_object(string, sides, threshold)
        if result:
            log.debug(f'Сторона успешно распознана: [{string}] -> [{result}]')
        else:
            log.warning(f'Не удалось распарсить сторону: [{string}] -> None')
        return result

    @staticmethod
    @cache
    def parse_operator(string: str | None, threshold: int = 90) -> str | None:
        """
        Парсинг оператора/поставщика по справочнику.
        """
        if string is None:
            log.warning('Не удалось распарсить оператора: строка пустая')
            return None
        operators = load_operators()
        result = Parser.parse_object(string, operators, threshold)
        if result:
            log.debug(f'Оператор успешно распознан: [{string}] -> [{result}]')
        else:
            log.warning(f'Не удалось распарсить оператора: [{string}] -> None')
        return result
