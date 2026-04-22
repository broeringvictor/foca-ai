from datetime import UTC, datetime
from uuid import UUID

from app.api.errors.exceptions import NotFoundError, BadRequestError
from app.application.dto.question.get_dto import GetQuestionResponse
from app.application.dto.question.related_dto import (
    FindRelatedQuestionsToNoteResponse,
    RelatedQuestionItem,
)
from app.domain.repositories.study_note_repository import IStudyNoteRepository
from app.domain.repositories.question_repository import IQuestionRepository

_RELEVANCE_THRESHOLD = 0.65


class FindRelatedQuestionsToNote:
    def __init__(
        self,
        study_note_repository: IStudyNoteRepository,
        question_repository: IQuestionRepository,
    ) -> None:
        self._study_note_repo = study_note_repository
        self._question_repo = question_repository

    async def execute(
        self, study_note_id: UUID, limit: int = 5, exam_id: UUID | None = None
    ) -> FindRelatedQuestionsToNoteResponse:
        source_note = await self._study_note_repo.find_by_id(study_note_id)
        if not source_note:
            raise NotFoundError("Nota de estudo não encontrada")

        if not source_note.embedding:
            raise BadRequestError("Nota de estudo sem embedding. Gere os embeddings primeiro.")

        similar_results = await self._question_repo.find_by_embedding_similarity(
            query_vector=source_note.embedding,
            limit=limit,
            exam_id=exam_id,
        )

        items = []
        changed = False
        for q, score in similar_results:
            items.append(
                RelatedQuestionItem(
                    question=GetQuestionResponse.model_validate(q),
                    score=score,
                )
            )
            if score >= _RELEVANCE_THRESHOLD:
                before = len(source_note.questions)
                source_note.add_question(q.id)
                if len(source_note.questions) != before:
                    changed = True

        if changed:
            source_note.updated_at = datetime.now(UTC)
            await self._study_note_repo.update(source_note)

        return FindRelatedQuestionsToNoteResponse(
            study_note_id=study_note_id,
            items=items,
        )
