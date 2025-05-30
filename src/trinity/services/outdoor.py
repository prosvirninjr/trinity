"""Бизнес-логика для наружной рекламы."""

import calendar
from datetime import datetime
from functools import cache


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
