from uuid import UUID

from pydantic import UUID8, Field

from app.domain.entities.base import Entity
from app.domain.enums.answer_quality import AnswerQuality
from app.domain.enums.law_area import LawArea
from app.domain.value_objects.sm2_progress import Sm2Algorithm, Sm2Progress
from app.domain.value_objects.tags import Tags


class StudyNote(Entity):
    """Entidade dos Markdowns destinados ao Estudo.

    :ivar user_id: User.id -> UUID8.
    :ivar area: Área do direito da nota.
    :ivar title: str, 4-100 caracteres.
    :ivar description: str opcional, 4-500 caracteres.
    :ivar content: str opcional, até 20000 caracteres (Markdown).
    :ivar tags: Tags livres (máx 20, cada uma até 30 caracteres).
    :ivar questions: IDs de questões relacionadas (score >= 0.65).
    :ivar review_progress: Progresso de repetição espaçada.
    """

    user_id: UUID8
    area: LawArea
    title: str = Field(..., min_length=4, max_length=100)
    description: str | None = Field(None, min_length=4, max_length=500)
    content: str | None = Field(None, max_length=20000)
    tags: Tags = Field(default_factory=list)
    embedding: list[float] | None = None
    questions: list[UUID] = Field(default_factory=list)
    review_progress: Sm2Progress = Field(default_factory=Sm2Progress.create_default)

    def add_question(self, question_id: UUID) -> None:
        if question_id not in self.questions:
            self.questions.append(question_id)

    def update_review(self, quality: AnswerQuality) -> None:
        self.review_progress = Sm2Algorithm.calculate_next_review(self.review_progress, quality)

    @classmethod
    def create(
        cls,
        user_id: UUID8,
        area: LawArea,
        title: str,
        description: str | None = None,
        content: str | None = None,
        tags: list[str] | None = None,
        embedding: list[float] | None = None,
        review_progress: Sm2Progress | None = None,
    ) -> "StudyNote":
        return cls(
            user_id=user_id,
            area=area,
            title=title,
            description=description,
            content=content,
            tags=tags or [],
            embedding=embedding,
            review_progress=review_progress or Sm2Progress.create_default(),
        )
