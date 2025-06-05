from typing import Any

import numpy as np
import polars as pl

from app_assets import load_ru_subjects
from core.ooh.logic import Geo
from core.ooh.panel import Construction as PConstruction
from core.ooh.panel import Panel
from core.ooh.schema import AnalyzerParams, CMethod, EOOHColumn, Formats, OOHColumn, OOHConfig, TOOHColumn
from orm.settings import OOHSettings

OOH_SUBJECTS = load_ru_subjects()


class Analyzer:
    """
    Класс для анализа адресной программы OOH и подбора похожих конструкций (панелей).

    Находит для каждой конструкции в адресной программе (`df`) набор
    аналогичных конструкций из базы данных (`db`) на основе
    географической близости, типа (digital/статика), размера, цены
    и, опционально, оператора. Рассчитывает веса для найденных
    аналогов и формирует объект `Panel`.

    Attributes:
        df (pl.DataFrame): Входная адресная программа.
        db (pl.DataFrame): База данных OOH конструкций для поиска аналогов.
        ooh_settings (OOHSettings): Настройки алгоритма анализа и расчета.
        result (pl.DataFrame | None): DataFrame с результатами анализа (после вызова execute).
        logger (logging.Logger): Экземпляр логгера для класса.
    """

    def __init__(self, df: pl.DataFrame, db: pl.DataFrame, ooh_settings: OOHSettings) -> None:
        """
        Инициализирует анализатор.

        Args:
            df: Адресная программа (DataFrame).
            db: База данных конструкций (DataFrame).
            ooh_settings: Настройки расчета.
        """
        self.df = df
        self.db = db
        self.ooh_settings = ooh_settings
        self.result: pl.DataFrame | None = None

    def _calc_dist(self, lat_1: float, lon_1: float, db: pl.DataFrame) -> pl.DataFrame:
        """
        Вычисляет геодезические расстояния (в км) по формуле Гаверсина.

        Args:
            lat_1: Широта исходной точки (градусы).
            lon_1: Долгота исходной точки (градусы).
            db: DataFrame с конструкциями, содержащий колонки широт и долгот.

        Returns:
            DataFrame `db` с добавленной колонкой расстояний ('_distance').
        """
        # Проверка на пустой DataFrame важна для предотвращения ошибок в .to_numpy().
        if db.is_empty():
            return db.with_columns(pl.lit(None).cast(pl.Float64).alias(TOOHColumn.distance.tech_name)).head(0)

        # Получаем координаты из базы данных (предполагаем, что колонки существуют).
        lat2 = db.get_column(OOHColumn.latitude.tech_name).to_numpy()
        lon2 = db.get_column(OOHColumn.longitude.tech_name).to_numpy()

        R = 6371.0  # Радиус Земли в км.
        lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(np.radians, [lat_1, lon_1, lat2, lon2])
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2.0) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        distances = R * c
        return db.with_columns(pl.Series(values=distances).alias(TOOHColumn.distance.tech_name))

    def _calc_weights(self, db: pl.DataFrame, radius: float) -> pl.DataFrame:
        """
        Вычисляет веса для конструкций на основе расстояния и текущего радиуса.

        Args:
            db: DataFrame с конструкциями, содержащий колонку '_distance'.
            radius: Текущий радиус поиска (км).

        Returns:
            DataFrame `db` с добавленной/обновленной колонкой весов ('_weight').
        """
        # Проверка на пустой DataFrame или отсутствие колонки расстояния важна.
        if db.is_empty():
            return db.with_columns(pl.lit(None).cast(pl.Float64).alias(TOOHColumn.weight.tech_name)).head(0)
        # Предполагаем, что колонка _distance существует после _calc_dist.

        distances = db.get_column(TOOHColumn.distance.tech_name).to_numpy()
        decay_rate: float = 1.0  # Коэффициент затухания.

        if 0 <= radius <= 0.1:
            weights = np.ones_like(distances)
        else:
            with np.errstate(divide='ignore', invalid='ignore'):
                weights = np.exp(-decay_rate * (distances / radius))
            weights[~np.isfinite(weights)] = 0.0
            weights = np.maximum(0, weights)
        return db.with_columns(pl.Series(TOOHColumn.weight.tech_name, weights))

    def _build_panel(self, db_cand: pl.DataFrame) -> Panel:
        """
        Создает объект Panel из DataFrame кандидатов.

        Args:
            db_cand: DataFrame с отобранными кандидатами.

        Returns:
            Объект Panel.
        """
        # Проверка на пустой DataFrame важна.
        if db_cand.is_empty():
            return Panel()

        # Собираем нужные колонки (предполагаем, что они существуют).
        req_struct = pl.struct(
            advertiser=pl.col(OOHColumn.advertiser.tech_name),
            operator=pl.col(OOHColumn.operator.tech_name),
            format=pl.col(OOHColumn.format_.tech_name),
            size=pl.col(OOHColumn.size.tech_name),
            side=pl.col(OOHColumn.side.tech_name),
            latitude=pl.col(OOHColumn.latitude.tech_name),
            longitude=pl.col(OOHColumn.longitude.tech_name),
            base_price=pl.col(EOOHColumn.base_price.tech_name),
            weight=pl.col(TOOHColumn.weight.tech_name),
        ).alias('p_data')
        # Используем встроенный тип list для аннотации.
        constr: list[PConstruction] = [
            PConstruction(**row) for row in db_cand.select(req_struct).get_column('p_data').to_list()
        ]
        return Panel(constr)

    # --- Функции Фильтрации ---

    def _filter_fmt_mf(self, db: pl.DataFrame) -> pl.DataFrame:
        """
        Фильтрует DataFrame, оставляя только конструкции формата MF.

        Args:
            db: Входной DataFrame.

        Returns:
            Отфильтрованный DataFrame.
        """
        # Предполагаем, что колонка формата существует.
        return db.filter(pl.col(OOHColumn.format_.tech_name).eq(Formats.MF.value))

    def _filter_subj(self, db: pl.DataFrame, **kwargs: Any) -> pl.DataFrame:
        """
        Фильтрует DataFrame по коду субъекта РФ (если метод OPERATOR_PLUS).

        Args:
            db: Входной DataFrame.
            **kwargs: Параметры анализируемой конструкции (содержит SUBJECT_CODE).

        Returns:
            Отфильтрованный DataFrame или исходный DataFrame.
        """
        if self.ooh_settings.c_method == CMethod.operator_plus:
            subj_code_col = EOOHColumn.subject_code.tech_name
            subj_code: str = kwargs[subj_code_col]
            # Предполагаем, что колонка субъекта существует.
            return db.filter(pl.col(subj_code_col).eq(subj_code))
        return db

    def _filter_dist_price(
        self, db: pl.DataFrame, radius: float, price_tol_abs: float, base_price: float
    ) -> pl.DataFrame:
        """
        Фильтрует DataFrame по максимальному расстоянию и допустимому отклонению цены.

        Args:
            db: Входной DataFrame (должен содержать '_distance' и 'base_price').
            radius: Максимальное допустимое расстояние (км).
            price_tol_abs: Абсолютное допустимое отклонение цены.
            base_price: Базовая цена анализируемой конструкции.

        Returns:
            Отфильтрованный DataFrame.
        """
        # Предполагаем, что колонки _distance и base_price существуют.
        dist_col = TOOHColumn.distance.tech_name
        price_col = EOOHColumn.base_price.tech_name
        return db.filter(
            (pl.col(dist_col) <= radius)
            & (pl.col(price_col).is_not_null())  # Проверка на Null остается важной.
            & ((pl.col(price_col) - base_price).abs() <= price_tol_abs)
        )

    def _filter_digital(self, db: pl.DataFrame, **kwargs: Any) -> pl.DataFrame:
        """
        Фильтрует DataFrame по совпадению признака digital/статика.

        Args:
            db: Входной DataFrame.
            **kwargs: Параметры анализируемой конструкции (содержит IS_DIGITAL).

        Returns:
            Отфильтрованный DataFrame.
        """
        digital_col = EOOHColumn.is_digital.tech_name
        is_digital: bool = kwargs[digital_col]
        # Предполагаем, что колонка существует.
        return db.filter(pl.col(digital_col).eq(is_digital))

    def _filter_size(self, db: pl.DataFrame, **kwargs: Any) -> pl.DataFrame:
        """
        Фильтрует DataFrame по схожести размеров (ширина, высота) с допуском.

        Args:
            db: Входной DataFrame.
            **kwargs: Параметры анализируемой конструкции (может содержать WIDTH, HEIGHT).

        Returns:
            Отфильтрованный DataFrame.
        """
        width_col = TOOHColumn.width.tech_name
        height_col = TOOHColumn.height.tech_name
        df_w: float | None = kwargs.get(width_col)
        df_h: float | None = kwargs.get(height_col)
        size_tol = AnalyzerParams.SIZE_TOLERANCE.value

        if df_w is not None and df_h is not None:
            # Предполагаем, что колонки размеров существуют в базе.
            w_tol = df_w * size_tol
            h_tol = df_h * size_tol
            return db.filter(
                pl.col(width_col).is_not_null()
                & pl.col(height_col).is_not_null()
                & ((pl.col(width_col) - df_w).abs() <= w_tol)
                & ((pl.col(height_col) - df_h).abs() <= h_tol)
            )
        elif df_w is not None or df_h is not None:
            return db.head(0)

        return db

    def _apply_op_filter(self, db: pl.DataFrame, **kwargs: Any) -> pl.DataFrame:
        """
        Применяет фильтр по оператору (логика Топ/Не-Топ для OPERATOR_PLUS).

        Args:
            db: Входной DataFrame.
            **kwargs: Параметры анализируемой конструкции (SUBJECT_CODE, OPERATOR).

        Returns:
            Отфильтрованный DataFrame.
        """
        operator_col = OOHColumn.operator.tech_name
        subj_code_col = EOOHColumn.subject_code.tech_name
        subj_code: str = kwargs[subj_code_col]
        target_op: str = kwargs[operator_col]

        # Получаем список топ-операторов (предполагаем, что OOH_SUBJECTS доступен).
        subj_info = OOH_SUBJECTS.get(subj_code, {})
        top_ops: list[str] = subj_info.get(OOHConfig.TOP_OPERATORS.value, [])  # type: ignore # Используем list.

        # Применяем логику, если список топ-операторов не пуст.
        if top_ops:
            # Предполагаем, что колонка оператора существует.
            is_target_top = target_op in top_ops
            return db.filter(
                pl.when(pl.lit(is_target_top))
                .then(pl.col(operator_col).eq(target_op))
                .otherwise(~pl.col(operator_col).is_in(top_ops))
            )
        # Если топ-операторов нет, фильтр не применяется.
        return db

    def _apply_lvl_fltrs(self, lvl: int, db: pl.DataFrame, **kwargs: Any) -> pl.DataFrame:
        """
        Применяет каскад фильтров уровня: digital, размер, оператор (если нужно).

        Args:
            lvl: Текущий уровень фильтрации (0, 1, 2, или -1 для MF).
            db: DataFrame для фильтрации.
            **kwargs: Параметры анализируемой конструкции.

        Returns:
            Отфильтрованный DataFrame.
        """
        # 1. Фильтр по Digital (предполагаем колонку существующей).
        filtered_db = self._filter_digital(db, **kwargs)
        if filtered_db.is_empty():
            return filtered_db

        # 2. Фильтр по Размеру (предполагаем колонки существующими).
        filtered_db = self._filter_size(filtered_db, **kwargs)
        if filtered_db.is_empty():
            return filtered_db

        # 3. Фильтр по Оператору (условно, предполагаем колонку существующей).
        if self.ooh_settings.c_method == CMethod.operator_plus and lvl not in [2, -1]:
            filtered_db = self._apply_op_filter(filtered_db, **kwargs)

        return filtered_db

    # --- Функции Проверки и Фильтрации Панели ---

    def _filter_panel_l0(self, panel: Panel) -> Panel:
        """
        Применяет специальную фильтрацию для панели на уровне 0 (уникальность и т.д.).

        Args:
            panel: Объект Panel для фильтрации.

        Returns:
            Отфильтрованный объект Panel.
        """
        if panel.is_empty():
            return panel
        # Вызов метода фильтрации панели (логика внутри Panel).
        panel.filter_panel()
        return panel

    def _check_panel_count(self, panel: Panel, lvl: int) -> bool:
        """
        Проверяет, соответствует ли размер панели требуемому минимуму для уровня.

        Args:
            panel: Проверяемая панель.
            lvl: Уровень фильтрации (0 или другие).

        Returns:
            True, если количество конструкций достаточно, иначе False.
        """
        req_count = AnalyzerParams.REQUIRED_COUNT_MIN.value if lvl == 0 else AnalyzerParams.REQUIRED_COUNT_DEFAULT.value
        is_sufficient = panel.size() >= req_count

        return is_sufficient

    # --- Методы Создания Панели (Оркестраторы) ---

    def _create_panel_mf(self, **kwargs: Any) -> Panel:
        """
        Создает панель для формата MF (Медиафасад).

        Args:
            **kwargs: Параметры строки из df.

        Returns:
            Объект Panel.
        """

        # --- Step MF.0: Извлечение параметров. ---
        df_lat: float = kwargs[OOHColumn.latitude.tech_name]
        df_lon: float = kwargs[OOHColumn.longitude.tech_name]
        df_price: float = kwargs[EOOHColumn.base_price.tech_name]
        radius_mf = AnalyzerParams.RADIUS_MAX_MF.value  # Радиус из настроек.
        price_tol_abs = AnalyzerParams.BASE_PRICE_TOLERANCE.value * abs(df_price)  # Допуск цены.

        # --- Step MF.1: Фильтрация по Формату MF. ---
        db_mf = self._filter_fmt_mf(self.db)
        if db_mf.is_empty():
            return Panel()

        # --- Step MF.2: Расчет Расстояний. ---
        db_mf = self._calc_dist(df_lat, df_lon, db_mf)

        # --- Step MF.3: Фильтрация по Радиусу и Цене. ---
        db_cand = self._filter_dist_price(db_mf, radius_mf, price_tol_abs, df_price)
        if db_cand.is_empty():
            return Panel()

        # --- Step MF.4: Фильтрация по Digital и Размеру. ---
        db_cand = self._apply_lvl_fltrs(lvl=-1, db=db_cand, **kwargs)  # lvl=-1 отключает фильтр оператора.
        if db_cand.is_empty():
            return Panel()

        # --- Step MF.5: Расчет Весов. ---
        db_cand = self._calc_weights(db_cand, radius=radius_mf)  # Вес от radius_mf.

        # --- Step MF.6: Построение Панели. ---
        panel = self._build_panel(db_cand)

        # --- Step MF.7: Возврат Панели. ---
        return panel

    def _create_panel_non_mf(self, **kwargs: Any) -> Panel:
        """
        Создает панель для НЕ-MF форматов (многоуровневый поиск).

        Args:
             **kwargs: Параметры строки из df.

        Returns:
            Объект Panel.
        """
        # --- Step P.0: Извлечение параметров. ---
        df_lat: float = kwargs[OOHColumn.latitude.tech_name]
        df_lon: float = kwargs[OOHColumn.longitude.tech_name]
        df_price: float = kwargs[EOOHColumn.base_price.tech_name]
        price_tol_abs = AnalyzerParams.BASE_PRICE_TOLERANCE.value * abs(df_price)  # Допуск цены.

        RAD_RANGE = np.arange(
            AnalyzerParams.RADIUS_MIN_DEFAULT.value,  # От мин. радиуса.
            AnalyzerParams.RADIUS_MAX_DEFAULT.value + AnalyzerParams.RADIUS_STEP_DEFAULT.value,  # До макс. радиуса.
            AnalyzerParams.RADIUS_STEP_DEFAULT.value,  # С шагом.
        )
        # RAD_RANGE = RAD_RANGE[RAD_RANGE > 1e-9]  # Исключаем 0.

        # --- Step P.1: Базовая Фильтрация (Только Субъект при OPERATOR_PLUS). ---
        # НЕ ФИЛЬТРУЕМ ПО ФОРМАТУ ЗДЕСЬ.
        base_db = self._filter_subj(self.db, **kwargs)
        if base_db.is_empty():
            return Panel()

        # --- Step P.2: Расчет Расстояний (Один раз). ---
        base_db_dist = self._calc_dist(df_lat, df_lon, base_db)

        # --- Step L: Итерация по Уровням Фильтрации (0, 1, 2). ---
        for lvl in range(3):
            # --- Step L.1: Применение Фильтров Уровня. ---
            # Фильтры: digital, размер, оператор (зависит от lvl).
            db_lvl_filtered = self._apply_lvl_fltrs(lvl, base_db_dist, **kwargs)

            # Если на этом уровне нет кандидатов после фильтров digital/size/op,
            # то нет смысла итерировать по радиусам - переходим к следующему уровню.
            if db_lvl_filtered.is_empty():
                continue  # К следующему lvl.

            # --- Step R: Итерация по Радиусам. ---
            for radius in RAD_RANGE:
                # --- Step R.1: Фильтр по Текущему Радиусу и Цене. ---
                db_cand = self._filter_dist_price(db_lvl_filtered, radius, price_tol_abs, df_price)  # type: ignore
                if db_cand.is_empty():
                    # self.logger.debug(f"Уровень {lvl}, Радиус {radius:.2f}: Нет кандидатов после фильтра радиус/цена.") # Опционально, может быть слишком много логов.
                    continue  # К следующему radius.

                # --- Step R.2: Расчет Весов. ---
                # Веса рассчитываются относительно ТЕКУЩЕГО радиуса `radius`.
                db_cand = self._calc_weights(db_cand, radius)  # type: ignore

                # --- Step R.3: Построение Панели. ---
                # Фильтрация по весу не применяется!.
                panel = self._build_panel(db_cand)
                if panel.is_empty():
                    continue  # На всякий случай.

                # --- Step R.4: Дополнительная Фильтрация Панели (только Уровень 0). ---
                if lvl == 0:
                    panel = self._filter_panel_l0(panel)  # Проверка уникальности и т.д.
                    if panel.is_empty():
                        continue  # К следующему radius.

                # --- Step R.5: Проверка Финального Количества. ---
                if self._check_panel_count(panel, lvl):
                    return panel  # Возвращаем результат.

        return Panel()

    def _create_panel(self, **kwargs: Any) -> Panel:
        """
        Диспетчер: вызывает _create_panel_mf или _create_panel_non_mf.

        Args:
            **kwargs: Параметры анализируемой конструкции (включая FORMAT).

        Returns:
            Созданная панель (Panel).
        """
        df_fmt: str = kwargs[OOHColumn.format_.tech_name]  # Получаем формат.
        # Вызов специфичной функции в зависимости от формата.
        if df_fmt == Formats.MF.value:
            return self._create_panel_mf(**kwargs)
        else:
            return self._create_panel_non_mf(**kwargs)

    # --- Основной Запуск и Результат ---

    def execute(self) -> None:
        """
        Выполняет процесс анализа для всех строк в `self.df`.
        """
        # Обработка пустого входного DataFrame.
        if self.df.is_empty():
            self.result = self.df.clone()  # Создаем пустой результат со структурой входа.
            # Добавляем ожидаемые колонки, если их нет.
            res_cols = [  # type: ignore
                ('panel_base_price', pl.Float64),
                (EOOHColumn.advertisers.tech_name, pl.String),
                (EOOHColumn.operators.tech_name, pl.String),
                (EOOHColumn.constructions.tech_name, pl.String),
                (EOOHColumn.advertiser_shares.tech_name, pl.String),
                (EOOHColumn.operator_shares.tech_name, pl.String),
                (EOOHColumn.subject_name.tech_name, pl.String),
            ]
            for col_name, col_type in res_cols:  # type: ignore
                if col_name not in self.result.columns:  # type: ignore
                    self.result = self.result.with_columns(pl.lit(None).cast(col_type).alias(col_name))  # type: ignore
            return

        # --- Шаг 0. Удаление записей анализируемого рекламодателя из базы данных. ---
        advertiser: str = self.df.get_column(OOHColumn.advertiser.tech_name).unique()[
            0
        ]  # Предполагаем, что все строки имеют одинаковый рекламодатель.

        self.db = self.db.filter(pl.col(OOHColumn.advertiser.tech_name) != advertiser)

        # --- Шаг 0.1: Удаление записей с нулевыми ценами. ---
        self.db = self.db.filter(
            (pl.col(EOOHColumn.base_price.tech_name).is_not_null()) & (pl.col(EOOHColumn.base_price.tech_name) > 0)
        )

        # --- Шаг 0.2: Удаление записей с длительностью аренды менее недели. ---
        self.db = self.db.filter(pl.col(EOOHColumn.rental_c.tech_name) > 0.3)

        # --- Шаг 1: Создание панелей. ---
        # Используем list для аннотации.
        panels: list[Panel] = [self._create_panel(**row) for row in self.df.iter_rows(named=True)]

        # --- Шаг 2: Извлечение данных. ---

        def get_or_none(func, panel, *args, **kwargs):
            return func(*args, **kwargs) if not panel.is_empty() else None

        def get_str_or_none(func, panel, *args, **kwargs):
            return str(func(*args, **kwargs)) if not panel.is_empty() else None

        # Используем list для аннотации.
        base_prices: list[float | None] = [
            get_or_none(p.calc_base_price, p, method=self.ooh_settings.s_method) for p in panels
        ]
        advertisers: list[str | None] = [get_str_or_none(p.get_advertisers, p, as_string=True) for p in panels]
        operators: list[str | None] = [get_str_or_none(p.get_operators, p, as_string=True) for p in panels]
        constructions: list[str | None] = [get_str_or_none(p.get_constructions, p, as_string=True) for p in panels]
        advertiser_shares: list[str | None] = [
            get_str_or_none(p.get_advertiser_shares, p, as_string=True) for p in panels
        ]
        operator_shares: list[str | None] = [get_str_or_none(p.get_operator_shares, p, as_string=True) for p in panels]

        # --- Шаг 3: Формирование результата. ---

        self.result = self.df.with_columns(
            pl.Series(name='panel_base_price', values=base_prices, dtype=pl.Float64),
            pl.Series(name=EOOHColumn.advertisers.tech_name, values=advertisers, dtype=pl.String),
            pl.Series(name=EOOHColumn.operators.tech_name, values=operators, dtype=pl.String),
            pl.Series(name=EOOHColumn.constructions.tech_name, values=constructions, dtype=pl.String),
            pl.Series(name=EOOHColumn.advertiser_shares.tech_name, values=advertiser_shares, dtype=pl.String),
            pl.Series(name=EOOHColumn.operator_shares.tech_name, values=operator_shares, dtype=pl.String),
        )

        # --- Шаг 4: Добавление названий субъектов. ---
        subj_code_col = EOOHColumn.subject_code.tech_name
        subj_name_col = EOOHColumn.subject_name.tech_name
        # Добавляем субъект только если есть код субъекта.
        if subj_code_col in self.result.columns:
            try:
                subj_codes = self.result.get_column(subj_code_col).to_list()
                # Используем Geo класс для получения названий.
                # Используем list для аннотации.
                subjects: list[str | None] = [
                    Geo.get_subject(str(code)) if code is not None else None for code in subj_codes
                ]
                self.result = self.result.with_columns(pl.Series(name=subj_name_col, values=subjects, dtype=pl.String))

            except Exception:
                # Добавляем пустую колонку в случае ошибки.
                self.result = self.result.with_columns(pl.lit(None).cast(pl.String).alias(subj_name_col))
        else:
            # Добавляем пустую колонку, если кода субъекта не было изначально.
            self.result = self.result.with_columns(pl.lit(None).cast(pl.String).alias(subj_name_col))

    def get_result(self) -> pl.DataFrame:
        """
        Возвращает DataFrame с результатами анализа, удаляя технические колонки.

        Returns:
            Финальный DataFrame с результатами.
        """
        if self.result is None:
            return self.df  # Возвращаем исходные данные.

        # Технические колонки для удаления.
        cols_to_drop = [
            TOOHColumn.width.tech_name,
            TOOHColumn.height.tech_name,
        ]
        cols_present = [col for col in cols_to_drop if col in self.result.columns]

        if cols_present:
            try:
                return self.result.drop(cols_present)
            except Exception:
                return self.result  # Возвращаем как есть при ошибке.
        else:
            return self.result
