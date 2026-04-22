from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, UUID8


class GetExamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: UUID8
    name: str
    edition: int
    year: int
    board: str
    first_phase_date: date | None
    second_phase_date: date | None
    created_at: datetime
    updated_at: datetime


class ListExamsResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    exams: list[GetExamResponse]


