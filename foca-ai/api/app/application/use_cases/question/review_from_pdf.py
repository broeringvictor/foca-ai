from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors.exceptions import BadRequestError
from app.application.dto.question.review_from_pdf_dto import (
    ReviewQuestionsFromPDFResponse,
)
from app.application.use_cases.question.area_validation import build_area_validation
from app.domain.entities.exam import Exam
from app.domain.repositories.exam_repository import IExamRepository
from app.domain.repositories.question_repository import IQuestionRepository
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
        exam_repository: IExamRepository,
        question_repository: IQuestionRepository,
        session: AsyncSession,
    ) -> None:
        self._extractor = extractor
        self._categorizer = categorizer
        self._exam_repository = exam_repository
        self._question_repository = question_repository
        self._session = session

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
            raw_exam = self._extractor.extract(pdf_bytes=pdf_bytes, options=options)
        except ValueError as exc:
            logger.warning(f"question.review_from_pdf: extraction_failed reason={exc}")
            raise BadRequestError(
                str(exc), field="pdf_file", source="file"
            ) from exc

        logger.info(
            "question.review_from_pdf: extracted edition={} exam_type={} color={} raw_questions={}",
            raw_exam.edition,
            raw_exam.exam_type,
            raw_exam.color,
            len(raw_exam.questions),
        )

        # 1. Persist the Exam entity
        exam = Exam.create(
            name=raw_exam.name,
            edition=raw_exam.edition,
            year=2024,  # Default or extract from name/metadata
            board="FGV",
            exam_type=raw_exam.exam_type,
            color=raw_exam.color,
        )
        await self._exam_repository.save(exam)

        # 2. Categorize and Persist Questions
        questions = self._categorizer.classify(raw_exam, exam_id=exam.id)

        for question in questions:
            await self._question_repository.save(question)

        await self._session.commit()

        area_validation = build_area_validation(questions)

        logger.info(
            "question.review_from_pdf: categorized questions={} within_expected_distribution={} distorted_areas={} exam_id={}",
            len(questions),
            area_validation.is_within_expected_distribution,
            area_validation.distorted_areas,
            exam.id,
        )

        return ReviewQuestionsFromPDFResponse(
            extracted_questions_count=len(raw_exam.questions),
            categorized_questions_count=len(questions),
            area_validation=area_validation,
        )
