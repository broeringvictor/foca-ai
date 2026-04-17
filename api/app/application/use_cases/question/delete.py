from uuid import UUID

from loguru import logger

from app.api.errors.exceptions import NotFoundError
from app.application.dto.question.delete_dto import DeleteQuestionResponse
from app.domain.repositories.question_repository import IQuestionRepository


class DeleteQuestion:
    def __init__(self, repository: IQuestionRepository) -> None:
        self._repo = repository

    async def execute(self, question_id: UUID) -> DeleteQuestionResponse:
        question = await self._repo.find_by_id(question_id)
        if question is None:
            raise NotFoundError(
                "Questão não encontrada", field="question_id", source="path"
            )

        try:
            await self._repo.delete(question_id)
        except Exception as e:
            logger.exception(f"Erro ao deletar questão: {e}")
            raise

        return DeleteQuestionResponse(question_id=question_id)
