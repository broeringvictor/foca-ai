from app.application.dto.study_note.create_dto import (
    CreateStudyNoteDTO,
    CreateStudyNoteResponse,
)
from app.domain.entities.study_note import StudyNote
from app.domain.repositories.study_note_repository import IStudyNoteRepository
from app.domain.services.embedding_service import IEmbeddingService


class CreateStudyNote:
    def __init__(
        self,
        repository: IStudyNoteRepository,
        embedding_service: IEmbeddingService,
    ) -> None:
        self._repo = repository
        self._embedding_service = embedding_service

    async def execute(self, input_data: CreateStudyNoteDTO) -> CreateStudyNoteResponse:
        embedding: list[float] | None = None
        if input_data.content and input_data.content.strip():
            embedding = await self._embedding_service.embed_query(input_data.content)

        study_note = StudyNote.create(
            user_id=input_data.user_id,
            title=input_data.title,
            description=input_data.description,
            content=input_data.content,
            tags=input_data.tags,
            embedding=embedding,
        )

        await self._repo.save(study_note)

        return CreateStudyNoteResponse(
            study_note_id=study_note.id,
            title=study_note.title,
            created_at=study_note.created_at,
        )
