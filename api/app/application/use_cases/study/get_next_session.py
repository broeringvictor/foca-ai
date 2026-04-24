import random
from uuid import UUID
from app.api.errors.exceptions import BadRequestError
from app.application.dto.study.study_dto import ListStudyProgressResponse, StudyAreaProgressDTO, QuestionWithProgressDTO
from app.domain.repositories.study_repository import IStudyRepository
from app.domain.repositories.question_repository import IQuestionRepository
from app.domain.repositories.study_question_repository import IStudyQuestionRepository
from app.domain.repositories.study_note_repository import IStudyNoteRepository

class GetNextStudySession:
    def __init__(
        self, 
        study_repository: IStudyRepository,
        question_repository: IQuestionRepository,
        study_question_repository: IStudyQuestionRepository,
        study_note_repository: IStudyNoteRepository
    ) -> None:
        self._study_repository = study_repository
        self._question_repository = question_repository
        self._study_question_repository = study_question_repository
        self._study_note_repo = study_note_repository

    async def execute(self, user_id: UUID, limit: int = 10) -> ListStudyProgressResponse:
        # Funil de Prioridade Evoluído com Aleatoriedade:
        # 1. Retenção: Questões SM-2 vencidas
        # 2. Foco nas Notas: Questões vinculadas a StudyNotes
        # 3. Reforço: Questões com muitos erros
        # 4. Descoberta: 75% High Score / 25% Low Score

        questions_map = {} # question_id -> (Question, Sm2Progress | None)
        
        # --- CAMADA 1: RETENÇÃO (SM-2 Vencidas) ---
        due_questions_progress = await self._study_question_repository.find_due_by_user_id(user_id, limit=limit)
        for dq in due_questions_progress:
            q = await self._question_repository.find_by_id(dq.question_id)
            if q:
                questions_map[q.id] = (q, dq.review_progress)

        # --- CAMADA 2: PESO DAS NOTAS (Questões Vinculadas) ---
        if len(questions_map) < limit:
            user_notes = await self._study_note_repo.find_all_by_user_id(user_id)
            linked_question_ids = []
            for note in user_notes:
                linked_question_ids.extend(note.questions)
            
            linked_question_ids = list(dict.fromkeys(linked_question_ids))
            
            for q_id in linked_question_ids:
                if len(questions_map) >= limit:
                    break
                if q_id not in questions_map:
                    q = await self._question_repository.find_by_id(q_id)
                    if q:
                        prog = await self._study_question_repository.find_by_user_and_question(user_id, q_id)
                        questions_map[q.id] = (q, prog.review_progress if prog else None)

        # --- CAMADA 3: REFORÇO (Erros) ---
        if len(questions_map) < limit:
            remaining = limit - len(questions_map)
            high_error_progress = await self._study_question_repository.find_high_error_by_user_id(user_id, limit=remaining)
            for he in high_error_progress:
                if len(questions_map) >= limit:
                    break
                if he.question_id not in questions_map:
                    q = await self._question_repository.find_by_id(he.question_id)
                    if q:
                        questions_map[q.id] = (q, he.review_progress)

        # --- CAMADA 4: DESCOBERTA (75% High / 25% Low) ---
        if len(questions_map) < limit:
            remaining = limit - len(questions_map)
            
            high_limit = max(1, int(remaining * 0.75))
            discovery_high = await self._question_repository.find_top_rated_not_answered(user_id, limit=high_limit)
            for q in discovery_high:
                if len(questions_map) >= limit: break
                questions_map[q.id] = (q, None)
                
            if len(questions_map) < limit:
                rem_after_high = limit - len(questions_map)
                discovery_low = await self._question_repository.find_low_rated_not_answered(user_id, limit=rem_after_high)
                for q in discovery_low:
                    if len(questions_map) >= limit: break
                    questions_map[q.id] = (q, None)

        # Shuffle para não ficar previsível
        final_list = list(questions_map.values())
        random.shuffle(final_list)

        # 4. Organizar a resposta agrupada por área
        area_groups = {}
        has_any_embedding = False
        for q, progress in final_list:
            if q.embedding is not None:
                has_any_embedding = True
                
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

        if questions_map and not has_any_embedding:
             raise BadRequestError("Não há questões com embeddings processados. Gere os embeddings das questões primeiro.")

        return ListStudyProgressResponse(items=list(area_groups.values()))
