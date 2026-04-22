from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, UUID8
from app.domain.enums.alternatives import Alternative
from app.domain.enums.law_area import LawArea


class UpdateQuestionDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    statement: str | None = Field(None, min_length=4, max_length=1500, examples=["Enunciado atualizado"])
    area: LawArea | None = Field(None, examples=[LawArea.CRIMINAL])
    correct: Alternative | None = Field(None, examples=[Alternative.B])
    alternative_a: str | None = Field(None, min_length=1, max_length=1000)
    alternative_b: str | None = Field(None, min_length=1, max_length=1000)
    alternative_c: str | None = Field(None, min_length=1, max_length=1000)
    alternative_d: str | None = Field(None, min_length=1, max_length=1000)
    tags: list[str] | None = Field(None, examples=[["tag1", "tag2"]])


class UpdateQuestionResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    question_id: UUID8 = Field(..., examples=["01965366-a7bf-8c8d-b791-b2fef0ddf742"])
    updated_at: datetime = Field(..., examples=["2026-04-16T20:45:00Z"])

