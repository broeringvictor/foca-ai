from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.model import table_registry

if TYPE_CHECKING:
    from app.infrastructure.model.exam_model import ExamModel


@table_registry.mapped_as_dataclass()
class QuestionModel:
    __tablename__ = "question"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    exam_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("exam.id", ondelete="CASCADE"),
        nullable=False,
    )
    statement: Mapped[str] = mapped_column(String(1500), nullable=False)
    area: Mapped[str] = mapped_column(String(40), nullable=False)
    correct: Mapped[str] = mapped_column(String(1), nullable=False)
    alternative_a: Mapped[str] = mapped_column(String(1000), nullable=False)
    alternative_b: Mapped[str] = mapped_column(String(1000), nullable=False)
    alternative_c: Mapped[str] = mapped_column(String(1000), nullable=False)
    alternative_d: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    tags: Mapped[list[str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default_factory=list,
    )

    exam: Mapped["ExamModel"] = relationship(back_populates="questions", init=False)
