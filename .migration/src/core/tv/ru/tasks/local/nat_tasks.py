import re

import polars as pl
import polars.selectors as sc

from app_assets import load_daytypes, load_nat_tvc_info
from core.tv.ru.tasks.local import schema
from core.tv.ru.tasks.local.logic import NatTVLogic, TVLogic
from core.utils.parser import Parser


def nat_base_task(df: pl.DataFrame) -> pl.DataFrame:
    # --- Загрузка служебной информации ---

    daytypes = load_daytypes()  # Тип дня
    tvc_info = load_nat_tvc_info()  # Справочник телекомпаний

    o_column = schema.NatOColumn()  # Оригинальные столбцы DataFrame
    e_column = schema.NatEColumn()  # Вычисляемые столбцы DataFrame

    # --- Предварительная обработка ---

    df = _drop_null(df)  # Удаление пустых столбцов
    df = _set_header(df)  # Определение и установка заголовка

    # Преобразование столбцов к нужному типу данных (str -> Float65 | Datetime)
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
        .map_elements(lambda x: NatTVLogic.get_weekday_name(x), return_dtype=pl.String)
        .alias(e_column.weekday_name.name)
    )

    # Создание столбца 'Время начала [0-24]
    df = df.with_columns(
        pl.col(o_column.spot_time_start.name)
        .map_elements(lambda x: NatTVLogic.normalize_time_format(x, as_string=True), return_dtype=pl.String)
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
        .map_elements(lambda x: NatTVLogic.get_time_interval(x), return_dtype=pl.String)
        .alias(e_column.time_interval_standard.name),
    )

    # Создание столбца 'Платформа оригинала'
    df = df.with_columns(
        pl.col(o_column.tv_company.name)
        .map_elements(
            lambda x: schema.Platform.TV.value if NatTVLogic.is_tvc(x) else schema.Platform.INTERNET.value,
            return_dtype=pl.String,
        )
        .alias(e_column.original_platform.name),
    )

    # Редактирование значений в столбце 'Телекомпания'. Удаление скобок и их содержимого (СЕТЕВОЕ ВЕЩАНИЕ)
    df = df.with_columns(
        pl.col(o_column.tv_company.name)
        .map_elements(lambda x: NatTVLogic.to_clean_tvc(x), return_dtype=pl.String)
        .alias(o_column.tv_company.name)
    )

    # Создание столбца 'Тип канала'
    df = df.with_columns(
        pl.col(o_column.tv_company.name)
        .map_elements(lambda x: NatTVLogic.get_tvc_type(x, tvc_info), return_dtype=pl.String)
        .alias(e_column.channel_type.name)
    )

    # Создание столбца 'Целевая аудитория'
    df = df.with_columns(
        pl.col(o_column.tv_company.name)
        .map_elements(lambda x: NatTVLogic.get_tvc_audience(x, tvc_info), return_dtype=pl.String)
        .alias(e_column.buying_audience.name),
    )

    # Создание столбца 'Телеканал №'. Для орбитального и сетевого вещания имена отличаются
    df = df.with_columns(
        pl.struct(
            [
                pl.col(o_column.tv_company.name),
                pl.col(o_column.spot_distribution.name),
            ]
        )
        .map_elements(
            lambda row: NatTVLogic.get_tvc_number(
                row[o_column.tv_company.name],
                row[o_column.spot_distribution.name],
                tvc_info,
            ),
            return_dtype=pl.Int64,
        )
        .alias(e_column.channel_number.name)
    )

    # Создание столбца 'Телеканал'
    df = df.with_columns(
        pl.struct(
            [
                pl.col(o_column.tv_company.name),
                pl.col(o_column.spot_distribution.name),
            ]
        )
        .map_elements(
            lambda row: NatTVLogic.get_tvc_name(
                row[o_column.tv_company.name],
                row[o_column.spot_distribution.name],
                tvc_info,
            ),
            return_dtype=pl.String,
        )
        .alias(e_column.channel.name)
    )

    # Создание столбца 'Позиционирование'
    df = df.with_columns(
        pl.when(
            pl.col(o_column.spot_positioning.name).eq(schema.Position.MIDDLE.value),
        )
        .then(pl.lit(schema.Position.MIDDLE.value))
        .otherwise(pl.lit(schema.Position.PREMIUM.value))
        .alias(e_column.positioning.name)
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
                pl.col(e_column.channel_type.name),
            ]
        )
        .map_elements(
            lambda row: schema.PrimeTime.PT.value
            if NatTVLogic.is_prime(
                TVLogic.get_hour(row[e_column.time_start_standard.name]),
                row[e_column.daytype.name].lower() != 'рабочий',
                row[e_column.channel_type.name].lower() == 'нац',
            )
            else schema.PrimeTime.OP.value,
            return_dtype=pl.String,
        )
        .alias(e_column.prime_time.name),
    )

    # --- Расчет TVR статистик ---

    # Объединение строк 'ТВ' и 'Интернет' вещания. Суммирование значений
    rating_columns = [col for col in df.columns if re.search(r'TV|Mobile|Desktop', col, re.IGNORECASE)]

    sum_exprs = [pl.sum(col).alias(col) for col in rating_columns]
    df_group = df.group_by(o_column.spot_id_out_original.name).agg(sum_exprs)

    non_rating_columns = [col for col in df.columns if col not in rating_columns]

    df_meta = (
        df.filter(pl.col(e_column.original_platform.name) == schema.Platform.TV.value)
        .select(non_rating_columns)
        .drop(e_column.original_platform.name)
        .unique(subset=[o_column.spot_id_out_original.name], keep='first')
    )

    df = df_meta.join(df_group, on=o_column.spot_id_out_original.name, how='left')

    # Расчет Sales TVR (TV, Desktop, Mobile)
    tv_columns = [col for col in df.columns if re.search(r'TV BA', col, re.IGNORECASE)]
    desktop_columns = [col for col in df.columns if re.search(r'Desktop BA', col, re.IGNORECASE)]
    mobile_columns = [col for col in df.columns if re.search(r'Mobile BA', col, re.IGNORECASE)]

    # TV
    tv_expr = pl.lit(None, dtype=pl.Float64)

    for col_name in reversed(tv_columns):
        tv_expr = (
            pl.when(pl.col(e_column.buying_audience.name) == col_name.removeprefix('TV BA '))
            .then(pl.col(col_name))
            .otherwise(tv_expr)
        )

    tv_expr = (
        pl.when(pl.col(e_column.buying_audience.name) == schema.Sale.MIN.value).then(pl.lit(0.0)).otherwise(tv_expr)
    )

    # Desktop
    desktop_expr = pl.lit(None, dtype=pl.Float64)

    for col_name in reversed(desktop_columns):
        desktop_expr = (
            pl.when(pl.col(e_column.buying_audience.name) == col_name.removeprefix('Desktop BA '))
            .then(pl.col(col_name))
            .otherwise(desktop_expr)
        )

    desktop_expr = (
        pl.when(pl.col(e_column.buying_audience.name) == schema.Sale.MIN.value)
        .then(pl.lit(0.0))
        .otherwise(desktop_expr)
    )

    # Mobile
    mobile_expr = pl.lit(None, dtype=pl.Float64)

    for col_name in reversed(mobile_columns):
        mobile_expr = (
            pl.when(pl.col(e_column.buying_audience.name) == col_name.removeprefix('Mobile BA '))
            .then(pl.col(col_name))
            .otherwise(mobile_expr)
        )

    mobile_expr = (
        pl.when(pl.col(e_column.buying_audience.name) == schema.Sale.MIN.value).then(pl.lit(0.0)).otherwise(mobile_expr)
    )

    df = df.with_columns(
        tv_expr.alias(e_column.sales_tvr_tv.name),
        desktop_expr.alias(e_column.sales_tvr_desktop.name),
        mobile_expr.alias(e_column.sales_tvr_mobile.name),
    )

    # Расчет Std. TVR и Big Sales TVR
    df = df.with_columns(
        # Считаем Sales Std. TVR (используя только что созданные столбцы)
        ((pl.col(e_column.sales_tvr_tv.name) * pl.col(o_column.spot_expected_duration.name)) / 20.0).alias(
            e_column.sales_std_tvr_tv.name
        ),
        ((pl.col(e_column.sales_tvr_desktop.name) * pl.col(o_column.spot_expected_duration.name)) / 20.0).alias(
            e_column.sales_std_tvr_desktop.name
        ),
        ((pl.col(e_column.sales_tvr_mobile.name) * pl.col(o_column.spot_expected_duration.name)) / 20.0).alias(
            e_column.sales_std_tvr_mobile.name
        ),
    ).with_columns(
        # Считаем Big Sales TVR (используя только что созданные столбцы)
        pl.sum_horizontal(
            e_column.sales_tvr_tv.name,
            e_column.sales_tvr_desktop.name,
            e_column.sales_tvr_mobile.name,
        ).alias(e_column.big_sales_tvr.name),
        pl.sum_horizontal(
            e_column.sales_std_tvr_tv.name,
            e_column.sales_std_tvr_desktop.name,
            e_column.sales_std_tvr_mobile.name,
        ).alias(e_column.big_sales_std_tvr.name),
    )

    # Удаление столбцов с баинговыми аудиториями
    df = df.select([col for col in df.columns if ' BA' not in col])

    # Расчет TVR статистик по целевым аудиториям
    tv_target_cols = [col for col in df.columns if col.startswith('TV') and 'BA' not in col]
    targets = sorted(list(set(col.replace('TV ', '') for col in tv_target_cols)))
    duration_col = pl.col(o_column.spot_expected_duration.name)  # Короткая ссылка на длительность

    tvr_exprs = []
    std_exprs = []
    big_exprs = []
    cols_to_drop = []

    for target in targets:
        # Имена исходных и новых колонок
        tv_col, desk_col, mob_col = f'TV {target}', f'Desktop {target}', f'Mobile {target}'
        tvr_tv, tvr_desk, tvr_mob = f'TVR {target} TV', f'TVR {target} Desktop', f'TVR {target} Mobile'
        std_tv, std_desk, std_mob = f'Std. TVR {target} TV', f'Std. TVR {target} Desktop', f'Std. TVR {target} Mobile'
        big_tvr, big_std = f'Big TVR {target}', f'Big Std. TVR {target}'

        # Создание TVR
        if tv_col in df.columns:
            tvr_exprs.append(pl.col(tv_col).alias(tvr_tv))
            cols_to_drop.append(tv_col)  # Помечаем исходный столбец для удаления

        if desk_col in df.columns:
            tvr_exprs.append(pl.col(desk_col).alias(tvr_desk))
            cols_to_drop.append(desk_col)

        if mob_col in df.columns:
            tvr_exprs.append(pl.col(mob_col).alias(tvr_mob))
            cols_to_drop.append(mob_col)

        # Расчет Std. TVR
        std_exprs.extend(
            [
                (pl.col(tvr_tv) * duration_col / 20.0).alias(std_tv),
                (pl.col(tvr_desk) * duration_col / 20.0).alias(std_desk),
                (pl.col(tvr_mob) * duration_col / 20.0).alias(std_mob),
            ]
        )

        # Расчет Big TVR и Big Std. TVR
        big_exprs.extend(
            [
                pl.sum_horizontal(tvr_tv, tvr_desk, tvr_mob).alias(big_tvr),
                pl.sum_horizontal(std_tv, std_desk, std_mob).alias(big_std),
            ]
        )

    df = df.with_columns(tvr_exprs)
    df = df.with_columns(std_exprs)
    df = df.with_columns(big_exprs)

    df = df.drop(list(set(cols_to_drop)))

    # Создание столбца 'Округление'
    df = df.with_columns(
        pl.struct(
            [
                pl.col(o_column.tv_company.name),
                pl.col(o_column.spot_distribution.name),
                pl.col(e_column.year.name),
            ]
        )
        .map_elements(
            lambda row: NatTVLogic.get_tvc_round(
                row[o_column.tv_company.name], row[o_column.spot_distribution.name], row[e_column.year.name], tvc_info
            ),
            return_dtype=pl.Float64,
        )
        .alias(e_column.rounding.name)
    )

    # Создание столбца 'GRP [округл.]'
    df = df.with_columns(
        pl.max_horizontal(e_column.big_sales_tvr.name, e_column.rounding.name).alias(e_column.grp_rounding.name)
    )

    # Создание столбца 'GRP20 [округл.]'
    df = df.with_columns(
        (pl.col(e_column.grp_rounding.name) * pl.col(o_column.spot_expected_duration.name) / 20.0).alias(
            e_column.grp20_rounding.name
        )
    )

    # Создание столбца 'GRP20 [min]'
    df = df.with_columns(
        pl.when(
            pl.col(o_column.spot_type.name) == schema.SpotType.CLIP.value,
        )
        .then(pl.col(e_column.grp20_rounding.name))
        .otherwise(pl.col(o_column.spot_expected_duration.name) / 60.0)
        .alias(e_column.grp20_min.name)
    )

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

    # Изъятие из схемы столбца 'Платформа оригинала' (не используется в выводе)
    _schema.pop(e_column.original_platform.name)

    df = df.cast(_schema)

    # Сортировка заголовка
    df = df.select(_sort_header(df.columns))

    # Сортировка значений
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
        exclude: Кортеж значений, которые должно быть исключены из заголовка и заменены на пустую строку.

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

    return df.slice(4)


