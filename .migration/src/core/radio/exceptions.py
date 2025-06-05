class RadioDataError(Exception):
    def __init__(self, message: str, field: object | None = None):
        self.field = field
        super().__init__(message)


class RadioLogicError(Exception):
    def __init__(self, message: str, field: object | None = None):
        self.field = field
        super().__init__(message)


class RadioTemplateError(Exception):
    def __init__(self, message: str, field: object | None = None):
        self.field = field
        super().__init__(message)
