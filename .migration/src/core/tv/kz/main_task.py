import datetime
import io
import logging
import re

import polars as pl
import polars.selectors as sc

from app_assets import load_kz_channels
from core.tv.kz import logic
from core.tv.kz.enums import Column, ConfigKey, Constant, PrimeTime, Seller
from core.tv.kz.exceptions import CalculationError, ConfigError, StructureError
from core.tv.kz.logic import get_date_parts, get_time_parts
from core.utils.tools import TextTools

KZ_CHANNELS_DATA = load_kz_channels()

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def _sort_columns(cols: list[str]) -> list[str]:
    non_stats_cols: list[str] = []  # Список для не-статистических столбцов.
    stats_cols: list[str] = []  # Список для статистических столбцов.
    # Паттерн для определения статистических столбцов.
    # Группы: 1=Префикс(BlkGRP%|GRP), 2=Модификатор(все остальное до аудитории), 3=Аудитория
    pat = r'^(BlkGRP%|GRP)((?:\s*\[30 сек\.\])?(?:\s*\((?:округл\.|округл\. точн\.)\))?)?(?:\s+(.+))?$'

    # Внутренняя функция для генерации ключа сортировки СТАТИСТИЧЕСКИХ столбцов.
    def _get_key(c: str) -> tuple:  # type: ignore
        m = re.match(pat, c.strip())
        # Не стат. столбец (самый высокий первый ключ) - на всякий случай, если попадет сюда.
        if not m:
            return (2, c, 0)

        pfx, mod, aud = m.groups()
        mod = mod.strip() if mod else ''
        aud = aud.strip() if aud else ''

        # Определяем 'проход': 0 для базовых/Total Ind., 1 для специфических аудиторий.
        is_pass_0 = aud == '' or aud == 'Total Ind.'
        pass_indicator = 0 if is_pass_0 else 1

        # Базовые характеристики для определения порядка.
        is_blk = pfx == 'BlkGRP%'
        is_30sec = '[30 сек.]' in mod
        is_round = '(округл.)' in mod
        is_not_round = '(округл. точн.)' in mod

        # Приоритет модификатора: 0=базовый, 1=30сек, 2=30сек(округл.), 3=30сек(округл. точн.).
        mod_prio = 0
        if is_30sec:
            if is_round:
                mod_prio = 2
            elif is_not_round:
                mod_prio = 3
            else:
                mod_prio = 1

        if is_pass_0:
            # --- Логика для Прохода 0 (Без аудитории / Total Ind.) ---
            # Порядок: Blk, Blk30, Blk30Rnd, Blk30NotRnd, BlkTotal, GRP, GRP30, GRP30Rnd, GRP30NotRnd, GRPTotal.
            pass0_prio = 0  # Приоритет внутри этого прохода.
            if is_blk:  # BlkGRP%.
                if aud == 'Total Ind.':
                    pass0_prio = 4  # Blk Total.
                else:
                    pass0_prio = mod_prio  # 0=Blk base, 1=Blk 30, 2=Blk 30 Rnd, 3=Blk 30 NotRnd
            else:  # GRP.
                if aud == 'Total Ind.':
                    pass0_prio = 9  # GRP Total.
                else:
                    pass0_prio = mod_prio + 5  # 5=GRP base, 6=GRP 30, 7=GRP 30 Rnd, 8=GRP 30 NotRnd
            # Ключ: (0=проход_0, приоритет_в_проходе_0, 0=заглушка_для_сорт_по_ауд).
            return (pass_indicator, pass0_prio, 0)

        else:
            # --- Логика для Прохода 1 (Специфические аудитории) ---
            # Порядок внутри аудитории: Blk, Blk30, Blk30Rnd, Blk30NotRnd, GRP, GRP30, GRP30Rnd, GRP30NotRnd.
            pass1_prio = 0  # Приоритет внутри аудитории.
            if is_blk:  # BlkGRP%.
                pass1_prio = mod_prio  # 0=Blk [Aud], 1=Blk 30 [Aud], 2=Blk 30 Rnd [Aud], 3=Blk 30 NotRnd [Aud]
            else:  # GRP.
                pass1_prio = mod_prio + 4  # 4=GRP [Aud], 5=GRP 30 [Aud], 6=GRP 30 Rnd [Aud], 7=GRP 30 NotRnd [Aud]
            # Ключ: (1=проход_1, имя_аудитории_для_сортировки, приоритет_внутри_аудитории).
            return (pass_indicator, aud, pass1_prio)

    # Разделение исходного списка на две группы.
    for c in cols:
        if re.match(pat, c.strip()):
            stats_cols.append(c)
        else:
            non_stats_cols.append(c)

    # Сортировка *только* списка статистических столбцов с новым ключом.
    sorted_stats = sorted(stats_cols, key=_get_key)  # type: ignore

    # Объединение: сначала не-статистические, затем отсортированные статистические.
    return non_stats_cols + sorted_stats


