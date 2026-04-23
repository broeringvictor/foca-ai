from uuid import UUID
from app.application.dto.study.study_dto import ListStudyProgressResponse, StudyAreaProgressDTO
from app.application.dto.question.get_dto import QuestionListItem
from app.domain.repositories.study_repository import IStudyRepository
from app.domain.repositories.question_repository import IQuestionRepository
from app.domain.enums.law_area import LawArea

class ListUserStudyProgress:
    def __init__(
        self, 
        study_repository: IStudyRepository,
        question_repository: IQuestionRepository
    ) -> None:
        self._study_repository = study_repository
        self._question_repository = question_repository

    async def execute(self, user_id: UUID) -> ListStudyProgressResponse:
        studies = await self._study_repository.find_all_by_user_id(user_id)
        study_map = {s.area: s.review_progress for s in studies}
        
        items = []
        for area in LawArea:
            # Buscar algumas questões para esta área
            questions = await self._question_repository.find_by_area(area, limit=5)
            
            items.append(
                StudyAreaProgressDTO(
                    area=area,
                    progress=study_map.get(area),
                    questions=[
                        QuestionListItem(
                            id=q.id,
                            statement=q.statement,
                            alternative_a=q.alternative_a,
                            alternative_b=q.alternative_b,
                            alternative_c=q.alternative_c,
                            alternative_d=q.alternative_d,
                        )
                        for q in questions
                    ]
                )
            )
            
        return ListStudyProgressResponse(items=items)
