import logging
import re

from core.tv.ru.tasks.mediascope.params.filters import BasedemoFilter, Sex
from core.utils.tools import TextTools

log = logging.getLogger(__name__)


def parse_demo(demo: str) -> BasedemoFilter:
    """
    Парсит строку с демографической переменной и возвращает объект BasedemoFilter.
    Формат (регистр не важен, скобки отбрасываются): [Sex] min_age-max_age|min_age+ [IncomeGroup] [IL min-max|min].
    """
    cleaned = TextTools.to_clean_string(demo)
    cleaned = cleaned.replace('(', '').replace(')', '')

    pattern = (
        r'^(?:(all|m|w)\s+)?'  # Пол
        r'(\d+)(?:-(\d+)|\+)'  # Возраст
        r'(?:\s+([ABC]+))?'  # Группа дохода
        r'(?:\s+IL\s+(\d+)(?:-(\d+))?)?$'  # Уровень дохода
    )
    match = re.match(pattern, cleaned, flags=re.IGNORECASE)
    if not match:
        raise ValueError('Неверный формат демографической строки')

    sex_str, min_age_s, max_age_s, grp_s, min_il_s, max_il_s = match.groups()

    # Пол
    sex_val: int | None = None
    if sex_str:
        s = sex_str.upper()
        if s == 'M':
            sex_val = Sex.MALE.value
        elif s == 'W':
            sex_val = Sex.FEMALE.value
        elif s == 'ALL':
            sex_val = None
        else:
            raise ValueError('Недопустимый пол')

    # Возраст
    min_age = int(min_age_s)
    max_age = int(max_age_s) if max_age_s else None
    if max_age is not None and min_age > max_age:
        raise ValueError('Неверный возрастной диапазон')

    # Проверка конфликтов IncomeGroup и IL
    if grp_s and min_il_s:
        raise ValueError('Нельзя одновременно указывать IncomeGroup и IncLevel')

    # IncomeGroup
    income_group = list(grp_s.upper()) if grp_s else None

    # IncLevel
    inc_level: list[int] | None = None
    if min_il_s:
        lo = int(min_il_s)
        if max_il_s:
            hi = int(max_il_s)
            if lo > hi:
                raise ValueError('Неверный диапазон IL')
            inc_level = list(range(lo, hi + 1))
        else:
            inc_level = [lo]

    try:
        return BasedemoFilter(
            sex=sex_val,
            min_age=min_age,
            max_age=max_age,
            income_group=income_group,
            inc_level=inc_level,
        )
    except Exception:
        log.exception('Не удалось создать объект BasedemoFilter')
        raise
