from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

class AddAnswerKeyToExamDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    exam_id: UUID
    pdf_bytes: bytes

class AddAnswerKeyToExamResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    exam_id: UUID
    questions_updated: int
