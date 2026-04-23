from uuid import UUID
from app.application.dto.study.study_dto import ListStudyProgressResponse, StudyAreaProgressDTO
from app.domain.repositories.study_repository import IStudyRepository

class ListDueLawAreas:
    def __init__(self, repository: IStudyRepository) -> None:
        self._repository = repository

    async def execute(self, user_id: UUID) -> ListStudyProgressResponse:
        due_studies = await self._repository.find_due_by_user_id(user_id)
        
        return ListStudyProgressResponse(
            items=[
                StudyAreaProgressDTO(
                    area=study.area,
                    progress=study.review_progress
                )
                for study in due_studies
            ]
        )
