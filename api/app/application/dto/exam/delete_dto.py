from pydantic import BaseModel, ConfigDict, Field, UUID8


class DeleteExamResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    exam_id: UUID8 = Field(..., examples=["01965354-a47f-816a-a4ce-f4fa7f87f617"])
    message: str = Field(default="Exam deleted successfully")

