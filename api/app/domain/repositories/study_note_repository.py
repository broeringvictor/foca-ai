from typing import Protocol
from uuid import UUID

from app.domain.entities.study_note import StudyNote


class IStudyNoteRepository(Protocol):
    async def save(self, study_note: StudyNote) -> None: ...
    async def find_by_id(self, study_note_id: UUID) -> StudyNote | None: ...
    async def find_all_by_user_id(self, user_id: UUID) -> list[StudyNote]: ...
