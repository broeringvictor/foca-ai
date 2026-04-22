from loguru import logger

from app.api.errors.exceptions import BadRequestError
from app.application.dto.question.extract_from_pdf_dto import ExtractFromPDFResponse
from app.domain.services.oab_extractor_service import IOABExtractorService
from app.domain.value_objects.raw_exam import ExtractionOptions


class ExtractQuestionsFromPDF:
    def __init__(self, service: IOABExtractorService) -> None:
        self._service = service

    async def execute(
        self, pdf_bytes: bytes, options: ExtractionOptions
    ) -> ExtractFromPDFResponse:
        try:
            exam = self._service.extract(pdf_bytes, options)
        except ValueError as e:
            logger.warning(f"Extração falhou: {e}")
            raise BadRequestError(
                str(e), field="pdf_file", source="file"
            ) from e

        return ExtractFromPDFResponse(
            exam=exam, questions_count=len(exam.questions)
        )
