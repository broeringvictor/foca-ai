from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.study.list_due import ListDueLawAreas
from app.application.use_cases.study.list_progress import ListUserStudyProgress
from app.application.use_cases.study.submit_review import SubmitAreaReview
from app.application.use_cases.study.get_next_session import GetNextStudySession
from app.infrastructure.repositories.question_repository import QuestionRepository
from app.infrastructure.repositories.study_repository import StudyRepository
from app.infrastructure.repositories.study_question_repository import StudyQuestionRepository
from app.infrastructure.repositories.study_note_repository import StudyNoteRepository
from app.infrastructure.session import get_session

def get_list_user_study_progress_dependency(
    session: AsyncSession = Depends(get_session),
) -> ListUserStudyProgress:
    return ListUserStudyProgress(
        study_repository=StudyRepository(session),
        question_repository=QuestionRepository(session),
        study_question_repository=StudyQuestionRepository(session)
    )

def get_list_due_law_areas_dependency(
    session: AsyncSession = Depends(get_session),
) -> ListDueLawAreas:
    return ListDueLawAreas(
        study_repository=StudyRepository(session),
        question_repository=QuestionRepository(session),
        study_question_repository=StudyQuestionRepository(session)
    )

def get_submit_area_review_dependency(
    session: AsyncSession = Depends(get_session),
) -> SubmitAreaReview:
    return SubmitAreaReview(
        study_repository=StudyRepository(session),
        question_repository=QuestionRepository(session),
        study_question_repository=StudyQuestionRepository(session)
    )

def get_next_study_session_dependency(
    session: AsyncSession = Depends(get_session),
) -> GetNextStudySession:
    return GetNextStudySession(
        study_repository=StudyRepository(session),
        question_repository=QuestionRepository(session),
        study_question_repository=StudyQuestionRepository(session),
        study_note_repository=StudyNoteRepository(session)
    )
