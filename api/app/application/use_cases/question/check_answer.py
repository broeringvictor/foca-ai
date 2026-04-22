from uuid import UUID

from app.api.errors.exceptions import NotFoundError
from app.application.dto.question.check_answer_dto import (
    CheckAnswerDTO,
    CheckAnswerResponse,
)
from app.domain.repositories.question_repository import IQuestionRepository


class CheckAnswer:
    def __init__(self, repository: IQuestionRepository) -> None:
        self._repo = repository

    async def execute(
        self, question_id: UUID, input_data: CheckAnswerDTO
    ) -> CheckAnswerResponse:
        question = await self._repo.find_by_id(question_id)
        if question is None:
            raise NotFoundError(
                "Questão não encontrada", field="question_id", source="path"
            )

        return CheckAnswerResponse(
            question_id=question.id,
            is_correct=question.correct == input_data.answer,
        )
