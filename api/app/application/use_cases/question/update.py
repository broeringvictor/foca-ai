from datetime import UTC, datetime
from uuid import UUID

from loguru import logger

from app.api.errors.exceptions import NotFoundError
from app.application.dto.question.update_dto import (
    UpdateQuestionDTO,
    UpdateQuestionResponse,
)
from app.domain.repositories.question_repository import IQuestionRepository


class UpdateQuestion:
    def __init__(self, repository: IQuestionRepository) -> None:
        self._repo = repository

    async def execute(
        self, question_id: UUID, input_data: UpdateQuestionDTO
    ) -> UpdateQuestionResponse:
        question = await self._repo.find_by_id(question_id)
        if question is None:
            raise NotFoundError(
                "Questão não encontrada", field="question_id", source="path"
            )

        updates = input_data.model_dump(exclude_unset=True)
        updates["updated_at"] = datetime.now(UTC)
        updated = question.model_copy(update=updates)

        try:
            await self._repo.update(updated)
        except Exception as e:
            logger.exception(f"Erro ao atualizar questão: {e}")
            raise

        return UpdateQuestionResponse(
            question_id=updated.id,
            updated_at=updated.updated_at,
        )
