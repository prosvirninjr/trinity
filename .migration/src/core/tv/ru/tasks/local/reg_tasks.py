import re

import polars as pl
import polars.selectors as sc

from app_assets import load_daytypes, load_reg_tvc_info
from core.tv.ru.tasks.local import schema
from core.tv.ru.tasks.local.logic import RegTVLogic, TVLogic
from core.utils.parser import Parser


def reg_base_task(df: pl.DataFrame) -> pl.DataFrame:
    # --- Загрузка служебной информации ---

    daytypes = load_daytypes()
    tvc_info = load_reg_tvc_info()  # Справочник телекомпаний

    o_column = schema.RegOColumn()  # Оригинальные столбцы DataFrame
    e_column = schema.RegEColumn()  # Вычисляемые столбцы DataFrame

    # --- Предварительная обработка ---

    df = _drop_null(df)  # Удаление пустых столбцов
    df = _set_header(df)  # Определение и установка заголовка
    df = _rename_header(df)  # Переименование заголовка

    # Преобразование столбцов к нужному типу данных (str -> Float64 | Datetime)
    for column in df.columns:
        try:
            df = df.with_columns(pl.col(column).str.replace(',', '.').cast(pl.Float64, strict=True).alias(column))
        except pl.exceptions.InvalidOperationError:
            continue

    df = df.with_columns(
        pl.col(o_column.date_.name).map_elements(lambda x: Parser.parse_date(x), return_dtype=pl.Datetime)
    )

    # --- Создание дополнительных столбцов и редактирование существующих ---

    # Создание столбца 'Год'
    df = df.with_columns(
        pl.col(o_column.date_.name).dt.year().cast(pl.Int64).alias(e_column.year.name),
    )

    # Создание столбца 'Месяц' (порядковый номер)
    df = df.with_columns(
        pl.col(o_column.date_.name).dt.month().cast(pl.Int64).alias(e_column.month.name),
    )

    # Создание столбца 'День недели' (порядковый номер)
    df = df.with_columns(
        pl.col(o_column.date_.name).dt.weekday().cast(pl.Int64).alias(e_column.weekday.name),
    )

    # Создание столбца 'Неделя' (порядковый номер)
    df = df.with_columns(
        pl.col(o_column.date_.name).dt.week().cast(pl.Int64).alias(e_column.week.name),
    )

    # Создание столбца 'День недели' (название)
    df = df.with_columns(
        pl.col(e_column.weekday.name)
        .map_elements(lambda x: TVLogic.get_weekday_name(x), return_dtype=pl.String)
        .alias(e_column.weekday_name.name)
    )

    # Создание столбца 'Время начала [0-24]'
    df = df.with_columns(
        pl.col(o_column.spot_time_start.name)
        .map_elements(lambda x: TVLogic.normalize_time_format(x, as_string=True), return_dtype=pl.String)
        .alias(e_column.time_start_standard.name),
    )

    # Создание столбца 'Час начала'
    df = df.with_columns(
        pl.col(e_column.time_start_standard.name)
        .str.split(':')
        .list.get(0)
        .cast(pl.Int64)
        .alias(e_column.hour_start_standard.name)
    )

    # Создание столбца 'Время суток'
    df = df.with_columns(
        pl.when((pl.col(e_column.hour_start_standard.name) >= 2) & (pl.col(e_column.hour_start_standard.name) <= 4))
        .then(pl.lit(schema.Day.NIGHT.value))
        .otherwise(pl.lit(schema.Day.DAY.value))
        .alias(e_column.day.name),
    )

    # Создание столбца 'Временной интервал'
    df = df.with_columns(
        pl.col(e_column.time_start_standard.name)
        .map_elements(lambda x: TVLogic.get_time_interval(x), return_dtype=pl.String)
        .alias(e_column.time_interval_standard.name),
    )

    df = df.with_columns(
        pl.struct([o_column.national_company.name, o_column.original_company.name])
        .map_elements(
            lambda r: RegTVLogic.get_audience(
                r[o_column.national_company.name], r[o_column.original_company.name], tvc_info
            ),
            return_dtype=pl.String,
        )
        .alias(e_column.buying_audience.name)
    )

    df = df.with_columns(
        pl.struct([o_column.national_company.name, o_column.original_company.name])
        .map_elements(
            lambda r: RegTVLogic.get_number(
                r[o_column.national_company.name], r[o_column.original_company.name], tvc_info
            ),
            return_dtype=pl.Int64,
        )
        .alias(e_column.channel_number.name)
    )

    df = df.with_columns(
        pl.struct([o_column.national_company.name, o_column.original_company.name])
        .map_elements(
            lambda r: RegTVLogic.get_name(
                r[o_column.national_company.name], r[o_column.original_company.name], tvc_info
            ),
            return_dtype=pl.String,
        )
        .alias(e_column.channel.name)
    )

    df = df.with_columns(
        pl.struct([o_column.national_company.name, o_column.original_company.name, e_column.year.name])
        .map_elements(
            lambda r: RegTVLogic.get_round(
                r[o_column.national_company.name], r[o_column.original_company.name], r[e_column.year.name], tvc_info
            ),
            return_dtype=pl.Float64,
        )
        .alias(e_column.rounding.name),
    )

    # Создание столбца 'Тип дня'
    df = df.with_columns(
        pl.col(o_column.date_.name)
        .map_elements(lambda x: TVLogic.get_daytype(x, daytypes), return_dtype=pl.String)
        .alias(e_column.daytype.name)
    )

    # Создание столбца 'Prime'
    df = df.with_columns(
        pl.struct(
            [
                pl.col(e_column.time_start_standard.name),
                pl.col(e_column.daytype.name),
                pl.col(e_column.channel.name),
            ]
        )
        .map_elements(
            lambda row: schema.PrimeTime.PT.value
            if RegTVLogic.is_prime(
                TVLogic.get_hour(row[e_column.time_start_standard.name]),
                TVLogic.get_minute(row[e_column.time_start_standard.name]),
                row[e_column.daytype.name].lower() != 'рабочий',
                row[e_column.channel.name],
            )
            else schema.PrimeTime.OP.value,
            return_dtype=pl.String,
        )
        .alias(e_column.prime_time.name)
    )

    # --- Расчет TVR статистик ---
    audiences = df.get_column(e_column.buying_audience.name).to_list()

    def _get_ba_value(metric: str, audience: str, idx: int) -> float:
        # Для минут всегда 0
        if audience.lower() == 'минуты':
            return 0.0
        col_name = f'BA {metric} {audience}'
        if col_name not in df.columns:
            raise KeyError(f"Column '{col_name}' not found")
        return df.get_column(col_name)[idx]

    # Собираем серии значений BA TVR и BA Std. TVR
    ba_tvr = [_get_ba_value('TVR', aud, i) for i, aud in enumerate(audiences)]
    ba_std_tvr = [_get_ba_value('Std. TVR', aud, i) for i, aud in enumerate(audiences)]

    df = df.with_columns(
        pl.Series('Sales TVR', ba_tvr, dtype=pl.Float64),
        pl.Series('Sales Std. TVR', ba_std_tvr, dtype=pl.Float64),
    )

    # --- Расчет GRP ---
    df = (
        df
        # Reg. GRP [округл.] = max(Reg. Sales TVR, rounding)
        .with_columns(
            pl.max_horizontal(
                [
                    pl.col('Sales TVR'),
                    pl.col(e_column.rounding.name),
                ]
            ).alias('GRP [округл.]')
        )
        # Reg. GRP20 [округл.] = Reg. GRP [округл.] * duration / 20
        .with_columns(
            (pl.col('GRP [округл.]') * pl.col(o_column.spot_expected_duration.name) / 20).alias('GRP20 [округл.]')
        )
        # Reg. GRP20 [min] для минут берет duration/60, иначе из Reg. GRP20 [округл.]
        .with_columns(
            pl.when(pl.col(e_column.buying_audience.name).str.to_lowercase() == 'минуты')
            .then(pl.col(o_column.spot_expected_duration.name) / 60)
            .otherwise(pl.col('GRP20 [округл.]'))
            .alias('GRP20 [min]')
        )
    )

    # Убираем все BA-столбцы
    df = df.drop([c for c in df.columns if c.startswith('BA ')] or [])

    # ---- Постобработка ----

    # Создание пустых столбцов 'Кампания' и 'Размещение'
    df = df.with_columns(
        pl.lit(None, dtype=pl.String).alias(e_column.campaign.name),
        pl.lit(None, dtype=pl.String).alias(e_column.placement.name),
    )

    # Округление значений до 4 знаков после запятой
    df = df.with_columns(sc.numeric().round(4))

    # Определение типов данных
    o_columns_dict = o_column.model_dump()
    e_columns_dict = e_column.model_dump()

    _schema: dict = {}

    for _, item in o_columns_dict.items():
        _schema[item['name']] = item['type_']

    for _, item in e_columns_dict.items():
        _schema[item['name']] = item['type_']

    df = df.cast(_schema)

    # Сортировка заголовка
    df = _sort_header(df)

    # Сортировка строк
    df = df.sort(
        by=[
            o_column.date_.name,  # По возрастанию (Столбец 'Дата')
            e_column.channel.name,  # По возрастанию (Столбец 'Телеканал')
            o_column.spot_distribution.name,  # По возрастанию (Столбец 'Ролик распространение')
            o_column.spot_type.name,  # По возрастанию (Столбец 'Ролик тип')
            e_column.time_start_standard.name,  # По возрастанию (Столбец 'Время начала [0-24]')
        ],
        descending=[False, False, False, False, False],
    )

    return df