def _sort_header(columns: list[str]) -> list[str]:
    """
    Сортирует названия столбцов по специфическим правилам, используя регулярные выражения и словари.

    Порядок сортировки:
        1. Столбцы без рейтингов (с сохранением исходного относительного порядка).
        2. Метрики 'Sales' (TVR -> Std. TVR -> Big -> Big Std.; внутри типа: TV -> Desktop -> Mobile).
        3. Метрики с аудиториями (группируются по названию аудитории в алфавитном порядке, затем TVR перед GRP):
            - Внутри типа TVR/GRP: Базовый -> Std. -> Big -> Big Std.
            - Внутри Базовый/Std.: TV -> Desktop -> Mobile (если применимо).
        4. Специальные GRP метрики ('GRP округл.', 'GRP20 округл.', 'GRP20/min').
        5. 'Кампания', затем 'Размещение' в конце.

    Args:
        columns: Список строк с названиями столбцов для сортировки.

    Returns:
        Новый список с названиями столбцов, отсортированными согласно правилам.
    """
    original_indices: dict[str, int] = {name: i for i, name in enumerate(columns)}

    # --- Карты для преобразования строк в числовые ключи сортировки ---
    platform_map: dict[str, int] = {'TV': 0, 'Desktop': 1, 'Mobile': 2}

    # Основные типы рейтинга + префиксы для аудиторных столбцов
    stat_type_map: dict[str, int] = {
        'TVR': 0,
        'Std. TVR': 1,
        'Big TVR': 2,
        'Big Std. TVR': 3,
        'GRP': 10,
        'Std. GRP': 11,
        'Big GRP': 12,
        'Big Std. GRP': 13,  # GRP > TVR
    }

    # Специальные GRP столбцы
    specific_grp_map: dict[str, int] = {'GRP [округл.]': 0, 'GRP20 [округл.]': 1, 'GRP20 [min.]': 2}

    # Sales столбцы (без аудитории)
    sales_map: dict[str, tuple[int, int]] = {
        'Sales TVR TV': (1, 0),
        'Sales TVR Desktop': (1, 1),
        'Sales TVR Mobile': (1, 2),
        'Sales Std. TVR TV': (2, 0),
        'Sales Std. TVR Desktop': (2, 1),
        'Sales Std. TVR Mobile': (2, 2),
        'Big Sales TVR': (3, 0),
        'Big Sales Std. TVR': (4, 0),
    }

    # --- Регулярное выражение для разбора столбцов с аудиторией ---
    audience_re = re.compile(r'^(Std\.|Big|Big Std\.)?\s?(TVR|GRP)\s(.*?)(?:\s(TV|Desktop|Mobile))?$')

    # --- Функция для генерации ключа сортировки ---
    def _get_key(col: str) -> tuple:
        """
        Генерирует ключ для сортировки столбца на основе его имени.

        Args:
            col (str): Имя столбца.

        Returns:
            tuple: Кортеж с маркером для сортировки.
        """
        # 1. Особые случаи: Кампания и Размещение (в конец)
        if col == 'Кампания':
            return (100, 0, '', 0, 0)
        if col == 'Размещение':
            return (100, 1, '', 0, 0)

        # 2. Sales столбцы (без аудитории)
        if col in sales_map:
            cat, sub_key = sales_map[col]
            return (cat, sub_key, '', 0, -1)

        # 3. Столбцы с аудиторией
        match = audience_re.match(col)
        if match:
            prefix, rating_type, audience, platform = match.groups()
            full_stat_type = f'{prefix.strip()} {rating_type}'.strip() if prefix else rating_type
            stat_key = stat_type_map.get(full_stat_type, 99)
            platform_key = platform_map.get(platform, -1)
            return (10, audience.strip(), stat_key, platform_key, 0)

        # 4. Специальные GRP столбцы
        if col in specific_grp_map:
            return (20, specific_grp_map[col], '', 0, -1)

        # 5. Остальные столбцы (в начало, сохраняя порядок)
        return (0, original_indices[col], '', 0, -1)

    # Сортировка с использованием lambda, вызывающей get_key
    return sorted(columns, key=lambda c: _get_key(c))