def _fill_row(row: list[str | None]) -> list[str]:
    target_list: list[str] = []
    non_empty_value = ''
    for item in row:
        current_value = '' if item is None else str(item)

        if current_value == '':
            target_list.append(non_empty_value)
        else:
            non_empty_value = current_value
            target_list.append(current_value)

    return target_list


def _transform_main_task(df: pl.DataFrame) -> pl.DataFrame:
    log.info('Трансформация выгрузки из InStar KZ...')

    log.debug('Поиск маркера для разделения статистик.')
    row_1_values = df.row(0, named=False)
    row_2_values = df.row(1, named=False)

    row_1_filled = _fill_row(list(row_1_values))
    row_2_filled = ['' if v is None else str(v) for v in row_2_values]

    split_column_index = -1

    for i, value in enumerate(row_1_filled):
        if value.strip():
            split_column_index = i
            break

    if split_column_index == -1:
        log.error('Не удалось найти маркер для разделения статистик.')
        raise StructureError('Не удалось найти маркер для разделения статистик.')
    else:
        log.debug('Маркер для разделения статистик найден.')

    log.debug('Определение заголовка.')
    final_column_names: list[str] = []
    num_columns = df.width

    for i in range(num_columns):
        part_1 = row_1_filled[i].strip()
        part_2 = row_2_filled[i].strip()

        if i < split_column_index:
            final_column_names.append(part_2)
        else:
            part_1 = '' if part_1 == 'Units >>' else part_1

            full_header = f'{part_1} {part_2}'.strip()
            final_column_names.append(full_header)

    df = df.slice(2, None)
    df.columns = final_column_names
    log.debug('Заголовок определен.')

    log.debug('Приведение столбцов к целевым типам.')
    for column in df.columns:
        try:
            df = df.with_columns(
                pl.col(column)
                .str.strip_chars()
                .map_elements(lambda x: '0' if x in ('.') else x, return_dtype=pl.String)
                .cast(pl.Float64, strict=True)
                .alias(column)
            )
        except pl.exceptions.InvalidOperationError:
            continue
    else:
        log.debug('Столбцы приведены к целевым типам.')

    log.info('Трансформация выгрузки из InStar KZ успешно завершена.')
    return df


