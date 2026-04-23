from pydantic import UUID8, Field
from app.domain.entities.base import Entity
from app.domain.enums.law_area import LawArea
from app.domain.value_objects.sm2_progress import Sm2Progress, Sm2Algorithm
from app.domain.enums.answer_quality import AnswerQuality

class Study(Entity):
    """Representa o progresso de estudo de um usuário em uma área específica (Direito)."""
    user_id: UUID8
    area: LawArea
    review_progress: Sm2Progress = Field(default_factory=Sm2Progress.create_default)

    def submit_review(self, quality: AnswerQuality) -> None:
        self.review_progress = Sm2Algorithm.calculate_next_review(self.review_progress, quality)

    @classmethod
    def create(cls, user_id: UUID8, area: LawArea) -> "Study":
        return cls(user_id=user_id, area=area)
