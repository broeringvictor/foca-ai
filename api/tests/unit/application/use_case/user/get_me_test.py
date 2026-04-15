import pytest
from unittest.mock import AsyncMock

from app.application.use_cases.user.get_me import GetMe
from app.domain.entities.user import User


def _make_user() -> User:
    return User.create(
        first_name="João",
        last_name="Silva",
        email="joao@example.com",
        password="Senha@1234",
    )


@pytest.fixture
def repo() -> AsyncMock:
    mock = AsyncMock()
    mock.find_by_id.return_value = _make_user()
    return mock


@pytest.fixture
def use_case(repo: AsyncMock) -> GetMe:
    return GetMe(repository=repo)


class TestGetMeSuccess:
    @pytest.mark.asyncio
    async def test_returns_user_id(self, use_case: GetMe):
        result = await use_case.execute("some-user-id")

        assert result.user_id is not None

    @pytest.mark.asyncio
    async def test_returns_email(self, use_case: GetMe):
        result = await use_case.execute("some-user-id")

        assert result.email == "joao@example.com"

    @pytest.mark.asyncio
    async def test_returns_name(self, use_case: GetMe):
        result = await use_case.execute("some-user-id")

        assert result.name.first_name == "João"
        assert result.name.last_name == "Silva"

    @pytest.mark.asyncio
    async def test_returns_is_active(self, use_case: GetMe):
        result = await use_case.execute("some-user-id")

        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_returns_timestamps(self, use_case: GetMe):
        result = await use_case.execute("some-user-id")

        assert result.create_at is not None
        assert result.modified_at is not None

    @pytest.mark.asyncio
    async def test_calls_repo_with_user_id(self, use_case: GetMe, repo: AsyncMock):
        await use_case.execute("some-user-id")

        repo.find_by_id.assert_awaited_once_with("some-user-id")


class TestGetMeUserNotFound:
    @pytest.mark.asyncio
    async def test_raises_when_user_not_found(self, use_case: GetMe, repo: AsyncMock):
        repo.find_by_id.return_value = None

        with pytest.raises(ValueError, match="Usuário não encontrado"):
            await use_case.execute("nonexistent-id")