def _calculate_main_task(df: pl.DataFrame) -> pl.DataFrame:
    log.info('Расчет основной выгрузки...')

    try:
        spot_positions: list[int] = df.get_column(Column.SPOT_POSITION.value).to_list()
        spots_counts: list[int] = df.get_column(Column.SPOTS_COUNT.value).to_list()
        positions: list[str] = [logic.get_spot_position(pos, cnt) for pos, cnt in zip(spot_positions, spots_counts)]
    except Exception:
        log.error('Ошибка при вычислении позиции ролика в блоке.', exc_info=True)
        raise CalculationError('Ошибка при вычислении позиции ролика в блоке.')

    try:
        df = df.with_columns(
            pl.Series(name=Column.POSITION.value, values=positions, dtype=pl.String),
        )
    except Exception:
        log.error('Ошибка при создании столбца с позицией ролика в блоке.', exc_info=True)
        raise StructureError('Ошибка при создании нового столбца с позицией ролика в блоке.')

    try:
        months = [get_date_parts(date_str)[1] for date_str in df.get_column(Column.DATE.value).to_list()]
        df = df.with_columns(
            pl.Series(name=Column.MONTH.value, values=months, dtype=pl.Int64),
        )
    except Exception:
        log.error('Ошибка при создании столбца с порядковым номером месяца.', exc_info=True)
        raise StructureError('Ошибка при создании столбца с порядковым номером месяца.')

    try:
        weeks: list[int] = []

        for string in df.get_column(Column.DATE.value).to_list():
            year, month, day = get_date_parts(string)
            weeks.append(datetime.date(year, month, day).isocalendar()[1])

        df = df.with_columns(
            pl.Series(name=Column.WEEK.value, values=weeks, dtype=pl.Int64),
        )
    except Exception:
        log.error('Ошибка при создании столбца с номером недели (ISO).', exc_info=True)
        raise StructureError('Ошибка при создании столбца с номером недели (ISO).')

    try:
        start_hours = [
            get_time_parts(time_str)[0] for time_str in df.get_column(Column.SPOT_START_TIME.value).to_list()
        ]
        end_hours = [get_time_parts(time_str)[0] for time_str in df.get_column(Column.SPOT_END_TIME.value).to_list()]
        prime_times = [
            PrimeTime.PRIME.value if logic.is_prime_time(sh, eh) else PrimeTime.OFF_PRIME.value
            for sh, eh in zip(start_hours, end_hours)
        ]

        df = df.with_columns(
            pl.Series(name=Column.PRIME.value, values=prime_times, dtype=pl.String),
        )
    except Exception:
        log.error('Ошибка при создании столбца с Prime.', exc_info=True)
        raise StructureError('Ошибка при создании столбца с Prime.')

    try:
        channels = df.get_column(Column.SPOT_TV_COMPANY.value).to_list()
        audiences: list[str] = [KZ_CHANNELS_DATA[channel][ConfigKey.AUDIENCE.value] for channel in channels]
        rounds: list[str] = [KZ_CHANNELS_DATA[channel][ConfigKey.ROUND.value] for channel in channels]
        sellers: list[str] = [KZ_CHANNELS_DATA[channel][ConfigKey.SELLER.value] for channel in channels]
    except Exception:
        log.error('Ошибка при обращении к конфигурации телеканалов.', exc_info=True)
        raise ConfigError('Ошибка при обращении к конфигурации телеканалов.')

    try:
        df = df.with_columns(
            pl.Series(name=Column.AUDIENCE.value, values=audiences, dtype=pl.String),
            pl.Series(name=Column.ROUND.value, values=rounds, dtype=pl.Float64),
            pl.Series(name=Column.SELLER.value, values=sellers, dtype=pl.String),
        )
    except Exception:
        log.error('Ошибка при создании вспомогательных столбцов.', exc_info=True)
        raise StructureError('Ошибка при создании вспомогательных столбцов.')

    # --- Расчет основных статистик BlkGRP%, GRP, GRP [30 сек.] ---
    try:
        blk_grp = [row[f'BlkGRP% !BA {audience}'] for audience, row in zip(audiences, df.iter_rows(named=True))]
        grp = [row[f'GRP !BA {audience}'] for audience, row in zip(audiences, df.iter_rows(named=True))]
        grp_30 = [row[f'GRP [30 sec.] !BA {audience}'] for audience, row in zip(audiences, df.iter_rows(named=True))]
    except Exception:
        log.error('Ошибка при вычислении основных статистик.', exc_info=True)
        raise CalculationError('Ошибка при вычислении основных статистик.')

    try:
        df = df.with_columns(
            pl.Series(name=Column.BLK_GRP_PERCENT.value, values=blk_grp, dtype=pl.Float64),
            pl.Series(name=Column.GRP.value, values=grp, dtype=pl.Float64),
            pl.Series(name=Column.GRP_30_SEC.value, values=grp_30, dtype=pl.Float64),
        )
    except Exception:
        log.error('Ошибка при создании столбцов с основными статистиками.', exc_info=True)
        raise StructureError('Ошибка при создании столбцов с основными статистиками.')

    # --- Расчет BlkGRP% [30 сек.] ---
    try:
        df = df.with_columns(
            (
                (pl.col(Column.BLK_GRP_PERCENT.value) * pl.col(Column.SPOT_EXPECTED_DURATION.value))
                / Constant.STANDARD_DURATION_SECONDS.value
            ).alias(Column.BLK_GRP_PERCENT_30_SEC.value),
        )
    except Exception:
        log.error('Ошибка при вычислении BlkGRP% [30 сек.].', exc_info=True)
        raise CalculationError('Ошибка при вычислении BlkGRP% [30 сек.].')

    # --- Расчет BlkGRP% [30 сек.] (округл.) ---
    try:
        df = df.with_columns(
            pl.when(pl.col(Column.SELLER.value) == Seller.TBM.value)
            .then(
                # Логика для TBM: Порог -> Масштаб -> Округление
                (
                    pl.when(pl.col(Column.BLK_GRP_PERCENT.value) < pl.col(Column.ROUND.value))
                    .then(pl.col(Column.ROUND.value))
                    .otherwise(pl.col(Column.BLK_GRP_PERCENT.value))
                    * pl.col(Column.SPOT_EXPECTED_DURATION.value)
                    / Constant.STANDARD_DURATION_SECONDS.value
                ).round(Constant.STANDARD_ROUNDING_PRECISION.value)
            )
            .when(pl.col(Column.SELLER.value) == Seller.VI.value)
            .then(
                (
                    # Логика для VI: Порог -> Масштаб -> БЕЗ Округления до 2 знаков.
                    pl.when(pl.col(Column.BLK_GRP_PERCENT.value) < pl.col(Column.ROUND.value))
                    .then(pl.col(Column.ROUND.value))
                    .otherwise(pl.col(Column.BLK_GRP_PERCENT.value))
                    * pl.col(Column.SPOT_EXPECTED_DURATION.value)
                    / Constant.STANDARD_DURATION_SECONDS.value
                )
            )
            .when(pl.col(Column.SELLER.value) == Seller.IMS_MN.value)
            .then(
                # Логика для IMS/MN: Масштаб -> Порог -> Округление
                pl.when(
                    # Условие: Масштабированное значение < Порог
                    (
                        pl.col(Column.BLK_GRP_PERCENT.value)
                        * pl.col(Column.SPOT_EXPECTED_DURATION.value)
                        / Constant.STANDARD_DURATION_SECONDS.value
                    )
                    < pl.col(Column.ROUND.value)
                )
                .then(
                    # Если условие True: взять Порог
                    pl.col(Column.ROUND.value)
                )
                .otherwise(
                    (
                        # Если условие False: взять Масштабированное значение
                        pl.col(Column.BLK_GRP_PERCENT.value)
                        * pl.col(Column.SPOT_EXPECTED_DURATION.value)
                        / Constant.STANDARD_DURATION_SECONDS.value
                    )
                )
                .round(Constant.STANDARD_ROUNDING_PRECISION.value)  # Округляем итоговый результат
            )
            .alias(Column.BLK_GRP_PERCENT_30_SEC_ROUNDED.value)
        )
    except Exception as e:
        log.error(f'Ошибка при вычислении BlkGRP% [30 сек.] (округл.): {e}', exc_info=True)
        raise CalculationError(f'Ошибка при вычислении BlkGRP% [30 сек.] (округл.): {e}') from e

    # --- Расчет GRP [30 сек.] (округл. точн.) ---
    try:
        df = df.with_columns(
            pl.when(pl.col(Column.SELLER.value) == Seller.IMS_MN.value)
            .then(
                pl.when(
                    (
                        (
                            pl.col(Column.GRP.value).round(Constant.STANDARD_ROUNDING_PRECISION.value)
                            * pl.col(Column.SPOT_EXPECTED_DURATION.value)
                        )
                        / (Constant.STANDARD_DURATION_SECONDS.value)
                    )
                    < pl.col(Column.ROUND.value)
                )
                .then(pl.col(Column.ROUND.value))
                .otherwise(
                    (
                        pl.col(Column.GRP.value).round(Constant.STANDARD_ROUNDING_PRECISION.value)
                        * pl.col(Column.SPOT_EXPECTED_DURATION.value)
                    )
                    / (Constant.STANDARD_DURATION_SECONDS.value)
                )
            )
            .otherwise(
                pl.when(
                    pl.col(Column.GRP.value).round(Constant.STANDARD_ROUNDING_PRECISION.value)
                    < pl.col(Column.ROUND.value)
                )
                .then(pl.col(Column.ROUND.value))
                .otherwise(
                    pl.col(Column.GRP.value).round(Constant.STANDARD_ROUNDING_PRECISION.value)
                    * pl.col(Column.SPOT_EXPECTED_DURATION.value)
                    / Constant.STANDARD_DURATION_SECONDS.value
                )
            )
            .alias(Column.GRP_30_SEC_NOT_ROUNDED.value)
        )
    except Exception:
        log.error('Ошибка при вычислении GRP [30 сек.] (округл. точн.).', exc_info=True)
        raise CalculationError('Ошибка при вычислении GRP [30 сек.] (округл. точн.)')

    # --- Расчет GRP [30 сек.] (округл.) ---
    try:
        df = df.with_columns(
            pl.when(pl.col(Column.SELLER.value) == Seller.IMS_MN.value)
            .then(
                pl.when(
                    (
                        (
                            pl.col(Column.GRP.value).round(Constant.STANDARD_ROUNDING_PRECISION.value)
                            * pl.col(Column.SPOT_EXPECTED_DURATION.value)
                        )
                        / (Constant.STANDARD_DURATION_SECONDS.value)
                    )
                    < pl.col(Column.ROUND.value)
                )
                .then(pl.col(Column.ROUND.value))
                .otherwise(
                    (
                        pl.col(Column.GRP.value).round(Constant.STANDARD_ROUNDING_PRECISION.value)
                        * pl.col(Column.SPOT_EXPECTED_DURATION.value)
                    )
                    / (Constant.STANDARD_DURATION_SECONDS.value)
                )
            )
            .otherwise(
                pl.when(
                    pl.col(Column.GRP.value).round(Constant.STANDARD_ROUNDING_PRECISION.value)
                    < pl.col(Column.ROUND.value)
                )
                .then(pl.col(Column.ROUND.value))
                .otherwise(
                    pl.col(Column.GRP.value).round(Constant.STANDARD_ROUNDING_PRECISION.value)
                    * pl.col(Column.SPOT_EXPECTED_DURATION.value)
                    / Constant.STANDARD_DURATION_SECONDS.value
                )
            )
            .round(Constant.STANDARD_ROUNDING_PRECISION.value)
            .alias(Column.GRP_30_SEC_ROUNDED.value)
        )
    except Exception:
        log.error('Ошибка при вычислении GRP [30 сек.] (округл.).', exc_info=True)
        raise CalculationError('Ошибка при вычислении GRP [30 сек.] (округл.)')

    try:
        log.debug('Поиск целевых аудиторий.')
        target_audiences: list[str] = []
        for col in df.columns:
            if (
                ('BlkGRP%' not in col)
                or (col == Column.BLK_GRP_PERCENT.value)
                or any(sub in col for sub in ['BA', 'Total', '[30 сек.]'])
            ):
                log.debug(f'Целевая аудитория не найдена. [столбец: {col}]')
                continue
            _, audience = col.split('BlkGRP% ')
            log.debug(f'Целевая аудитория найдена. [столбец: {col}] [аудитория: {audience}]')
            target_audiences.append(audience.strip())
    except Exception:
        log.error('Ошибка при поиске целевых аудиторий.', exc_info=True)
        raise CalculationError('Ошибка при получении списка целевых аудиторий.')
    else:
        log.debug(f'Целевые аудитории найдены. [{", ".join(target_audiences)}]')

    if not target_audiences:
        log.error('Не удалось найти целевые аудитории.', exc_info=True)
        raise CalculationError('Не удалось найти целевые аудитории.')

    for audience in target_audiences:
        try:
            df = df.with_columns(
                pl.Series(
                    name=f'{Column.BLK_GRP_PERCENT.value} {audience}',
                    values=[row[f'BlkGRP% {audience}'] for row in df.iter_rows(named=True)],
                    dtype=pl.Float64,
                ),
                pl.Series(
                    name=f'{Column.GRP.value} {audience}',
                    values=[row[f'GRP {audience}'] for row in df.iter_rows(named=True)],
                    dtype=pl.Float64,
                ),
                pl.Series(
                    name=f'{Column.GRP_30_SEC.value} {audience}',
                    values=[row[f'GRP [30 sec.] {audience}'] for row in df.iter_rows(named=True)],
                    dtype=pl.Float64,
                ),
            )
        except Exception:
            log.error(f'Ошибка при создании столбцов основных статистик для аудитории [{audience}].', exc_info=True)
            raise StructureError(f'Ошибка при создании столбцов основных статистик для аудитории [{audience}].')

    # --- Расчет доли двойных выходов ---
    log.debug('Начало расчета доли двойных выходов.')
    df = df.with_columns(
        (
            pl.col(Column.SPOT_TV_COMPANY).cast(pl.String)
            + pl.col(Column.DATE).cast(pl.String)
            + pl.col(Column.BREAK_START_TIME).cast(pl.String)
            + pl.col(Column.SPOT_ID).cast(pl.String)
        )
        .map_elements(lambda x: TextTools.get_hash(x), return_dtype=pl.String)
        .alias(Column.UNIQUE_ID.value)
    )
    log.debug('Уникальные идентификаторы созданы.')

    temp_df = df.group_by(pl.col(Column.UNIQUE_ID.value)).agg(
        pl.col(Column.SPOT_ID.value).count().alias(Column.COUNT.value)
    )
    log.debug('Группировка по уникальному идентификатору завершена.')

    temp_df = temp_df.with_columns(
        ((pl.col(Column.COUNT.value) - 1) / pl.col(Column.COUNT.value)).alias(Column.DOUBLE_SHARE.value)
    )
    log.debug('Вычисление доли двойных выходов выполнено.')
    temp_df = temp_df.drop(Column.COUNT.value)
    log.debug('Удален вспомогательный столбец с количеством.')

    df = df.join(temp_df, on=Column.UNIQUE_ID.value, how='left')
    log.debug('Объединение с таблицей доли двойных выходов завершено.')
    df = df.drop(Column.UNIQUE_ID.value)
    log.debug('Удален столбец уникальных идентификаторов.')

    # --- Удаление лишних столбцов ---
    log.debug('Удаление лишних столбцов.')

    ba_audiences: list[str] = list({info[ConfigKey.AUDIENCE] for info in KZ_CHANNELS_DATA.values()})

    for column in df.columns:
        if ('BA' in column) or ('sec' in column) or any(ba_audience in column for ba_audience in ba_audiences):
            log.debug(f'Удаление столбца [{column}].')
            df = df.drop(column)
    else:
        log.debug('Лишние столбцы удалены.')

    # --- Сортировка столбцов ---
    log.debug('Сортировка столбцов.')
    sorted_columns = _sort_columns(df.columns)
    df = df.select(sorted_columns)
    log.debug('Столбцы отсортированы.')
    # --- Округление значений ---
    df = df.with_columns(
        sc.numeric()
        .exclude([Column.GRP_30_SEC_NOT_ROUNDED.value, Column.BLK_GRP_PERCENT_30_SEC_ROUNDED.value])
        .round(Constant.STANDARD_ROUNDING_PRECISION.value)
    )

    log.info('Расчет основной выгрузки успешно завершен.')

    return df


