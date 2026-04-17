from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.exam.create import CreateExam
from app.application.use_cases.exam.delete import DeleteExam
from app.application.use_cases.exam.get import GetExam, ListExams
from app.application.use_cases.exam.update import UpdateExam
from app.infrastructure.repositories.exam_repository import ExamRepository
from app.infrastructure.repositories.question_repository import QuestionRepository
from app.infrastructure.session import get_session


def get_create_exam_dependency(
    session: AsyncSession = Depends(get_session),
) -> CreateExam:
    return CreateExam(repository=ExamRepository(session))


def get_update_exam_dependency(
    session: AsyncSession = Depends(get_session),
) -> UpdateExam:
    return UpdateExam(repository=ExamRepository(session))


def get_delete_exam_dependency(
    session: AsyncSession = Depends(get_session),
) -> DeleteExam:
    return DeleteExam(
        repository=ExamRepository(session),
        question_repository=QuestionRepository(session),
    )


def get_exam_dependency(
    session: AsyncSession = Depends(get_session),
) -> GetExam:
    return GetExam(repository=ExamRepository(session))


def list_exams_dependency(
    session: AsyncSession = Depends(get_session),
) -> ListExams:
    return ListExams(repository=ExamRepository(session))
