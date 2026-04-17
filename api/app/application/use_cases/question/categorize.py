from app.application.dto.question.categorize_dto import (
    CategorizeQuestionsDTO,
    CategorizeQuestionsResponse,
)
from app.domain.services.question_categorization_service import (
    IQuestionCategorizationService,
)


class CategorizeQuestions:
    def __init__(self, service: IQuestionCategorizationService) -> None:
        self._service = service

    async def execute(
        self, input_data: CategorizeQuestionsDTO
    ) -> CategorizeQuestionsResponse:
        questions = self._service.classify(input_data.exam)
        return CategorizeQuestionsResponse(
            questions=questions,
            questions_count=len(questions),
        )

