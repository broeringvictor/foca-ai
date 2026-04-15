from fastapi import APIRouter, status, Depends

from app.api.dependecies.user import get_create_user_dependency
from app.api.errors.schemas import ErrorResponse
from app.application.dto.auth.authenticate_dto import AuthenticateDTO, AuthenticateResponse
from app.application.use_cases.auth.authenticate import AuthenticateUser

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    summary="Authenticate",
    description="Autentica um usuário e retorna um token JWT http-only",
    response_model=AuthenticateUser,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ErrorResponse, "description": "Entrada inválida"},
        409: {"model": ErrorResponse, "description": "Email já cadastrado"},
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    },
)
async def authenticate(
    body: AuthenticateDTO,
    use_case: AuthenticateUser = Depends(get_create_user_dependency),
) -> CreateUserOutput:
    return await use_case.execute(body)