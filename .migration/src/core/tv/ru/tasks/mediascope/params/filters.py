"""
Для согласованности с PEP8, CamelCase транслируется в snake_case.
Имена параметров в фильтрах соответствуют аналогичным в Mediascope API.
"""

import enum
from datetime import datetime, time

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator
from typing_extensions import Annotated


class Location(enum.IntEnum):
    """Место просмотра."""

    HOME = 1  # Дом
    DACHA = 2  # Дача

    @classmethod
    def get_values(cls) -> list[int]:
        """Возвращает отсортированный список констант."""
        return sorted(member.value for member in cls)


class Sex(enum.IntEnum):
    """Пол."""

    MALE = 1  # Мужчины
    FEMALE = 2  # Женщины

    @classmethod
    def get_values(cls) -> list[int]:
        """Возвращает отсортированный список констант."""
        return sorted(member.value for member in cls)


class IncomeGroup(enum.StrEnum):
    """Группа дохода."""

    A = 'A'  # Группа A
    B = 'B'  # Группа B
    C = 'C'  # Группа C

    @classmethod
    def get_values(cls) -> list[str]:
        """Возвращает отсортированный список констант."""
        return sorted(member.value for member in cls)


# TODO: Подписать значения для каждого уровня дохода
class IncLevel(enum.IntEnum):
    """Уровень дохода."""

    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6

    @classmethod
    def get_values(cls) -> list[int]:
        """Возвращает отсортированный список констант."""
        return sorted(member.value for member in cls)


class BreakIssueStatus(enum.StrEnum):
    """Блок статус."""

    R = 'R'  # Реальный
    V = 'V'  # Виртуальный

    @classmethod
    def get_values(cls) -> list[str]:
        """Возвращает отсортированный список констант."""
        return sorted(member.value for member in cls)


class BreakContentType(enum.StrEnum):
    """Блок контент."""

    A = 'A'  # Анонсы
    C = 'C'  # Коммерческий
    P = 'P'  # Политический
    S = 'S'  # Спонсорский

    @classmethod
    def get_values(cls) -> list[str]:
        """Возвращает отсортированный список констант."""
        return sorted(member.value for member in cls)


class BreakDistributionType(enum.StrEnum):
    """Блок распространение."""

    L = 'L'  # Локальный
    N = 'N'  # Сетевой
    O = 'O'  # Орбитальный # noqa: E741

    @classmethod
    def get_values(cls) -> list[str]:
        """Возвращает отсортированный список констант."""
        return sorted(member.value for member in cls)


class AdIssueStatus(enum.StrEnum):
    """Ролик статус."""

    R = 'R'  # Реальный
    V = 'V'  # Виртуальный

    @classmethod
    def get_values(cls) -> list[str]:
        """Возвращает отсортированный список констант."""
        return sorted(member.value for member in cls)


class AdDistributionType(enum.StrEnum):
    """Ролик распространение."""

    L = 'L'  # Локальный
    N = 'N'  # Сетевой
    O = 'O'  # Орбитальный  # noqa: E741

    @classmethod
    def get_values(cls) -> list[str]:
        """Возвращает отсортированный список констант."""
        return sorted(member.value for member in cls)


class AdType(enum.IntEnum):
    """Ролик тип."""

    _1 = 1  # Ролик
    _5 = 5  # Спонсор
    _10 = 10  # Телемагазин
    _15 = 15  # Анонс: спонсор
    _23 = 23  # Спонсорская заставка
    _24 = 24  # Погода: спонсор
    _25 = 25  # Анонс: спонсорская заставка

    @classmethod
    def get_values(cls) -> list[int]:
        """Возвращает отсортированный список констант."""
        return sorted(member.value for member in cls)


class Weekday(enum.IntEnum):
    """День недели."""

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    @classmethod
    def get_values(cls) -> list[int]:
        """Возвращает отсортированный список констант."""
        return sorted(member.value for member in cls)


class Daytype(enum.StrEnum):
    """Тип дня."""

    WEEKDAY = 'W'  # Рабочий
    WEEKEND = 'E'  # Выходной
    HOLIDAY = 'H'  # Праздник
    MOURNING = 'F'  # День траура

    @classmethod
    def get_values(cls) -> list[str]:
        """Возвращает отсортированный список констант."""
        return sorted(member.value for member in cls)


