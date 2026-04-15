from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from services import AuthService
from app.domain.entities.user import User
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.session import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_auth_service(
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    return AuthService(repository=UserRepository(session))


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: AuthService = Depends(get_auth_service),
) -> User:
    return await service.get_current_user(token)
