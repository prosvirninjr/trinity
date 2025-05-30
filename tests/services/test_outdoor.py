from datetime import datetime

import pytest

from trinity.services.outdoor import Coefficient


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
