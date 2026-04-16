from pydantic import BaseModel, ConfigDict, Field, UUID8


class DeleteQuestionResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    question_id: UUID8 = Field(..., examples=["01965366-a7bf-8c8d-b791-b2fef0ddf742"])
    message: str = Field(default="Question deleted successfully")

