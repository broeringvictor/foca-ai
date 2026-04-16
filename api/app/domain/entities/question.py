from pydantic import UUID8, Field

from app.domain.entities.base import Entity
from app.domain.enums.alternatives import Alternative
from app.domain.enums.law_area import LawArea
from app.domain.value_objects.tags import Tags


class Question(Entity):
    """Questão objetiva de um exame (ex: OAB 1ª fase).

    :ivar exam_id: Exam.id -> UUID8.
    :ivar statement: Enunciado da questão (4-1500 caracteres).
    :ivar area: Área do direito da questão.
    :ivar correct: Alternativa correta (A-D).
    :ivar alternative_a: Texto da alternativa A (1-500 caracteres).
    :ivar alternative_b: Texto da alternativa B (1-500 caracteres).
    :ivar alternative_c: Texto da alternativa C (1-500 caracteres).
    :ivar alternative_d: Texto da alternativa D (1-500 caracteres).
    :ivar tags: Tags livres (máx 20, cada uma até 30 caracteres).
    """

    exam_id: UUID8
    statement: str = Field(..., min_length=4, max_length=1500)
    area: LawArea
    correct: Alternative
    alternative_a: str = Field(..., min_length=1, max_length=1000)
    alternative_b: str = Field(..., min_length=1, max_length=1000)
    alternative_c: str = Field(..., min_length=1, max_length=1000)
    alternative_d: str = Field(..., min_length=1, max_length=1000)
    tags: Tags = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        exam_id: UUID8,
        statement: str,
        area: LawArea,
        correct: Alternative,
        alternative_a: str,
        alternative_b: str,
        alternative_c: str,
        alternative_d: str,
        tags: list[str] | None = None,
    ) -> "Question":
        return cls(
            exam_id=exam_id,
            statement=statement,
            area=area,
            correct=correct,
            alternative_a=alternative_a,
            alternative_b=alternative_b,
            alternative_c=alternative_c,
            alternative_d=alternative_d,
            tags=tags or [],
        )
