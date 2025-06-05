from datetime import date

from aiogram_dialog.widgets.kbd import CalendarConfig

from app_assets import load_mediascope_cats


def get_available_period(db: int) -> tuple[date, date]:
    """
    Возвращает доступный период для базы данных.

    Базы данных:
        0 - TV Index All Russia
        1 - TV Index Cities
        2 - TV Index Russia 100+

    Args:
        db: Id базы данных.

    Returns:
        Доступный период в виде кортежа (начальная дата, конечная дата).
    """

    period_info = load_mediascope_cats().get_availability_period().to_dict()

    start_date = date.fromisoformat(period_info['periodFrom'][db])
    end_date = date.fromisoformat(period_info['periodTo'][db])

    return start_date, end_date


def create_calendar_config(
    min_date: date = date(2023, 1, 1),
    max_date: date = date(2025, 12, 31),
    firstweekday: int = 0,  # Понедельник – первый день
    month_columns: int = 3,
) -> CalendarConfig:
    """
    Возвращает готовую конфигурацию календаря с заданными параметрами.

    Args:
        min_date: Минимальная дата.
        max_date: Максимальная дата.
        firstweekday: Первый день недели (0 - понедельник, 6 - воскресенье).
        month_columns: Количество колонок для отображения месяцев.

    Returns:
        Конфигурация календаря.
    """
    return CalendarConfig(
        min_date=min_date,
        max_date=max_date,
        firstweekday=firstweekday,
        month_columns=month_columns,
    )
