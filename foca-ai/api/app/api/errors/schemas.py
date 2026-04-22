from pydantic import BaseModel, ConfigDict


class ErrorItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    field: str
    message: str
    source: str | None = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    detail: list[ErrorItem]
