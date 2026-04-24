from uuid import UUID

from fastapi import APIRouter, Depends, Form, Query, status

from app.api.dependecies.auth import get_current_user_id
from app.api.dependecies.question import (
    get_add_answer_key_to_exam_dependency,
    get_categorize_questions_dependency,
    get_check_answer_dependency,
    get_create_question_dependency,
    get_delete_question_dependency,
    get_generate_embeddings_for_exam_dependency,
    get_next_question_by_exam_dependency,
    get_pdf_bytes_for_review,
    get_question_dependency,
    get_recategorize_existing_dependency,
    get_review_questions_from_pdf_dependency,
    get_update_question_dependency,
    list_questions_by_exam_dependency,
)
from app.api.dependecies.study_note import get_find_related_study_notes_dependency
from app.application.dto.study_note.related_dto import FindRelatedStudyNotesResponse
from app.application.use_cases.study_note.find_related_to_question import (
    FindRelatedStudyNotes,
)
from app.api.errors.schemas import ErrorResponse
from app.application.dto.question.add_answer_key_dto import (
    AddAnswerKeyToExamDTO,
    AddAnswerKeyToExamResponse,
)
from app.application.dto.question.categorize_dto import (
    CategorizeQuestionsDTO,
    CategorizeQuestionsResponse,
)
from app.application.dto.question.recategorize_dto import (
    RecategorizeExistingDTO,
    RecategorizeExistingResponse,
)
from app.application.dto.question.check_answer_dto import (
    CheckAnswerDTO,
    CheckAnswerResponse,
)
from app.application.dto.question.create_dto import (
    CreateQuestionDTO,
    CreateQuestionResponse,
)
from app.application.dto.question.delete_dto import DeleteQuestionResponse
from app.application.dto.question.get_dto import (
    GetQuestionResponse,
    ListQuestionsResponse,
    PaginatedQuestionResponse,
)
from app.application.dto.question.review_from_pdf_dto import ReviewQuestionsFromPDFResponse
from app.application.dto.question.update_dto import (
    UpdateQuestionDTO,
    UpdateQuestionResponse,
)
from app.application.use_cases.question.categorize import CategorizeQuestions
from app.application.use_cases.question.recategorize_existing import RecategorizeExisting
from app.application.use_cases.question.check_answer import CheckAnswer
from app.application.use_cases.question.create import CreateQuestion
from app.application.use_cases.question.delete import DeleteQuestion
from app.application.use_cases.question.generate_embeddings import GenerateEmbeddingsForExam
from app.application.use_cases.question.get import (
    GetNextQuestionByExam,
    GetQuestion,
    ListQuestionsByExam,
)
from app.application.use_cases.question.review_from_pdf import ReviewQuestionsFromPDF
from app.application.use_cases.question.update import UpdateQuestion
from app.domain.value_objects.raw_exam import ExtractionOptions

router = APIRouter(
    prefix="/questions",
    tags=["questions"],
    dependencies=[Depends(get_current_user_id)],
)


@router.post(
    "/",
    summary="create",
    description="Cria uma nova questão vinculada a um exame.",
    response_model=CreateQuestionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Entrada inválida"},
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    },
)
async def create_question(
    body: CreateQuestionDTO,
    use_case: CreateQuestion = Depends(get_create_question_dependency),
) -> CreateQuestionResponse:
    return await use_case.execute(body)


@router.get(
    "/{question_id}",
    summary="get",
    description="Retorna uma questão pelo id.",
    response_model=GetQuestionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Questão não encontrada"},
    },
)
async def get_question(
    question_id: UUID,
    use_case: GetQuestion = Depends(get_question_dependency),
) -> GetQuestionResponse:
    return await use_case.execute(question_id)


@router.get(
    "/exam/{exam_id}",
    summary="list by exam",
    description="Lista todas as questões de um exame.",
    response_model=ListQuestionsResponse,
    status_code=status.HTTP_200_OK,
)
async def list_questions_by_exam(
    exam_id: UUID,
    use_case: ListQuestionsByExam = Depends(list_questions_by_exam_dependency),
) -> ListQuestionsResponse:
    return await use_case.execute(exam_id)


@router.get(
    "/exam/{exam_id}/next",
    summary="get next question",
    description="Retorna uma questão específica de um exame baseada no índice (0 a N-1).",
    response_model=PaginatedQuestionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_next_question_by_exam(
    exam_id: UUID,
    index: int = Query(0, ge=0),
    use_case: GetNextQuestionByExam = Depends(get_next_question_by_exam_dependency),
) -> PaginatedQuestionResponse:
    return await use_case.execute(exam_id, index)


@router.post(
    "/exam/{exam_id}/generate-embeddings",
    summary="generate exam embeddings",
    description="Gera embeddings para todas as questões de um exame que ainda não possuem.",
    status_code=status.HTTP_200_OK,
)
async def generate_exam_embeddings(
    exam_id: UUID,
    use_case: GenerateEmbeddingsForExam = Depends(get_generate_embeddings_for_exam_dependency),
) -> dict:
    return await use_case.execute(exam_id)


@router.patch(
    "/{question_id}",
    summary="update",
    description="Atualiza campos de uma questão existente.",
    response_model=UpdateQuestionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Questão não encontrada"},
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    },
)
async def update_question(
    question_id: UUID,
    body: UpdateQuestionDTO,
    use_case: UpdateQuestion = Depends(get_update_question_dependency),
) -> UpdateQuestionResponse:
    return await use_case.execute(question_id, body)


