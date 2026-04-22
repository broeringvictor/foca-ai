from loguru import logger

from app.application.dto.question.create_dto import (
    CreateQuestionDTO,
    CreateQuestionResponse,
)
from app.domain.entities.question import Question
from app.domain.repositories.question_repository import IQuestionRepository


class CreateQuestion:
    def __init__(self, repository: IQuestionRepository) -> None:
        self._repo = repository

    async def execute(self, input_data: CreateQuestionDTO) -> CreateQuestionResponse:
        question = Question.create(
            exam_id=input_data.exam_id,
            statement=input_data.statement,
            area=input_data.area,
            correct=input_data.correct,
            alternative_a=input_data.alternative_a,
            alternative_b=input_data.alternative_b,
            alternative_c=input_data.alternative_c,
            alternative_d=input_data.alternative_d,
            tags=input_data.tags,
        )

        try:
            await self._repo.save(question)
        except Exception as e:
            logger.exception(f"Erro ao salvar questão: {e}")
            raise

        return CreateQuestionResponse(
            question_id=question.id,
            statement=question.statement,
            created_at=question.created_at,
        )
