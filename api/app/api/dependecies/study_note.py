from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.study_note.create import CreateStudyNote
from app.application.use_cases.study_note.delete import DeleteStudyNote
from app.application.use_cases.study_note.find_related_questions import (
    FindRelatedQuestionsToNote,
)
from app.application.use_cases.study_note.find_related_to_note import (
    FindRelatedStudyNotesToNote,
)
from app.application.use_cases.study_note.find_related_to_question import (
    FindRelatedStudyNotes,
)
from app.application.use_cases.study_note.generate_embedding import GenerateStudyNoteEmbedding
from app.application.use_cases.study_note.get import GetStudyNote
from app.application.use_cases.study_note.get_question_list import GetStudyNoteQuestionList
from app.application.use_cases.study_note.list import ListStudyNotes
from app.application.use_cases.study_note.update import UpdateStudyNote
from app.infrastructure.embedding import get_embedding_model
from app.infrastructure.repositories.question_repository import QuestionRepository
from app.infrastructure.repositories.study_note_repository import StudyNoteRepository
from app.infrastructure.session import get_session


def get_create_study_note_dependency(
    session: AsyncSession = Depends(get_session),
) -> CreateStudyNote:
    return CreateStudyNote(repository=StudyNoteRepository(session))


def get_find_related_study_notes_dependency(
    session: AsyncSession = Depends(get_session),
) -> FindRelatedStudyNotes:
    return FindRelatedStudyNotes(
        study_note_repository=StudyNoteRepository(session),
        question_repository=QuestionRepository(session),
    )


def get_find_related_study_notes_to_note_dependency(
    session: AsyncSession = Depends(get_session),
) -> FindRelatedStudyNotesToNote:
    return FindRelatedStudyNotesToNote(
        study_note_repository=StudyNoteRepository(session),
    )


def get_find_related_questions_to_note_dependency(
    session: AsyncSession = Depends(get_session),
) -> FindRelatedQuestionsToNote:
    return FindRelatedQuestionsToNote(
        study_note_repository=StudyNoteRepository(session),
        question_repository=QuestionRepository(session),
    )


def get_study_note_question_list_dependency(
    session: AsyncSession = Depends(get_session),
) -> GetStudyNoteQuestionList:
    return GetStudyNoteQuestionList(
        study_note_repository=StudyNoteRepository(session),
        question_repository=QuestionRepository(session),
    )


def get_list_study_notes_dependency(
    session: AsyncSession = Depends(get_session),
) -> ListStudyNotes:
    return ListStudyNotes(repository=StudyNoteRepository(session))


def get_get_study_note_dependency(
    session: AsyncSession = Depends(get_session),
) -> GetStudyNote:
    return GetStudyNote(repository=StudyNoteRepository(session))


def get_update_study_note_dependency(
    session: AsyncSession = Depends(get_session),
) -> UpdateStudyNote:
    return UpdateStudyNote(repository=StudyNoteRepository(session))


def get_delete_study_note_dependency(
    session: AsyncSession = Depends(get_session),
) -> DeleteStudyNote:
    return DeleteStudyNote(repository=StudyNoteRepository(session))


def get_generate_embedding_dependency(
    session: AsyncSession = Depends(get_session),
) -> GenerateStudyNoteEmbedding:
    return GenerateStudyNoteEmbedding(
        repository=StudyNoteRepository(session),
        embeddings=get_embedding_model(),
    )
