from datetime import datetime, UTC
from uuid import uuid8

from pydantic import BaseModel, Field, UUID8


class Entity(BaseModel):
    """Base de toda entidade do domínio: id + timestamps."""

    id: UUID8 = Field(
        default_factory=uuid8,
        description="UUID8 gerado automaticamente.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Data de criação (UTC).",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Data da última modificação (UTC).",
    )
