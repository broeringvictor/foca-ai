from __future__ import annotations

from datetime import datetime, UTC
from typing import TYPE_CHECKING
from uuid import UUID

from pgvector.sqlalchemy import HALFVEC
from sqlalchemy import JSON, DateTime, ForeignKey, String, Integer, Float
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
    
    # Defaults ao final
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default_factory=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default_factory=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )

    number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    priority_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.2, server_default="0.2")
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="unclassified")

    tags: Mapped[list[str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default_factory=list,
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        HALFVEC(3072).with_variant(JSON(), "sqlite"),
        nullable=True,
        default=None,
    )

    exam: Mapped["ExamModel"] = relationship(back_populates="questions", init=False)
