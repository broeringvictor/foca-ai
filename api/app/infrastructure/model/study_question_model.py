from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.model import table_registry


@table_registry.mapped_as_dataclass()
class StudyQuestionModel:
    __tablename__ = "study_question"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("question.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    review_progress: Mapped[dict] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_user_question_study"),
    )
