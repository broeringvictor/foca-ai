from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.model import table_registry


@table_registry.mapped_as_dataclass()
class StudyModel:
    __tablename__ = "study"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    area: Mapped[str] = mapped_column(String(100), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    review_progress: Mapped[dict] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default_factory=lambda: {
            "ease_factor": 2.5,
            "interval_days": 0,
            "next_review_date": datetime.now(timezone.utc).date().isoformat(),
            "card_status": 0,
            "lapsed_count": 0,
        },
    )

    __table_args__ = (
        UniqueConstraint("user_id", "area", name="uq_user_area_study"),
    )
