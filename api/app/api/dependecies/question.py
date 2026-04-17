from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.question.check_answer import CheckAnswer
from app.application.use_cases.question.create import CreateQuestion
from app.application.use_cases.question.delete import DeleteQuestion
from app.application.use_cases.question.get import GetQuestion, ListQuestionsByExam
from app.application.use_cases.question.update import UpdateQuestion
from app.infrastructure.repositories.question_repository import QuestionRepository
from app.infrastructure.session import get_session


def get_create_question_dependency(
    session: AsyncSession = Depends(get_session),
) -> CreateQuestion:
    return CreateQuestion(repository=QuestionRepository(session))


def get_update_question_dependency(
    session: AsyncSession = Depends(get_session),
) -> UpdateQuestion:
    return UpdateQuestion(repository=QuestionRepository(session))


def get_delete_question_dependency(
    session: AsyncSession = Depends(get_session),
) -> DeleteQuestion:
    return DeleteQuestion(repository=QuestionRepository(session))


def get_question_dependency(
    session: AsyncSession = Depends(get_session),
) -> GetQuestion:
    return GetQuestion(repository=QuestionRepository(session))


def list_questions_by_exam_dependency(
    session: AsyncSession = Depends(get_session),
) -> ListQuestionsByExam:
    return ListQuestionsByExam(repository=QuestionRepository(session))


def get_check_answer_dependency(
    session: AsyncSession = Depends(get_session),
) -> CheckAnswer:
    return CheckAnswer(repository=QuestionRepository(session))
