from datetime import datetime

import pytest

from trinity.services.logics import Coefficient, MParser


class TestCoefficient:
    @pytest.mark.parametrize(
        'date_from, date_to, round, expected',
        [
            (datetime(2023, 1, 1), datetime(2023, 1, 31), 1, 1.0),
            (datetime(2023, 2, 1), datetime(2023, 2, 28), 1, 1.0),
            (datetime(2023, 2, 1), datetime(2023, 2, 14), 1, 0.5),
            (datetime(2023, 1, 15), datetime(2023, 1, 31), 1, 0.5),
        ],
    )
    def test_calc_rental_c(self, date_from: datetime, date_to: datetime, round: int, expected: float):
        """Проверяет корректность вычисления коэффициента длительности аренды."""
        assert Coefficient.calc_rental_c(date_from, date_to, round) == expected

    @pytest.mark.parametrize(
        'format_, spot_duration, spots_per_block, block_duration, round, expected',
        [
            ('MF', 15, 1, 300, 1, 1.0),
            ('MF', 15, 2, 300, 1, 2.0),
            ('DBB', 5, 1, 50, 1, 1.0),
            ('DBB', 5, 0.5, 50, 1, 0.5),
        ],
    )
    def test_calc_digital_c(
        self,
        format_: str,
        spot_duration: float,
        spots_per_block: float,
        block_duration: float,
        round: int,
        expected: float,
    ):
        """Проверяет корректность вычисления коэффициента digital размещения."""
        assert Coefficient.calc_digital_c(format_, spot_duration, spots_per_block, block_duration, round) == expected


class TestMParser:
    @pytest.mark.parametrize(
        'advertiser, expected',
        [
            ('А101', 'А101'),
            ('НСПК', 'НСПК'),
            ('Домклик', 'Домклик'),
            ('X5 Group', 'X5 Group'),
            ('Х5 Group', 'X5 Group'),
            ('Чижик', 'Чижик'),
            ('Перекресток', 'Перекресток'),
            ('Магнит', 'Магнит'),
            ('Дикси', 'Дикси'),
            ('АО "НСПК"', 'НСПК'),
        ],
    )
    def test_parse_advertiser(self, advertiser: str, expected: str):
        """Проверяет корректность парсинга рекламодателя с разными вариантами входных данных."""
        assert MParser.parse_advertiser(advertiser) == expected

    @pytest.mark.parametrize(
        'city, expected',
        [
            ['Москва', 'Москва'],
            ['Новосибирск', 'Новосибирск'],
            ['Санкт-Петербург', 'Санкт-Петербург'],
            ['Нижний Новгород', 'Нижний Новгород'],
            ['Казань', 'Казань'],
            ['Московская область', 'Московская область'],
            ['Самара', 'Самара'],
            ['Екатеринбург', 'Екатеринбург'],
        ],
    )
    def test_parse_city(self, city: str, expected: str):
        """Проверяет корректность парсинга города с разными вариантами входных данных."""
        assert MParser.parse_city(city) == expected

    def test_parse_line(self, line_cases):
        """Проверяет корректность парсинга строки с разными вариантами входных данных."""
        city, line, station, expected = line_cases
        assert MParser.parse_line(city, line, station) == expected
