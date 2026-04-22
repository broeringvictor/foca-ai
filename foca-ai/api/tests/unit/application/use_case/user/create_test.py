import pytest
from unittest.mock import AsyncMock

from app.application.use_cases.user.create import CreateUser
from app.application.dto.user.create_dto import CreateUserDTO
from app.domain.entities.user import User


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


@pytest.fixture
def repo() -> AsyncMock:
    mock = AsyncMock()
    mock.find_by_email.return_value = None
    mock.save.return_value = None
    return mock


@pytest.fixture
def use_case(repo: AsyncMock) -> CreateUser:
    return CreateUser(repository=repo)


class TestCreateUserSuccess:
    @pytest.mark.asyncio
    async def test_returns_output_with_email(self, use_case: CreateUser):
        result = await use_case.execute(_make_input())

        assert result.email == "joao@example.com"

    @pytest.mark.asyncio
    async def test_returns_output_with_name(self, use_case: CreateUser):
        result = await use_case.execute(_make_input())

        assert result.name.first_name == "João"
        assert result.name.last_name == "Silva"

    @pytest.mark.asyncio
    async def test_returns_output_with_user_id(self, use_case: CreateUser):
        result = await use_case.execute(_make_input())

        assert result.user_id is not None

    @pytest.mark.asyncio
    async def test_calls_save(self, use_case: CreateUser, repo: AsyncMock):
        await use_case.execute(_make_input())

        repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_checks_email_before_saving(
        self, use_case: CreateUser, repo: AsyncMock
    ):
        await use_case.execute(_make_input())

        repo.find_by_email.assert_awaited_once_with("joao@example.com")


class TestCreateUserPasswordMismatch:
    @pytest.mark.asyncio
    async def test_raises_when_passwords_differ(self, use_case: CreateUser):
        input_data = _make_input(password_confirm="OutraSenha@1234")

        with pytest.raises(ValueError, match="senhas são divergentes"):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_does_not_call_repo_when_passwords_differ(
        self, use_case: CreateUser, repo: AsyncMock
    ):
        input_data = _make_input(password_confirm="OutraSenha@1234")

        with pytest.raises(ValueError):
            await use_case.execute(input_data)

        repo.find_by_email.assert_not_awaited()
        repo.save.assert_not_awaited()


class TestCreateUserDuplicateEmail:
    @pytest.mark.asyncio
    async def test_raises_when_email_already_exists(
        self, use_case: CreateUser, repo: AsyncMock
    ):
        repo.find_by_email.return_value = User.create(
            "Maria", "Costa", "Senha@1234", "joao@example.com"
        )

        with pytest.raises(ValueError, match="já está em uso"):
            await use_case.execute(_make_input())

    @pytest.mark.asyncio
    async def test_does_not_save_when_email_exists(
        self, use_case: CreateUser, repo: AsyncMock
    ):
        repo.find_by_email.return_value = User.create(
            "Maria", "Costa", "Senha@1234", "joao@example.com"
        )

        with pytest.raises(ValueError):
            await use_case.execute(_make_input())

        repo.save.assert_not_awaited()


class TestCreateUserSaveFailure:
    @pytest.mark.asyncio
    async def test_raises_when_save_fails(self, use_case: CreateUser, repo: AsyncMock):
        repo.save.side_effect = RuntimeError("banco fora do ar")

        with pytest.raises(RuntimeError, match="banco fora do ar"):
            await use_case.execute(_make_input())
