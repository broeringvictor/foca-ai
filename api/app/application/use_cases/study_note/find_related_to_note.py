from uuid import UUID
from app.api.errors.exceptions import NotFoundError, BadRequestError
from app.application.dto.study_note.related_dto import (
    FindRelatedStudyNotesToNoteResponse,
    RelatedStudyNoteItem,
)
from app.domain.repositories.study_note_repository import IStudyNoteRepository

class FindRelatedStudyNotesToNote:
    def __init__(
        self,
        study_note_repository: IStudyNoteRepository,
    ) -> None:
        self._repo = study_note_repository

    async def execute(
        self, user_id: UUID, study_note_id: UUID, limit: int = 5
    ) -> FindRelatedStudyNotesToNoteResponse:
        # 1. Buscar a nota de origem
        source_note = await self._repo.find_by_id(study_note_id)
        if not source_note:
            raise NotFoundError("Nota de estudo não encontrada")
        
        # 2. Validar se tem embedding
        if not source_note.embedding:
            raise BadRequestError("Nota de estudo sem embedding. Gere os embeddings primeiro.")

        # 3. Buscar notas semelhantes do mesmo usuário
        # Limit + 1 para excluir a própria nota caso ela venha no resultado
        similar_results = await self._repo.find_by_embedding_similarity(
            user_id=user_id,
            query_vector=source_note.embedding,
            limit=limit + 1,
        )

        items = []
        for note, score in similar_results:
            if note.id == study_note_id:
                continue
            
            items.append(
                RelatedStudyNoteItem(
                    id=note.id,
                    title=note.title,
                    description=note.description,
                    tags=note.tags,
                    score=score,
                )
            )

        return FindRelatedStudyNotesToNoteResponse(
            study_note_id=study_note_id,
            items=items[:limit],
        )
