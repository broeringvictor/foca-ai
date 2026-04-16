from datetime import datetime
from uuid import UUID

from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, MappedColumn

from app.infrastructure.model import table_registry


@table_registry.mapped_as_dataclass()
class StudyNoteModel:

    __tablename__ = "study_note"

    id: Mapped[UUID] = MappedColumn(PG_UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = MappedColumn(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    tags: Mapped[list[str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default_factory=list,
    )

    user: Mapped["UserModel"] = relationship(back_populates="study_notes", init=False)
