import re
from datetime import date, datetime, time

from core.tv.ru.tasks.local import schema


class TVLogic:
    """Общая логика работы с данными."""

    @staticmethod
    def get_time_parts(string: str) -> list[int]:
        """
        Извлекает часы, минуты и секунды из строки 'ЧЧ:ММ:СС'.

        Args:
            string: Строка времени в формате 'ЧЧ:ММ:СС'.

        Returns:
            Список из трех целых чисел (часы, минуты, секунды).
        """
        return list(map(int, string.split(':')))

    @staticmethod
    def get_hour(string: str) -> int:
        """
        Извлекает час начала из строки 'ЧЧ:ММ:СС'.

        Args:
            string: Строка времени в формате 'ЧЧ:ММ:СС'.

        Returns:
            Час начала.
        """
        return TVLogic.get_time_parts(string)[0]

    @staticmethod
    def get_minute(string: str) -> int:
        """
        Извлекает минуты из строки 'ЧЧ:ММ:СС'.

        Args:
            string: Строка времени в формате 'ЧЧ:ММ:СС'.

        Returns:
            Минуты.
        """
        return TVLogic.get_time_parts(string)[1]

    @staticmethod
    def get_date_parts(string: str) -> list[int]:
        """
        Извлекает год, месяц и день из строки даты.

        Args:
            string: Строка даты в одном из поддерживаемых форматов.

        Returns:
            Список из трех целых чисел [год, месяц, день].
        """
        n1, n2, n3 = map(int, re.split(r'[-/.]', string))

        if len(str(n1)) == 4:
            return [n1, n2, n3]

        return [n3, n2, n1]

    @staticmethod
    def normalize_time_format(time_str: str, as_string: bool = False) -> time | str:
        """
        Переводит время из формата 24h+ в стандартный формат 24h.

        Args:
            time_str: Строка времени в формате 'ЧЧ:ММ:СС'.
            as_string: Если True, возвращает время как строку 'ЧЧ:ММ:СС', иначе возвращает объект datetime.time.

        Returns:
            Объект datetime.time или строка времени в формате 'ЧЧ:ММ:СС'.
        """
        hours, minutes, seconds = TVLogic.get_time_parts(time_str)
        normalized_hours = hours % 24

        if as_string:
            return f'{normalized_hours:02d}:{minutes:02d}:{seconds:02d}'
        else:
            return time(normalized_hours, minutes, seconds)

    @staticmethod
    def get_time_interval(time_str: str) -> str | None:
        """
        Возвращает предопределенный временной интервал на основе часа из строки времени.

        Args:
            time_str: Строка времени в формате "ЧЧ:ММ:СС" (24h).

        Returns:
            Строка временного интервала.
        """
        hours = int(time_str.split(':')[0])

        # Определяем интервалы и соответствующие им строки
        time_intervals = {
            (6, 8): '06:00:00-09:00:00',
            (9, 12): '09:00:00-13:00:00',
            (13, 15): '13:00:00-16:00:00',
            (16, 18): '16:00:00-19:00:00',
            (19, 21): '19:00:00-22:00:00',
            (22, 23): '22:00:00-00:00:00',
            (0, 5): '00:00:00-06:00:00',
        }

        # Ищем подходящий интервал
        for (start_hour, end_hour), interval_str in time_intervals.items():
            if start_hour <= hours <= end_hour:
                return interval_str

        raise ValueError('Не удалось определить временной интервал')

    @staticmethod
    def get_weekday_name(weekday: int) -> str:
        """
        Возвращает название дня недели на русском языке.

        Args:
            weekday: Номер дня недели (1 - понедельник, 7 - воскресенье).

        Returns:
            Название дня недели на русском языке.
        """
        weekdays = {
            1: 'Понедельник',
            2: 'Вторник',
            3: 'Среда',
            4: 'Четверг',
            5: 'Пятница',
            6: 'Суббота',
            7: 'Воскресенье',
        }

        return weekdays[weekday]

    @staticmethod
    def to_clean_tvc(tvc: str) -> str:
        """
        Приводит название телекомпании к чистому виду, удаляя скобки и значения внутри скобок.

        Args:
            tvc: Название телекомпании.

        Returns:
            Очищенное название телекомпании.
        """
        return re.sub(r'\s*\(.*?\)', '', tvc).strip()

    @staticmethod
    def get_daytype(dt: date | datetime, daytypes: dict[str, str]) -> str:
        """
        Возвращает тип дня для заданной даты.

        Args:
            dt: Объект datetime.date или datetime.datetime.
            daytypes: Словарь вида {'YYYY-MM-DD': 'тип дня'}.

        Returns:
            Строка с типом дня или None, если дата не найдена в словаре.
        """
        date_key = dt.strftime('%Y-%m-%d')
        daytype = daytypes.get(date_key)

        if daytype is None:
            raise ValueError('Не найден тип дня для даты [%s]', date_key)

        return daytype


