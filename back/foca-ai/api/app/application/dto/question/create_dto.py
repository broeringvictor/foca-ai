from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, UUID8
from app.domain.enums.alternatives import Alternative
from app.domain.enums.law_area import LawArea


class CreateQuestionDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    exam_id: UUID8 = Field(..., examples=["01965354-a47f-816a-a4ce-f4fa7f87f617"])
    statement: str = Field(..., min_length=4, max_length=1500, examples=["Qual a cor do cavalo branco de Napoleão?"])
    area: LawArea = Field(..., examples=[LawArea.ETHICS])
    correct: Alternative = Field(..., examples=[Alternative.A])
    alternative_a: str = Field(..., min_length=1, max_length=1000, examples=["Branco"])
    alternative_b: str = Field(..., min_length=1, max_length=1000, examples=["Preto"])
    alternative_c: str = Field(..., min_length=1, max_length=1000, examples=["Marrom"])
    alternative_d: str = Field(..., min_length=1, max_length=1000, examples=["Cinza"])
    tags: list[str] = Field(default_factory=list, examples=[["história", "curiosidades"]])


class CreateQuestionResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    question_id: UUID8 = Field(..., examples=["01965366-a7bf-8c8d-b791-b2fef0ddf742"])
    statement: str = Field(..., examples=["Qual a cor do cavalo branco de Napoleão?"])
    created_at: datetime = Field(..., examples=["2026-04-16T20:30:00Z"])

