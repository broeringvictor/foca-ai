from pydantic import UUID8, Field
from app.domain.entities.base import Entity
from app.domain.value_objects.sm2_progress import Sm2Progress, Sm2Algorithm
from app.domain.enums.answer_quality import AnswerQuality

class StudyQuestion(Entity):
    """Representa o progresso de estudo de um usuário em uma questão específica."""
    user_id: UUID8
    question_id: UUID8
    review_progress: Sm2Progress = Field(default_factory=Sm2Progress.create_default)

    def submit_review(self, quality: AnswerQuality) -> None:
        self.review_progress = Sm2Algorithm.calculate_next_review(self.review_progress, quality)

    @classmethod
    def create(cls, user_id: UUID8, question_id: UUID8) -> "StudyQuestion":
        return cls(user_id=user_id, question_id=question_id)