class Region(enum.IntEnum):
    """Регион."""

    MOSKVA = 1  # МОСКВА
    SANKT_PETERBURG = 2  # САНКТ-ПЕТЕРБУРГ
    TVER = 3  # ТВЕРЬ
    NIZHNIY_NOVGOROD = 4  # НИЖНИЙ НОВГОРОД
    VOLGOGRAD = 5  # ВОЛГОГРАД
    SAMARA = 6  # САМАРА
    YAROSLAVL = 7  # ЯРОСЛАВЛЬ
    VORONEZH = 8  # ВОРОНЕЖ
    ROSTOV_NA_DONU = 9  # РОСТОВ-НА-ДОНУ
    SARATOV = 10  # САРАТОВ
    EKATERINBURG = 12  # ЕКАТЕРИНБУРГ
    CHELYABINSK = 13  # ЧЕЛЯБИНСК
    PERM = 14  # ПЕРМЬ
    NOVOSIBIRSK = 15  # НОВОСИБИРСК
    TYUMEN = 16  # ТЮМЕНЬ
    KRASNOYARSK = 17  # КРАСНОЯРСК
    VLADIVOSTOK = 18  # ВЛАДИВОСТОК
    KAZAN = 19  # КАЗАНЬ
    UFA = 20  # УФА
    OMSK = 21  # ОМСК
    KRASNODAR = 23  # КРАСНОДАР
    IRKUTSK = 25  # ИРКУТСК
    KHABAROVSK = 26  # ХАБАРОВСК
    STAVROPOL = 39  # СТАВРОПОЛЬ
    BARNAUL = 40  # БАРНАУЛ
    KEMEROVO = 45  # КЕМЕРОВО
    TOMSK = 55  # ТОМСК

    @classmethod
    def get_values(cls) -> list[int]:
        """Возвращает отсортированный список кодов регионов."""
        return sorted(member.value for member in cls)


class BasedemoFilter(BaseModel):
    """Фильтр по демографии."""

    sex: Annotated[int | None, Field(default=None)]
    min_age: Annotated[int | None, Field(default=None, ge=4, le=99)]
    max_age: Annotated[int | None, Field(default=None, ge=4, le=99)]
    income_group: Annotated[list[str] | None, Field(default=None)]
    inc_level: Annotated[list[int] | None, Field(default=None)]

    @field_validator('sex')
    def valudate_sex(cls, v: int | None) -> int | None:
        """Проверяет корректность значения для фильтра."""
        if v is None:
            return None

        if v not in Sex.get_values():
            raise ValueError('Недопустимое значение для фильтра')

        return v

    @field_validator('income_group')
    def validate_income_group(cls, v: list[str] | None) -> tuple[str, ...] | None:
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        if not all(inc in IncomeGroup.get_values() for inc in v):
            raise ValueError('Недопустимое значение для фильтра')

        return tuple(v)

    @field_validator('inc_level')
    def validate_inc_level(cls, v: list[int] | None) -> tuple[int, ...] | None:
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        if not all(inc in IncLevel.get_values() for inc in v):
            raise ValueError('Недопустимое значение для фильтра')

        return tuple(v)

    @computed_field
    @property
    def filter(self) -> str | None:
        """Возвращает строку фильтра в SQL-подобном синтаксисе."""
        parts: list[str] = []

        # Если пол не указан, фильтр не применяется
        if self.sex is not None:
            parts.append(f'sex = {self.sex}')

        if self.min_age is not None:
            parts.append(f'age >= {self.min_age}')

        if self.max_age is not None:
            parts.append(f'age <= {self.max_age}')

        if self.income_group is not None:
            mapping = {'A': 1, 'B': 2, 'C': 3}

            groups = tuple(sorted(mapping[x] for x in self.income_group))

            if len(groups) == 1:
                parts.append(f'incomeGroupRussia = {groups[0]}')
            else:
                parts.append(f'incomeGroupRussia IN ({", ".join(map(str, groups))})')

        if self.inc_level is not None:
            sorted_levels = tuple(sorted(self.inc_level))

            if len(sorted_levels) == 1:
                parts.append(f'incLevel = {sorted_levels[0]}')
            else:
                levels = ', '.join(map(str, sorted_levels))
                parts.append(f'incLevel IN ({levels})')

        return ' AND '.join(parts) if parts else None


class DateFilter(BaseModel):
    """Фильтр по периоду."""

    lower_bound: Annotated[datetime, Field(description='Начальная дата')]
    upper_bound: Annotated[datetime, Field(description='Конечная дата')]

    @model_validator(mode='after')
    def validate_model(self):
        """Проверяет корректность значений для фильтра."""
        if self.lower_bound > self.upper_bound:
            raise ValueError('Начальная дата не может быть позже конечной даты')

        return self

    @computed_field
    @property
    def filter(self) -> list[tuple[str, str]]:
        """Возвращает строку фильтра в SQL-подобном синтаксисе."""
        # NOTE: Особенность API. Фильтр должен возвращать список кортежей из двух строковых значений
        return [(self.lower_bound.strftime('%Y-%m-%d'), self.upper_bound.strftime('%Y-%m-%d'))]


