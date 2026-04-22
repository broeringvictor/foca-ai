from uuid import UUID

from app.application.dto.study_note.list_dto import ListStudyNotesResponse, StudyNoteListItem
from app.domain.repositories.study_note_repository import IStudyNoteRepository


class ListStudyNotes:
    def __init__(self, repository: IStudyNoteRepository) -> None:
        self._repository = repository

    async def execute(self, user_id: UUID) -> ListStudyNotesResponse:
        notes = await self._repository.find_all_by_user_id(user_id)
        items = [
            StudyNoteListItem(id=note.id, title=note.title, has_embedding=note.embedding is not None)
            for note in notes
        ]
        return ListStudyNotesResponse(items=items)
