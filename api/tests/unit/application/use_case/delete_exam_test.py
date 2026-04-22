from uuid import uuid8
from unittest.mock import AsyncMock

import pytest

from app.api.errors.exceptions import NotFoundError
from app.application.use_cases.exam.delete import DeleteExam


@pytest.fixture
def exam_repo() -> AsyncMock:
    mock = AsyncMock()
    mock.find_by_id.return_value = object()
    return mock


@pytest.fixture
def question_repo() -> AsyncMock:
    mock = AsyncMock()
    mock.delete_all_by_exam_id.return_value = 3
    return mock


@pytest.fixture
def use_case(exam_repo: AsyncMock, question_repo: AsyncMock) -> DeleteExam:
    return DeleteExam(repository=exam_repo, question_repository=question_repo)


class TestDeleteExam:
    @pytest.mark.asyncio
    async def test_deletes_related_questions_before_exam(
        self,
        use_case: DeleteExam,
        exam_repo: AsyncMock,
        question_repo: AsyncMock,
    ):
        exam_id = uuid8()

        result = await use_case.execute(exam_id)

        question_repo.delete_all_by_exam_id.assert_awaited_once_with(exam_id)
        exam_repo.delete.assert_awaited_once_with(exam_id)
        assert result.exam_id == exam_id

    @pytest.mark.asyncio
    async def test_raises_not_found_when_exam_does_not_exist(
        self,
        use_case: DeleteExam,
        exam_repo: AsyncMock,
        question_repo: AsyncMock,
    ):
        exam_repo.find_by_id.return_value = None
        exam_id = uuid8()

        with pytest.raises(NotFoundError, match="Exame não encontrado"):
            await use_case.execute(exam_id)

        question_repo.delete_all_by_exam_id.assert_not_called()
        exam_repo.delete.assert_not_called()
