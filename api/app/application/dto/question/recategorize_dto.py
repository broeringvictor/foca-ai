from pydantic import UUID8, BaseModel, ConfigDict, Field, field_validator
from app.application.dto.question.get_dto import GetQuestionResponse

class RecategorizeExistingDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    exam_id: UUID8 | None = None
    question_id: UUID8 | None = None
    format_statement: bool = True
    categorize_tags: bool = True
    categorize_law_area: bool = True

    @field_validator("exam_id", "question_id", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: object) -> object:
        if v == "":
            return None
        return v


class RecategorizeExistingResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    updated_count: int
    questions: list[GetQuestionResponse]
