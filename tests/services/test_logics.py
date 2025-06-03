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

    @pytest.mark.xfail
    def test_parse_line(self, line_cases):
        """Проверяет корректность парсинга строки с разными вариантами входных данных."""
        city, line, station, expected = line_cases
        assert MParser.parse_line(city, line, station) == expected

    @pytest.mark.xfail
    def test_parse_station(self, station_cases):
        """Проверяет корректность парсинга станции с разными вариантами входных данных."""
        city, station, expected = station_cases
        assert MParser.parse_station(city, station) == expected

    @pytest.mark.parametrize(
        'format_, expected',
        [
            ('Экран (транзит)', 'SCREEN'),
            ('Световой короб (транзит)', 'LB'),
            ('экран', 'SCREEN'),
            ('Кристалайт', 'LB'),
            ('Двусторонний стикер', 'STICKER'),
            ('Screen', 'SCREEN'),
            ('Сити-формат цифровой', 'DCF'),
            ('Стикер', 'STICKER'),
            ('Стикеры на турникетах', 'STICKER'),
            ('Цифровой экран 3х1', 'SCREEN'),
            ('LB', 'LB'),
            ('Экраны в вагонах', 'SCREEN'),
            ('стикер в простенке', 'STICKER'),
            ('стикер', 'STICKER'),
            ('Стикер (транзит)', 'STICKER'),
            ('Лайтбокс', 'LB'),
            ('Лайт Бокс', 'LB'),
            ('DCF', 'DCF'),
        ],
    )
    def test_parse_format(self, format_: str, expected: str):
        assert MParser.parse_format(format_) == expected

    @pytest.mark.parametrize(
        'size, expected',
        [
            ('60x72см', '0.6x0.7'),
            ('1,2x1,8', '1.2x1.8'),
            ('1.2x1.8', '1.2x1.8'),
            ('38х40см', '0.4x0.4'),
            ('3х2', '2.0x3.0'),
            ('1,2х1,8', '1.2x1.8'),
            ('0.8x1.2 м', '0.8x1.2'),
            ('2x1.5', '1.5x2.0'),
            ('0.6x0.9', '0.6x0.9'),
            ('5 сек, 416x572рх', None),
            ('5 сек', None),
            ('А4 (1-й ярус)', 'A4'),
            ('1.2х1.8', '1.2x1.8'),
            ('300х600', '0.3x0.6'),
            ('А3', 'A3'),
            ('0,9x0,18', '0.25x0.9'),
            ('5 сек (1280x416)', None),
            ('0,42x0,72', '0.4x0.7'),
            ('51х41см-1', '0.4x0.5'),
            ('1.2x1.8 (5 сек)', '1.2x1.8'),
            ('42х72см', '0.4x0.7'),
            ('1.20x1.80', '1.2x1.8'),
            ('35х15', '0.2x0.4'),
            ('5 сек (1080х1920)', None),
            ('10сек', None),
            ('5 сек (1080x1920)', None),
            ('Экран, 24"', None),
            ('10 сек', None),
            ('3.00x1.50', '1.5x3.0'),
            ('0.95x1.3', '1.0x1.3'),
            ('35х15см', '0.2x0.4'),
            ('40 сек', None),
            ('1280x512', None),
            ('3x2', '2.0x3.0'),
            ('51х85см', '0.5x0.9'),
            ('60x30см-1', '0.3x0.6'),
            ('1.80x1.20', '1.2x1.8'),
            ('0.6x0.9 м', '0.6x0.9'),
            ('42х35см-1', '0.4x0.4'),
            ('А2', 'A2'),
            ('2.75х1.55', '1.6x2.8'),
            ('5  сек, 1.2x1.8', '1.2x1.8'),
            ('416x290', '0.3x0.4'),
            ('1x1,8', '1.0x1.8'),
        ],
    )
    def test_parse_size(self, size: str, expected: str):
        assert MParser.parse_size(size) == expected
