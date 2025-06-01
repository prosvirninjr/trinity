from datetime import datetime

import pytest

from trinity.services.logic import Coefficient


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
