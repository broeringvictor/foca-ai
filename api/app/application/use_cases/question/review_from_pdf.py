from loguru import logger

from app.api.errors.exceptions import BadRequestError
from app.application.dto.question.review_from_pdf_dto import (
    ReviewQuestionsFromPDFResponse,
)
from app.application.use_cases.question.area_validation import build_area_validation
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
        logger.info(
            "question.review_from_pdf: start pdf_bytes={} header={} footer={} split={}",
            len(pdf_bytes),
            options.header_height,
            options.footer_height,
            options.column_split,
        )

        try:
            exam = self._extractor.extract(pdf_bytes=pdf_bytes, options=options)
        except ValueError as exc:
            logger.warning(f"question.review_from_pdf: extraction_failed reason={exc}")
            raise BadRequestError(
                str(exc), field="pdf_file", source="file"
            ) from exc

        logger.info(
            "question.review_from_pdf: extracted edition={} exam_type={} color={} raw_questions={}",
            exam.edition,
            exam.exam_type,
            exam.color,
            len(exam.questions),
        )

        questions = self._categorizer.classify(exam)
        area_validation = build_area_validation(questions)

        logger.info(
            "question.review_from_pdf: categorized questions={} within_expected_distribution={} distorted_areas={}",
            len(questions),
            area_validation.is_within_expected_distribution,
            area_validation.distorted_areas,
        )

        return ReviewQuestionsFromPDFResponse(
            exam=exam,
            questions=questions,
            extracted_questions_count=len(exam.questions),
            categorized_questions_count=len(questions),
            area_validation=area_validation,
        )
