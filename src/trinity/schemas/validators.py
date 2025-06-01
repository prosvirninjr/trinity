from typing import Any


def is_number(value: Any) -> Any:
    """Pydantic валидатор. Проверяет, является ли значение числом."""
    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
        pass

    raise ValueError('Значение не является числом.', value)
