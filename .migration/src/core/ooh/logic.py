import calendar
import logging
import math
from datetime import datetime

import geopandas as gpd
from shapely.geometry import Point

from app_assets import load_geo_data, load_ooh_coefficients
from functools import cache

OOH_COEFFICIENTS = load_ooh_coefficients()
OOH_GEODATA = load_geo_data()

log = logging.getLogger(__name__)


class Construction:
    """Класс для вспомогательных операций, связанных с конструкциями."""

    @staticmethod
    @cache
    def get_sizes(size: str) -> tuple[float | None, float | None]:
        """
        Парсит строку с размером в формате 'W x H' и возвращает кортеж (width, height).

        Args:
            size (str): Строка с размерами в формате 'W x H'.

        Returns:
            tuple[float | None, float | None]: Кортеж с шириной и высотой. В случае неудачи возвращает (None, None).
        """
        try:
            dimensions = [float(dim.strip()) for dim in size.split('x')]
            if len(dimensions) != 2:
                return None, None
            return min(dimensions), max(dimensions)
        except (ValueError, AttributeError):
            return None, None

    @staticmethod
    @cache
    def are_sizes_similar(
        size_1: str | None, size_2: str | None, tolerance: float = 0.15, strict: bool = False
    ) -> bool:
        """
        Проверяет схожесть размеров с учетом относительной погрешности.

        Args:
            size_1 (str | None): Первый размер в формате 'W x H' или None.
            size_2 (str | None): Второй размер в формате 'W x H' или None.
            tolerance (float): Относительный допуск (0.15 = 15%).
            strict (bool): Если False, то некорректный формат ввода ('W x H') не вызывает ошибку,
                а приводит к возврату False.

        Returns:
            bool: True, если:
              - Оба размера None;
              - Размеры идентичны;
              - Размеры отличаются не более чем на `tolerance`.
            False, если:
              - Только один из размеров None;
              - Размеры отличаются более чем на `tolerance`;
              - Формат размеров неверный и `strict=False`.

        Raises:
            ValueError: Если формат любого из размеров неверный и `strict=True`.
        """

        # Обработка None значений
        if size_1 is None and size_2 is None:
            return True
        if size_1 is None or size_2 is None:
            return False

        # Если размеры идентичны, возвращаем True без дополнительных вычислений
        if size_1 == size_2:
            return True

        try:
            w1, h1 = map(float, size_1.split('x'))
            w2, h2 = map(float, size_2.split('x'))
        except ValueError:
            if strict:
                raise ValueError("Неверный формат размера. Ожидаемый формат 'W x H' для обоих размеров.")
            else:
                return False

        w_tol = w1 * tolerance
        h_tol = h1 * tolerance

        return abs(w1 - w2) <= w_tol and abs(h1 - h2) <= h_tol

    @staticmethod
    @cache
    def calc_square(size: str, n: int = 4) -> float:
        """
        Вычисляет площадь конструкции из строки формата 'Ширина x Высота'.

        Args:
            size (str): Строка с размерами в формате 'W x H'.
            n (int): Округление.

        Returns:
            float: Площадь конструкции.
        Raises:
            ValueError: Если формат размера неверный.
        """
        try:
            width, height = (float(part) for part in size.split('x'))
        except ValueError:
            raise ValueError("Неверный формат размера. Ожидаемый формат 'W x H'.")

        return round(width * height, n)


