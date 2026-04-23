from datetime import UTC, datetime
from uuid import UUID

from loguru import logger

from app.api.errors.exceptions import BadRequestError, NotFoundError
from app.application.dto.study_note.related_dto import (
    FindRelatedStudyNotesResponse,
    RelatedStudyNoteItem,
)
from app.domain.repositories.question_repository import IQuestionRepository
from app.domain.repositories.study_note_repository import IStudyNoteRepository

# TODO: Refine this threshold. 0.4 is a temporary value to increase matches.
_RELEVANCE_THRESHOLD = 0.4


class FindRelatedStudyNotes:
    def __init__(
        self,
        study_note_repository: IStudyNoteRepository,
        question_repository: IQuestionRepository,
    ) -> None:
        self._study_note_repo = study_note_repository
        self._question_repo = question_repository

    async def execute(
        self,
        user_id: UUID,
        question_id: UUID,
        limit: int,
    ) -> FindRelatedStudyNotesResponse:
        question = await self._question_repo.find_by_id(question_id)
        if question is None:
            raise NotFoundError("Questão não encontrada", field="question_id")

        if not question.embedding:
            logger.warning(
                "study_note.find_related: question_not_indexed question_id={}",
                question_id,
            )
            raise BadRequestError(
                "Questão ainda não foi indexada (sem embedding).",
                field="question_id",
            )

        matches = await self._study_note_repo.find_by_embedding_similarity(
            user_id=user_id,
            query_vector=question.embedding,
            limit=limit,
        )

        items = []
        for note, score in matches:
            clamped = max(0.0, min(1.0, score))
            items.append(
                RelatedStudyNoteItem(
                    id=note.id,
                    title=note.title,
                    description=note.description,
                    tags=list(note.tags),
                    score=clamped,
                )
            )
            if clamped >= _RELEVANCE_THRESHOLD:
                note.add_question(question_id)
                note.updated_at = datetime.now(UTC)
                await self._study_note_repo.update(note)

        return FindRelatedStudyNotesResponse(
            question_id=question.id,
            items=items,
        )
