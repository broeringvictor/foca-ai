import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.use_cases.auth.authenticate import AuthenticateUser
from app.application.dto.auth.authenticate_dto import AuthenticateDTO
from app.domain.entities.user import User


def _make_input(**overrides) -> AuthenticateDTO:
    defaults = {
        "email": "joao@example.com",
        "password": "Senha@1234",
    }
    defaults.update(overrides)
    return AuthenticateDTO(**defaults)


def _make_user(is_active: bool = True) -> User:
    return User.create(
        first_name="João",
        last_name="Silva",
        email="joao@example.com",
        password="Senha@1234",
    )


@pytest.fixture
def repo() -> AsyncMock:
    mock = AsyncMock()
    mock.find_by_email_for_auth.return_value = _make_user()
    return mock


@pytest.fixture
def service() -> MagicMock:
    mock = MagicMock()
    mock.generate_token_jwt.return_value = "fake.jwt.token"
    return mock


@pytest.fixture
def use_case(repo: AsyncMock, service: MagicMock) -> AuthenticateUser:
    return AuthenticateUser(repository=repo, service=service)


class TestAuthenticateSuccess:
    @pytest.mark.asyncio
    async def test_returns_token(self, use_case: AuthenticateUser):
        result = await use_case.execute(_make_input())

        assert result.token == "fake.jwt.token"

    @pytest.mark.asyncio
    async def test_calls_repo_with_email(self, use_case: AuthenticateUser, repo: AsyncMock):
        await use_case.execute(_make_input())

        repo.find_by_email_for_auth.assert_awaited_once_with("joao@example.com")

    @pytest.mark.asyncio
    async def test_calls_service_with_user_data(
        self, use_case: AuthenticateUser, service: MagicMock
    ):
        result = await use_case.execute(_make_input())

        service.generate_token_jwt.assert_called_once()
        call_kwargs = service.generate_token_jwt.call_args.kwargs
        assert call_kwargs["email"] == "joao@example.com"
        assert "user_id" in call_kwargs
        assert "name" in call_kwargs


class TestAuthenticateUserNotFound:
    @pytest.mark.asyncio
    async def test_raises_when_user_not_found(self, use_case: AuthenticateUser, repo: AsyncMock):
        repo.find_by_email_for_auth.return_value = None

        with pytest.raises(ValueError, match="Credenciais inválidas"):
            await use_case.execute(_make_input())

    @pytest.mark.asyncio
    async def test_does_not_call_service_when_user_not_found(
        self, use_case: AuthenticateUser, repo: AsyncMock, service: MagicMock
    ):
        repo.find_by_email_for_auth.return_value = None

        with pytest.raises(ValueError):
            await use_case.execute(_make_input())

        service.generate_token_jwt.assert_not_called()


class TestAuthenticateInactiveUser:
    @pytest.mark.asyncio
    async def test_raises_when_user_inactive(self, use_case: AuthenticateUser, repo: AsyncMock):
        user = _make_user()
        user.is_active = False
        repo.find_by_email_for_auth.return_value = user

        with pytest.raises(ValueError, match="Usuário inativo"):
            await use_case.execute(_make_input())

    @pytest.mark.asyncio
    async def test_does_not_call_service_when_user_inactive(
        self, use_case: AuthenticateUser, repo: AsyncMock, service: MagicMock
    ):
        user = _make_user()
        user.is_active = False
        repo.find_by_email_for_auth.return_value = user

        with pytest.raises(ValueError):
            await use_case.execute(_make_input())

        service.generate_token_jwt.assert_not_called()


class TestAuthenticateWrongPassword:
    @pytest.mark.asyncio
    async def test_raises_when_password_wrong(self, use_case: AuthenticateUser, repo: AsyncMock):
        with pytest.raises(ValueError, match="Credenciais inválidas"):
            await use_case.execute(_make_input(password="SenhaErrada@123"))

    @pytest.mark.asyncio
    async def test_does_not_call_service_when_password_wrong(
        self, use_case: AuthenticateUser, repo: AsyncMock, service: MagicMock
    ):
        with pytest.raises(ValueError):
            await use_case.execute(_make_input(password="SenhaErrada@123"))

        service.generate_token_jwt.assert_not_called()
