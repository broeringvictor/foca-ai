from pathlib import Path

from fastapi import Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependecies.embeddings import get_embedding_service_dependency
from app.api.errors.exceptions import BadRequestError
from app.application.use_cases.question.add_answer_key import AddAnswerKeyToExam
from app.application.use_cases.question.categorize import CategorizeQuestions
from app.application.use_cases.question.check_answer import CheckAnswer
from app.application.use_cases.question.create import CreateQuestion
from app.application.use_cases.question.delete import DeleteQuestion
from app.application.use_cases.question.get import GetQuestion, ListQuestionsByExam
from app.application.use_cases.question.review_from_pdf import ReviewQuestionsFromPDF
from app.application.use_cases.question.update import UpdateQuestion
from app.domain.services.embedding_service import IEmbeddingService
from app.domain.services.oab_extractor_service import IOABExtractorService
from app.domain.services.question_categorization_service import IQuestionCategorizationService
from app.infrastructure.llm import get_llm_model
from app.infrastructure.repositories.exam_repository import ExamRepository
from app.infrastructure.repositories.question_repository import QuestionRepository
from app.infrastructure.services.extract_oab_answer_key import ExtractOABAnswerKeyService
from app.infrastructure.services.extract_oab_question import ExtractOABQuestionService
from app.infrastructure.services.question_categorization_service import QuestionCategorizationService
from app.infrastructure.session import get_session

ALLOWED_PDF_EXTENSIONS = {".pdf"}
ALLOWED_PDF_MIME_TYPES = {"application/pdf", "application/octet-stream", "", None}
MAX_PDF_BYTES = 100 * 1024 * 1024
PDF_SIGNATURE = b"%PDF-"
PDF_SIGNATURE_SCAN_BYTES = 1024


def _has_pdf_signature(content: bytes) -> bool:
    return PDF_SIGNATURE in content[:PDF_SIGNATURE_SCAN_BYTES]


async def get_pdf_bytes_for_review(
    pdf_file: UploadFile = File(...),
) -> bytes:
    filename = pdf_file.filename or ""
    if not filename or Path(filename).name != filename:
        raise BadRequestError("Nome do arquivo inválido", field="pdf_file", source="file")

    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_PDF_EXTENSIONS:
        raise BadRequestError("Arquivo deve ser .pdf", field="pdf_file", source="file")

    if pdf_file.content_type not in ALLOWED_PDF_MIME_TYPES:
        raise BadRequestError(
            "Content-Type do arquivo inválido para PDF",
            field="pdf_file",
            source="file",
        )

    if pdf_file.size is not None and pdf_file.size > MAX_PDF_BYTES:
        raise BadRequestError(
            "Arquivo PDF excede o tamanho máximo permitido",
            field="pdf_file",
            source="file",
        )

    content = await pdf_file.read()
    if not content:
        raise BadRequestError("Arquivo PDF vazio", field="pdf_file", source="file")

    if len(content) > MAX_PDF_BYTES:
        raise BadRequestError(
            "Arquivo PDF excede o tamanho máximo permitido",
            field="pdf_file",
            source="file",
        )

    if not _has_pdf_signature(content):
        raise BadRequestError(
            "Arquivo não parece ser um PDF válido",
            field="pdf_file",
            source="file",
        )

    return content


def get_create_question_dependency(
    session: AsyncSession = Depends(get_session),
    embedding_service: IEmbeddingService = Depends(get_embedding_service_dependency),
) -> CreateQuestion:
    return CreateQuestion(
        repository=QuestionRepository(session),
        embedding_service=embedding_service,
    )


def get_update_question_dependency(
    session: AsyncSession = Depends(get_session),
) -> UpdateQuestion:
    return UpdateQuestion(repository=QuestionRepository(session))


def get_delete_question_dependency(
    session: AsyncSession = Depends(get_session),
) -> DeleteQuestion:
    return DeleteQuestion(repository=QuestionRepository(session))


def get_question_dependency(
    session: AsyncSession = Depends(get_session),
) -> GetQuestion:
    return GetQuestion(repository=QuestionRepository(session))


def list_questions_by_exam_dependency(
    session: AsyncSession = Depends(get_session),
) -> ListQuestionsByExam:
    return ListQuestionsByExam(repository=QuestionRepository(session))


def get_check_answer_dependency(
    session: AsyncSession = Depends(get_session),
) -> CheckAnswer:
    return CheckAnswer(repository=QuestionRepository(session))


def get_question_categorization_service_dependency() -> IQuestionCategorizationService:
    # Composition root: LLM is created here and injected into the infrastructure service.
    llm = get_llm_model()
    return QuestionCategorizationService(llm=llm)


def get_oab_extractor_service_dependency() -> IOABExtractorService:
    return ExtractOABQuestionService()


def get_review_questions_from_pdf_dependency(
    session: AsyncSession = Depends(get_session),
) -> ReviewQuestionsFromPDF:
    return ReviewQuestionsFromPDF(
        extractor=get_oab_extractor_service_dependency(),
        categorizer=get_question_categorization_service_dependency(),
        exam_repository=ExamRepository(session),
        question_repository=QuestionRepository(session),
        session=session,
    )


def get_add_answer_key_to_exam_dependency(
    session: AsyncSession = Depends(get_session),
    embedding_service: IEmbeddingService = Depends(get_embedding_service_dependency),
) -> AddAnswerKeyToExam:
    return AddAnswerKeyToExam(
        exam_repository=ExamRepository(session),
        question_repository=QuestionRepository(session),
        answer_key_service=ExtractOABAnswerKeyService(),
        embedding_service=embedding_service,
        session=session,
    )


def get_categorize_questions_dependency() -> CategorizeQuestions:
    return CategorizeQuestions(
        service=get_question_categorization_service_dependency(),
    )