def _create_workbook(df: pl.DataFrame, sheet_name: str = 'Основная выгрузка') -> bytes:
    """
    Конвертирует polars DataFrame в рабочую книгу Excel (.xlsx) в виде байтового представления.

    Args:
        df: polars DataFrame.
        sheet_name: имя листа рабочей книги.

    Returns:
        байтовое представление рабочей книги Excel.
    """
    buffer = io.BytesIO()

    df.write_excel(workbook=buffer, worksheet=sheet_name)

    buffer.seek(0)
    bytes = buffer.getvalue()

    buffer.close()

    return bytes


def create_main_task(df: pl.DataFrame, as_bytes: bool = True) -> bytes | pl.DataFrame:
    """
    Создает основную выгрузку в виде байтового представления Excel или polars DataFrame.

    Args:
        df: polars DataFrame.
        as_bytes: флаг, указывающий, нужно ли возвращать байтовое представление Excel или polars DataFrame.

    Returns:
        байтовое представление в виде рабочей книги Excel или polars DataFrame.
    """
    try:
        df = _transform_main_task(df)
    except StructureError:
        log.error('Не удалось трансформировать выгрузку.', exc_info=True)
        raise StructureError('Не удалось трансформировать выгрузку.')

    try:
        df = _calculate_main_task(df)
    except CalculationError:
        log.error('Не удалось выполнить расчет.', exc_info=True)
        raise CalculationError('Не удалось выполнить расчет.')

    if as_bytes:
        log.debug('Возврат основной выгрузки в виде байтового представления Excel.')
        return _create_workbook(df, sheet_name='Основная выгрузка')
    else:
        log.debug('Возврат основной выгрузки в виде polars DataFrame.')
        return df
