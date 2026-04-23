from loguru import logger
from app.api.errors.exceptions import BadRequestError, NotFoundError
from app.application.dto.question.categorize_dto import (
    RecategorizeExistingDTO,
    RecategorizeExistingResponse,
)
from app.domain.repositories.question_repository import IQuestionRepository
from app.domain.services.question_categorization_service import (
    IQuestionCategorizationService,
)


class RecategorizeExisting:
    def __init__(
        self,
        repository: IQuestionRepository,
        service: IQuestionCategorizationService,
    ) -> None:
        self._repository = repository
        self._service = service

    async def execute(
        self, input_data: RecategorizeExistingDTO
    ) -> RecategorizeExistingResponse:
        if not input_data.exam_id and not input_data.question_id:
            raise BadRequestError("Deve ser fornecido um exam_id ou um question_id.")

        questions = []
        if input_data.question_id:
            q = await self._repository.find_by_id(input_data.question_id)
            if not q:
                raise NotFoundError("Questão não encontrada", field="question_id")
            questions = [q]
        else:
            questions = await self._repository.find_all_by_exam_id(input_data.exam_id)
            if not questions:
                raise NotFoundError("Nenhuma questão encontrada para este exame", field="exam_id")

        logger.info(
            "question.recategorize_existing: start count={} format_statement={} categorize_tags={} categorize_law_area={}",
            len(questions),
            input_data.format_statement,
            input_data.categorize_tags,
            input_data.categorize_law_area,
        )

        updated_questions = self._service.recategorize(
            questions=questions,
            format_statement=input_data.format_statement,
            categorize_tags=input_data.categorize_tags,
            categorize_law_area=input_data.categorize_law_area,
        )

        for q in updated_questions:
            await self._repository.update(q)

        logger.info(
            "question.recategorize_existing: done count={}",
            len(updated_questions),
        )

        return RecategorizeExistingResponse(
            updated_count=len(updated_questions),
            questions=updated_questions,
        )
