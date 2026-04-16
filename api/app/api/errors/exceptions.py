class AppValueError(ValueError):
    status_code: int = 400

    def __init__(self, message: str, field: str = "geral", source: str | None = None) -> None:
        super().__init__(message)
        self.field = field
        self.source = source


class BadRequestError(AppValueError):
    status_code = 400


class ConflictError(AppValueError):
    status_code = 409


class NotFoundError(AppValueError):
    status_code = 404

