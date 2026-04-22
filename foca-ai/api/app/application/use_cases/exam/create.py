from loguru import logger

from app.application.dto.exam.create_dto import CreateExamDTO, CreateExamResponse
from app.domain.entities.exam import Exam
from app.domain.repositories.exam_repository import IExamRepository


class CreateExam:
    def __init__(self, repository: IExamRepository) -> None:
        self._repo = repository

    async def execute(self, input_data: CreateExamDTO) -> CreateExamResponse:
        exam = Exam.create(
            name=input_data.name,
            edition=input_data.edition,
            year=input_data.year,
            board=input_data.board,
            first_phase_date=input_data.first_phase_date,
            second_phase_date=input_data.second_phase_date,
        )

        try:
            await self._repo.save(exam)
        except Exception as e:
            logger.exception(f"Erro ao salvar exame: {e}")
            raise

        return CreateExamResponse(
            exam_id=exam.id,
            name=exam.name,
            edition=exam.edition,
            created_at=exam.created_at,
        )
