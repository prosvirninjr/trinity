import logging
import math
from collections.abc import Callable
from dataclasses import dataclass, fields
from datetime import date, datetime
from typing import Any

import polars as pl
from pydantic import ValidationError

from core.ooh.exceptions import OOHDataError, OOHHeaderError, OOHLogicError
from core.ooh.schema import OOHColumn, OOHRecord
from core.utils.tools import TextTools

log = logging.getLogger(__name__)


@dataclass
class Errors:
    """Контейнер для хранения ошибок при валидации OOH-шаблона."""

    template: OOHHeaderError | None = None
    data: OOHDataError | None = None
    logic: OOHLogicError | None = None


class Guardian:
    """
    Валидатор OOH-шаблона: проверяет заголовок, данные и логику.
    """

    def __init__(
        self,
        template: pl.DataFrame,
        schema: Any,
        validators: list[tuple[Callable, list[str]]],
    ) -> None:
        """
        Инициализирует валидатор.

        Args:
            template (pl.DataFrame): исходный шаблон.
            schema (Any): Pydantic-схема колонок.
            validators (list[tuple[Callable, list[str]]]):
                валидаторы логики и их столбцы.
        """
        self.template = template
        self.schema = schema
        self.validators = validators
        self.df: pl.DataFrame | None = None
        self.errors: Errors = Errors()

    def _valid_header(self) -> None:
        """
        Проверяет наличие обязательных столбцов.

        Raises:
            OOHTemplateError: если отсутствуют колонки.
        """
        expected = [f.default.orig_name for f in fields(self.schema)]  # type: ignore

        log.debug(f'Ожидаемые колонки: {expected}')
        log.debug(f'Фактические колонки: {self.template.columns}')

        missing = list(set(expected) - set(map(TextTools.to_clean_string, self.template.columns)))

        if missing:
            raise OOHHeaderError('Отсутствуют обязательные столбцы в шаблоне.', missing)

    def _valid_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Валидирует каждую строку через Pydantic и собирает новый DataFrame.

        Args:
            df (pl.DataFrame): копия исходного шаблона.

        Returns:
            pl.DataFrame: DataFrame с корректными строками и типами.

        Raises:
            OOHDataError: при ошибках валидации значений.
        """
        # 1. Переименовать колонки в технические
        df.columns = [f.default.tech_name for f in fields(self.schema)]  # type: ignore

        valid_rows: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        # 2. Проверить каждую строку
        for idx, row in enumerate(df.iter_rows(named=True), start=1):
            try:
                valid_rows.append(OOHRecord(**row).model_dump())
            except ValidationError as e:
                errors.append({'idx': idx, 'exception': e})

        if errors:
            raise OOHDataError('Ошибки валидации данных', errors)

        # 3. Построить DataFrame с правильными типами
        TYPE_MAPPING = {
            int: pl.Int64,
            float: pl.Float64,
            str: pl.String,
            bool: pl.Boolean,
            date: pl.Date,
            datetime: pl.Datetime,
        }
        schema = {item.name: TYPE_MAPPING[getattr(OOHColumn, item.name).type_] for item in fields(OOHColumn)}
        return pl.DataFrame(valid_rows, schema=schema)

    def _valid_logic(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Проверяет логические зависимости между столбцами.

        Args:
            df (pl.DataFrame): DataFrame после проверки данных.

        Returns:
            pl.DataFrame: тот же DataFrame при успешных проверках.

        Raises:
            OOHLogicError: при логических ошибках.
        """
        errors: list[dict[str, Any]] = []

        for idx, row in enumerate(df.iter_rows(named=True), start=1):
            for fn, cols in self.validators:
                try:
                    fn(*(row[col] for col in cols))
                except ValueError as e:
                    errors.append({'idx': idx, 'exception': e})

        if errors:
            raise OOHLogicError('Ошибки логики данных', errors)
        return df

    def validate(self) -> None:
        """
        Запускает все этапы валидации: header, data, logic.
        Результат записывается в self.df или self.errors.
        """
        try:
            self._valid_header()
        except OOHHeaderError as e:
            self.errors.template = e
            return

        try:
            df = self._valid_data(self.template.clone())
        except OOHDataError as e:
            self.errors.data = e
            return

        try:
            df = self._valid_logic(df)
        except OOHLogicError as e:
            self.errors.logic = e
            return

        self.df = df

    def is_valid(self) -> bool:
        """
        Проверяет, прошла ли валидация без ошибок.

        Returns:
            bool: True, если ошибок нет.
        """
        return self.df is not None

    def _h_errors_json(self, result: list[str]) -> list[dict[str, Any]]:
        """
        Формирует человекочитаемый список ошибок заголовка.

        Args:
            result (list[dict]): ошибки из OOHHeaderError.

        Returns:
            list[dict]: словари с ключами 'Столбец', 'Ошибка'.
        """
        return [{'Столбец': item, 'Ошибка': 'Столбец отсутствует в шаблоне.'} for item in result]

    def _d_errors_json(self, result: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Формирует человекочитаемый список ошибок данных.

        Args:
            result (list[dict]): ошибки из OOHDataError.

        Returns:
            list[dict]: словари с ключами 'Строка', 'Столбец', 'Ошибка'.
        """
        cols = {f.name: getattr(OOHColumn, f.name).orig_name for f in fields(OOHColumn)}
        out: list[dict[str, Any]] = []

        for item in result:
            idx = item['idx']
            exc: ValidationError = item['exception']  # type: ignore
            for err in exc.errors():  # type: ignore
                col, msg = err['loc'][0], err['msg'].removeprefix('Value error, ')
                out.append(
                    {
                        'Строка': idx,
                        'Столбец': cols.get(col, col),  # type: ignore
                        'Ошибка': msg,
                    }
                )

        return out

    def _l_errors_json(self, result: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Формирует человекочитаемый список логических ошибок.

        Args:
            result (list[dict]): ошибки из OOHLogicError.

        Returns:
            list[dict]: словари с ключами 'Строка', 'Ошибка'.
        """
        return [{'Строка': item['idx'], 'Ошибка': str(item['exception'])} for item in result]

    def get_report(self):
        """
        Возвращает отчет о валидации.

        Returns:
            str: сообщение об ошибке шаблона.
            list[dict]: ошибки данных или логики.

        Raises:
            ValueError: если валидация не завершена или отсутствуют ошибки.
        """
        if self.errors.template is not None:
            return self._h_errors_json(self.errors.template.field)  # type: ignore
        if self.errors.data is not None:
            return self._d_errors_json(self.errors.data.field)  # type: ignore
        if self.errors.logic is not None:
            return self._l_errors_json(self.errors.logic.field)  # type: ignore

        raise ValueError('Валидация не завершена или отсутствуют ошибки в шаблоне.')

    def get_valid_df(self) -> pl.DataFrame:
        """
        Возвращает валидированный DataFrame.

        Returns:
            pl.DataFrame: валидированный DataFrame.

        Raises:
            ValueError: если валидация не завершена или есть ошибки.
        """
        if self.df is None:
            raise ValueError('Валидация не завершена или есть ошибки в шаблоне.')

        return self.df


# NOTE: Валидаторы логики OOH-шаблона.
def _val_period(month: int, start_date: datetime, end_date: datetime) -> None:
    if start_date > end_date:
        raise ValueError('Дата начала аренды не может быть позже даты окончания аренды.')
    if start_date.month != end_date.month:
        raise ValueError('Месяц даты начала аренды не соответствует месяцу даты окончания аренды.')
    if start_date.year != end_date.year:
        raise ValueError('Год даты начала аренды не соответствует году даты окончания аренды.')
    if start_date.month != month:
        raise ValueError('Месяц даты начала аренды не соответствует месяцу аренды.')
    if end_date.month != month:
        raise ValueError('Месяц даты окончания аренды не соответствует месяцу аренды.')


def _val_digital(
    spot_duration: float | None,
    spots_per_block: float | None,
    block_duration: float | None,
    spots_per_day: float | None,
    hours_per_day: float | None,
) -> None:
    digital_params = [spot_duration, spots_per_block, block_duration, spots_per_day, hours_per_day]
    if all(p is None for p in digital_params):
        return
    if any(p is not None for p in digital_params) and not all(p is not None for p in digital_params):
        raise ValueError('Для цифрового формата должны быть заполнены все параметры.')

    assert spot_duration is not None
    assert spots_per_block is not None
    assert block_duration is not None

    _spot_duration = float(spot_duration)
    _spots_per_block = float(spots_per_block)
    _block_duration = float(block_duration)
    if _spot_duration > _block_duration:
        raise ValueError('Длительность ролика не может быть больше длительности блока.')
    if (_spot_duration * _spots_per_block) > _block_duration:
        if not math.isclose(_spot_duration * _spots_per_block, _block_duration, rel_tol=1e-9):
            raise ValueError('Общий хронометраж роликов с учетом выходов в блоке превышает длительность блока.')


def _val_placement_prices(
    placement_price_net: float,
    placement_price_list: float,
    placement_discount: float,
) -> None:
    expected_price_net = placement_price_list * (1.0 - placement_discount)
    if not math.isclose(placement_price_net, expected_price_net, rel_tol=0.01):
        raise ValueError('Стоимость размещения без НДС не соответствует расчетной.')


def _val_placement_vat(
    placement_price_with_vat: float,
    placement_price_net: float,
    placement_vat: float,
) -> None:
    expected_price_with_vat = placement_price_net * (1.0 + placement_vat)
    if not math.isclose(placement_price_with_vat, expected_price_with_vat, rel_tol=0.01):
        raise ValueError('Стоимость размещения с НДС не соответствует расчетной.')


def _val_production_total(
    production_price_net_total: float,
    production_price_net: float,
    production_quantity: int,
) -> None:
    expected_total = production_price_net * production_quantity
    if production_price_net == 0 or production_quantity == 0:
        if not math.isclose(production_price_net_total, 0.0, abs_tol=1e-9):
            raise ValueError(
                'Стоимость производства (без НДС) всего формата должна быть 0, если цена или количество = 0.'
            )
    elif not math.isclose(production_price_net_total, expected_total, rel_tol=0.01):
        raise ValueError('Стоимость производства (без НДС) всего формата не соответствует расчетной.')


def _val_production_vat(
    production_price_total_with_vat: float,
    production_price_net_total: float,
    production_vat: float,
) -> None:
    expected_total_with_vat = production_price_net_total * (1.0 + production_vat)
    if not math.isclose(production_price_total_with_vat, expected_total_with_vat, rel_tol=0.01):
        raise ValueError('Стоимость производства (с НДС) всего формата не соответствует расчетной.')


def _val_main_installation_vat(
    main_installation_price_with_vat: float,
    main_installation_price_net: float,
    main_installation_vat: float,
) -> None:
    expected_price_with_vat = main_installation_price_net * (1.0 + main_installation_vat)
    if not math.isclose(main_installation_price_with_vat, expected_price_with_vat, rel_tol=0.01):
        raise ValueError('Стоимость основного монтажа с НДС не соответствует расчетной.')


def _val_extra_installation_total(
    extra_installation_price_net_total: float,
    extra_installation_price_net: float,
    extra_installation_quantity: int,
) -> None:
    expected_total = extra_installation_price_net * extra_installation_quantity
    if extra_installation_price_net == 0 or extra_installation_quantity == 0:
        if not math.isclose(extra_installation_price_net_total, 0.0, abs_tol=1e-9):
            raise ValueError('Стоимость доп. монтажа (без НДС) итого должна быть 0, если цена или количество = 0.')
    elif not math.isclose(extra_installation_price_net_total, expected_total, rel_tol=0.01):
        raise ValueError('Стоимость доп. монтажа (без НДС) итого не соответствует расчетной.')


def _val_extra_installation_vat(
    extra_installation_price_total_with_vat: float,
    extra_installation_price_net_total: float,
    extra_installation_vat: float,
) -> None:
    expected_total_with_vat = extra_installation_price_net_total * (1.0 + extra_installation_vat)
    if not math.isclose(extra_installation_price_total_with_vat, expected_total_with_vat, rel_tol=0.01):
        raise ValueError('Стоимость доп. монтажа (с НДС) итого не соответствует расчетной.')


def _val_delivery_vat(
    delivery_price_with_vat: float,
    delivery_price_net: float,
    delivery_vat: float,
) -> None:
    expected_price_with_vat = delivery_price_net * (1.0 + delivery_vat)
    if not math.isclose(delivery_price_with_vat, expected_price_with_vat, rel_tol=0.01):
        raise ValueError('Стоимость доставки с НДС не соответствует расчетной.')


def _val_total_price_net(
    price_net_total: float,
    placement_price_net: float,
    production_price_net_total: float,
    main_installation_price_net: float,
    extra_installation_price_net_total: float,
    delivery_price_net: float,
) -> None:
    components = [
        placement_price_net,
        production_price_net_total,
        main_installation_price_net,
        extra_installation_price_net_total,
        delivery_price_net,
    ]
    expected_total_net = sum(float(comp) for comp in components)
    if not math.isclose(price_net_total, expected_total_net, rel_tol=0.01):
        raise ValueError('Итого стоимость формата (без НДС) не соответствует сумме компонентов.')


def _val_total_price_with_vat(
    price_total_with_vat: float,
    placement_price_with_vat: float,
    production_price_total_with_vat: float,
    main_installation_price_with_vat: float,
    extra_installation_price_total_with_vat: float,
    delivery_price_with_vat: float,
) -> None:
    components_vat = [
        placement_price_with_vat,
        production_price_total_with_vat,
        main_installation_price_with_vat,
        extra_installation_price_total_with_vat,
        delivery_price_with_vat,
    ]
    expected_total_with_vat = sum(float(comp) for comp in components_vat)
    if not math.isclose(price_total_with_vat, expected_total_with_vat, rel_tol=0.01):
        raise ValueError('Итого стоимость формата (с НДС) не соответствует сумме компонентов.')


# Список валидаторов логики OOH-шаблона.
validators: list[tuple[Callable, list[str]]] = [
    (
        _val_period,
        [
            OOHColumn.month.tech_name,
            OOHColumn.start_date.tech_name,
            OOHColumn.end_date.tech_name,
        ],
    ),
    (
        _val_digital,
        [
            OOHColumn.spot_duration.tech_name,
            OOHColumn.spots_per_block.tech_name,
            OOHColumn.block_duration.tech_name,
            OOHColumn.spots_per_day.tech_name,
            OOHColumn.hours_per_day.tech_name,
        ],
    ),
    (
        _val_placement_prices,
        [
            OOHColumn.placement_price_net.tech_name,
            OOHColumn.placement_price_list.tech_name,
            OOHColumn.placement_discount.tech_name,
        ],
    ),
    (
        _val_placement_vat,
        [
            OOHColumn.placement_price_with_vat.tech_name,
            OOHColumn.placement_price_net.tech_name,
            OOHColumn.placement_vat.tech_name,
        ],
    ),
    (
        _val_production_total,
        [
            OOHColumn.production_price_net_total.tech_name,
            OOHColumn.production_price_net.tech_name,
            OOHColumn.production_quantity_format.tech_name,
        ],
    ),
    (
        _val_production_vat,
        [
            OOHColumn.production_price_total_with_vat.tech_name,
            OOHColumn.production_price_net_total.tech_name,
            OOHColumn.production_vat.tech_name,
        ],
    ),
    (
        _val_main_installation_vat,
        [
            OOHColumn.main_installation_price_with_vat.tech_name,
            OOHColumn.main_installation_price_net.tech_name,
            OOHColumn.main_installation_vat.tech_name,
        ],
    ),
    (
        _val_extra_installation_total,
        [
            OOHColumn.extra_installation_price_net_total.tech_name,
            OOHColumn.extra_installation_price_net.tech_name,
            OOHColumn.extra_installation_quantity.tech_name,
        ],
    ),
    (
        _val_extra_installation_vat,
        [
            OOHColumn.extra_installation_price_total_with_vat.tech_name,
            OOHColumn.extra_installation_price_net_total.tech_name,
            OOHColumn.extra_installation_vat.tech_name,
        ],
    ),
    (
        _val_delivery_vat,
        [
            OOHColumn.delivery_price_with_vat.tech_name,
            OOHColumn.delivery_price_net.tech_name,
            OOHColumn.delivery_vat.tech_name,
        ],
    ),
    (
        _val_total_price_net,
        [
            OOHColumn.price_net_total_format.tech_name,
            OOHColumn.placement_price_net.tech_name,
            OOHColumn.production_price_net_total.tech_name,
            OOHColumn.main_installation_price_net.tech_name,
            OOHColumn.extra_installation_price_net_total.tech_name,
            OOHColumn.delivery_price_net.tech_name,
        ],
    ),
    (
        _val_total_price_with_vat,
        [
            OOHColumn.price_total_with_vat_format.tech_name,
            OOHColumn.placement_price_with_vat.tech_name,
            OOHColumn.production_price_total_with_vat.tech_name,
            OOHColumn.main_installation_price_with_vat.tech_name,
            OOHColumn.extra_installation_price_total_with_vat.tech_name,
            OOHColumn.delivery_price_with_vat.tech_name,
        ],
    ),
]
