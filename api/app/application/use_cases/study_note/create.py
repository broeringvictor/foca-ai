from app.application.dto.study_note.create_dto import (
    CreateStudyNoteDTO,
    CreateStudyNoteResponse,
)
from app.domain.entities.study_note import StudyNote
from app.domain.repositories.study_note_repository import IStudyNoteRepository


class CreateStudyNote:
    def __init__(self, repository: IStudyNoteRepository) -> None:
        self._repo = repository

    async def execute(self, input_data: CreateStudyNoteDTO) -> CreateStudyNoteResponse:
        study_note = StudyNote.create(
            user_id=input_data.user_id,
            area=input_data.area,
            title=input_data.title,
            description=input_data.description,
            content=input_data.content,
            tags=input_data.tags,
        )

        await self._repo.save(study_note)

        return CreateStudyNoteResponse(
            study_note_id=study_note.id,
            title=study_note.title,
            created_at=study_note.created_at,
        )
