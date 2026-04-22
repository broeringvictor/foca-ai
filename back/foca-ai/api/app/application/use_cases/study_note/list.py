from uuid import UUID

from app.application.dto.study_note.list_dto import ListStudyNotesResponse, StudyNoteListItem
from app.domain.repositories.study_note_repository import IStudyNoteRepository


class ListStudyNotes:
    def __init__(self, repository: IStudyNoteRepository) -> None:
        self._repository = repository

    async def execute(self, user_id: UUID) -> ListStudyNotesResponse:
        summaries = await self._repository.find_summaries_by_user_id(user_id)
        items = [
            StudyNoteListItem(id=note_id, title=title, has_embedding=has_embedding)
            for note_id, title, has_embedding in summaries
        ]
        return ListStudyNotesResponse(items=items)
