from pydantic import BaseModel, ConfigDict, Field

from app.application.dto.question.area_validation_dto import AreaDistributionValidation


class ReviewQuestionsFromPDFResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    extracted_questions_count: int = Field(..., ge=0, examples=[80])
    categorized_questions_count: int = Field(..., ge=0, examples=[80])
    area_validation: AreaDistributionValidation
