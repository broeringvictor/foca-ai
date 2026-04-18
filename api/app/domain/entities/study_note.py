from pydantic import UUID8, Field

from app.domain.entities.base import Entity
from app.domain.value_objects.tags import Tags


class StudyNote(Entity):
    """Entidade dos Markdowns destinados ao Estudo.

    :ivar user_id: User.id -> UUID8.
    :ivar title: str, 4-100 caracteres.
    :ivar description: str opcional, 4-500 caracteres.
    :ivar content: str opcional, até 20000 caracteres (Markdown).
    :ivar tags: Tags livres (máx 20, cada uma até 30 caracteres).
    """

    user_id: UUID8
    title: str = Field(..., min_length=4, max_length=100)
    description: str | None = Field(None, min_length=4, max_length=500)
    content: str | None = Field(None, max_length=20000)
    tags: Tags = Field(default_factory=list)
    embedding: list[float] | None = None

    @classmethod
    def create(
        cls,
        user_id: UUID8,
        title: str,
        description: str | None = None,
        content: str | None = None,
        tags: list[str] | None = None,
        embedding: list[float] | None = None,
    ) -> "StudyNote":
        return cls(
            user_id=user_id,
            title=title,
            description=description,
            content=content,
            tags=tags or [],
            embedding=embedding,
        )
