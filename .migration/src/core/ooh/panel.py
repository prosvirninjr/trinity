import numpy as np
import scipy as sp
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from core.ooh.logic import Geo
from core.ooh.schema import SMethod


class Construction(BaseModel):
    """Конструкция панели."""

    advertiser: Annotated[str, Field(title='Рекламодатель')]
    operator: Annotated[str | None, Field(title='Оператор')]
    format: Annotated[str, Field(title='Формат')]
    size: Annotated[str | None, Field(title='Размер')]
    side: Annotated[str | None, Field(title='Сторона')]
    latitude: Annotated[float, Field(title='Широта')]
    longitude: Annotated[float, Field(title='Долгота')]
    base_price: Annotated[float, Field(title='Базовая стоимость.')]
    weight: Annotated[float, Field(default=1.0, title='Вес конструкции (удаленность).')]

    @property
    def description(self) -> str:
        # Если размер не указан, используем placeholder '-'.
        size = '-' if self.size is None else self.size
        return f'{self.format} {size}'


class Panel:
    def __init__(self, constructions: list[Construction] = []) -> None:
        self.constructions = constructions

    def filter_panel(self) -> None:
        """Оставляет конструкции с уникальными комбинациями рекламодателей и координат."""
        unique_constructions: list[Construction] = []

        for construction in self.constructions:
            # Флаг, указывающий, является ли текущая конструкция дубликатом.
            is_duplicate = False

            # Сравнение текущей конструкции с уже найденными уникальными конструкциями.
            for unique_construction in unique_constructions:
                # Проверка, совпадает ли рекламодатель.
                if construction.advertiser == unique_construction.advertiser:
                    # Проверка, находятся ли конструкции близко друг к другу (в радиусе 10 метров).
                    if Geo.is_close(
                        lat_1=construction.latitude,
                        lon_1=construction.longitude,
                        lat_2=unique_construction.latitude,
                        lon_2=unique_construction.longitude,
                        radius=0.01,  # 10 метров.
                    ):
                        # Если рекламодатель совпадает и координаты близки, пометить как дубликат.
                        is_duplicate = True
                        # Прервать внутренний цикл, так как дубликат найден.
                        break

            # Если конструкция не является дубликатом, добавить ее в список уникальных.
            if not is_duplicate:
                unique_constructions.append(construction)

        self.constructions = unique_constructions

    def is_empty(self) -> bool:
        """
        Проверяет наличие конструкций в панели.

        Returns:
            bool: True, если панель пуста, иначе False.
        """
        return not self.constructions

    def size(self) -> int:
        """
        Возвращает количество конструкций в панели.

        Returns:
            int: Количество конструкций в панели.
        """
        return len(self.constructions)

    def _calc_mean_price(self) -> float:
        """
        Вычисляет среднюю стоимость конструкции в панели.

        Returns:
            Средняя стоимость конструкции в панели.
        """
        # Если панель пуста, возвращаем 0.
        if self.is_empty():
            return 0.0

        prices: list[float] = [c.base_price for c in self.constructions]

        return float(np.mean(prices))

    def _calc_weighted_mean_price(self) -> float:
        """
        Вычисляет средневзвешенную стоимость конструкции в панели.

        Returns:
            Средневзвешенная стоимость конструкции в панели.
        """
        # Если панель пуста, возвращаем 0.
        if self.is_empty():
            return 0.0

        prices: list[float] = [c.base_price for c in self.constructions]
        weights: list[float] = [c.weight for c in self.constructions]

        return float(np.average(prices, weights=weights))

    def _calc_trimmed_mean_price(self) -> float:
        """
        Вычисляет усеченную среднюю стоимость конструкции в панели.

        Returns:
            float: Усеченная средняя стоимость конструкции в панели.
        """
        # Если панель пуста, возвращаем 0.
        if self.is_empty():
            return 0.0

        prices: list[float] = [c.base_price for c in self.constructions]

        return sp.stats.trim_mean(prices, proportiontocut=0.1)  # 10% отрезаем с каждой стороны.

    def _calc_median_price(self) -> float:
        """
        Вычисляет медианную стоимость конструкции в панели.

        Returns:
            float: Медианная стоимость конструкции в панели.
        """
        # Если панель пуста, возвращаем 0.
        if self.is_empty():
            return 0.0

        prices: list[float] = [c.base_price for c in self.constructions]

        return float(np.median(prices))

    def calc_base_price(self, method: str = SMethod.mean, n: int = 0) -> float:
        """
        Вычисляет базовую стоимость конструкции в панели.

        Args:
            method (str, optional): Метод вычисления базовой стоимости.
            n (int, optional): Количество знаков после запятой для округления.

        Returns:
            float: Базовая стоимость конструкции в панели.
        """
        if method == SMethod.mean:
            return round(self._calc_mean_price(), n)
        elif method == SMethod.weighted_mean:
            return round(self._calc_weighted_mean_price(), n)
        elif method == SMethod.trimmed_mean:
            return round(self._calc_trimmed_mean_price(), n)
        elif method == SMethod.median:
            return round(self._calc_median_price(), n)

        raise ValueError(f'Метод вычисления базовой стоимости не поддерживается. [{method}]')

    def get_advertisers(self, as_string: bool = False) -> list[str] | str:
        """
        Возвращает уникальных рекламодателей из конструкции.

        Args:
            as_string (bool, optional): Если True, возвращает строку с рекламодателями, иначе список.

        Returns:
            list[str] | str: Уникальные рекламодатели.
        """
        unique_advertisers = sorted(list({c.advertiser for c in self.constructions}))

        if as_string:
            return ', '.join(unique_advertisers)

        return unique_advertisers

    def get_operators(self, as_string: bool = False) -> list[str] | str:
        """
        Возвращает уникальных операторов из конструкции.

        Args:
            as_string (bool, optional): Если True, возвращает строку с операторами, иначе список.

        Returns:
            list[str] | str: Уникальные операторы.
        """
        unique_operators = sorted(list({c.operator for c in self.constructions if c.operator}))

        if as_string:
            return ', '.join(unique_operators)

        return unique_operators

    def get_constructions(self, as_string: bool = False) -> list[str] | str:
        """
        Возвращает уникальные конструкции из панели.
        Args:
            as_string (bool, optional): Если True, возвращает строку с конструкциями, иначе список.
        Returns:
            list[str] | str: Уникальные конструкции.
        """

        unique_constructions = sorted(list({c.description for c in self.constructions}))

        if as_string:
            return ', '.join(unique_constructions)

        return unique_constructions

    def _get_attribute_shares(
        self, attribute_name: str, as_string: bool = False, top_n: int | None = None, n: int = 1
    ) -> dict[str, float] | str:
        """
        Вспомогательный метод для расчета долей по заданному атрибуту конструкций.

        Args:
            attribute_name (str): Имя атрибута.
            as_string (bool, optional): Вернуть результат в виде строки. Defaults to False.
            top_n (int | None, optional): Ограничить вывод топ-N элементами, остальные сгруппировать в 'Остальные'.
            n (int, optional): Количество знаков после запятой для округления.

        Returns:
            dict[str, float] | str: Словарь с долями или строка.
        """
        counts: dict[str, int] = {}
        total: int = 0

        for c in self.constructions:
            value: str | None = getattr(c, attribute_name)

            if value is not None:
                counts[value] = counts.get(value, 0) + 1
                total += 1

        result_dict: dict[str, float] = {}

        if total > 0:
            sorted_items: list[tuple[str, int]] = sorted(counts.items(), key=lambda item: item[1], reverse=True)

            if top_n is not None and top_n < len(sorted_items):
                top_items: list[tuple[str, int]] = sorted_items[:top_n]
                rest_count: int = sum(count for _, count in sorted_items[top_n:])

                if rest_count > 0:
                    top_items.append(('Остальные', rest_count))

                sorted_items = top_items

            result_dict = {name: round((count / total) * 100, n) for name, count in sorted_items}

        if as_string:
            return ', '.join(f'{name}: {share:.{n}f}%' for name, share in result_dict.items())

        return result_dict

    def get_operator_shares(
        self, as_string: bool = False, top_n: int | None = None, n: int = 2
    ) -> dict[str, float] | str:
        """
        Возвращает доли операторов в панели.

        Args:
            as_string (bool, optional): Вернуть результат в виде строки. Defaults to False.
            top_n (int | None, optional): Ограничить вывод топ-N операторами, остальные сгруппировать в 'Остальные'.
            n (int, optional): Количество знаков после запятой для округления. Defaults to 2.

        Returns:
            dict[str, float] | str: Словарь с долями операторов или строка.
        """
        return self._get_attribute_shares('operator', as_string, top_n, n)

    def get_advertiser_shares(
        self, as_string: bool = False, top_n: int | None = None, n: int = 2
    ) -> dict[str, float] | str:
        """
        Возвращает доли рекламодателей в панели.

        Args:
            as_string (bool, optional): Вернуть результат в виде строки. Defaults to False.
            top_n (int | None, optional): Ограничить вывод топ-N рекламодателями, остальные сгруппировать в 'Остальные'.
            n (int, optional): Количество знаков после запятой для округления. Defaults to 2.

        Returns:
            dict[str, float] | str: Словарь с долями рекламодателей или строка.
        """
        return self._get_attribute_shares('advertiser', as_string, top_n, n)
