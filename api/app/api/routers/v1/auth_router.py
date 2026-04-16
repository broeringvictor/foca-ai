from fastapi import APIRouter, Response, status, Depends

from app.api.dependecies.auth import get_authenticate_user_dependency
from app.api.errors.schemas import ErrorResponse
from app.application.dto.auth.authenticate_dto import AuthenticateDTO, AuthenticateResponse
from app.application.use_cases.auth.authenticate import AuthenticateUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/authenticate",
    summary="Authenticate",
    description="Autentica um usuário e retorna um token JWT via cookie HttpOnly",
    response_model=AuthenticateResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Credenciais inválidas"},
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    },
)
async def authenticate(
    response: Response,
    body: AuthenticateDTO,
    use_case: AuthenticateUser = Depends(get_authenticate_user_dependency),
) -> AuthenticateResponse:
    result = await use_case.execute(body)

    response.set_cookie(
        key="access_token",
        value=f"Bearer {result.token}",
        httponly=True,
        secure=False,   # TODO: mudar para True em produção
        samesite="lax",  # TODO: avaliar em produção
    )

    return result
