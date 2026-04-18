from uuid import UUID
from app.api.errors.exceptions import NotFoundError, BadRequestError
from app.application.dto.question.get_dto import GetQuestionResponse
from app.application.dto.question.related_dto import (
    FindRelatedQuestionsToNoteResponse,
    RelatedQuestionItem,
)
from app.domain.repositories.study_note_repository import IStudyNoteRepository
from app.domain.repositories.question_repository import IQuestionRepository

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
        # 1. Buscar a nota de origem
        source_note = await self._study_note_repo.find_by_id(study_note_id)
        if not source_note:
            raise NotFoundError("Nota de estudo não encontrada")
        
        # 2. Validar se tem embedding
        if not source_note.embedding:
            raise BadRequestError("Nota de estudo sem embedding. Gere os embeddings primeiro.")

        # 3. Buscar questões semelhantes (opcionalmente filtrando por exame)
        similar_results = await self._question_repo.find_by_embedding_similarity(
            query_vector=source_note.embedding,
            limit=limit,
            exam_id=exam_id,
        )

        items = [
            RelatedQuestionItem(
                question=GetQuestionResponse.model_validate(q),
                score=score,
            )
            for q, score in similar_results
        ]

        return FindRelatedQuestionsToNoteResponse(
            study_note_id=study_note_id,
            items=items,
        )
