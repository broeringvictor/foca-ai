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
from app.domain.repositories.study_question_repository import IStudyQuestionRepository
from app.domain.entities.study_question import StudyQuestion

# TODO: Refine this threshold. 0.4 is a temporary value to increase matches.
_RELEVANCE_THRESHOLD = 0.4


class FindRelatedQuestionsToNote:
    def __init__(
        self,
        study_note_repository: IStudyNoteRepository,
        question_repository: IQuestionRepository,
        study_question_repository: IStudyQuestionRepository,
    ) -> None:
        self._study_note_repo = study_note_repository
        self._question_repo = question_repository
        self._study_question_repo = study_question_repository

    async def execute(
        self, study_note_id: UUID, limit: int = 5, exam_id: UUID | None = None
    ) -> FindRelatedQuestionsToNoteResponse:
        source_note = await self._study_note_repo.find_by_id(study_note_id)
        if not source_note:
            raise NotFoundError("Nota de estudo não encontrada")

        if not source_note.embedding:
            raise BadRequestError("Nota de estudo sem embedding. Gere os embeddings primeiro.")

        # Check if there are any questions with embeddings to search against
        similar_results = await self._question_repo.find_by_embedding_similarity(
            query_vector=source_note.embedding,
            limit=limit,
            exam_id=exam_id,
        )

        if not similar_results:
            error_msg = "Não há questões com embeddings processados"
            if exam_id:
                error_msg += " para este exame"
            error_msg += ". Gere os embeddings das questões primeiro."
            raise BadRequestError(error_msg)

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
                    # Assegura que existe um registro de estudo para esta questão para o usuário
                    existing_study = await self._study_question_repo.find_by_user_and_question(
                        source_note.user_id, q.id
                    )
                    if not existing_study:
                        new_study_q = StudyQuestion.create(source_note.user_id, q.id)
                        await self._study_question_repo.save(new_study_q)

        if changed:
            source_note.updated_at = datetime.now(UTC)
            await self._study_note_repo.update(source_note)

        return FindRelatedQuestionsToNoteResponse(
            study_note_id=study_note_id,
            items=items,
        )
