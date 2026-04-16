from pydantic import UUID8, Field

from app.domain.entities.base import Entity


class StudyNote(Entity):
    """Entidade dos Markdowns destinados ao Estudo.

    :ivar user_id: User.id -> UUID8.
    :ivar title: str, 4-100 caracteres.
    :ivar description: str opcional, 4-500 caracteres.
    :ivar content: str opcional, até 20000 caracteres (Markdown).
    :ivar tags: list[str], default [].
    """

    user_id: UUID8
    title: str = Field(..., min_length=4, max_length=100)
    description: str | None = Field(None, min_length=4, max_length=500)
    content: str | None = Field(None, max_length=20000)
    tags: list[str] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
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
