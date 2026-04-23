from uuid import UUID
from app.api.errors.exceptions import BadRequestError
from app.application.dto.study.study_dto import ListStudyProgressResponse, StudyAreaProgressDTO, QuestionWithProgressDTO
from app.domain.repositories.study_repository import IStudyRepository
from app.domain.repositories.question_repository import IQuestionRepository
from app.domain.repositories.study_question_repository import IStudyQuestionRepository
from app.domain.enums.law_area import LawArea

class ListUserStudyProgress:
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
        studies = await self._study_repository.find_all_by_user_id(user_id)
        study_map = {s.area: s.review_progress for s in studies}
        
        # Buscar todo o progresso de questões do usuário de uma vez para eficiência
        question_studies = await self._study_question_repository.find_all_by_user_id(user_id)
        question_progress_map = {qs.question_id: qs.review_progress for qs in question_studies}

        items = []
        has_any_embedding = False
        for area in LawArea:
            # Buscar algumas questões para esta área
            questions = await self._question_repository.find_by_area(area, limit=5)
            
            dto_questions = []
            for q in questions:
                if q.embedding is not None:
                    has_any_embedding = True
                
                dto_questions.append(
                    QuestionWithProgressDTO(
                        id=q.id,
                        statement=q.statement,
                        alternative_a=q.alternative_a,
                        alternative_b=q.alternative_b,
                        alternative_c=q.alternative_c,
                        alternative_d=q.alternative_d,
                        has_embedding=q.embedding is not None,
                        progress=question_progress_map.get(q.id)
                    )
                )

            items.append(
                StudyAreaProgressDTO(
                    area=area,
                    progress=study_map.get(area),
                    questions=dto_questions
                )
            )
            
        if not has_any_embedding:
             raise BadRequestError("Não há questões com embeddings processados. Gere os embeddings das questões primeiro.")

        return ListStudyProgressResponse(items=items)
