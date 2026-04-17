from uuid import UUID

from loguru import logger

from app.api.errors.exceptions import NotFoundError
from app.application.dto.exam.delete_dto import DeleteExamResponse
from app.domain.repositories.exam_repository import IExamRepository


class DeleteExam:
    def __init__(self, repository: IExamRepository) -> None:
        self._repo = repository

    async def execute(self, exam_id: UUID) -> DeleteExamResponse:
        exam = await self._repo.find_by_id(exam_id)
        if exam is None:
            raise NotFoundError(
                "Exame não encontrado", field="exam_id", source="path"
            )

        try:
            await self._repo.delete(exam_id)
        except Exception as e:
            logger.exception(f"Erro ao deletar exame: {e}")
            raise

        return DeleteExamResponse(exam_id=exam_id)
