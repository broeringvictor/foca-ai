from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependecies.auth import get_current_user_id
from app.api.dependecies.question import (
    get_check_answer_dependency,
    get_create_question_dependency,
    get_delete_question_dependency,
    get_question_dependency,
    get_update_question_dependency,
    list_questions_by_exam_dependency,
)
from app.api.errors.schemas import ErrorResponse
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
)
from app.application.dto.question.update_dto import (
    UpdateQuestionDTO,
    UpdateQuestionResponse,
)
from app.application.use_cases.question.check_answer import CheckAnswer
from app.application.use_cases.question.create import CreateQuestion
from app.application.use_cases.question.delete import DeleteQuestion
from app.application.use_cases.question.get import GetQuestion, ListQuestionsByExam
from app.application.use_cases.question.update import UpdateQuestion

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
