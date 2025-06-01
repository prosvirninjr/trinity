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
            ('123', 123.0),
            ('123.0', 123.0),
            ('123,4', 123.4),
            ('1,123.0', 1123.0),
            ('-1.5', -1.5),
            ('.5', 0.5),
        ],
    )
    def test_parse_number(self, string: str, expected: float | None):
        assert Parser.parse_number(string) == expected
