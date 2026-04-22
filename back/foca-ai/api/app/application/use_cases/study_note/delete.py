from uuid import UUID

from loguru import logger

from app.api.errors.exceptions import NotFoundError
from app.application.dto.study_note.delete_dto import DeleteStudyNoteResponse
from app.domain.repositories.study_note_repository import IStudyNoteRepository


class DeleteStudyNote:
    def __init__(self, repository: IStudyNoteRepository) -> None:
        self._repo = repository

    async def execute(self, study_note_id: UUID) -> DeleteStudyNoteResponse:
        note = await self._repo.find_by_id(study_note_id)
        if note is None:
            raise NotFoundError("study note not found", field="study_note_id", source="path")

        logger.info("study_note.delete: id={}", study_note_id)
        await self._repo.delete(study_note_id)

        return DeleteStudyNoteResponse(study_note_id=study_note_id)
