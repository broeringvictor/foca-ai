from loguru import logger

from app.application.dto.question.categorize_dto import (
    CategorizeQuestionsDTO,
    CategorizeQuestionsResponse,
)
from app.application.dto.question.get_dto import QuestionListItem
from app.application.use_cases.question.area_validation import build_area_validation
from app.domain.services.question_categorization_service import (
    IQuestionCategorizationService,
)


class CategorizeQuestions:
    def __init__(self, service: IQuestionCategorizationService) -> None:
        self._service = service

    async def execute(
        self, input_data: CategorizeQuestionsDTO
    ) -> CategorizeQuestionsResponse:
        logger.info(
            "question.categorize: start edition={} total_raw_questions={}",
            input_data.exam.edition,
            len(input_data.exam.questions),
        )

        questions = self._service.classify(input_data.exam)
        area_validation = build_area_validation(questions)

        logger.info(
            "question.categorize: done categorized_questions={} within_expected_distribution={}",
            len(questions),
            area_validation.is_within_expected_distribution,
        )

        return CategorizeQuestionsResponse(
            questions=[QuestionListItem.model_validate(q) for q in questions],
            questions_count=len(questions),
            area_validation=area_validation,
        )
