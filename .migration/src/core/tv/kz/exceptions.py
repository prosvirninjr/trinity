class StructureError(Exception):
    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message)


class CalculationError(Exception):
    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message)


class ConfigError(Exception):
    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message)