@router.post(
    "/{question_id}/check",
    summary="check answer",
    description="Verifica se a alternativa enviada é a correta e retorna booleano.",
    response_model=CheckAnswerResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Questão não encontrada"},
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    },
)
async def check_answer(
    question_id: UUID,
    body: CheckAnswerDTO,
    use_case: CheckAnswer = Depends(get_check_answer_dependency),
) -> CheckAnswerResponse:
    return await use_case.execute(question_id, body)


@router.delete(
    "/{question_id}",
    summary="delete",
    description="Remove uma questão pelo id.",
    response_model=DeleteQuestionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Questão não encontrada"},
    },
)
async def delete_question(
    question_id: UUID,
    use_case: DeleteQuestion = Depends(get_delete_question_dependency),
) -> DeleteQuestionResponse:
    return await use_case.execute(question_id)


@router.post(
    "/categorize",
    summary="categorize",
    description="Classifica automaticamente as questões de uma prova OAB usando o serviço de categorização.",
    response_model=CategorizeQuestionsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Entrada inválida"},
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    },
)
async def categorize_questions(
    body: CategorizeQuestionsDTO,
    use_case: CategorizeQuestions = Depends(get_categorize_questions_dependency),
) -> CategorizeQuestionsResponse:
    return await use_case.execute(body)


@router.post(
    "/recategorize-existing",
    summary="recategorize existing",
    description=(
        "Recategoriza questões já existentes no banco de dados.\n\n"
        "- Pode passar `exam_id` para recategorizar todas as questões de um exame.\n"
        "- Pode passar `question_id` para recategorizar apenas uma questão.\n"
        "- Filtros: `format_statement`, `categorize_tags`, `categorize_law_area`."
    ),
    response_model=RecategorizeExistingResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Entrada inválida"},
        404: {"model": ErrorResponse, "description": "Não encontrado"},
    },
)
async def recategorize_existing_questions(
    body: RecategorizeExistingDTO,
    use_case: RecategorizeExisting = Depends(get_recategorize_existing_dependency),
) -> RecategorizeExistingResponse:
    return await use_case.execute(body)


@router.post(
    "/exam/{exam_id}/add-answer-key",
    summary="add answer key",
    description="Importa o gabarito oficial de um PDF e atualiza as questões de um exame.",
    response_model=AddAnswerKeyToExamResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Exame não encontrado"},
        400: {"model": ErrorResponse, "description": "Erro no processamento do PDF"},
    },
)
async def add_answer_key(
    exam_id: UUID,
    pdf_bytes: bytes = Depends(get_pdf_bytes_for_review),
    use_case: AddAnswerKeyToExam = Depends(get_add_answer_key_to_exam_dependency),
) -> AddAnswerKeyToExamResponse:
    input_data = AddAnswerKeyToExamDTO(exam_id=exam_id, pdf_bytes=pdf_bytes)
    return await use_case.execute(input_data)


@router.post(
    "/{question_id}/related-study-notes",
    summary="related study notes",
    description=(
        "Busca as notas de estudo do usuário semanticamente próximas da questão "
        "(kNN via embeddings) e salva automaticamente nas notas com score ≥ 0.65."
    ),
    response_model=FindRelatedStudyNotesResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Questão sem embedding"},
        404: {"model": ErrorResponse, "description": "Questão não encontrada"},
    },
)
async def related_study_notes(
    question_id: UUID,
    limit: int = Query(5, ge=1, le=20),
    user_id: UUID = Depends(get_current_user_id),
    use_case: FindRelatedStudyNotes = Depends(get_find_related_study_notes_dependency),
) -> FindRelatedStudyNotesResponse:
    return await use_case.execute(
        user_id=user_id, question_id=question_id, limit=limit
    )


@router.post(
    "/review-from-pdf",
    summary="extract + categorize",
    description="Extrai questões de um PDF, categoriza e retorna uma lista para revisão humana em uma única chamada.",
    response_model=ReviewQuestionsFromPDFResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Entrada inválida"},
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    },
)
async def review_questions_from_pdf(
    pdf_bytes: bytes = Depends(get_pdf_bytes_for_review),
    header_height: int = Form(65),
    footer_height: int = Form(60),
    column_split: int = Form(298),
    use_case: ReviewQuestionsFromPDF = Depends(get_review_questions_from_pdf_dependency),
) -> ReviewQuestionsFromPDFResponse:
    options = ExtractionOptions(
        header_height=header_height,
        footer_height=footer_height,
        column_split=column_split,
    )
    return await use_case.execute(pdf_bytes=pdf_bytes, options=options)
