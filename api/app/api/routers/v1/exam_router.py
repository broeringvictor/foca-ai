from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependecies.auth import get_current_user_id
from app.api.dependecies.exam import (
    get_create_exam_dependency,
    get_delete_exam_dependency,
    get_exam_dependency,
    get_update_exam_dependency,
    list_exams_dependency,
)
from app.api.errors.schemas import ErrorResponse
from app.application.dto.exam.create_dto import CreateExamDTO, CreateExamResponse
from app.application.dto.exam.delete_dto import DeleteExamResponse
from app.application.dto.exam.get_dto import GetExamResponse, ListExamsResponse
from app.application.dto.exam.update_dto import UpdateExamDTO, UpdateExamResponse
from app.application.use_cases.exam.create import CreateExam
from app.application.use_cases.exam.delete import DeleteExam
from app.application.use_cases.exam.get import GetExam, ListExams
from app.application.use_cases.exam.update import UpdateExam

router = APIRouter(
    prefix="/exams",
    tags=["exams"],
    dependencies=[Depends(get_current_user_id)],
)


@router.post(
    "/",
    summary="create",
    description="Cria um novo exame.",
    response_model=CreateExamResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Entrada inválida"},
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    },
)
async def create_exam(
    body: CreateExamDTO,
    use_case: CreateExam = Depends(get_create_exam_dependency),
) -> CreateExamResponse:
    return await use_case.execute(body)


@router.get(
    "/",
    summary="list",
    description="Lista todos os exames cadastrados.",
    response_model=ListExamsResponse,
    status_code=status.HTTP_200_OK,
)
async def list_exams(
    use_case: ListExams = Depends(list_exams_dependency),
) -> ListExamsResponse:
    return await use_case.execute()


@router.get(
    "/{exam_id}",
    summary="get",
    description="Retorna um exame pelo id.",
    response_model=GetExamResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Exame não encontrado"},
    },
)
async def get_exam(
    exam_id: UUID,
    use_case: GetExam = Depends(get_exam_dependency),
) -> GetExamResponse:
    return await use_case.execute(exam_id)


@router.patch(
    "/{exam_id}",
    summary="update",
    description="Atualiza campos de um exame existente.",
    response_model=UpdateExamResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Exame não encontrado"},
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    },
)
async def update_exam(
    exam_id: UUID,
    body: UpdateExamDTO,
    use_case: UpdateExam = Depends(get_update_exam_dependency),
) -> UpdateExamResponse:
    return await use_case.execute(exam_id, body)


@router.delete(
    "/{exam_id}",
    summary="delete",
    description="Remove um exame pelo id.",
    response_model=DeleteExamResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Exame não encontrado"},
    },
)
async def delete_exam(
    exam_id: UUID,
    use_case: DeleteExam = Depends(get_delete_exam_dependency),
) -> DeleteExamResponse:
    return await use_case.execute(exam_id)
