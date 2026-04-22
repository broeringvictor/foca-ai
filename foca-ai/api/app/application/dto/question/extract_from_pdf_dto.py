from pydantic import BaseModel, ConfigDict, Field

from app.domain.value_objects.raw_exam import RawExam


class ExtractFromPDFResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    exam: RawExam
    questions_count: int = Field(..., ge=0, examples=[80])
