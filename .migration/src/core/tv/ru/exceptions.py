class CrosstabTaskError(Exception):
    """Исключение для ошибки при расчете crosstab задачи."""

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message)


class CrosstabEmptyResult(Exception):
    """Исключение для пустого результата crosstab задачи."""

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message)