class WeekdayFilter(BaseModel):
    """Фильтр по дням недели."""

    research_week_day: Annotated[list[int] | None, Field(default=None)]

    @field_validator('research_week_day')
    def validate_research_week_day(cls, v: list[int] | None) -> tuple[int, ...] | None:
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        if not all(wd in Weekday.get_values() for wd in v):
            raise ValueError('Недопустимое значение для фильтра')

        return tuple(v)

    @computed_field
    @property
    def filter(self) -> str | None:
        """Возвращает строку фильтра в SQL-подобном синтаксисе."""
        if self.research_week_day is None:
            return None

        values = tuple(sorted(self.research_week_day))

        if len(values) == 1:
            return f'researchWeekDay = {values[0]}'
        else:
            return f'researchWeekDay IN ({", ".join(map(str, values))})'


class DaytypeFilter(BaseModel):
    """Фильтр по типу дня."""

    research_day_type: Annotated[list[str] | None, Field(default=None)]

    @field_validator('research_day_type')
    def validate_research_day_type(cls, v: list[str] | None) -> tuple[str, ...] | None:
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        if not all(dt in Daytype.get_values() for dt in v):
            raise ValueError('Недопустимое значение для фильтра')

        return tuple(v)

    @computed_field
    @property
    def filter(self) -> str | None:
        """Возвращает строку фильтра в SQL-подобном синтаксисе."""
        if self.research_day_type is None:
            return None

        values = tuple(sorted(self.research_day_type))

        if len(values) == 1:
            return f'researchDayType = {values[0]}'
        else:
            return f'researchDayType IN ({", ".join(values)})'


class CompanyFilter(BaseModel):
    """Фильтр по компаниям."""

    tv_company_id: Annotated[list[int] | None, Field(default=None)]
    tv_thematic_id: Annotated[list[int] | None, Field(default=None)]
    tv_net_id: Annotated[list[int] | None, Field(default=None)]
    region_id: Annotated[int | None, Field(default=None)]
    tv_company_holding_id: Annotated[list[int] | None, Field(default=None)]
    tv_company_media_holding_id: Annotated[list[int] | None, Field(default=None)]

    @field_validator('tv_company_id')
    def validate_tv_company_id(cls, v: list[int] | None) -> tuple[int, ...] | None:
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        return tuple(v)

    @field_validator('tv_thematic_id')
    def validate_tv_thematic_id(cls, v: list[int] | None) -> tuple[int, ...] | None:
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        return tuple(v)

    @field_validator('tv_net_id')
    def validate_tv_net_id(cls, v: list[int] | None) -> tuple[int, ...] | None:
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        return tuple(v)

    @field_validator('region_id')
    def validate_region_id(cls, v: int | None) -> int | None:
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        return v

    @field_validator('tv_company_holding_id')
    def validate_tv_company_holding_id(cls, v: list[int] | None) -> tuple[int, ...] | None:
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        return tuple(v)

    @field_validator('tv_company_media_holding_id')
    def validate_tv_company_media_holding_id(cls, v: list[int] | None) -> tuple[int, ...] | None:
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        return tuple(v)

    @computed_field
    @property
    def filter(self) -> str | None:
        """Возвращает строку фильтра в SQL-подобном синтаксисе."""
        parts: list[str] = []

        if self.tv_company_id is not None:
            values = tuple(sorted(self.tv_company_id))
            if len(values) == 1:
                parts.append(f'tvCompanyId = {values[0]}')
            else:
                parts.append(f'tvCompanyId IN ({", ".join(map(str, values))})')

        if self.tv_thematic_id is not None:
            values = tuple(sorted(self.tv_thematic_id))
            if len(values) == 1:
                parts.append(f'tvThematicId = {values[0]}')
            else:
                parts.append(f'tvThematicId IN ({", ".join(map(str, values))})')

        if self.tv_net_id is not None:
            values = tuple(sorted(self.tv_net_id))
            if len(values) == 1:
                parts.append(f'tvNetId = {values[0]}')
            else:
                parts.append(f'tvNetId IN ({", ".join(map(str, values))})')

        # WARNING: Идиоты из Mediascope не могут сделать нормальный фильтр по нескольким регионам.
        # Поэтому приходится для каждого региона делать отдельный запрос.
        if self.region_id is not None:
            parts.append(f'regionId = {self.region_id}')

        if self.tv_company_holding_id is not None:
            values = tuple(sorted(self.tv_company_holding_id))
            if len(values) == 1:
                parts.append(f'tvCompanyHoldingId = {values[0]}')
            else:
                parts.append(f'tvCompanyHoldingId IN ({", ".join(map(str, values))})')

        if self.tv_company_media_holding_id is not None:
            values = tuple(sorted(self.tv_company_media_holding_id))
            if len(values) == 1:
                parts.append(f'tvCompanyMediaHoldingId = {values[0]}')
            else:
                parts.append(f'tvCompanyMediaHoldingId IN ({", ".join(map(str, values))})')

        return ' AND '.join(parts) if parts else None


