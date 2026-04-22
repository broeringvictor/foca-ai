from uuid import UUID

from sqlalchemy import JSON, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.model import table_registry


@table_registry.mapped_as_dataclass()
class ExamStatsView:
    """Read-only: agregações por exame (total de questões e contagem por área).

    ``questions_by_area`` é um JSONB no formato ``{"civil": 10, "criminal": 5}``.
    Tabela física é a VIEW ``v_exam_stats``, criada via Alembic.
    """

    __tablename__ = "v_exam_stats"
    __table_args__ = {"info": {"is_view": True}}

    exam_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    edition: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)
    total_questions: Mapped[int] = mapped_column(Integer)
    questions_by_area: Mapped[dict[str, int] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite")
    )
