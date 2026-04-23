from typing import Protocol

from pydantic import UUID8

from app.domain.entities.question import Question
from app.domain.value_objects.raw_exam import RawExam


class IQuestionCategorizationService(Protocol):
    def classify(
        self, raw_exam: RawExam, exam_id: UUID8 | None = None
    ) -> list[Question]: ...

    def recategorize(
        self,
        questions: list[Question],
        format_statement: bool = True,
        categorize_tags: bool = True,
        categorize_law_area: bool = True,
    ) -> list[Question]: ...
