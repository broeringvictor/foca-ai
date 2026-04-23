from pydantic import BaseModel, ConfigDict, Field

from app.application.dto.question.area_validation_dto import AreaDistributionValidation
from app.domain.entities.question import Question
from app.domain.value_objects.raw_exam import RawExam


class CategorizeQuestionsDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    exam: RawExam


class CategorizeQuestionsResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    questions: list[Question] = Field(default_factory=list)
    questions_count: int = Field(..., ge=0, examples=[80])
    area_validation: AreaDistributionValidation


class RecategorizeExistingDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    exam_id: UUID8 | None = None
    question_id: UUID8 | None = None
    format_statement: bool = True
    categorize_tags: bool = True
    categorize_law_area: bool = True


class RecategorizeExistingResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    updated_count: int
    questions: list[Question]