class TimeFilter(BaseModel):
    """Фильтр по временному диапазону."""

    lower_bound: Annotated[time | None, Field(default=None)]
    upper_bound: Annotated[time | None, Field(default=None)]

    @model_validator(mode='after')
    def validate_model(self):
        """Проверяет корректность значений для фильтра."""
        if self.lower_bound is not None and self.upper_bound is not None:
            if self.lower_bound >= self.upper_bound:
                raise ValueError('Начальная граница времени должна быть меньше конечной')

        return self

    @computed_field
    @property
    def filter(self) -> str | None:
        """Возвращает строку фильтра в SQL-подобном синтаксисе."""
        parts: list[str] = []

        if self.lower_bound is not None:
            parts.append(f'timeBand1 >= {self.lower_bound.strftime("%H%M%S")}')

        if self.upper_bound is not None:
            parts.append(f'timeBand1 < {self.upper_bound.strftime("%H%M%S")}')

        return ' AND '.join(parts) if parts else None


class LocationFilter(BaseModel):
    """Фильтр по месту просмотра."""

    location_id: Annotated[int | None, Field(default=None)]

    @field_validator('location_id')
    def validate_location_id(cls, v: int | None) -> int | None:
        """Проверяет корректность значения для фильтра."""
        if v is None:
            return None

        if v not in Location.get_values():
            raise ValueError('Недопустимое значение для фильтра')

        return v

    @computed_field
    @property
    def filter(self) -> str | None:
        """Возвращает строку фильтра в SQL-подобном синтаксисе."""
        if self.location_id is None:
            return None

        return f'locationId = {self.location_id}'


class ProgramFilter(BaseModel):
    """Фильтр по программам."""

    lower_bound_program_start_time: Annotated[time | None, Field(default=None)]
    upper_bound_program_start_time: Annotated[time | None, Field(default=None)]
    program_duration: Annotated[time | None, Field(default=None)]
    program_type_id: Annotated[list[int] | None, Field(default=None)]

    @field_validator('program_type_id')
    def validate_program_type_id(cls, v: list[int] | None) -> tuple[int, ...] | None:
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        return tuple(v)

    @model_validator(mode='after')
    def validate_model(self):
        """Проверяет корректность границ времени."""
        if (
            self.lower_bound_program_start_time is not None
            and self.upper_bound_program_start_time is not None
            and self.lower_bound_program_start_time > self.upper_bound_program_start_time
        ):
            raise ValueError('Время начала не может быть позже времени окончания.')

        return self

    @computed_field
    @property
    def filter(self) -> str | None:
        """Возвращает строку фильтра в SQL-подобном синтаксисе."""
        parts: list[str] = []

        if self.program_duration is not None:
            total_seconds = (
                self.program_duration.hour * 3600 + self.program_duration.minute * 60 + self.program_duration.second
            )
            parts.append(f'programDuration >= {total_seconds}')

        if self.lower_bound_program_start_time is not None:
            parts.append(f'programStartTime >= {self.lower_bound_program_start_time.strftime("%H%M%S")}')

        if self.upper_bound_program_start_time is not None:
            parts.append(f'programStartTime <= {self.upper_bound_program_start_time.strftime("%H%M%S")}')

        if self.program_type_id is not None:
            values = tuple(sorted(self.program_type_id))

            if len(values) == 1:
                parts.append(f'programTypeId = {values[0]}')
            else:
                parts.append(f'programTypeId IN ({", ".join(map(str, values))})')

        return ' AND '.join(parts) if parts else None