def _drop_null(df: pl.DataFrame) -> pl.DataFrame:
    """
    Удаляет пустые столбцы из DataFrame.

    Args:
        df: Исходный DataFrame.

    Returns:
        DataFrame без пустых столбцов.
    """
    return df[[s.name for s in df if not (s.null_count() == df.height)]]


def _build_header(r1: tuple[str], r2: tuple[str], r3: tuple[str], exclude: tuple[str | None, ...]) -> list:
    """
    Генерирует заголовок на основании первых трех строк исходного DataFrame.

    Args:
        r1: Первая строка DataFrame.
        r2: Вторая строка DataFrame.
        r3: Третья строка DataFrame.
        exclude: Кортеж значений, которые должны быть исключены из заголовка и заменены на пустую строку.

    Returns:
        Заголовок DataFrame.
    """
    _r1 = [i if i not in exclude else '' for i in r1]
    _r2 = [i if i not in exclude else '' for i in r2]
    _r3 = [i if i not in exclude else '' for i in r3]

    return [' '.join((i, k, j)).strip() for i, k, j in zip(_r1, _r2, _r3)]


def _set_header(df: pl.DataFrame) -> pl.DataFrame:
    """
    Определяет заголовок DataFrame на основании первых трех строк исходного DataFrame.

    Args:
        df: Исходный DataFrame.

    Returns:
        DataFrame с обновленным заголовком и удаленными первыми тремя строками.
    """
    df.columns = _build_header(df.row(0), df.row(1), df.row(2), exclude=('TVR', 'Consolidated', None))
    return df.slice(3)


