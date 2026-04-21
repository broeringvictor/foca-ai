from datetime import datetime
from pydantic import BaseModel, ConfigDict, UUID8
from app.domain.enums.law_area import LawArea


class GetQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: UUID8
    exam_id: UUID8
    statement: str
    area: LawArea
    alternative_a: str
    alternative_b: str
    alternative_c: str
    alternative_d: str
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class ListQuestionsResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    questions: list[GetQuestionResponse]


class PaginatedQuestionResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: GetQuestionResponse | None
    current_index: int
    total_questions: int
    has_next: bool


class QuestionListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: UUID8
    statement: str
    alternative_a: str
    alternative_b: str
    alternative_c: str
    alternative_d: str


class GetQuestionsListResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    questions: list[QuestionListItem]

