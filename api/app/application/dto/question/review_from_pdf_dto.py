from pydantic import BaseModel, ConfigDict, Field

from app.application.dto.question.area_validation_dto import AreaDistributionValidation
from app.domain.entities.question import Question
from app.domain.value_objects.raw_exam import RawExam


class ReviewQuestionsFromPDFResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    exam: RawExam
    questions: list[Question] = Field(default_factory=list)
    extracted_questions_count: int = Field(..., ge=0, examples=[80])
    categorized_questions_count: int = Field(..., ge=0, examples=[80])
    area_validation: AreaDistributionValidation
