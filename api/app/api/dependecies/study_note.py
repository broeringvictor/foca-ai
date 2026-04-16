from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.study_note.create import CreateStudyNote
from app.infrastructure.repositories.study_note_repository import StudyNoteRepository
from app.infrastructure.session import get_session


def get_create_study_note_dependency(
    session: AsyncSession = Depends(get_session),
) -> CreateStudyNote:
    return CreateStudyNote(repository=StudyNoteRepository(session))
