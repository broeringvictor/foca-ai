import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors.exceptions import BadRequestError, ConflictError
from app.application.use_cases.user.create import CreateUser
from app.application.dto.user.create_dto import CreateUserDTO
from app.infrastructure.repositories.user_repository import UserRepository


def _make_input(**overrides) -> CreateUserDTO:
    defaults = {
        "first_name": "João",
        "last_name": "Silva",
        "email": "joao@example.com",
        "password": "Senha@1234",
        "password_confirm": "Senha@1234",
    }
    defaults.update(overrides)
    return CreateUserDTO(**defaults)


@pytest_asyncio.fixture
async def repo(session: AsyncSession) -> UserRepository:
    return UserRepository(session)


@pytest_asyncio.fixture
async def use_case(repo: UserRepository) -> CreateUser:
    return CreateUser(repository=repo)


class TestCreateUserIntegration:
    @pytest.mark.asyncio
    async def test_creates_and_persists_user(
        self, use_case: CreateUser, repo: UserRepository, session: AsyncSession
    ):
        result = await use_case.execute(_make_input())
        await session.flush()

        found = await repo.find_by_email("joao@example.com")

        assert found is not None
        assert found.id == result.user_id
        assert found.name.first_name == "João"
        assert found.name.last_name == "Silva"

    @pytest.mark.asyncio
    async def test_password_is_hashed_correctly(
        self, use_case: CreateUser, repo: UserRepository, session: AsyncSession
    ):
        await use_case.execute(_make_input())
        await session.flush()

        found = await repo.find_by_email("joao@example.com")

        assert found.password.verify("Senha@1234") is True
        assert found.password.hashed_value != "Senha@1234"

    @pytest.mark.asyncio
    async def test_rejects_duplicate_email(
        self, use_case: CreateUser, session: AsyncSession
    ):
        await use_case.execute(_make_input())
        await session.flush()

        with pytest.raises(ConflictError, match="já está em uso"):
            await use_case.execute(
                _make_input(
                    first_name="Maria",
                    last_name="Costa",
                )
            )

    @pytest.mark.asyncio
    async def test_rejects_password_mismatch(self, use_case: CreateUser):
        with pytest.raises(BadRequestError, match="senhas são divergentes"):
            await use_case.execute(_make_input(password_confirm="OutraSenha"))

    @pytest.mark.asyncio
    async def test_user_is_active_by_default(
        self, use_case: CreateUser, repo: UserRepository, session: AsyncSession
    ):
        await use_case.execute(_make_input())
        await session.flush()

        found = await repo.find_by_email("joao@example.com")

        assert found.is_active is True

    @pytest.mark.asyncio
    async def test_normalizes_email_to_lowercase(
        self, use_case: CreateUser, repo: UserRepository, session: AsyncSession
    ):
        await use_case.execute(_make_input(email="JOAO@Example.COM"))
        await session.flush()

        found = await repo.find_by_email("joao@example.com")

        assert found is not None
        assert found.email == "joao@example.com"
