from fastapi import APIRouter, status, Depends

from app.api.dependecies.auth import get_current_user_id, get_me_dependency
from app.api.dependecies.user import get_create_user_dependency
from app.api.errors.schemas import ErrorResponse
from app.application.dto.user.create_dto import CreateUserResponse, CreateUserDTO
from app.application.dto.user.get_me_dto import GetMeResponse
from app.application.use_cases.user.create import CreateUser
from app.application.use_cases.user.get_me import GetMe

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    summary="Create",
    response_model=CreateUserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Entrada inválida"},
        409: {"model": ErrorResponse, "description": "Email já cadastrado"},
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    },
)
async def create_user(
    body: CreateUserDTO,
    use_case: CreateUser = Depends(get_create_user_dependency),
) -> CreateUserResponse:
    return await use_case.execute(body)


@router.get(
    "/me",
    summary="Me",
    description="Retorna os dados do usuário autenticado",
    response_model=GetMeResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Token inválido ou expirado"},
        404: {"model": ErrorResponse, "description": "Usuário não encontrado"},
    },
)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    use_case: GetMe = Depends(get_me_dependency),
) -> GetMeResponse:
    return await use_case.execute(user_id)