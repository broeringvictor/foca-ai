from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, UUID8


class CreateExamDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=4, max_length=150, examples=["XL Exame de Ordem Unificado"])
    edition: int = Field(..., gt=0, examples=[40])
    year: int = Field(..., ge=2000, le=2100, examples=[2024])
    board: str = Field(..., min_length=2, max_length=100, examples=["FGV"])
    first_phase_date: date | None = Field(None, examples=["2024-03-24"])
    second_phase_date: date | None = Field(None, examples=["2024-05-19"])


class CreateExamResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    exam_id: UUID8 = Field(..., examples=["01965354-a47f-816a-a4ce-f4fa7f87f617"])
    name: str = Field(..., examples=["XL Exame de Ordem Unificado"])
    edition: int = Field(..., examples=[40])
    created_at: datetime = Field(..., examples=["2026-04-16T20:30:00Z"])