class NatTVLogic(TVLogic):
    """Специфичная для национального ТВ логика работы с данными."""

    @staticmethod
    def is_prime(hour: int, is_weekend: bool, is_national: bool) -> bool:
        """
        Проверяет, входит ли выход в границу prime time по следующей логике:

            Национальная телекомпания:
            • выходные или праздники: 08:00–23:59
            • будни: 07:00–07:59 или 18:00–23:59
            Прочие:
            • выходные или праздники: круглосуточно
            • будни: 17:00–23:59

        Args:
            hour: Час, который нужно проверить.
            is_weekend: True, если день является выходным или праздником.
            is_national: True, если телекомпания является национальной.

        Returns:
            True, если prime time, иначе False.
        """
        if is_national:
            if is_weekend:
                return 8 <= hour < 24
            return (7 <= hour < 8) or (18 <= hour < 24)
        else:
            if is_weekend:
                return True
            return 17 <= hour < 24

    @staticmethod
    def is_tvc(tvc: str, tv_mark: str = 'Сетевое') -> bool:
        """
        Проверяет, является ли запись ТВ размещением.

        Args:
            tvc: Название телекомпании (сырое).
            tv_mark: Маркер, размещения (по умолчанию 'Сетевое').

        Returns:
            True, если запись является ТВ размещением, иначе False.
        """
        return tv_mark.lower() in tvc.lower()

    @staticmethod
    def get_tvc_type(tvc: str, tvc_info: dict) -> str:
        """
        Возвращает тип канала для указанной телекомпании.

        Args:
            tvc: Название телекомпании (очищенное).
            tvc_info: Словарь со справочной информацией о телекомпаниях.

        Returns:
            Тип канала.

        Raises:
            ValueError: Если телекомпания не найдена в словаре или для нее не указан тип канала.
        """
        info: str | None = tvc_info.get(tvc)

        if info is None:
            raise ValueError('Не найдена информация о телекомпании [%s]', tvc)

        tvc_type: str | None = info.get('type_')

        if tvc_type is None:
            raise ValueError('Не указан тип канала для телекомпании [%s]', tvc)

        return tvc_type

    @staticmethod
    def get_tvc_audience(tvc: str, tvc_info: dict) -> str:
        """
        Возвращает целевую аудиторию для указанной телекомпании.

        Args:
            tvc: Название телекомпании.
            tvc_info: Справочный словарь с информацией о телекомпаниях.

        Returns:
            Целевая аудитория.

        Raises:
            ValueError: Если информация или целевая аудитория не найдена для телекомпании.
        """
        info = tvc_info.get(tvc)

        if info is None or 'audience' not in info:
            raise ValueError('Не найдена целевая аудитория для телекомпании [%s]', tvc)

        return info['audience']

    @staticmethod
    def get_tvc_number(tvc: str, distribution: str, tvc_info: dict) -> int | None:
        """
        Возвращает номер канала для указанной телекомпании в заданном способе дистрибуции.

        Args:
            tvc: Название телекомпании.
            distribution: Вещание.
            tvc_info: Справочный словарь с информацией о телекомпаниях.

        Returns:
            Номер канала или None, если явно указан null в данных.

        Raises:
            ValueError: Если информация о телекомпании не найдена или отсутствует ключ для данного способа вещания.
        """
        info = tvc_info.get(tvc)
        if info is None:
            raise ValueError(f'Не найдена информация о телекомпании [{tvc}]')

        ids = info.get('id', {})
        key = 'orbital' if distribution == schema.Distribution.ORBITAL.value else 'network'

        # Если ключ совсем не присутствует — считаем, что данные отсутствуют
        if key not in ids:
            raise ValueError(f'Не найден номер для телекомпании [{tvc}], вещание [{distribution}]')

        # Если ключ есть, но значение None — это валидная ситуация, возвращаем None
        return ids[key]

    @staticmethod
    def get_tvc_name(tvc: str, distribution: str, tvc_info: dict) -> str | None:
        """
        Возвращает имя канала для указанной телекомпании в заданном способе дистрибуции.

        Args:
            tvc: Название телекомпании.
            distribution: Вещание.
            tvc_info: Словарь с информацией о телекомпаниях.

        Returns:
            Имя канала или None, если явно указано null.

        Raises:
            ValueError: Если информация о телекомпании или ключ для вида вещания не найдены.
        """
        info = tvc_info.get(tvc)
        if info is None:
            raise ValueError(f'Не найдена информация о телекомпании [{tvc}]')

        names = info.get('name', {})
        key = 'orbital' if distribution == schema.Distribution.ORBITAL.value else 'network'

        # Если ключ отсутствует — ошибка
        if key not in names:
            raise ValueError(f'Не найден ключ [{key}] для имени канала телекомпании [{tvc}]')

        # Если ключ есть, но значение None — возвращаем None
        return names[key]

    @staticmethod
    def get_tvc_round(tvc: str, distribution: str, year: int, tvc_info: dict) -> float | None:
        """
        Возвращает коэффициент округления для указанной телекомпании в заданном году и способе дистрибуции.

        Args:
            tvc: Название телекомпании (очищенное).
            distribution: Вещание.
            year: Год.
            tvc_info: Справочный словарь с информацией о телекомпаниях.

        Returns:
            Коэффициент округления или 0.0, если явно указано null.
        """
        info = tvc_info.get(tvc)
        if info is None or 'round' not in info:
            raise ValueError(f'Не найдена информация об округлении для телекомпании [{tvc}]')

        round_info = info['round']
        if str(year) not in round_info:
            raise ValueError(f'Нет данных об округлении для года [{year}] и телекомпании [{tvc}]')

        year_entry = round_info[str(year)]

        # Если в данных стоит None, возвращаем 0.0
        if year_entry is None:
            return 0.0

        key = 'orbital' if distribution == schema.Distribution.ORBITAL.value else 'network'

        if key not in year_entry:
            raise ValueError(f'Не найден коэффициент округления для [{key}], телекомпания [{tvc}], год [{year}]')

        return year_entry[key]