def _rename_header(df: pl.DataFrame) -> pl.DataFrame:
    """
    Переименовывает заголовки DataFrame согласно определенным правилам:
    - Удаляет лишние пробелы из каждого заголовка.
    - Идентифицирует и стандартизирует префиксы, связанные с 'BA'.
    - Идентифицирует и стандартизирует компоненты, связанные с TVR-метриками.
    - После всех преобразований для значений с префиксом BA,
        если сразу после BA не стоит 'TVR' или 'Std. TVR', добавляет 'TVR'.
    - Для рейтинговых столбцов без префикса BA/TVR/Std. TVR в начале добавляет 'TVR'.
        Нерейтинговым столбцам TVR не добавляется.
    """

    def _clean(s: str) -> str:
        return ' '.join(s.strip().split())

    def _map(col: str) -> str:
        s = _clean(col)
        parts: list[str] = []

        # 1. Обработка префикса BA
        if '!BA Reg 2020' in s:
            parts.append('BA')
            s = _clean(s.replace('!BA Reg 2020', '', 1))
        elif s.startswith('BA '):
            parts.append('BA')
            s = _clean(s[3:])

        # 2. Обработка TVR компонента
        if 'Reg. Stand. TVR (20)' in s:
            parts.append('Std. TVR')
            s = _clean(s.replace('Reg. Stand. TVR (20)', '', 1))
        elif 'Stand. TVR (20)' in s:
            parts.append('Std. TVR')
            s = _clean(s.replace('Stand. TVR (20)', '', 1))
        elif 'Reg. TVR' in s:
            parts.append('TVR')
            s = _clean(s.replace('Reg. TVR', '', 1))

        # 3. Общая замена 'Stand.' на 'Std.' в оставшейся части
        if 'Stand.' in s:
            s = _clean(s.replace('Stand.', 'Std.'))

        # 4. Удаление специфической фразы "Дом, Дача, Вне Дома"
        phrase = 'Дом, Дача, Вне Дома'
        if phrase in s:
            s = _clean(s.replace(phrase, ''))

        # 5. Оставшаяся часть строки
        if s:
            parts.append(s)

        # 6. Если у BA нет сразу TVR/Std. TVR, добавить TVR
        if parts and parts[0] == 'BA' and (len(parts) == 1 or parts[1] not in ('TVR', 'Std. TVR')):
            parts.insert(1, 'TVR')

        # 7. Для рейтинговых столбцов без BA/TVR/Std. TVR в начале добавить TVR.
        #    Признак рейтингового столбца — наличие цифр (целевой аудитории) или BA в исходном имени.
        if parts and parts[0] not in ('BA', 'TVR', 'Std. TVR'):
            is_rating = bool(re.search(r'\d', col)) or col.startswith('BA')
            if is_rating:
                parts.insert(0, 'TVR')

        return ' '.join(parts) or col

    df = df.rename({c: _map(c) for c in df.columns})

    # Заменяем 'Список товаров' на 'Список продуктов', если он есть в заголовке
    if 'Список товаров' in df.columns:
        df = df.rename({'Список товаров': 'Список продуктов'})

    return df


