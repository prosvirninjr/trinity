class OOHDataError(Exception):
    def __init__(self, message: str, field: object | None = None):
        self.field = field
        super().__init__(message)


class OOHLogicError(Exception):
    def __init__(self, message: str, field: object | None = None):
        self.field = field
        super().__init__(message)


class OOHTemplateError(Exception):
    def __init__(self, message: str, field: object | None = None):
        self.field = field
        super().__init__(message)


class OOHHeaderError(Exception):
    def __init__(self, message: str, field: object | None = None):
        self.field = field
        super().__init__(message)
