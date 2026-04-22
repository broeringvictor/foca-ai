from datetime import date, datetime
from uuid import UUID

from sqlalchemy import JSON, Date, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.model import table_registry


@table_registry.mapped_as_dataclass()
class QuestionDetailView:
    """Read-only: questão com metadados do exame já resolvidos via JOIN.

    Tabela física é a VIEW ``v_question_detail``, criada via Alembic.
    """

    __tablename__ = "v_question_detail"
    __table_args__ = {"info": {"is_view": True}}

    question_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    statement: Mapped[str] = mapped_column(String(1500))
    area: Mapped[str] = mapped_column(String(40))
    correct: Mapped[str] = mapped_column(String(1))
    alternative_a: Mapped[str] = mapped_column(String(1000))
    alternative_b: Mapped[str] = mapped_column(String(1000))
    alternative_c: Mapped[str] = mapped_column(String(1000))
    alternative_d: Mapped[str] = mapped_column(String(1000))
    tags: Mapped[list[str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    exam_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True))
    exam_name: Mapped[str] = mapped_column(String(150))
    exam_edition: Mapped[int] = mapped_column(Integer)
    exam_year: Mapped[int] = mapped_column(Integer)
    exam_board: Mapped[str] = mapped_column(String(100))
    first_phase_date: Mapped[date | None] = mapped_column(Date)
    second_phase_date: Mapped[date | None] = mapped_column(Date)
