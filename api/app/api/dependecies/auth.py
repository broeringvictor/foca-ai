from fastapi import Depends
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors.exceptions import BadRequestError
from app.application.use_cases.auth.authenticate import AuthenticateUser
from app.application.use_cases.user.get_me import GetMe
from app.infrastructure.repositories.auth_repository import AuthRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.security.jwt import decode_access_token
from app.infrastructure.security.oauth2_cookie import OAuth2PasswordBearerWithCookie
from app.infrastructure.services.auth_service import AuthService
from app.infrastructure.session import get_session

oauth2_scheme = OAuth2PasswordBearerWithCookie(token_url="/api/v1/auth/authenticate")


def get_authenticate_user_dependency(
    session: AsyncSession = Depends(get_session),
) -> AuthenticateUser:
    return AuthenticateUser(
        repository=AuthRepository(session),
        service=AuthService(),
    )


def get_current_user_id(
    token: str = Depends(oauth2_scheme),
) -> str:
    try:
        payload = decode_access_token(token)
    except ExpiredSignatureError:
        raise BadRequestError("Token expirado", field="token", source="cookie")
    except InvalidTokenError:
        raise BadRequestError("Token inválido", field="token", source="cookie")

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise BadRequestError("Token inválido", field="token", source="cookie")

    return user_id


def get_me_dependency(
    session: AsyncSession = Depends(get_session),
) -> GetMe:
    return GetMe(repository=UserRepository(session))
