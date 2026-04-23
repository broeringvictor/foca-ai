from datetime import datetime

from pydantic import UUID8, BaseModel, ConfigDict, Field


class GetStudyNoteResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID8
    title: str
    description: str | None
    content: str | None
    tags: list[str]
    questions: list[str]
    has_embedding: bool
    created_at: datetime = Field(..., examples=["2026-04-16T20:30:00Z"])
    updated_at: datetime = Field(..., examples=["2026-04-16T20:30:00Z"])
