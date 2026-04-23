from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.study_question import StudyQuestion

class IStudyQuestionRepository(ABC):
    @abstractmethod
    async def save(self, study_question: StudyQuestion) -> None:
        pass

    @abstractmethod
    async def update(self, study_question: StudyQuestion) -> None:
        pass

    @abstractmethod
    async def find_by_user_and_question(self, user_id: UUID, question_id: UUID) -> StudyQuestion | None:
        pass

    @abstractmethod
    async def find_all_by_user_id(self, user_id: UUID) -> list[StudyQuestion]:
        pass

    @abstractmethod
    async def find_due_by_user_id(self, user_id: UUID, limit: int = 20) -> list[StudyQuestion]:
        pass

    @abstractmethod
    async def find_high_error_by_user_id(self, user_id: UUID, limit: int = 10) -> list[StudyQuestion]:
        pass
