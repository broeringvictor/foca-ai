from pydantic import UUID8, BaseModel, ConfigDict, Field
from app.application.dto.question.get_dto import GetQuestionResponse

class RelatedQuestionItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: GetQuestionResponse
    score: float = Field(..., ge=0.0, le=1.0)

class FindRelatedQuestionsToNoteResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    study_note_id: UUID8
    items: list[RelatedQuestionItem] = Field(default_factory=list)