class BreakFilter(BaseModel):
    break_distribution_type: Annotated[list[str] | None, Field(default=None)]
    break_content_type: Annotated[list[str] | None, Field(default=None)]
    break_issue_status_id: Annotated[str | None, Field(default=None)]

    @field_validator('break_distribution_type')
    def validate_break_distribution_type(cls, v):
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        if not all(item in BreakDistributionType.get_values() for item in v):
            raise ValueError('Недопустимое значение для фильтра')

        return tuple(sorted(v))

    @field_validator('break_content_type')
    def validate_break_content_type(cls, v):
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        if not all(item in BreakContentType.get_values() for item in v):
            raise ValueError('Недопустимое значение для фильтра')

        return tuple(sorted(v))

    @field_validator('break_issue_status_id')
    def validate_break_issue_status_id(cls, v):
        """Проверяет корректность значения для фильтра."""
        if v is None:
            return None

        if v not in BreakIssueStatus.get_values():
            raise ValueError('Недопустимое значение для фильтра')

        return v

    @computed_field
    @property
    def filter(self) -> str | None:
        """Возвращает строку фильтра в SQL-подобном синтаксисе."""
        parts: list[str] = []

        if self.break_issue_status_id is not None:
            parts.append(f'breaksIssueStatusId = {self.break_issue_status_id}')

        if self.break_content_type is not None:
            vals = tuple(self.break_content_type)
            if len(vals) == 1:
                parts.append(f'breaksContentType = {vals[0]}')
            else:
                parts.append(f'breaksContentType IN ({", ".join(vals)})')

        if self.break_distribution_type is not None:
            vals = tuple(self.break_distribution_type)
            if len(vals) == 1:
                parts.append(f'breaksDistributionType = {vals[0]}')
            else:
                parts.append(f'breaksDistributionType IN ({", ".join(vals)})')

        return ' AND '.join(parts) if parts else None


class AdFilter(BaseModel):
    ad_issue_status_id: Annotated[str | None, Field(default=None)]
    ad_type_id: Annotated[list[int] | None, Field(default=None)]
    ad_distribution_type: Annotated[list[str] | None, Field(default=None)]

    @field_validator('ad_issue_status_id')
    def validate_ad_issue_status_id(cls, v):
        """Проверяет корректность значения для фильтра."""
        if v is None:
            return None

        if v not in AdIssueStatus.get_values():
            raise ValueError('Недопустимое значение для фильтра')

        return v

    @field_validator('ad_type_id')
    def validate_ad_type_id(cls, v):
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        if not all(item in AdType.get_values() for item in v):
            raise ValueError('Недопустимое значение для фильтра')

        return tuple(sorted(v))

    @field_validator('ad_distribution_type')
    def validate_ad_distribution_type(cls, v):
        """Проверяет корректность значений для фильтра."""
        if not v:
            return None

        if len(set(v)) != len(v):
            raise ValueError('Последовательность содержит дубликаты')

        if not all(item in AdDistributionType.get_values() for item in v):
            raise ValueError('Недопустимое значение для фильтра')

        return tuple(sorted(v))

    @computed_field
    @property
    def filter(self) -> str | None:
        """Возвращает строку фильтра в SQL-подобном синтаксисе."""
        parts: list[str] = []

        if self.ad_issue_status_id is not None:
            parts.append(f'adIssueStatusId = {self.ad_issue_status_id}')

        if self.ad_type_id is not None:
            vals = tuple(self.ad_type_id)
            if len(vals) == 1:
                parts.append(f'adTypeId = {vals[0]}')
            else:
                parts.append(f'adTypeId IN ({", ".join(map(str, vals))})')

        if self.ad_distribution_type is not None:
            vals = tuple(self.ad_distribution_type)
            if len(vals) == 1:
                parts.append(f'adDistributionType = {vals[0]}')
            else:
                parts.append(f'adDistributionType IN ({", ".join(vals)})')

        return ' AND '.join(parts) if parts else None


# NOTE: Заглушка. Не используется для работы с API в данный момент.
class TargetdemoFilter(BasedemoFilter):
    pass

    @property
    def filter(self) -> None:
        return


# NOTE: Заглушка. Не используется для работы с API в данный момент.
class RegionFilter(BaseModel):
    pass

    @property
    def filter(self) -> None:
        return


# NOTE: Заглушка. Не используется для работы с API в данный момент.
class SubjectFilter(BaseModel):
    pass

    @property
    def filter(self) -> str | None:
        return


# NOTE: Заглушка. Не используется для работы с API в данный момент.
class RespondentFilter(BaseModel):
    pass

    @property
    def filter(self) -> str | None:
        return


# NOTE: Заглушка. Не используется для работы с API в данный момент.
class PlatformFilter(BaseModel):
    pass

    @property
    def filter(self) -> str | None:
        return


# NOTE: Заглушка. Не используется для работы с API в данный момент.
class PlaybackTypeFilter(BaseModel):
    pass

    @property
    def filter(self) -> str | None:
        return


# NOTE: Заглушка. Не используется для работы с API в данный момент.
class BigTVFilter(BaseModel):
    pass

    @property
    def filter(self) -> str | None:
        return
