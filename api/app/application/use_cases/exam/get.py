from uuid import UUID

from app.api.errors.exceptions import NotFoundError
from app.application.dto.exam.get_dto import GetExamResponse, ListExamsResponse
from app.domain.repositories.exam_repository import IExamRepository


class GetExam:
    def __init__(self, repository: IExamRepository) -> None:
        self._repo = repository

    async def execute(self, exam_id: UUID) -> GetExamResponse:
        exam = await self._repo.find_by_id(exam_id)
        if exam is None:
            raise NotFoundError(
                "Exame não encontrado", field="exam_id", source="path"
            )

        return GetExamResponse.model_validate(exam)


class ListExams:
    def __init__(self, repository: IExamRepository) -> None:
        self._repo = repository

    async def execute(self) -> ListExamsResponse:
        exams = await self._repo.find_all()
        return ListExamsResponse(
            exams=[GetExamResponse.model_validate(e) for e in exams]
        )
