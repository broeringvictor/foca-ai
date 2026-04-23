from uuid import UUID
from app.api.errors.exceptions import NotFoundError
from app.application.dto.study_note.review_dto import SubmitReviewDTO, SubmitReviewResponse
from app.domain.repositories.study_note_repository import IStudyNoteRepository


class SubmitReview:
    def __init__(self, repository: IStudyNoteRepository) -> None:
        self._repository = repository

    async def execute(self, study_note_id: UUID, user_id: UUID, dto: SubmitReviewDTO) -> SubmitReviewResponse:
        note = await self._repository.find_by_id(study_note_id)
        if note is None or note.user_id != user_id:
            raise NotFoundError(
                "study note not found",
                field="study_note_id",
                source="path",
            )
        
        note.update_review(dto.quality)
        await self._repository.update(note)
        
        return SubmitReviewResponse(
            study_note_id=note.id,
            new_progress=note.review_progress
        )
