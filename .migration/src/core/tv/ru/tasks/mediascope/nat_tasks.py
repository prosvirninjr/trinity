from datetime import datetime
from typing import Any

import polars as pl
import polars.selectors as sc

from core.tv.ru.tasks.mediascope.crosstab import CrosstabTask
from core.tv.ru.tasks.mediascope.params.filters import BreakFilter, DateFilter
from core.tv.ru.tasks.mediascope.params.options import IssueTypes, KitIds, Options
from core.tv.ru.tasks.mediascope.params.slices import BreakSlices, ChannelSlices
from core.tv.ru.tasks.mediascope.params.statistics import TVRStatistics
from core.tv.ru.tasks.mediascope.parser import parse_demo


def nat_affinity_task(
    start_date: datetime,
    end_date: datetime,
    audience: str,
    delay: float = 0.5,
) -> pl.DataFrame:
    """
    Выполняет расчет Avg. Affinity по рынку.

    Args:
        start_date: Начальная дата в формате YYYY-MM-DD.
        end_date: Конечная дата в формате YYYY-MM-DD.
        audience: Целевая аудитория.
        delay: Задержка между запросами к API.

    Returns:
        DataFrame с результатами расчета Avg. Affinity по рынку.
    """
    statistics = [
        TVRStatistics.SALES_RTG_PER_AVG.value,
        TVRStatistics.RTG_PER_AVG.value,
    ]
    options: dict[str, Any] = {
        Options.KIT_ID.value: KitIds.TV_INDEX_ALL_RUSSIA.value,
        Options.ISSUE_TYPE.value: IssueTypes.BREAK.value,
    }
    slices = [
        ChannelSlices.TV_COMPANY_NAME.value,
        BreakSlices.BREAKS_DISTRIBUTION_TYPE_NAME.value,
    ]
    breaks_filter = BreakFilter(
        break_issue_status_id='R',  # Статус 'Реальный'
        break_content_type=['C'],  # Блок 'Коммерческий'
        break_distribution_type=['N', 'O'],  # Распространение 'Сетевое' и 'Орбитальное'
    )

    task = CrosstabTask(
        date_filter=DateFilter(
            lower_bound=start_date,
            upper_bound=end_date,
        ),
        basedemo_filter=parse_demo(audience),  # type: ignore
        statistics=statistics,
        options=options,
        slices=slices,
        break_filter=breaks_filter,
    )

    # Выполняем запросы
    df = task.run(delay)

    # Добавляем колонку Affinity и приводим результат к финальному виду
    df = (
        df.with_columns(
            pl.when(pl.col(TVRStatistics.SALES_RTG_PER_AVG.value) != 0)
            .then(pl.col(TVRStatistics.RTG_PER_AVG.value) / pl.col(TVRStatistics.SALES_RTG_PER_AVG.value))
            .otherwise(None)
            .alias(f'Affinity {audience}')
        )
        .sort(
            # Сортируем по телеканалу и типу блока
            [
                pl.col(ChannelSlices.TV_COMPANY_NAME.value),
                pl.col(BreakSlices.BREAKS_DISTRIBUTION_TYPE_NAME.value),
            ],
            descending=[False, True],
        )
        .rename(
            {
                ChannelSlices.TV_COMPANY_NAME.value: 'Телекомпания',
                BreakSlices.BREAKS_DISTRIBUTION_TYPE_NAME.value: 'Блок распространение',
                TVRStatistics.RTG_PER_AVG.value: f'Avg. TVR {audience}',
                TVRStatistics.SALES_RTG_PER_AVG.value: 'Avg. Sales TVR',
            }
        )
        .select(
            [
                'Телекомпания',
                'Блок распространение',
                f'Avg. TVR {audience}',
                'Avg. Sales TVR',
                f'Affinity {audience}',
            ]
        )
    )

    # Постобработка
    df = df.fill_nan(None)
    df = df.with_columns(sc.numeric().round(4))

    return df
