from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.value_objects.name import Name
from app.domain.value_objects.password import Password
from app.domain.value_objects.recoverty_code import RecoveryCode
from app.infrastructure.model.user_model import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── persistência ──────────────────────────────────────────────────────────

    async def save(self, user: User) -> None:
        model = self._to_model(user)
        self._session.add(model)


    # ── busca ──────────────────────────────────────────────────────────────────

    async def find_by_id(self, user_id: str | UUID) -> User | None:
        uid = user_id if isinstance(user_id, UUID) else UUID(user_id)
        stmt = select(UserModel).where(UserModel.id == uid)
        result = await self._session.execute(stmt)
        model: UserModel | None = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def find_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model: UserModel | None = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    # ── mapeamento ────────────────────────────────────────────────────────────

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            name=Name(first_name=model.first_name, last_name=model.last_name),
            email=model.email,
            password=Password.from_hash(model.hashed_password),
            recovery_code=RecoveryCode(code=model.code, expires_at=model.expires_at),
            is_active=model.is_active,
            create_at=model.create_at,
            modified_at=model.modified_at,
        )

    @staticmethod
    def _to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id,
            first_name=user.name.first_name,
            last_name=user.name.last_name,
            email=user.email,
            hashed_password=user.password.hashed_value,
            code=str(user.recovery_code.code),
            expires_at=user.recovery_code.expires_at,
            create_at=user.create_at,
            modified_at=user.modified_at,
            is_active=user.is_active,
        )

