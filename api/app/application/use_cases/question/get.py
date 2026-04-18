from uuid import UUID

from app.api.errors.exceptions import NotFoundError
from app.application.dto.question.get_dto import (
    GetQuestionResponse,
    ListQuestionsResponse,
    PaginatedQuestionResponse,
)
from app.domain.repositories.question_repository import IQuestionRepository


class GetQuestion:
    def __init__(self, repository: IQuestionRepository) -> None:
        self._repo = repository

    async def execute(self, question_id: UUID) -> GetQuestionResponse:
        question = await self._repo.find_by_id(question_id)
        if question is None:
            raise NotFoundError(
                "Questão não encontrada", field="question_id", source="path"
            )

        return GetQuestionResponse.model_validate(question)


class ListQuestionsByExam:
    def __init__(self, repository: IQuestionRepository) -> None:
        self._repo = repository

    async def execute(self, exam_id: UUID) -> ListQuestionsResponse:
        questions = await self._repo.find_all_by_exam_id(exam_id)
        return ListQuestionsResponse(
            questions=[GetQuestionResponse.model_validate(q) for q in questions]
        )


class GetNextQuestionByExam:
    def __init__(self, repository: IQuestionRepository) -> None:
        self._repo = repository

    async def execute(self, exam_id: UUID, index: int) -> PaginatedQuestionResponse:
        total = await self._repo.count_by_exam_id(exam_id)
        question = await self._repo.find_one_by_exam_id_at_index(exam_id, index)

        return PaginatedQuestionResponse(
            question=(
                GetQuestionResponse.model_validate(question)
                if question
                else None
            ),
            current_index=index,
            total_questions=total,
            has_next=index + 1 < total,
        )
