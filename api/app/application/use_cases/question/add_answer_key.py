from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors.exceptions import NotFoundError
from app.application.dto.question.add_answer_key_dto import (
    AddAnswerKeyToExamDTO,
    AddAnswerKeyToExamResponse,
)
from app.domain.repositories.exam_repository import IExamRepository
from app.domain.repositories.question_repository import IQuestionRepository
from app.infrastructure.services.extract_oab_answer_key import ExtractOABAnswerKeyService


class AddAnswerKeyToExam:
    def __init__(
        self,
        exam_repository: IExamRepository,
        question_repository: IQuestionRepository,
        answer_key_service: ExtractOABAnswerKeyService,
        session: AsyncSession,
    ) -> None:
        self._exam_repository = exam_repository
        self._question_repository = question_repository
        self._answer_key_service = answer_key_service
        self._session = session

    async def execute(self, input_data: AddAnswerKeyToExamDTO) -> AddAnswerKeyToExamResponse:
        logger.info("question.add_answer_key: start exam_id={}", input_data.exam_id)

        # 1. Buscar o exame
        exam = await self._exam_repository.find_by_id(input_data.exam_id)
        if not exam:
            logger.error("question.add_answer_key: exam_not_found exam_id={}", input_data.exam_id)
            raise NotFoundError("Exame não encontrado")

        # 2. Extrair o gabarito do PDF baseado no tipo do exame
        try:
            answer_map = self._answer_key_service.extract(
                input_data.pdf_bytes, exam_type=exam.exam_type
            )
        except ValueError as exc:
            logger.error("question.add_answer_key: extraction_failed reason={}", exc)
            raise exc

        # 3. Buscar todas as questões do exame
        questions = await self._question_repository.find_all_by_exam_id(exam.id)

        updated_questions = [q for q in questions if q.number in answer_map]
        for question in updated_questions:
            question.correct = answer_map[question.number]
            await self._question_repository.update(question)

        updated_count = len(updated_questions)

        # 4. Commit explícito
        await self._session.commit()

        logger.info(
            "question.add_answer_key: done exam_id={} questions_updated={}",
            exam.id,
            updated_count,
        )

        return AddAnswerKeyToExamResponse(
            exam_id=exam.id,
            questions_updated=updated_count,
        )
