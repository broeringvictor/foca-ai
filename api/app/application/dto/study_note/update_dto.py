from datetime import datetime

from pydantic import UUID8, BaseModel, ConfigDict, Field


class UpdateStudyNoteDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    title: str | None = Field(None, min_length=4, max_length=100)
    description: str | None = Field(None, min_length=4, max_length=500)
    content: str | None = None
    tags: list[str] | None = None


class UpdateStudyNoteResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID8
    title: str
    updated_at: datetime = Field(..., examples=["2026-04-22T00:00:00Z"])
