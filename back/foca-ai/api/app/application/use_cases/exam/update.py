from datetime import UTC, datetime
from uuid import UUID

from loguru import logger

from app.api.errors.exceptions import NotFoundError
from app.application.dto.exam.update_dto import UpdateExamDTO, UpdateExamResponse
from app.domain.repositories.exam_repository import IExamRepository


class UpdateExam:
    def __init__(self, repository: IExamRepository) -> None:
        self._repo = repository

    async def execute(
        self, exam_id: UUID, input_data: UpdateExamDTO
    ) -> UpdateExamResponse:
        exam = await self._repo.find_by_id(exam_id)
        if exam is None:
            raise NotFoundError(
                "Exame não encontrado", field="exam_id", source="path"
            )

        updates = input_data.model_dump(exclude_unset=True)
        updates["updated_at"] = datetime.now(UTC)
        updated = exam.model_copy(update=updates)

        try:
            await self._repo.update(updated)
        except Exception as e:
            logger.exception(f"Erro ao atualizar exame: {e}")
            raise

        return UpdateExamResponse(
            exam_id=updated.id,
            name=updated.name,
            updated_at=updated.updated_at,
        )
