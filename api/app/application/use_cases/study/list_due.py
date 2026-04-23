from uuid import UUID
from app.application.dto.study.study_dto import ListStudyProgressResponse, StudyAreaProgressDTO, QuestionWithProgressDTO
from app.domain.repositories.study_repository import IStudyRepository
from app.domain.repositories.question_repository import IQuestionRepository
from app.domain.repositories.study_question_repository import IStudyQuestionRepository

class ListDueLawAreas:
    def __init__(
        self, 
        study_repository: IStudyRepository,
        question_repository: IQuestionRepository,
        study_question_repository: IStudyQuestionRepository
    ) -> None:
        self._study_repository = study_repository
        self._question_repository = question_repository
        self._study_question_repository = study_question_repository

    async def execute(self, user_id: UUID) -> ListStudyProgressResponse:
        due_studies = await self._study_repository.find_due_by_user_id(user_id)
        if not due_studies:
            return ListStudyProgressResponse(items=[])

        # Buscar todo o progresso de questões do usuário de uma vez para eficiência
        question_studies = await self._study_question_repository.find_all_by_user_id(user_id)
        question_progress_map = {qs.question_id: qs.review_progress for qs in question_studies}
        
        items = []
        for study in due_studies:
            # Buscar algumas questões para esta área que está vencida
            questions = await self._question_repository.find_by_area(study.area, limit=10)
            
            items.append(
                StudyAreaProgressDTO(
                    area=study.area,
                    progress=study.review_progress,
                    questions=[
                        QuestionWithProgressDTO(
                            id=q.id,
                            statement=q.statement,
                            alternative_a=q.alternative_a,
                            alternative_b=q.alternative_b,
                            alternative_c=q.alternative_c,
                            alternative_d=q.alternative_d,
                            progress=question_progress_map.get(q.id)
                        )
                        for q in questions
                    ]
                )
            )
        
        return ListStudyProgressResponse(items=items)
