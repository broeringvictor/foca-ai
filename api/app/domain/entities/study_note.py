from datetime import datetime

from uuid import uuid8

from pydantic import BaseModel, UUID8, Field


class StudyNote(BaseModel):
    id: UUID8 = Field(default_factory=uuid8)
    user_id: UUID8
    title: str = Field(..., min_length=4, max_length=100)
    description: str | None = Field(None, min_length=4, max_length=500)
    content: str | None = Field(None, max_length=5000)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def create(cls,
               user_id: UUID8,
               title: str,
               description: str | None = None,
               content: str | None = None,
               tags: list[str] | None = None,
               ) -> "StudyNote":
        return cls(
            user_id=user_id,
            title=title,
            description=description,
            content=content,
            tags=tags or [],
        )