class TemplateDataError(Exception):
    """Исключение для ошибок валидации данных шаблона."""

    def __init__(self, message: str, field: object | None = None):
        self.field = field
        super().__init__(message)
