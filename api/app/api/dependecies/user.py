from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.user.create import CreateUser
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.session import get_session


def get_create_user_dependency(
    session: AsyncSession = Depends(get_session),
) -> CreateUser:
    return CreateUser(repository=UserRepository(session))