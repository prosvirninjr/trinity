import pickle
from datetime import datetime

import polars as pl
import redis
from polars import DataFrame

from app_assets import load_ooh_coefficients
from app_settings import load_settings
from core.ooh.logic import Coefficient
from core.ooh.schema import EOOHColumn, OOHColumn, Template
from core.radio.models import RadioTable
from core.utils.tools import singleton
from orm.sql_builder import get_engine
from orm.sql_queries import select_ooh, select_radio


@singleton
class OOHDatabase:
    """Менеджер базы данных OOH."""

    REDIS_KEY: str = "OOH"

    def __init__(self) -> None:
        """
        Устанавливает Redis-соединение и загружает DataFrame OOH.

        Returns:
            None
        """
        self.redis: redis.Redis = redis.Redis(host=load_settings().REDIS_HOST)
        cache = self.redis.get(self.REDIS_KEY)

        if cache:
            self.db: DataFrame = pickle.loads(cache)  # type: ignore
        else:
            self.db: DataFrame = self._load_db()
            self.redis.set(self.REDIS_KEY, pickle.dumps(self.db))

    def _load_db(self) -> DataFrame:
        """
        Загружает и предобрабатывает данные из PostgreSQL.

        Returns:
            DataFrame: Предобработанный DataFrame.
        """
        engine = get_engine()  # SQLAlchemy engine.
        return self._preprocess(select_ooh(engine, as_polars=True))  # type: ignore

    def _preprocess(self, df: DataFrame) -> DataFrame:
        """
        Применяет шаблонную обработку к DataFrame.

        Args:
            df (DataFrame): Исходный DataFrame.

        Returns:
            DataFrame: Обработанный DataFrame.
        """
        template = Template(df)
        template.process_template()

        return template.get_df()

    def _filter_database(
        self,
        df: DataFrame,
        panel: list[str] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        subject_codes: list[str] | None = None,
    ) -> DataFrame:
        """
        Фильтрует DataFrame по заданным параметрам.

        Args:
            df (DataFrame): Входной DataFrame.
            panel (list[str] | None): Рекламодатели.
            start_date (datetime | None): Начало периода.
            end_date (datetime | None): Конец периода.
            subject_codes (list[str] | None): Коды субъектов.

        Returns:
            DataFrame: Отфильтрованный DataFrame.
        """
        filtered = df
        if panel:
            filtered = filtered.filter(pl.col(OOHColumn.advertiser.tech_name).is_in(panel))
        if start_date:
            filtered = filtered.filter(pl.col(OOHColumn.start_date.tech_name) >= start_date)
        if end_date:
            filtered = filtered.filter(pl.col(OOHColumn.end_date.tech_name) <= end_date)
        if subject_codes:
            filtered = filtered.filter(pl.col(EOOHColumn.subject_code.tech_name).is_in(subject_codes))
        return filtered

    def _clean_price_trash(self, df: DataFrame) -> DataFrame:
        """
        Удаляет нулевые цены и выбросы методом IQR.

        Args:
            df (DataFrame): Входной DataFrame.

        Returns:
            DataFrame: Очищенный DataFrame.
        """
        group_cols = [
            OOHColumn.advertiser.tech_name,
            OOHColumn.operator.tech_name,
            OOHColumn.format_.tech_name,
            EOOHColumn.is_digital.tech_name,
            EOOHColumn.subject_code.tech_name,
        ]

        positive_df = df.filter(pl.col(EOOHColumn.base_price.tech_name) > 0)

        bounds = (
            positive_df.group_by(group_cols)
            .agg(
                [
                    pl.col(EOOHColumn.base_price.tech_name).quantile(0.25).alias("Q1"),
                    pl.col(EOOHColumn.base_price.tech_name).quantile(0.75).alias("Q3"),
                ]
            )
            .with_columns(
                [
                    (pl.col("Q3") - pl.col("Q1")).alias("IQR"),
                ]
            )
            .select(
                group_cols
                + [
                    (pl.col("Q1") - 1.5 * pl.col("IQR")).alias("lower_bound"),
                    (pl.col("Q3") + 1.5 * pl.col("IQR")).alias("upper_bound"),
                ]
            )
        )

        cleaned_df = (
            df.join(bounds, on=group_cols, how="left")
            .filter(
                (pl.col("lower_bound").is_null() | (pl.col(EOOHColumn.base_price.tech_name) >= pl.col("lower_bound")))
                & (pl.col("upper_bound").is_null() | (pl.col(EOOHColumn.base_price.tech_name) <= pl.col("upper_bound")))
            )
            .drop("lower_bound", "upper_bound")
        )

        return cleaned_df

    def _correct_base_price(self, df: DataFrame, target_year: int) -> DataFrame:
        """
        Корректирует базовую цену по инфляции к целевому году.

        Args:
            df (DataFrame): Входной DataFrame.
            target_year (int): Целевой год.

        Returns:
            DataFrame: DataFrame с обновленной ценой.
        """
        # Загрузка коэффициентов инфляции
        ooh_coefficients: dict = load_ooh_coefficients()
        rates_dict = ooh_coefficients["inflation"]

        def _rate(row: dict) -> float:
            return Coefficient.calc_inflation_c(
                rates_dict=rates_dict,
                subject_code=row[EOOHColumn.subject_code.tech_name],
                format_type=row[OOHColumn.format_.tech_name],
                year_from=row[OOHColumn.start_date.tech_name].year,
                year_to=target_year,
                default_rates={"2023": 1.25, "2024": 1.25},  # Коэффициенты по умолчанию.
            )

        rates = [_rate(r) for r in df.iter_rows(named=True)]

        # Базовая цена с учетом инфляции.
        df = df.with_columns(
            (pl.col(EOOHColumn.base_price.tech_name) * pl.Series(rates, dtype=pl.Float64)).alias(
                EOOHColumn.base_price.tech_name
            )
        )
        return df

    def get_database(
        self,
        panel: list[str] | None = None,
        target_year: int | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        subject_codes: list[str] | None = None,
        clean: bool = True,
    ) -> DataFrame:
        """
        Возвращает DataFrame с применением фильтров и корректировок.

        Args:
            panel (list[str] | None): Рекламодатели.
            target_year (int | None): Целевой год.
            start_date (datetime | None): Начало периода.
            end_date (datetime | None): Конец периода.
            subject_codes (list[str] | None): Коды субъектов.
            clean (bool): Удалять выбросы.

        Returns:
            DataFrame: Итоговый DataFrame.
        """
        df = self.db.clone()

        df = self._filter_database(df, panel, start_date, end_date, subject_codes)

        if target_year:
            df = self._correct_base_price(df, target_year)
        if clean:
            df = self._clean_price_trash(df)

        return df

    def get_advertisers(self) -> list[str]:
        """
        Список уникальных рекламодателей.

        Returns:
            list[str]: Рекламодатели.
        """
        return sorted(self.db.select(OOHColumn.advertiser.tech_name).unique().to_series().to_list())

    def get_available_period(self) -> tuple[datetime, datetime]:
        """
        Доступный период в базе данных.

        Returns:
            tuple[datetime, datetime]: Доступный период.
        """
        start_date = self.db.select(OOHColumn.start_date.tech_name).min().to_series()[0]
        end_date = self.db.select(OOHColumn.end_date.tech_name).max().to_series()[0]

        return (start_date, end_date)

    def reload(self) -> None:
        """
        Очищает кэш и перезагружает базу данных.

        Returns:
            None
        """
        self.redis.delete(self.REDIS_KEY)
        self.db = self._load_db()
        self.redis.set(self.REDIS_KEY, pickle.dumps(self.db))


