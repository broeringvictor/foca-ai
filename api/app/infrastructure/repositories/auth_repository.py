from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app.domain.entities.user import User
from app.domain.value_objects.password import Password
from app.infrastructure.model.user_model import UserModel


class AuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── busca ──────────────────────────────────────────────────────────────────
    async def find_by_email_for_auth(self, email: str) -> User | None:
        stmt = (
            select(UserModel)
            .options(load_only(
                UserModel.id,
                UserModel.email,
                UserModel.hashed_password,
                UserModel.is_active,
            ))
            .where(UserModel.email == email)
        )
        result = await self._session.execute(stmt)
        model: UserModel | None = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_auth_entity(model)

    @staticmethod
    def _to_auth_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password=Password.from_hash(model.hashed_password),
            is_active=model.is_active,
        )