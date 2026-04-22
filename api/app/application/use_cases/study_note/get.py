from uuid import UUID

from app.api.errors.exceptions import NotFoundError
from app.application.dto.study_note.get_dto import GetStudyNoteResponse
from app.domain.repositories.study_note_repository import IStudyNoteRepository


class GetStudyNote:
    def __init__(self, repository: IStudyNoteRepository) -> None:
        self._repository = repository

    async def execute(self, study_note_id: UUID, user_id: UUID) -> GetStudyNoteResponse:
        note = await self._repository.find_by_id(study_note_id)
        if note is None or note.user_id != user_id:
            raise NotFoundError(
                "study note not found",
                field="study_note_id",
                source="path",
            )
        return GetStudyNoteResponse(
            id=note.id,
            title=note.title,
            description=note.description,
            content=note.content,
            tags=list(note.tags),
            questions=[str(question_id) for question_id in note.questions],
            created_at=note.created_at,
            updated_at=note.updated_at,
        )
