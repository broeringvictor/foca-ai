from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.model import table_registry

if TYPE_CHECKING:
    from app.infrastructure.model.question_model import QuestionModel


@table_registry.mapped_as_dataclass()
class ExamModel:
    __tablename__ = "exam"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    edition: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    board: Mapped[str] = mapped_column(String(100), nullable=False)
    exam_type: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    color: Mapped[str] = mapped_column(String(30), nullable=False, default="BRANCA")
    first_phase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    second_phase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    questions: Mapped[list["QuestionModel"]] = relationship(
        back_populates="exam",
        cascade="all, delete-orphan",
        passive_deletes=True,
        init=False,
        default_factory=list,
    )
