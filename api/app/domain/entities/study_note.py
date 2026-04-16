from datetime import datetime

from uuid import uuid8

from pydantic import BaseModel, UUID8, Field


class StudyNote(BaseModel):
    """Entidade dos Markdowns destinados ao Estudo.

    :ivar id: UUID8.
    :ivar user_id: User.id -> UUID8.
    :ivar title: str, 4-100 caracteres.
    :ivar description: str opcional, 4-500 caracteres.
    :ivar content: str opcional, até 5000 caracteres (Markdown).
    :ivar tags: list[str], default [].
    :ivar created_at: UTC.
    :ivar updated_at: UTC.
    """

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