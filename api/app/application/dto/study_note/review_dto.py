from uuid import UUID
from pydantic import BaseModel
from app.domain.enums.answer_quality import AnswerQuality
from app.domain.value_objects.sm2_progress import Sm2Progress


class SubmitReviewDTO(BaseModel):
    quality: AnswerQuality


class SubmitReviewResponse(BaseModel):
    study_note_id: UUID
    new_progress: Sm2Progress
