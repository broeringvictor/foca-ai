from pydantic import BaseModel, ConfigDict, Field

from app.application.dto.question.area_validation_dto import AreaDistributionValidation
from app.application.dto.question.get_dto import QuestionListItem
from app.domain.value_objects.raw_exam import RawExam


class CategorizeQuestionsDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    exam: RawExam


class CategorizeQuestionsResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    questions: list[QuestionListItem] = Field(default_factory=list)
    questions_count: int = Field(..., ge=0, examples=[80])
    area_validation: AreaDistributionValidation