class RegTVLogic(TVLogic):
    """Специфичная для регионального ТВ логика работы с данными."""

    @staticmethod
    def is_prime(hour: int, minute: int, is_weekend: bool, channel: str) -> bool:
        """
        Проверяет региональный прайм-тайм по часам:

          Первый, Россия 1, НТВ, СТС, Пятый канал, РЕН ТВ, ТВЦ Москва (и локальные каналы с выделенным праймом):
            • выходные: круглосуточно
            • будни: 18–23 (18:00-23:59)
          ТНТ:
            • выходные: круглосуточно
            • будни: 18:00–00:30 (т.е. 18-23 или 00:00-00:29)
          РБК Москва, РБК Санкт-Петербург:
            • любой день: 07:00–10:00 (07:00-09:59) или 18:00–24:00 (18:00-23:59)
          Прочие:
            • круглосуточно
        """
        primary = ['Первый', 'Россия 1', 'НТВ', 'СТС', 'Пятый канал', 'РЕН ТВ', 'ТВЦ Москва']
        tnt = ['ТНТ']
        rbk = ['РБК Москва', 'РБК Санкт-Петербург']

        if channel in primary:
            return is_weekend or (18 <= hour <= 23)

        if channel in tnt:
            if is_weekend:
                return True
            else:
                return (18 <= hour <= 23) or (hour == 0 and minute < 30)

        if channel in rbk:
            return (7 <= hour < 10) or (18 <= hour <= 23)

        return True

    @staticmethod
    def get_number(national: str, original: str, info: dict) -> int:
        """
        Возвращает номер канала.

        Args:
            national: Название национальной телекомпании или спецкатегории.
            original: Оригинальное название локального канала (ключ).
            info: Справочный словарь с данными по всем каналам.

        Returns:
            Номер канала.

        Raises:
            ValueError: Если номер канала не найден.
        """
        SPECIAL = 'ИЗМЕРЯЕМОЕ ЛОКАЛЬНОЕ ТВ'

        if national == SPECIAL:
            loc = info.get(SPECIAL, {}).get(original, {})

            if 'number' not in loc:
                raise ValueError('Не найден номер канала [%s][%s]' % (SPECIAL, original))

            return loc['number']

        company = info.get(national, {})

        if 'number' not in company:
            raise ValueError('Не найден номер канала [%s]' % national)

        return company['number']

    @staticmethod
    def get_audience(national: str, original: str, info: dict) -> str:
        """
        Возвращает целевую аудиторию канала.

        Args:
            national: Название национальной телекомпании или спецкатегории.
            original: Оригинальное название локального канала (ключ).
            info: Справочный словарь с данными по всем каналам.

        Returns:
            Строка с целевой аудиторией.

        Raises:
            ValueError: Если данные об аудитории не найдены.
        """
        SPECIAL = 'ИЗМЕРЯЕМОЕ ЛОКАЛЬНОЕ ТВ'

        if national == SPECIAL:
            aud = info.get(SPECIAL, {}).get(original, {})

            if 'audience' not in aud:
                raise ValueError('Не найдена аудитория [%s][%s]' % (SPECIAL, original))

            return aud['audience']

        aud = info.get(national, {}).get(original, {})

        if 'audience' not in aud:
            raise ValueError('Не найдена аудитория [%s][%s]' % (national, original))

        return aud['audience']

    @staticmethod
    def get_name(national: str, original: str, info: dict) -> str:
        """
        Возвращает имя канала.

        Args:
            national: Название национальной телекомпании или спецкатегории.
            original: Оригинальное название локального канала (ключ).
            info: Справочный словарь с данными по всем каналам.

        Returns:
            Имя канала.

        Raises:
            ValueError: Если имя канала не найдено.
        """
        SPECIAL = 'ИЗМЕРЯЕМОЕ ЛОКАЛЬНОЕ ТВ'

        if national == SPECIAL:
            loc = info.get(SPECIAL, {}).get(original, {})

            if 'name' not in loc:
                raise ValueError('Не найдено имя канала [%s][%s]' % (SPECIAL, original))

            return loc['name']

        company = info.get(national, {})

        if 'name' not in company:
            raise ValueError('Не найдено имя канала [%s]' % national)

        return company['name']

    @staticmethod
    def get_round(national: str, original: str, year: int, info: dict) -> float:
        """
        Возвращает коэффициент округления для канала за указанный год.

        Args:
            national: Название национальной телекомпании или спецкатегории.
            original: Оригинальное название локального канала (ключ).
            year: Год, за который нужен коэффициент округления.
            info: Справочный словарь с данными по всем каналам.

        Returns:
            Коеффициент округления (float). Если в данных стоит null, возвращается 0.0.

        Raises:
            ValueError: Если нет данных об округлении.
        """
        SPECIAL = 'ИЗМЕРЯЕМОЕ ЛОКАЛЬНОЕ ТВ'

        if national == SPECIAL:
            loc = info.get(SPECIAL, {}).get(original, {})
            rounds = loc.get('round', {})
            val = rounds.get(str(year))

            if val is None:
                return 0.0

            return val

        company = info.get(national, {})
        rounds = company.get('round', {})

        if str(year) not in rounds:
            raise ValueError('Нет данных об округлении за %s [%s]' % (year, national))

        return rounds[str(year)] or 0.0
