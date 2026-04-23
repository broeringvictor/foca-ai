from uuid import UUID
from app.api.errors.exceptions import NotFoundError
from app.application.dto.study.study_dto import SubmitAreaReviewDTO, SubmitAreaReviewResponse
from app.domain.repositories.study_repository import IStudyRepository
from app.domain.repositories.question_repository import IQuestionRepository
from app.domain.repositories.study_question_repository import IStudyQuestionRepository
from app.domain.entities.study import Study
from app.domain.entities.study_question import StudyQuestion
from app.domain.enums.answer_quality import AnswerQuality

class SubmitAreaReview:
    def __init__(
        self, 
        study_repository: IStudyRepository,
        question_repository: IQuestionRepository,
        study_question_repository: IStudyQuestionRepository
    ) -> None:
        self._study_repository = study_repository
        self._question_repository = question_repository
        self._study_question_repository = study_question_repository

    async def execute(self, user_id: UUID, dto: SubmitAreaReviewDTO) -> SubmitAreaReviewResponse:
        # 1. Buscar a questão para saber a área e o gabarito
        question = await self._question_repository.find_by_id(dto.question_id)
        if not question:
            raise NotFoundError("question not found", field="question_id", source="body")

        # 2. Verificar se a resposta está correta
        is_correct = question.correct == dto.response
        
        # 3. Determinar a qualidade efetiva: se errou, forçamos AGAIN (0)
        effective_quality = dto.quality if is_correct else AnswerQuality.AGAIN

        # 4. Atualizar o progresso da Área
        study = await self._study_repository.find_by_user_and_area(user_id, question.area)
        
        if not study:
            study = Study.create(user_id, question.area)
            study.submit_review(effective_quality)
            await self._study_repository.save(study)
        else:
            study.submit_review(effective_quality)
            await self._study_repository.update(study)

        # 5. Atualizar o progresso da Questão individual
        study_q = await self._study_question_repository.find_by_user_and_question(user_id, question.id)
        
        if not study_q:
            study_q = StudyQuestion.create(user_id, question.id)
            study_q.submit_review(effective_quality)
            await self._study_question_repository.save(study_q)
        else:
            study_q.submit_review(effective_quality)
            await self._study_question_repository.update(study_q)
            
        return SubmitAreaReviewResponse(
            area=study.area,
            is_correct=is_correct,
            correct_alternative=question.correct,
            new_progress=study.review_progress
        )
