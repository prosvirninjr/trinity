"""Бизнес-логика для наружной рекламы."""

import calendar
import json
import logging
import os
import re
from datetime import datetime
from functools import cache
from importlib.resources import files

from trinity.utils.tools import Parser, TextTools, round_

# Проверяем наличие папки и создаем ее при необходимости.
log_path = files('trinity').joinpath('..', '..', '.logs')

if not os.path.exists(log_path):
    os.makedirs(log_path)


# Настраиваем фильтрацию логов.
class DuplicateFilter(logging.Filter):
    """Не позволяет логировать дублирующиеся сообщения."""

    def __init__(self):
        super().__init__()
        self._seen: set[str] = set()

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()

        if msg in self._seen:
            return False

        self._seen.add(msg)

        return True


# Настраиваем форматирование логов.
formatter = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# Настраиваем логирование.
file_handler = logging.FileHandler(log_path / 'parser.log', mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.addFilter(DuplicateFilter())
file_handler.setFormatter(formatter)


log = logging.getLogger(__name__)
log.propagate = False  # Отключаем передачу сообщений родительским логгерам.
log.setLevel(logging.DEBUG)
log.addHandler(file_handler)


class Coefficient:
    @staticmethod
    @cache
    def calc_rental_c(date_from: datetime, date_to: datetime, n: int = 4) -> float:
        """
        Вычисляет коэффициент длительности аренды на основе дат начала и окончания.
        Коэффициент рассчитывается как отношение количества дней аренды к количеству дней в месяце.

        Args:
            date_from (datetime): Дата начала аренды.
            date_to (datetime): Дата окончания аренды.
            n (int): Количество знаков после запятой для округления.

        Returns:
            float: Коэффициент длительности аренды, округленный до n знаков после запятой.
        """
        days = (date_to - date_from).days + 1
        days_in_month = calendar.monthrange(date_from.year, date_from.month)[1]

        rental_c = days / days_in_month

        return round(rental_c, n)

    @staticmethod
    @cache
    def calc_digital_c(
        format_: str, spot_duration: float, spots_per_block: float, block_duration: float, n: int = 4
    ) -> float:
        """
        Вычисляет коэффициент digital размещения на основе параметров конструкции.
        Коэффициент рассчитывается как отношение произведения длительности ролика на объем размещения
        к стандартному объему размещения, зависящему от формата конструкции.

        При вычислении коэффициента общее время работы конструкции в сутки принимается равным 24 часам (86400 секунд).

        Объемы размещения:
        - MF (Medium Format): 15 * 288 (15 секунд * 288 выходов в сутки при длительности блока 300 секунд).
        - Прочие форматы: 5 * 1728 (5 секунд * 1728 выходов в сутки при длительности блока 50 секунд).

        Args:
            format_ (str): Формат конструкции.
            spot_duration (float): Длительность ролика в секундах.
            spots_per_block (float): Количество выходов в блоке.
            block_duration (float): Длительность блока в секундах.
            n (int): Количество знаков после запятой для округления.

        Returns:
            float: Коэффициент digital размещения, округленный до n знаков после запятой.
        """
        denominator = (15 * 288) if format_ == 'MF' else (5 * 1728)
        digital_c = (spot_duration * ((86400 / block_duration) * spots_per_block)) / denominator

        return round(digital_c, n)


class Construction:
    @staticmethod
    @cache
    def get_sizes(size: str) -> tuple[float, float]:
        """
        Парсит строку с размером в формате 'W x H' и возвращает кортеж (width, height).

        Args:
            size (str): Строка с размерами в формате 'W x H'.

        Returns:
            tuple[float, float]: Кортеж с шириной и высотой. В случае неудачи возвращает (0, 0).
        """
        try:
            dimensions = [float(dim.strip()) for dim in size.split('x')]
            if len(dimensions) != 2:
                return 0, 0
            return min(dimensions), max(dimensions)
        except (ValueError, AttributeError):
            return 0, 0


class MParser:
    """
    Расширенный парсер для бизнес-логики наружной рекламы.
    """

    @staticmethod
    @cache
    def parse_advertiser(advertiser: str) -> str | None:
        choices = json.load(open(files('trinity').joinpath('data', 'mapping', 'advertisers.json')))
        result = Parser.parse_object(advertiser, choices, threshold=90)

        if result is None:
            log.warning('Не удалось распознать рекламодателя: %s', advertiser)
        else:
            log.info('Рекламодатель распознан: %s -> %s', advertiser, result)

        return result

    @staticmethod
    @cache
    def parse_city(city: str) -> str | None:
        choices = json.load(open(files('trinity').joinpath('data', 'mapping', 'cities.json')))
        result = Parser.parse_object(city, choices, threshold=90)

        if result is None:
            log.warning('Не удалось распознать город: %s', city)
        else:
            log.info('Город распознан: %s -> %s', city, result)

        return result

    @staticmethod
    def _get_line_choices(metro: dict, city: str) -> dict[str, list[str]]:
        """
        Возвращает словарь {линия: варианты} для указанного города на основе общего словаря metro.
        """
        city_data = metro[city]

        return {ln: data.get('_self', {}).get('options', []) for ln, data in city_data.items() if '_self' in data}

    @staticmethod
    def _get_station_choices(metro: dict, city: str) -> dict[str, list[str]]:
        """
        Возвращает словарь {станция: варианты} для указанного города на основе общего словаря metro.
        """
        city_data = metro[city]
        choices: dict[str, list[str]] = {}

        for line_data in city_data.values():
            for st_name, st_data in line_data.items():
                # Пропускаем мета-узел и дубликаты.
                if st_name == '_self' or st_name in choices:
                    continue

                # Включаем станцию даже если список вариантов пуст.
                choices[st_name] = st_data.get('options', [])

        return choices

    @staticmethod
    @cache
    def parse_line(city: str, line: str | None, station: str | None) -> str | None:
        # 1. Если станция и линия не указаны, возвращаем None.
        if line is None and station is None:
            return None

        metro = json.load(open(files('trinity').joinpath('data', 'mapping', 'metro.json')))
        line_choices = MParser._get_line_choices(metro, city)
        station_choices = MParser._get_station_choices(metro, city)

        # 2. Логика определения линии вне зависимости от станции.
        if station is None:
            guessed_line = Parser.parse_object(line, line_choices, threshold=90)

            if guessed_line:
                log.info('Линия распознана: (%s, %s, %s) -> %s', city, line, station, guessed_line)
                return guessed_line

            log.warning('Не удалось распознать линию: (%s, %s, %s)', city, line, station)
            return None

        # 3. Логика определения линии с учётом станции. # Сначала пытаемся распознать линию.
        guessed_line = Parser.parse_object(line, line_choices, threshold=90)

        if not guessed_line:
            log.warning('Не удалось распознать линию: (%s, %s, %s)', city, line, station)
            return None

        # Пытаемся распознать станцию (fuzzy), и / или смотрим точное совпадение.
        fuzzy_station = Parser.parse_object(station, station_choices, threshold=90)

        # Специальная логика для МЦД.
        if guessed_line.startswith('МЦД'):
            base_mcd = 'МЦД'

            for mcd_line in filter(lambda x: x.startswith('МЦД-'), line_choices):
                stations = metro[city].get(mcd_line, {})

                if station in stations or (fuzzy_station and fuzzy_station in stations):
                    log.info('Линия распознана: (%s, %s, %s) -> %s', city, line, station, mcd_line)
                    return mcd_line

            log.info('Линия распознана: (%s, %s, %s) -> %s', city, line, station, base_mcd)
            return base_mcd

        stations_on_line = metro[city][guessed_line]

        if station in stations_on_line or (fuzzy_station and fuzzy_station in stations_on_line):
            log.info('Линия распознана: (%s, %s, %s) -> %s', city, line, station, guessed_line)
            return guessed_line

        log.warning('Не удалось распознать линию: (%s, %s, %s)', city, line, station)
        return None

    @staticmethod
    @cache
    def parse_station(city: str, station: str) -> str | None:
        """
        Стандартизирует название станции для указанного города.
        """
        if station is None:
            return None

        metro = json.load(open(files('trinity').joinpath('data', 'mapping', 'metro.json'), encoding='utf-8'))
        station_choices = MParser._get_station_choices(metro, city)

        result = Parser.parse_object(station, station_choices, threshold=90)

        if result is None:
            log.warning('Не удалось распознать станцию: (%s, %s)', city, station)
        else:
            log.info('Станция распознана: (%s, %s) -> %s', city, station, result)

        return result

    @staticmethod
    @cache
    def parse_location(location: str | None) -> str | None:
        """
        Стандартизирует название локации.
        """
        if location is None:
            return None

        locations = json.load(open(files('trinity').joinpath('data', 'mapping', 'locations.json')))
        result = Parser.parse_object(location, locations, threshold=90)

        if result is None:
            log.warning('Не удалось распознать локацию: %s', location)
        else:
            log.info('Локация распознана: %s -> %s', location, result)

        return result

    @staticmethod
    @cache
    def parse_format(format_: str) -> str | None:
        """
        Стандартизирует название формата конструкции.
        """
        if format_ is None:
            return None

        formats = json.load(open(files('trinity').joinpath('data', 'mapping', 'formats.json')))
        result = Parser.parse_object(format_, formats, threshold=90)

        if result is None:
            log.warning('Не удалось распознать формат: %s', format_)
        else:
            log.info('Формат распознан: %s -> %s', format_, result)

        return result

    @staticmethod
    @cache
    def _extract_size(string: str, n: int = 1) -> str | None:
        # Удаляем единицы измерения (см, м, мм) и лишние пробелы.
        string_without_units = re.sub(r'\s*(см|м|мм)\b', '', string, flags=re.IGNORECASE)
        cleaned_string = TextTools.to_clean(string_without_units)

        # Ищем числа с разделителями (x, х, X, Х, *, ×).
        match = re.search(r'(\d+[,.]?\d*)\s*([xхXХ*×])\s*(\d+[,.]?\d*)', cleaned_string)

        # Если не найдено совпадений, возвращаем None.
        if not match:
            return None

        # Иначе извлекаем числа из регулярного выражения.
        try:
            width = float(match.group(1).replace(',', '.'))
            height = float(match.group(3).replace(',', '.'))

            width, height = sorted((width, height))

            width, height = round_(width, n), round_(height, n)
        except ValueError:
            # Если произошла ошибка при преобразовании, возвращаем None.
            return None
        else:
            return 'x'.join(map(str, (width, height)))

    @staticmethod
    @cache
    def parse_size(string: str | None, threshold: int = 100) -> str | None:
        """
        Сначала пробуем по справочнику размеров, затем экстрактор чисел.
        """
        if string is None:
            log.warning('Не удалось распарсить размер: строка пустая')
            return None

        # Сначала пытаемся распарсить размер по справочнику.
        sizes = json.load(open(files('trinity').joinpath('data', 'mapping', 'sizes.json')))
        parsed = Parser.parse_object(string, sizes, threshold)

        if parsed:
            if parsed == '-':
                log.warning('Размер распознан, но не подпадает под стандартную запись: %s', string)
                return None

            log.info('Размер распознан: %s -> %s', string, parsed)
            return parsed

        # Если не удалось распарсить по справочнику, пробуем экстрактор чисел.
        result = MParser._extract_size(string)

        if result:
            log.info('Размер распознан: %s -> %s', string, result)
        else:
            log.warning('Не удалось распарсить размер: %s', string)

        return result
