from datetime import datetime

import pytest

from trinity.utils.tools import Parser, TextTools


class TestTextTools:
    @pytest.mark.parametrize(
        'string, expected',
        [
            ('Apple', 'Apple'),
            ('  Apple  ', 'Apple'),
            ('\nApple\n', 'Apple'),
            ('\t\n\r Apple \t\n\r', 'Apple'),
        ],
    )
    def test_to_clean(self, string: str, expected: str):
        assert TextTools.to_clean(string) == expected

    @pytest.mark.parametrize(
        'string, max_length, expected',
        [
            ('Hello', 10, 'Hello'),
            ('Hello, world!', 10, 'Hello, ...'),
        ],
    )
    def test_to_trunc(self, string: str, max_length: int, expected: str):
        assert TextTools.to_trunc(string, max_length) == expected

    @pytest.mark.parametrize(
        'string, expected',
        [
            ('-', True),
            ('', True),
            ('\n', True),
            ('\t', True),
            (' ', True),
            ('n/a', True),
            ('none', True),
        ],
    )
    def test_is_empty(self, string: str, expected: bool):
        assert TextTools.is_empty(string) == expected

    @pytest.mark.skip(reason='Тестирование метода излишне, так как hashlib - встроенная библиотека.')
    def test_get_hash(self):
        pass


class TestParser:
    @pytest.mark.parametrize(
        'string, expected',
        [
            # Целые числа.
            ('123', 123.0),
            ('0', 0.0),
            # Числа с плавающей точкой (точка как разделитель).
            ('123.0', 123.0),
            ('0.5', 0.5),
            ('.5', 0.5),
            # Числа с плавающей точкой (запятая как разделитель).
            ('123,4', 123.4),
            ('0,75', 0.75),
            # Отрицательные числа.
            ('-1.5', -1.5),
            ('-10', -10.0),
            ('-0,5', -0.5),
            # Числа с разделителями тысяч (пробел, запятая, точка).
            ('1,123.0', 1123.0),  # Запятая как разделитель тысяч, точка - десятичный.
            ('1 234.5', 1234.5),  # Пробел как разделитель тысяч, точка - десятичный.
            ('1 000 000', 1000000.0),  # Пробелы как разделители тысяч, целое число.
            ('2,000,000.75', 2000000.75),  # Запятые как разделители тысяч, точка - десятичный.
            # Числа с ведущими или конечными пробелами.
            ('  123.45  ', 123.45),
            ('\t42,7\n', 42.7),
            # Невалидные или пустые строки.
            ('-', None),
            (' ', None),
            ('', None),
        ],
    )
    def test_parse_number(self, string: str, expected: float | None):
        assert Parser.parse_number(string) == expected

    @pytest.mark.parametrize(
        'string, expected',
        [
            # Форматы YYYY-MM-DD и с разными разделителями.
            ('2025-06-01', datetime(2025, 6, 1, 0, 0, 0)),
            ('2025/06/01', datetime(2025, 6, 1, 0, 0, 0)),
            ('2025.06.01', datetime(2025, 6, 1, 0, 0, 0)),
            ('2025-06-01 15:30:45', datetime(2025, 6, 1, 0, 0, 0)),
            ('2025/06/01 23:59:59', datetime(2025, 6, 1, 0, 0, 0)),
            ('2025.06.01 08:00:00', datetime(2025, 6, 1, 0, 0, 0)),
            # Форматы DD-MM-YYYY и с разными разделителями.
            ('01-06-2025', datetime(2025, 6, 1, 0, 0, 0)),
            ('01/06/2025', datetime(2025, 6, 1, 0, 0, 0)),
            ('01.06.2025', datetime(2025, 6, 1, 0, 0, 0)),
            ('01-06-2025 12:00:00', datetime(2025, 6, 1, 0, 0, 0)),
            ('01/06/2025 05:05:05', datetime(2025, 6, 1, 0, 0, 0)),
            ('01.06.2025 19:19:19', datetime(2025, 6, 1, 0, 0, 0)),
            # Некорректные или пустые строки.
            ('', None),
            (' ', None),
            ('not a date', None),
            ('2025-13-01', None),  # Неверный месяц.
            ('31-02-2025', None),  # Неверная дата.
        ],
    )
    def test_parse_date(self, string: str, expected: datetime | None):
        assert Parser.parse_date(string) == expected

    # TODO: Реализовать тест.
    @pytest.mark.skip(reason='Пока не реализован.')
    def test_parse_object(self):
        pass

    @pytest.mark.parametrize(
        'string, expected',
        [
            ('10:00 - 11:00', '10:00:00-11:00:00'),
            ('09:30 - 10:30', '09:30:00-10:30:00'),
            ('12:00 - 13:00', '12:00:00-13:00:00'),
            ('14:00 - 15:00', '14:00:00-15:00:00'),
        ],
    )
    def test_parse_timeslot(self, string: str, expected: str | None):
        assert Parser.parse_timeslot(string) == expected
