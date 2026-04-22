from pydantic import BaseModel, ConfigDict, Field, UUID8

from app.domain.enums.alternatives import Alternative


class CheckAnswerDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    answer: Alternative = Field(..., examples=[Alternative.A])


class CheckAnswerResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    question_id: UUID8 = Field(..., examples=["01965366-a7bf-8c8d-b791-b2fef0ddf742"])
    is_correct: bool = Field(..., examples=[True])
