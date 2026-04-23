from uuid import UUID
from app.application.dto.study.study_dto import ListStudyProgressResponse, StudyAreaProgressDTO
from app.domain.repositories.study_repository import IStudyRepository
from app.domain.enums.law_area import LawArea

class ListUserStudyProgress:
    def __init__(self, repository: IStudyRepository) -> None:
        self._repository = repository

    async def execute(self, user_id: UUID) -> ListStudyProgressResponse:
        studies = await self._repository.find_all_by_user_id(user_id)
        study_map = {s.area: s.review_progress for s in studies}
        
        items = []
        for area in LawArea:
            items.append(
                StudyAreaProgressDTO(
                    area=area,
                    progress=study_map.get(area)
                )
            )
            
        return ListStudyProgressResponse(items=items)
