import logging
from dataclasses import fields
from datetime import date, datetime
from typing import Sequence

import polars as pl
from polars import DataFrame
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.attributes import flag_modified
from sqlmodel import Session, select

from core.ooh.schema import OOHColumn
from core.radio.models import RadioColumn
from orm.sql_tables import OOH, Employee, Radio

log = logging.getLogger(__name__)


# NOTE: SELECT-запросы.
def select_employee(engine, tg_id: int | None = None) -> Employee | Sequence[Employee]:
    """
    Возвращает одного или нескольких сотрудников.

    Args:
        engine (Engine): SQLAlchemy engine.
        tg_id (int | None): Telegram id сотрудника (по умолчанию None).

    Returns:
        Employee | Sequence[Employee]: Один или несколько сотрудников.

    Raises:
        NoResultFound: Если не найдено ни одной записи.
    """
    with Session(engine) as session:
        if tg_id:
            statement = select(Employee).where(Employee.tg_id == tg_id)

            try:
                result = session.exec(statement).one()
            except NoResultFound:
                log.exception('Не удалось найти сотрудника с указанным Telegram ID.')
                raise
            else:
                return result

        statement = select(Employee)
        result = session.exec(statement).all()

        if not result:
            log.error('Не удалось найти сотрудников.')
            raise NoResultFound

        return result


def _oohs_to_polars(oohs: Sequence[OOH]) -> pl.DataFrame:
    """
    Преобразует набор OOH объектов в polars DataFrame (vstack).
    """
    TYPE_MAPPING = {
        int: pl.Int64,
        float: pl.Float64,
        str: pl.String,
        bool: pl.Boolean,
        date: pl.Date,
        datetime: pl.Datetime,
    }

    # Строим схему на основании описания колонок в OOHColumn.
    schema = {fld.name: TYPE_MAPPING[getattr(OOHColumn, fld.name).type_] for fld in fields(OOHColumn)}  # type: ignore

    dfs = [pl.DataFrame(ooh.template, schema=schema) for ooh in oohs]

    return pl.concat(dfs)


def _radios_to_polars(radios: Sequence[Radio]) -> pl.DataFrame:
    """
    Преобразует набор Radio объектов в polars DataFrame (vstack).
    """
    TYPE_MAPPING = {
        int: pl.Int64,
        float: pl.Float64,
        str: pl.String,
        bool: pl.Boolean,
        date: pl.Date,
        datetime: pl.Datetime,
    }

    # Строим схему, начиная с 'advertiser', чтобы он был первым.
    schema = {'advertiser': pl.String}

    radio_schema = {fld.name: TYPE_MAPPING[getattr(RadioColumn, fld.name).type_] for fld in fields(RadioColumn)}

    schema.update(radio_schema)

    dfs = [pl.DataFrame(radio.template, schema=schema) for radio in radios]

    return pl.concat(dfs)


def select_ooh(engine, as_polars: bool = False) -> pl.DataFrame | Sequence[OOH]:
    """
    Возвращает одину или несколько записей из таблицы OOH.

    Args:
        engine (Engine): SQLAlchemy engine.

    Returns:
        pl.DataFrame | Sequence[OOH]: Одина или несколько записей из таблицы OOH.

    Raises:
        NoResultFound: Если не найдено ни одной записи.
    """
    with Session(engine) as session:
        statement = select(OOH)

        result = session.exec(statement).all()

        if not result:
            log.error('Не удалось найти шаблоны за указанный год.')
            raise NoResultFound

        if as_polars:
            return _oohs_to_polars(result)

        return result


def select_radio(engine, as_polars: bool = False) -> pl.DataFrame | Sequence[Radio]:
    """
    Возвращает одину или несколько записей из таблицы Radio.

    Args:
        engine (Engine): SQLAlchemy engine.

    Returns:
        pl.DataFrame | Sequence[Radio]: Одина или несколько записей из таблицы Radio.

    Raises:
        NoResultFound: Если не найдено ни одной записи.
    """
    with Session(engine) as session:
        statement = select(Radio)

        result = session.exec(statement).all()

        if not result:
            log.error('Не удалось найти шаблоны за указанный год.')
            raise NoResultFound

        if as_polars:
            return _radios_to_polars(result)

        return result


# NOTE: UPDATE-запросы.
def update_employee(
    engine, tg_id: int, username: str | None = None, is_admin: bool | None = None, settings: dict | None = None
) -> None:
    """
    Обновляет настройки сотрудника.

    Args:
        engine (Engine): SQLAlchemy engine.
        tg_id (int): Telegram id сотрудника.
        settings (ESettings): Объект настроек сотрудника.

    Raises:
        NoResultFound: Если не найдено ни одной записи.
    """
    with Session(engine) as session:
        statement = select(Employee).where(Employee.tg_id == tg_id)

        try:
            employee = session.exec(statement).one()
        except NoResultFound:
            log.exception('Не удалось найти сотрудника с указанным Telegram ID.')
            raise

        if username is not None:
            employee.username = username
        if is_admin is not None:
            employee.is_admin = is_admin
        if settings is not None:
            employee.settings = settings
            flag_modified(employee, 'settings')

        session.add(employee)
        session.commit()


# NOTE: INSERT-запросы.
def insert_employee(engine, tg_id: int, username: str, is_admin: bool, settings: dict) -> None:
    with Session(engine) as session:
        session.add(Employee(tg_id=tg_id, username=username, is_admin=is_admin, settings=settings))
        session.commit()


def insert_ooh(engine, template: dict | DataFrame) -> None:
    """Вставляет валидный шаблон (необработанный) OOH в базу данных."""
    if isinstance(template, DataFrame):
        # Преобразуем DataFrame в словарь.
        template = template.to_dict(as_series=False)

    # JSON не поддерживает datetime, поэтому преобразуем его в ISO формат.
    template = {
        col: [v.isoformat() if isinstance(v, (date, datetime)) else v for v in vals] for col, vals in template.items()
    }

    with Session(engine) as session:
        session.add(OOH(template=template))
        session.commit()


# NOTE: В шаблоне Radio не используется столбец 'Рекламодатель', поэтому необходимо передавать его отдельно.
def insert_radio(engine, advertiser: str, template: DataFrame) -> None:
    template = template.with_columns(pl.lit(advertiser).alias('advertiser'))
    _template = template.to_dict(as_series=False)

    # JSON не поддерживает datetime, поэтому преобразуем его в ISO формат.
    document = {
        col: [v.isoformat() if isinstance(v, (date, datetime)) else v for v in vals] for col, vals in _template.items()
    }

    with Session(engine) as session:
        session.add(Radio(template=document))
        session.commit()
