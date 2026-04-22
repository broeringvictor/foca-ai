from pydantic import UUID8, Field

from app.domain.entities.base import Entity
from app.domain.enums.alternatives import Alternative
from app.domain.enums.law_area import LawArea
from app.domain.value_objects.tags import Tags


class Question(Entity):
    """Questo objetiva de um exame (ex: OAB 1 fase).

    :ivar exam_id: Exam.id -> UUID8.
    :ivar number: Numero da questao no caderno (1-80).
    :ivar statement: Enunciado da questo (4-1500 caracteres).
    :ivar area: Área do direito da questão.
    :ivar correct: Alternativa correta (A-D).
    :ivar alternative_a: Texto da alternativa A (1-500 caracteres).
    :ivar alternative_b: Texto da alternativa B (1-500 caracteres).
    :ivar alternative_c: Texto da alternativa C (1-500 caracteres).
    :ivar alternative_d: Texto da alternativa D (1-500 caracteres).
    :ivar tags: Tags livres (mx 20, cada uma at 30 caracteres).
    :ivar confidence: Confianca na classificacao da area.
    :ivar source: Fonte da classificacao (ex: initial, review).
    """

    exam_id: UUID8
    number: int = Field(..., gt=0)
    statement: str = Field(..., min_length=4, max_length=1500)
    area: LawArea
    correct: Alternative
    alternative_a: str = Field(..., min_length=1, max_length=1000)
    alternative_b: str = Field(..., min_length=1, max_length=1000)
    alternative_c: str = Field(..., min_length=1, max_length=1000)
    alternative_d: str = Field(..., min_length=1, max_length=1000)
    tags: Tags = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source: str = Field(default="unclassified")
    embedding: list[float] | None = None

    @property
    def embedding_text(self) -> str:
        """Texto usado como input do embedding: enunciado + alternativa correta."""
        correct_text = {
            Alternative.A: self.alternative_a,
            Alternative.B: self.alternative_b,
            Alternative.C: self.alternative_c,
            Alternative.D: self.alternative_d,
        }[self.correct]
        return f"{self.statement}\n\n{correct_text}"

    @classmethod
    def create(
        cls,
        exam_id: UUID8,
        number: int,
        statement: str,
        area: LawArea,
        correct: Alternative,
        alternative_a: str,
        alternative_b: str,
        alternative_c: str,
        alternative_d: str,
        tags: list[str] | None = None,
        confidence: float = 0.0,
        source: str = "unclassified",
        embedding: list[float] | None = None,
    ) -> "Question":
        return cls(
            exam_id=exam_id,
            number=number,
            statement=statement,
            area=area,
            correct=correct,
            alternative_a=alternative_a,
            alternative_b=alternative_b,
            alternative_c=alternative_c,
            alternative_d=alternative_d,
            tags=tags or [],
            confidence=confidence,
            source=source,
            embedding=embedding,
        )