def _sort_header(df: pl.DataFrame) -> pl.DataFrame:
    """
    Сортирует заголовок DataFrame по определенному порядку.

    Args:
        df: Исходный DataFrame.

    Returns:
        DataFrame с отсортированным заголовком.
    """
    cols = df.columns
    tail_special = ['Кампания', 'Размещение']

    # 1. non-rating
    non_rating = [c for c in cols if 'TVR' not in c and 'GRP' not in c and c not in tail_special]

    # 2. базовые TVR
    fixed_tvr = [c for c in ('Sales TVR', 'Sales Std. TVR') if c in cols]

    # 3. аудитории
    tvr_cols = [c for c in cols if (c.startswith('TVR ') or c.startswith('Std. TVR ')) and c not in fixed_tvr]
    audiences = sorted({c.rsplit(' ', 1)[1] for c in tvr_cols})
    audience_tvr = []
    for aud in audiences:
        for prefix in ('TVR ', 'Std. TVR '):
            name = f'{prefix}{aud}'
            if name in cols:
                audience_tvr.append(name)

    # 4. остальные (кроме GRP и кампании/размещения)
    fixed_grp = ['GRP [округл.]', 'GRP20 [округл.]', 'GRP20 [min]']
    rest = [
        c
        for c in cols
        if c not in non_rating
        and c not in fixed_tvr
        and c not in audience_tvr
        and c not in fixed_grp
        and c not in tail_special
    ]

    # 5. GRP метрики
    grp_metrics = [c for c in fixed_grp if c in cols]

    # 6. кампании/размещения
    tail = [c for c in tail_special if c in cols]

    final_order = non_rating + fixed_tvr + audience_tvr + rest + grp_metrics + tail
    return df.select(final_order)
