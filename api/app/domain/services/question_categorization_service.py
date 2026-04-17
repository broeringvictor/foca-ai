from typing import Protocol

from app.domain.entities.question import Question
from app.domain.value_objects.raw_exam import RawExam


class IQuestionCategorizationService(Protocol):
    def classify(self, raw_exam: RawExam) -> list[Question]: ...
