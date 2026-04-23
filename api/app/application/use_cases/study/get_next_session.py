from uuid import UUID
from app.application.dto.study.study_dto import ListStudyProgressResponse, StudyAreaProgressDTO, QuestionWithProgressDTO
from app.domain.repositories.study_repository import IStudyRepository
from app.domain.repositories.question_repository import IQuestionRepository
from app.domain.repositories.study_question_repository import IStudyQuestionRepository

class GetNextStudySession:
    def __init__(
        self, 
        study_repository: IStudyRepository,
        question_repository: IQuestionRepository,
        study_question_repository: IStudyQuestionRepository
    ) -> None:
        self._study_repository = study_repository
        self._question_repository = question_repository
        self._study_question_repository = study_question_repository

    async def execute(self, user_id: UUID, limit: int = 10) -> ListStudyProgressResponse:
        # Funil de Prioridade:
        # 1. Retenção: Questões SM-2 vencidas (até 40% do limite)
        # 2. Reforço: Questões com muitos erros (até 30% do limite)
        # 3. Descoberta: Questões novas com nota alta (restante)

        questions_map = {} # question_id -> (Question, Sm2Progress | None)
        
        # --- CAMADA 1: RETENÇÃO (SM-2 Vencidas) ---
        retention_limit = max(1, int(limit * 0.4))
        due_questions_progress = await self._study_question_repository.find_due_by_user_id(user_id, limit=retention_limit)
        for dq in due_questions_progress:
            q = await self._question_repository.find_by_id(dq.question_id)
            if q:
                questions_map[q.id] = (q, dq.review_progress)

        # --- CAMADA 2: REFORÇO (Erros) ---
        if len(questions_map) < limit:
            reinforcement_limit = max(1, int(limit * 0.3))
            high_error_progress = await self._study_question_repository.find_high_error_by_user_id(user_id, limit=reinforcement_limit)
            for he in high_error_progress:
                if len(questions_map) >= (limit - 1): # Deixa espaço para pelo menos uma nova
                    break
                if he.question_id not in questions_map:
                    q = await self._question_repository.find_by_id(he.question_id)
                    if q:
                        questions_map[q.id] = (q, he.review_progress)

        # --- CAMADA 3: DESCOBERTA (Nota Alta / Discovery) ---
        if len(questions_map) < limit:
            remaining = limit - len(questions_map)
            # Busca questões que o usuário nunca respondeu, ordenadas por priority_score
            discovery_questions = await self._question_repository.find_top_rated_not_answered(user_id, limit=remaining)
            for q in discovery_questions:
                questions_map[q.id] = (q, None)

        # 4. Organizar a resposta agrupada por área
        area_groups = {}
        for q, progress in questions_map.values():
            if q.area not in area_groups:
                area_study = await self._study_repository.find_by_user_and_area(user_id, q.area)
                area_groups[q.area] = StudyAreaProgressDTO(
                    area=q.area,
                    progress=area_study.review_progress if area_study else None,
                    questions=[]
                )
            
            area_groups[q.area].questions.append(
                QuestionWithProgressDTO(
                    id=q.id,
                    statement=q.statement,
                    alternative_a=q.alternative_a,
                    alternative_b=q.alternative_b,
                    alternative_c=q.alternative_c,
                    alternative_d=q.alternative_d,
                    has_embedding=q.embedding is not None,
                    progress=progress
                )
            )

        return ListStudyProgressResponse(items=list(area_groups.values()))