class Geo:
    """Класс для вспомогательных географических вычислений."""

    @staticmethod
    @cache
    def calc_distance(
        lat_1: float, lon_1: float, lat_2: float, lon_2: float, n: int = 4, meters: bool = False
    ) -> float:
        """
        Вычисляет расстояние между двумя точками на сфере (Земле).

        Args:
            lat_1 (float): Широта первой точки.
            lon_1 (float): Долгота первой точки.
            lat_2 (float): Широта второй точки.
            lon_2 (float): Долгота второй точки.
            n (int): Округление.
            meters (bool): Если True, возвращает расстояние в метрах, иначе в километрах.

        Returns:
            float: Расстояние между двумя точками.
        """
        # Земной радиус в км.
        R = 6371.0  # noqa

        lat1_rad = math.radians(lat_1)
        lon1_rad = math.radians(lon_1)
        lat2_rad = math.radians(lat_2)
        lon2_rad = math.radians(lon_2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c

        # Переводим в метры, если требуется.
        if meters:
            distance *= 1000

        return round(distance, n)

    @staticmethod
    @cache
    def is_close(lat_1: float, lon_1: float, lat_2: float, lon_2: float, radius: float, meters: bool = False) -> bool:
        """
        Проверяет, находятся ли точки в пределах радиуса поиска.

        Args:
            lat_1 (float): Широта первой точки.
            lon_1 (float): Долгота первой точки.
            lat_2 (float): Широта второй точки.
            lon_2 (float): Долгота второй точки.
            radius (float): Радиус поиска (в км. или м., в зависимости от `meters`).
            meters (bool): Если True, радиус и расчеты в метрах, иначе в километрах.

        Returns:
            bool: True если расстояние между точками <= радиусу.
        """
        distance = Geo.calc_distance(lat_1, lon_1, lat_2, lon_2, meters=meters)

        return distance <= radius

    @staticmethod
    @cache
    def is_in_russia(lat: float, lon: float, tolerance_m: float = 500) -> bool:
        """
        Проверяет, находится ли точка в пределах Российской Федерации.

        Args:
            lat (float): Широта точки.
            lon (float): Долгота точки.
            tolerance_m (float): Допустимое расстояние до границы в метрах.

        Returns:
            bool: True если точка находится в пределах России.
        """
        point = gpd.GeoSeries([Point(lon, lat)], crs='EPSG:4326').to_crs(epsg=3857).geometry[0]

        return bool(OOH_GEODATA['RUSSIA'].geometry.intersects(point.buffer(tolerance_m)).any())  # type: ignore

    @staticmethod
    @cache
    def locate_point(lat: float, lon: float, tolerance_m: int = 2000, strict: bool = False) -> str | None:
        """
        Определяет субъект по координатам.

        Args:
            lat (float): Широта точки.
            lon (float): Долгота точки.
            tolerance_m (int): Допустимое расстояние до границы в метрах.

        Returns:
            str: Код субъекта.

        Raises:
            LocationNotFoundError: Если субъект не найден.
        """
        point = gpd.GeoSeries([Point(lon, lat)], crs='EPSG:4326').to_crs(epsg=3857).geometry[0].buffer(tolerance_m)

        for subject in OOH_GEODATA:
            if subject.lower().strip() == 'russia':
                continue
            if OOH_GEODATA[subject].geometry.intersects(point).any():  # type: ignore
                return subject

        if not strict:
            log.warning(f'Субъект не найден для координат: [{lat}][{lon}]')
            return

        raise ValueError(f'Субъект не найден для координат: [{lat}][{lon}]')

    @staticmethod
    @cache
    def get_subject(subject_code: str) -> str:
        """
        Возвращает название субъекта по его коду.

        Args:
            subject_code (str): Код субъекта.

        Returns:
            str: Название субъекта или 'Регионы', если код не найден.
        """
        if subject_code == 'RU-MOW':
            return 'Москва'
        elif subject_code == 'RU-MOS':
            return 'Московская область'
        elif subject_code == 'RU-SPB':
            return 'Санкт-Петербург'
        elif subject_code == 'RU-LEN':
            return 'Ленинградская область'

        return 'Регионы'


class Coefficient:
    """Класс для вычисления коэффициентов."""

    @staticmethod
    @cache
    def calc_distance_c(distance: float, radius: float, decay_rate: float = 1.0, n: int = 4) -> float:
        """Вычисляет коэффициент удаленности конструкции от искомой.

        Args:
            distance: Расстояние до объекта.
            radius: Радиус поиска.
            decay_rate: Коэффициент скорости затухания (чем меньше, тем медленнее затухание).
            n: Округление.

        Returns:
            Коэффициент удаленности конструкции от искомой.
        """
        # Если радиус достаточно мал, коэффициент равен 1.0.
        if 0 <= radius <= 0.1:
            return 1.0

        distance_c = math.exp(-decay_rate * (distance / radius))

        return round(distance_c, n)

    @staticmethod
    @cache
    def calc_rental_c(start_date: datetime, end_date: datetime, n: int = 4) -> float:
        """Вычисляет коэффициент длительности аренды.

        Args:
            start_date: Дата начала аренды.
            end_date: Дата окончания аренды.
            n: Округление.

        Returns:
            Коэффициент длительности аренды.
        """
        days = (end_date - start_date).days + 1
        days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]

        rental_c = days / days_in_month

        return round(rental_c, n)

    @staticmethod
    @cache
    def calc_digital_c(
        format_: str, spot_duration: float, spots_per_block: float, block_duration: float, n: int = 4
    ) -> float:
        """
        Вычисляет коэффициент digital конструкции.

        Args:
            format_: Формат конструкции.
            spot_duration: Длительность ролика.
            spots_per_block: Количество роликов в блоке.
            block_duration: Длительность блока.
            n: Округление.

        Returns:
            Коэффициент digital.
        """
        denominator = (15 * 288) if format_ == 'MF' else (5 * 1728)
        digital_c = (spot_duration * ((86400 / block_duration) * spots_per_block)) / denominator

        return round(digital_c, n)

    @staticmethod
    @cache
    def calc_season_c(month: int, strict: bool = False, n: int = 4) -> float:
        """
        Возвращает сезонный коэффициент для указанного месяца.

        Args:
            month: Номер месяца.
            strict: Вызвать исключение, если отсутствует сезонный коэффициент для указанного месяца, иначе вернуть 1.0.
            n: Округление.

        Returns:
            Коэффициент сезонности.

        Raises:
            KeyError: Если отсутствует сезонный коэффициент для какого-либо месяца.
        """
        try:
            season_c = OOH_COEFFICIENTS['season'][str(month)]
        except (KeyError, TypeError):
            if not strict:
                return 1.0

            raise KeyError(f'Отсутствует сезонный коэффициент для {str(month)} месяца.')

        return round(season_c, n)

    @staticmethod
    @cache
    def calc_side_c(side: str, strict: bool = False, n: int = 4) -> float:
        """
        Возвращает коэффициент за сторону.

        Args:
            side: Название стороны.
            strict: Вызвать исключение, если отсутствует коэффициент за сторону, иначе вернуть 1.0.
            n: Округление.

        Returns:
            Коэффициент за сторону.

        Raises:
            KeyError: Если отсутствует коэффициент за сторону.
        """
        try:
            side_c = OOH_COEFFICIENTS['side'][side]
        except (KeyError, TypeError):
            if not strict:
                return 1.0

            raise KeyError(f'Отсутствует коэффициент за сторону {side}.')

        return round(side_c, n)

    @staticmethod
    def calc_inflation_c(
        rates_dict: dict,
        subject_code: str,
        format_type: str,
        year_from: int,
        year_to: int,
        default_rates: dict | None = None,
        n: int = 4,
    ) -> float:
        """
        Calculates the cumulative rate coefficient for a given subject, format, and period.

        If the specific subject or format is not found in `rates_dict`, it attempts to use
        the `default_rates` dictionary for the calculation. The rates represent the year-over-year
        change; for example, a value of 1.25 for the key '2023' means a 25% increase from 2023 to 2024.

        Args:
            rates_dict: A dictionary containing the rate data, structured as {subject: {format: {year: rate}}}.
            subject_code: The subject code (e.g., 'RU-SPB').
            format_type: The format type (e.g., 'CB').
            year_from: The starting year.
            year_to: The ending year.
            default_rates: An optional dictionary containing default rates {year: rate}, used if the
                            specific subject/format combination is not found in `rates_dict`.
            n: The number of decimal places to round to. Defaults to 4.

        Returns:
            The cumulative rate coefficient.

        Raises:
            KeyError: If the rate for a specific year in the period is missing in both the specific
                        rates dictionary (if applicable) and the `default_rates` (if provided and used).
                        Also raised if `default_rates` are needed but not provided.
            ValueError: If a rate needed for division (when year_from > year_to) is zero.
        """
        cumulative_rate = 1.0
        target_rates = None

        # Try to get specific rates
        subject_specific_rates = rates_dict.get(subject_code)
        if subject_specific_rates:
            target_rates = subject_specific_rates.get(format_type)

        # If specific rates not found, try default rates
        if target_rates is None:
            if default_rates is None:
                raise KeyError(f"Rates not found for subject '{subject_code}', format '{format_type}'")
            target_rates = default_rates
            rate_source_description = 'default rates'
        else:
            rate_source_description = f"subject '{subject_code}', format '{format_type}'"

        if year_from == year_to:
            return cumulative_rate

        if year_from < year_to:
            # Calculate cumulative rate for increasing years (multiplication)
            for year in range(year_from, year_to):
                year_str = str(year)
                try:
                    rate_for_year = target_rates[year_str]
                    cumulative_rate *= rate_for_year
                except KeyError:
                    raise KeyError(f'Rate for year {year_str} not found in {rate_source_description}.')
        else:  # year_from > year_to
            # Calculate cumulative rate for decreasing years (division)
            for year in range(year_to, year_from):
                year_str = str(year)
                try:
                    rate_for_year = target_rates[year_str]
                    if rate_for_year == 0:
                        raise ValueError(f'Rate for year {year_str} is zero')
                    cumulative_rate /= rate_for_year
                except KeyError:
                    raise KeyError(f'Rate for year {year_str} not found in {rate_source_description}.')

        return round(cumulative_rate, n)
