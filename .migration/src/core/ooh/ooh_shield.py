import math
from dataclasses import fields
from datetime import datetime
from typing import Any, Callable

import polars as pl

from core.ooh.exceptions import OOHLogicError
from core.ooh.schema import OOHColumn


def check_ooh_template(df: pl.DataFrame) -> None:
    """
    Логическая валидация OOH-шаблона.
    Пробегает по всем строкам и вызывает набор _check_* функций,
    собирая все ошибки. В случае наличия поднимает OOHLogicError.
    """

    # Определяем для каждой проверки функцию и список полей (tech_name)
    validators: list[tuple[Callable[..., Any], list[str]]] = [
        (
            _check_period,
            [
                OOHColumn.month.tech_name,
                OOHColumn.start_date.tech_name,
                OOHColumn.end_date.tech_name,
            ],
        ),
        (
            _check_digital_params,
            [
                OOHColumn.spot_duration.tech_name,
                OOHColumn.spots_per_block.tech_name,
                OOHColumn.block_duration.tech_name,
                OOHColumn.spots_per_day.tech_name,
                OOHColumn.hours_per_day.tech_name,
            ],
        ),
        (
            _check_placement_prices_logic,
            [
                OOHColumn.placement_price_net.tech_name,
                OOHColumn.placement_price_list.tech_name,
                OOHColumn.placement_discount.tech_name,
            ],
        ),
        (
            _check_placement_vat_logic,
            [
                OOHColumn.placement_price_with_vat.tech_name,
                OOHColumn.placement_price_net.tech_name,
                OOHColumn.placement_vat.tech_name,
            ],
        ),
        (
            _check_production_total_logic,
            [
                OOHColumn.production_price_net_total.tech_name,
                OOHColumn.production_price_net.tech_name,
                OOHColumn.production_quantity_format.tech_name,
            ],
        ),
        (
            _check_production_vat_logic,
            [
                OOHColumn.production_price_total_with_vat.tech_name,
                OOHColumn.production_price_net_total.tech_name,
                OOHColumn.production_vat.tech_name,
            ],
        ),
        (
            _check_main_installation_vat_logic,
            [
                OOHColumn.main_installation_price_with_vat.tech_name,
                OOHColumn.main_installation_price_net.tech_name,
                OOHColumn.main_installation_vat.tech_name,
            ],
        ),
        (
            _check_extra_installation_total_logic,
            [
                OOHColumn.extra_installation_price_net_total.tech_name,
                OOHColumn.extra_installation_price_net.tech_name,
                OOHColumn.extra_installation_quantity.tech_name,
            ],
        ),
        (
            _check_extra_installation_vat_logic,
            [
                OOHColumn.extra_installation_price_total_with_vat.tech_name,
                OOHColumn.extra_installation_price_net_total.tech_name,
                OOHColumn.extra_installation_vat.tech_name,
            ],
        ),
        (
            _check_delivery_vat_logic,
            [
                OOHColumn.delivery_price_with_vat.tech_name,
                OOHColumn.delivery_price_net.tech_name,
                OOHColumn.delivery_vat.tech_name,
            ],
        ),
        (
            _check_total_price_net_logic,
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
            _check_total_price_with_vat_logic,
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

    exceptions: list[dict[str, Any]] = []

    for i, r in enumerate(df.iter_rows(named=True), start=1):
        for fn, cols in validators:
            try:
                fn(*(r[col] for col in cols))
            except ValueError as e:
                exceptions.append({'row': i, 'exception': e})
                continue

    if exceptions:
        raise OOHLogicError('Ошибки валидации данных', exceptions)

    return None


def _check_period(month: int, start_date: datetime, end_date: datetime) -> None:
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


def _check_digital_params(
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


def _check_placement_prices_logic(
    placement_price_net: float,
    placement_price_list: float,
    placement_discount: float,
) -> None:
    expected_price_net = placement_price_list * (1.0 - placement_discount)
    if not math.isclose(placement_price_net, expected_price_net, rel_tol=0.01):
        raise ValueError('Стоимость размещения без НДС не соответствует расчетной.')


def _check_placement_vat_logic(
    placement_price_with_vat: float,
    placement_price_net: float,
    placement_vat: float,
) -> None:
    expected_price_with_vat = placement_price_net * (1.0 + placement_vat)
    if not math.isclose(placement_price_with_vat, expected_price_with_vat, rel_tol=0.01):
        raise ValueError('Стоимость размещения с НДС не соответствует расчетной.')


def _check_production_total_logic(
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


def _check_production_vat_logic(
    production_price_total_with_vat: float,
    production_price_net_total: float,
    production_vat: float,
) -> None:
    expected_total_with_vat = production_price_net_total * (1.0 + production_vat)
    if not math.isclose(production_price_total_with_vat, expected_total_with_vat, rel_tol=0.01):
        raise ValueError('Стоимость производства (с НДС) всего формата не соответствует расчетной.')


def _check_main_installation_vat_logic(
    main_installation_price_with_vat: float,
    main_installation_price_net: float,
    main_installation_vat: float,
) -> None:
    expected_price_with_vat = main_installation_price_net * (1.0 + main_installation_vat)
    if not math.isclose(main_installation_price_with_vat, expected_price_with_vat, rel_tol=0.01):
        raise ValueError('Стоимость основного монтажа с НДС не соответствует расчетной.')


def _check_extra_installation_total_logic(
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


def _check_extra_installation_vat_logic(
    extra_installation_price_total_with_vat: float,
    extra_installation_price_net_total: float,
    extra_installation_vat: float,
) -> None:
    expected_total_with_vat = extra_installation_price_net_total * (1.0 + extra_installation_vat)
    if not math.isclose(extra_installation_price_total_with_vat, expected_total_with_vat, rel_tol=0.01):
        raise ValueError('Стоимость доп. монтажа (с НДС) итого не соответствует расчетной.')


def _check_delivery_vat_logic(
    delivery_price_with_vat: float,
    delivery_price_net: float,
    delivery_vat: float,
) -> None:
    expected_price_with_vat = delivery_price_net * (1.0 + delivery_vat)
    if not math.isclose(delivery_price_with_vat, expected_price_with_vat, rel_tol=0.01):
        raise ValueError('Стоимость доставки с НДС не соответствует расчетной.')


def _check_total_price_net_logic(
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


def _check_total_price_with_vat_logic(
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


def v_errors_json(result: list[dict[str, object]]) -> list[dict[str, object]]:  # type: ignore
    """Преобразует список ошибок в формат, удобный для чтения."""
    errors: list[dict[str, object]] = []
    cols = {f.name: getattr(OOHColumn, f.name).orig_name for f in fields(OOHColumn)} # type: ignore

    for item in result:
        row = item['row']
        exception = item['exception']
        for error in exception.errors():  # type: ignore
            column = error['loc'][0]  # type: ignore
            message = error['msg']  # type: ignore

            column = cols.get(column, column)  # type: ignore
            message = message.removeprefix('Value error, ')  # type: ignore

            errors.append(
                {
                    'Строка': int(row),  # type: ignore
                    'Столбец': str(column),
                    'Ошибка': str(message),
                }
            )

    return errors


def l_errors_json(result: list[dict[str, object]]) -> list[dict[str, object]]:  # type: ignore
    errors: list[dict[str, object]] = []

    for item in result:
        row = item['row']
        exception = item['exception']
        message = str(exception)

        errors.append(
            {
                'Строка': int(row),  # type: ignore
                'Ошибка': message,
            }
        )

    return errors
