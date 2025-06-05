import logging
import time
from typing import Any

import polars as pl
from mediascope_api.mediavortex import tasks  # type: ignore
from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.tv.ru.tasks.mediascope.params import filters

log = logging.getLogger(__name__)


def _merge_join(dfs: list[pl.DataFrame], slices: list[str]) -> pl.DataFrame:
    """Левый join списка DataFrame по ключам slices и сортировка столбцов."""
    if not dfs:
        return pl.DataFrame()

    base = dfs[0]

    for df in dfs[1:]:
        base = base.join(df, on=slices, how='left')

    return base.select(sorted(base.columns))


def _merge_stack(dfs: list[pl.DataFrame]) -> pl.DataFrame:
    """Вертикальное объединение (vstack) списка DataFrame с сортировкой колонок."""
    if not dfs:
        return pl.DataFrame()

    result = dfs[0].select(sorted(dfs[0].columns))

    for df in dfs[1:]:
        df_sorted = df.select(sorted(df.columns))
        result = result.vstack(df_sorted)

    return result


class CrosstabTask(BaseModel):
    """Класс для выполнения crosstab задач в MediaVortex API."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    date_filter: filters.DateFilter
    statistics: list[str]
    options: dict[str, Any]
    slices: list[str]
    region_ids: list[int] | None = None

    weekday_filter: filters.WeekdayFilter = Field(default_factory=filters.WeekdayFilter)  # type: ignore
    daytype_filter: filters.DaytypeFilter = Field(default_factory=filters.DaytypeFilter)  # type: ignore
    company_filter: filters.CompanyFilter = Field(default_factory=filters.CompanyFilter)  # type: ignore
    region_filter: filters.RegionFilter = Field(default_factory=filters.RegionFilter)
    location_filter: filters.LocationFilter = Field(default_factory=filters.LocationFilter)  # type: ignore
    basedemo_filter: filters.BasedemoFilter = Field(default_factory=filters.BasedemoFilter)  # type: ignore
    targetdemo_filter: filters.TargetdemoFilter = Field(default_factory=filters.TargetdemoFilter)  # type: ignore
    program_filter: filters.ProgramFilter = Field(default_factory=filters.ProgramFilter)  # type: ignore
    break_filter: filters.BreakFilter = Field(default_factory=filters.BreakFilter)  # type: ignore
    ad_filter: filters.AdFilter = Field(default_factory=filters.AdFilter)  # type: ignore
    subject_filter: filters.SubjectFilter = Field(default_factory=filters.SubjectFilter)
    respondent_filter: filters.RespondentFilter = Field(default_factory=filters.RespondentFilter)
    platform_filter: filters.PlatformFilter = Field(default_factory=filters.PlatformFilter)
    playbacktype_filter: filters.PlaybackTypeFilter = Field(default_factory=filters.PlaybackTypeFilter)
    bigtv_filter: filters.BigTVFilter = Field(default_factory=filters.BigTVFilter)
    sortings: dict[str, str] = Field(default_factory=dict)

    mtask: tasks.MediaVortexTask = Field(default_factory=tasks.MediaVortexTask, init=False)  # type: ignore

    @field_validator('statistics', 'slices', mode='before')
    def _check_non_empty_list(cls, v: list[Any]) -> list[Any]:
        if not v:
            raise ValueError('Список не может быть пустым')
        return v

    def _build_params(self, stat: str, region_id: int | None) -> dict[str, Any]:
        """Формирует словарь параметров для одного запроса."""
        # Делаем копии фильтров, чтобы не менять исходные объекты
        bd = self.basedemo_filter.model_copy()
        cf = self.company_filter.model_copy()

        # Sale-статистики всегда без basedemo или с модифицированным ключом
        if 'sale' in stat.lower() or bd.filter is None:
            bd_value = None
        else:
            # В зависимости от kit_id заменяем группу дохода на Russia
            bd_filter = bd.filter

            bd_value = (
                bd_filter.replace('incomeGroupRussia', 'incomeGroup') if self.options.get('kitId') == 3 else bd_filter
            )

        # Если передан region_id, фильтруем компании по нему
        if region_id is not None:
            cf.region_id = region_id

        return {
            'date_filter': self.date_filter.filter,
            'weekday_filter': self.weekday_filter.filter,
            'daytype_filter': self.daytype_filter.filter,
            'company_filter': cf.filter,
            'region_filter': self.region_filter.filter,
            'location_filter': self.location_filter.filter,
            'basedemo_filter': bd_value,
            'targetdemo_filter': self.targetdemo_filter.filter,
            'program_filter': self.program_filter.filter,
            'break_filter': self.break_filter.filter,
            'ad_filter': self.ad_filter.filter,
            'subject_filter': self.subject_filter.filter,
            'respondent_filter': self.respondent_filter.filter,
            'platform_filter': self.platform_filter.filter,
            'playbacktype_filter': self.playbacktype_filter.filter,
            'bigtv_filter': self.bigtv_filter.filter,
            'slices': self.slices,
            'statistics': [stat],
            'sortings': self.sortings,
            'options': self.options,
            'add_city_to_basedemo_from_region': region_id is not None,
            'add_city_to_targetdemo_from_region': region_id is not None,
        }

    def _fetch_df(self, stat: str, region_id: int | None, delay: float) -> pl.DataFrame:
        """Отправляет запрос к API, ждет выполнения задачи и возвращает DataFrame."""
        params = self._build_params(stat, region_id)
        config = self.mtask.build_crosstab_task(**params)  # type: ignore
        task_id = self.mtask.send_crosstab_task(config)  # type: ignore
        done = self.mtask.wait_task(task_id)  # type: ignore
        result = self.mtask.get_result(done)  # type: ignore

        if result is None:
            log.warning(f'Task {task_id} вернул пустой результат')
            return pl.DataFrame()

        df = pl.from_pandas(self.mtask.result2table(result))  # type: ignore
        time.sleep(delay)

        return df

    def run(self, delay: float = 0.5) -> pl.DataFrame:
        """Выполняет запросы и собирает результаты по городам и статистикам.

        Args:
            delay (float): время ожидания между запросами в секундах.

        Returns:
            pl.DataFrame: итоговая таблица.
        """
        if self.region_ids:
            all_dfs: list[pl.DataFrame] = []
            for rid in self.region_ids:
                dfs: list[pl.DataFrame] = []
                for i, stat in enumerate(self.statistics):
                    df = self._fetch_df(stat, rid, delay if i < len(self.statistics) - 1 else 0)

                    if not df.is_empty():
                        dfs.append(df)

                if not dfs:
                    continue

                merged_city = _merge_join(dfs, self.slices)
                all_dfs.append(merged_city)

            if not all_dfs:
                return pl.DataFrame()

            return _merge_stack(all_dfs)

        # Без разбивки по регионам
        dfs = []

        for i, stat in enumerate(self.statistics):
            df = self._fetch_df(stat, None, delay if i < len(self.statistics) - 1 else 0)

            if not df.is_empty():
                dfs.append(df)

        if not dfs:
            return pl.DataFrame()

        result = _merge_join(dfs, self.slices)

        result = result.fill_nan(None)

        return result
