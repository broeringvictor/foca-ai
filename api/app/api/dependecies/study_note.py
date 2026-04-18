from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependecies.embeddings import get_embedding_service_dependency
from app.application.use_cases.study_note.create import CreateStudyNote
from app.application.use_cases.study_note.find_related_to_question import (
    FindRelatedStudyNotes,
)
from app.domain.services.embedding_service import IEmbeddingService
from app.infrastructure.repositories.question_repository import QuestionRepository
from app.infrastructure.repositories.study_note_repository import StudyNoteRepository
from app.infrastructure.session import get_session


def get_create_study_note_dependency(
    session: AsyncSession = Depends(get_session),
    embedding_service: IEmbeddingService = Depends(get_embedding_service_dependency),
) -> CreateStudyNote:
    return CreateStudyNote(
        repository=StudyNoteRepository(session),
        embedding_service=embedding_service,
    )


def get_find_related_study_notes_dependency(
    session: AsyncSession = Depends(get_session),
) -> FindRelatedStudyNotes:
    return FindRelatedStudyNotes(
        study_note_repository=StudyNoteRepository(session),
        question_repository=QuestionRepository(session),
    )
