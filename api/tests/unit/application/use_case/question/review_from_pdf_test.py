import pytest
from unittest.mock import MagicMock

from app.api.errors.exceptions import BadRequestError
from app.application.use_cases.question.review_from_pdf import ReviewQuestionsFromPDF
from app.domain.value_objects.raw_exam import ExtractionOptions, RawExam


@pytest.fixture
def options() -> ExtractionOptions:
    return ExtractionOptions(header_height=65, footer_height=60, column_split=298)


@pytest.fixture
def exam() -> RawExam:
    return RawExam(
        edition=45,
        name="45 EXAME DE ORDEM UNIFICADO",
        exam_type=1,
        color="BRANCA",
        questions=[],
    )


@pytest.fixture
def extractor(exam: RawExam) -> MagicMock:
    mock = MagicMock()
    mock.extract.return_value = exam
    return mock


@pytest.fixture
def categorizer() -> MagicMock:
    mock = MagicMock()
    mock.classify.return_value = []
    return mock


@pytest.fixture
def use_case(extractor: MagicMock, categorizer: MagicMock) -> ReviewQuestionsFromPDF:
    return ReviewQuestionsFromPDF(extractor=extractor, categorizer=categorizer)


class TestReviewQuestionsFromPDF:
    @pytest.mark.asyncio
    async def test_execute_returns_response(
        self,
        use_case: ReviewQuestionsFromPDF,
        extractor: MagicMock,
        categorizer: MagicMock,
        options: ExtractionOptions,
    ):
        result = await use_case.execute(pdf_bytes=b"pdf", options=options)

        extractor.extract.assert_called_once_with(pdf_bytes=b"pdf", options=options)
        categorizer.classify.assert_called_once()
        assert result.extracted_questions_count == 0
        assert result.categorized_questions_count == 0
        assert result.area_validation.total_questions == 0
        assert result.area_validation.counts_by_area

    @pytest.mark.asyncio
    async def test_execute_raises_bad_request_when_extractor_fails(
        self,
        use_case: ReviewQuestionsFromPDF,
        extractor: MagicMock,
        options: ExtractionOptions,
    ):
        extractor.extract.side_effect = ValueError("PDF invalido")

        with pytest.raises(BadRequestError, match="PDF invalido"):
            await use_case.execute(pdf_bytes=b"broken", options=options)
