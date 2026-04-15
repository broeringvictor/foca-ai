from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.auth.authenticate import AuthenticateUser
from app.infrastructure.repositories.auth_repository import AuthRepository
from app.infrastructure.services.auth_service import AuthService
from app.infrastructure.session import get_session


def get_authenticate_user_dependency(
    session: AsyncSession = Depends(get_session),
) -> AuthenticateUser:
    return AuthenticateUser(
        repository=AuthRepository(session),
        service=AuthService(),
    )
