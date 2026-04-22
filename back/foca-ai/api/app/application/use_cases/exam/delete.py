from uuid import UUID

from loguru import logger

from app.api.errors.exceptions import NotFoundError
from app.application.dto.exam.delete_dto import DeleteExamResponse
from app.domain.repositories.exam_repository import IExamRepository
from app.domain.repositories.question_repository import IQuestionRepository


class DeleteExam:
    def __init__(
        self,
        repository: IExamRepository,
        question_repository: IQuestionRepository,
    ) -> None:
        self._repo = repository
        self._question_repo = question_repository

    async def execute(self, exam_id: UUID) -> DeleteExamResponse:
        logger.info("exam.delete: start exam_id={}", exam_id)
        exam = await self._repo.find_by_id(exam_id)
        if exam is None:
            logger.warning("exam.delete: exam_not_found exam_id={}", exam_id)
            raise NotFoundError(
                "Exame não encontrado", field="exam_id", source="path"
            )

        try:
            deleted_questions = await self._question_repo.delete_all_by_exam_id(exam_id)
            logger.info(
                "exam.delete: related_questions_deleted exam_id={} count={}",
                exam_id,
                deleted_questions,
            )
            await self._repo.delete(exam_id)
            logger.info("exam.delete: exam_deleted exam_id={}", exam_id)
        except Exception as e:
            logger.exception(f"Erro ao deletar exame e questões relacionadas: {e}")
            raise

        return DeleteExamResponse(exam_id=exam_id)
