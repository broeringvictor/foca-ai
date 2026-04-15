import pytest
import pytest_asyncio
from uuid import uuid8
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.infrastructure.repository.user_repository import UserRepository


@pytest_asyncio.fixture
async def repo(session: AsyncSession) -> UserRepository:
    return UserRepository(session)


@pytest_asyncio.fixture
async def saved_user(repo: UserRepository, session: AsyncSession) -> User:
    user = User.create("João", "Silva", "Senha@1234", "joao@example.com")
    await repo.save(user)
    await session.flush()
    return user


class TestUserRepositorySave:
    @pytest.mark.asyncio
    async def test_save_persists_user(
        self, repo: UserRepository, session: AsyncSession
    ):
        user = User.create("Maria", "Costa", "Senha@1234", "maria@example.com")
        await repo.save(user)
        await session.flush()

        found = await repo.find_by_id(user.id)

        assert found is not None
        assert found.id == user.id

    @pytest.mark.asyncio
    async def test_save_preserves_email(
        self, repo: UserRepository, session: AsyncSession
    ):
        user = User.create("Carlos", "Lima", "Senha@1234", "carlos@example.com")
        await repo.save(user)
        await session.flush()

        found = await repo.find_by_id(user.id)

        assert found.email == "carlos@example.com"

    @pytest.mark.asyncio
    async def test_save_preserves_active_status(
        self, repo: UserRepository, session: AsyncSession
    ):
        user = User.create("Ana", "Souza", "Senha@1234", "ana@example.com")
        await repo.save(user)
        await session.flush()

        found = await repo.find_by_id(user.id)

        assert found.is_active is True


class TestUserRepositoryFindById:
    @pytest.mark.asyncio
    async def test_find_by_id_returns_user(
        self, repo: UserRepository, saved_user: User
    ):
        found = await repo.find_by_id(saved_user.id)

        assert found is not None
        assert found.id == saved_user.id

    @pytest.mark.asyncio
    async def test_find_by_id_returns_none_when_not_found(self, repo: UserRepository):
        found = await repo.find_by_id(uuid8())

        assert found is None

    @pytest.mark.asyncio
    async def test_find_by_id_reconstructs_name(
        self, repo: UserRepository, saved_user: User
    ):
        found = await repo.find_by_id(saved_user.id)

        assert found.name.first_name == saved_user.name.first_name
        assert found.name.last_name == saved_user.name.last_name

    @pytest.mark.asyncio
    async def test_find_by_id_reconstructs_password(
        self, repo: UserRepository, saved_user: User
    ):
        found = await repo.find_by_id(saved_user.id)

        assert found.password.verify("Senha@1234") is True


class TestUserRepositoryFindByEmail:
    @pytest.mark.asyncio
    async def test_find_by_email_returns_user(
        self, repo: UserRepository, saved_user: User
    ):
        found = await repo.find_by_email("joao@example.com")

        assert found is not None
        assert found.email == "joao@example.com"

    @pytest.mark.asyncio
    async def test_find_by_email_returns_none_when_not_found(
        self, repo: UserRepository
    ):
        found = await repo.find_by_email("naoexiste@example.com")

        assert found is None
