from datetime import UTC, datetime
from uuid import UUID

from loguru import logger

from app.api.errors.exceptions import NotFoundError
from app.application.dto.study_note.update_dto import UpdateStudyNoteDTO, UpdateStudyNoteResponse
from app.domain.repositories.study_note_repository import IStudyNoteRepository


class UpdateStudyNote:
    def __init__(self, repository: IStudyNoteRepository) -> None:
        self._repo = repository

    async def execute(self, study_note_id: UUID, dto: UpdateStudyNoteDTO) -> UpdateStudyNoteResponse:
        note = await self._repo.find_by_id(study_note_id)
        if note is None:
            raise NotFoundError("study note not found", field="study_note_id", source="path")

        updates = {k: v for k, v in dto.model_dump().items() if v is not None}
        updates["updated_at"] = datetime.now(UTC)
        updated = note.model_copy(update=updates)

        logger.info("study_note.update: id={}", study_note_id)
        await self._repo.update(updated)

        return UpdateStudyNoteResponse(id=updated.id, title=updated.title, updated_at=updated.updated_at)