@singleton
class RadioDatabase:
    """Менеджер базы данных Radio."""

    REDIS_KEY: str = "Radio"

    def __init__(self) -> None:
        """
        Устанавливает Redis-соединение и загружает DataFrame Radio.

        Returns:
            None
        """
        self.redis: redis.Redis = redis.Redis(host=load_settings().REDIS_HOST)
        cache = self.redis.get(self.REDIS_KEY)

        if cache:
            self.db: DataFrame = pickle.loads(cache)  # type: ignore
        else:
            self.db: DataFrame = self._load_db()
            self.redis.set(self.REDIS_KEY, pickle.dumps(self.db))

    def _preprocess(self, df: DataFrame) -> DataFrame:
        """
        Применяет шаблонную обработку к DataFrame.

        Args:
            df (DataFrame): Исходный DataFrame.

        Returns:
            DataFrame: Обработанный DataFrame.
        """
        template = RadioTable(df)
        template.process_template()

        return template.get_df()

    def _load_db(self) -> DataFrame:
        """Загружает и предобрабатывает данные из PostgreSQL.

        Returns:
            DataFrame: Предобработанный DataFrame.

        """
        engine = get_engine()  # SQLAlchemy engine.
        return self._preprocess(select_radio(engine, as_polars=True))  # type: ignore

    def _get_prices(self, df: DataFrame, panel: list[str] | None = None) -> DataFrame:
        """Создает панель по таймслотам (Прайс-лист за 30 сек. с учетом скидки)."""
        if panel:
            df = df.filter(pl.col("advertiser").is_in(panel))

        prices = df.filter(
            (pl.col("status") == "Фактическое размещение")
            & (pl.col("discount") != 0)
            & (pl.col("price_net_30_wed") != 0)
            & (pl.col("price_net_30_wkd") != 0)
        )
        discount_factor = 1 - pl.col("discount")
        prices = prices.with_columns(
            (pl.col("price_net_30_wed") * discount_factor).alias("price_net_30_wed_with_discount"),
            (pl.col("price_net_30_wkd") * discount_factor).alias("price_net_30_wkd_with_discount"),
        )
        result = prices.group_by(["radiostation", "broadcast", "timeslot"]).agg(
            pl.mean("price_net_30_wed_with_discount").alias("Ср. стоимость (будни)"),
            pl.mean("price_net_30_wkd_with_discount").alias("Ср. стоимость (выходные)"),
        )

        return result

    def _get_discounts(self, df: DataFrame, panel: list[str] | None = None) -> DataFrame:
        """Создает панель по скидкам."""
        if panel:
            df = df.filter(pl.col("advertiser").is_in(panel))

        discounts = df.filter((pl.col("status") == "Фактическое размещение") & (pl.col("discount") != 0))
        result = discounts.group_by(["radiostation", "broadcast"]).agg(pl.mean("discount").alias("Ср. скидка"))

        return result

    def get_panel(self, by_discounts: bool = True, panel: list[str] | None = None) -> DataFrame:
        """
        Возвращает DataFrame с применением фильттров и корректировок.

        Args:
            by_discounts (bool): если True — по скидкам, иначе — по таймслотам.
            panel (list[str] | None): список радиостанций для фильтрации.
        """
        df = self.db.clone()

        if by_discounts:
            return self._get_discounts(df, panel)

        else:
            return self._get_prices(df, panel)

    def reload(self) -> None:
        """
        Очищает кэш и перезагружает базу данных.

        Returns:
            None
        """
        self.redis.delete(self.REDIS_KEY)
        self.db = self._load_db()
        self.redis.set(self.REDIS_KEY, pickle.dumps(self.db))

    def get_advertisers(self) -> list[str]:
        """
        Список уникальных рекламодателей.

        Returns:
            list[str]: Рекламодатели.
        """
        return sorted(self.db.select("advertiser").unique().to_series().to_list())
