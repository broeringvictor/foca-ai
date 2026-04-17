from loguru import logger

from app.api.errors.exceptions import BadRequestError
from app.application.dto.question.review_from_pdf_dto import (
    ReviewQuestionsFromPDFResponse,
)
from app.domain.services.oab_extractor_service import IOABExtractorService
from app.domain.services.question_categorization_service import (
    IQuestionCategorizationService,
)
from app.domain.value_objects.raw_exam import ExtractionOptions


class ReviewQuestionsFromPDF:
    def __init__(
        self,
        extractor: IOABExtractorService,
        categorizer: IQuestionCategorizationService,
    ) -> None:
        self._extractor = extractor
        self._categorizer = categorizer

    async def execute(
        self, pdf_bytes: bytes, options: ExtractionOptions
    ) -> ReviewQuestionsFromPDFResponse:
        try:
            exam = self._extractor.extract(pdf_bytes=pdf_bytes, options=options)
        except ValueError as exc:
            logger.warning(f"Extração falhou: {exc}")
            raise BadRequestError(
                str(exc), field="pdf_file", source="file"
            ) from exc

        questions = self._categorizer.classify(exam)
        return ReviewQuestionsFromPDFResponse(
            exam=exam,
            questions=questions,
            extracted_questions_count=len(exam.questions),
            categorized_questions_count=len(questions),
        )

