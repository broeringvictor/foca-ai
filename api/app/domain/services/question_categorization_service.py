from typing import Any, Protocol

from app.domain.entities.question import Question
from app.domain.value_objects.raw_exam import RawExam


class IChatModel(Protocol):
    def invoke(self, input: Any, **kwargs: Any) -> Any: ...


class IQuestionCategorizationService(Protocol):
    def classify(self, raw_exam: RawExam) -> list[Question]: ...
