import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors.exceptions import BadRequestError
from app.application.use_cases.auth.authenticate import AuthenticateUser
from app.application.dto.auth.authenticate_dto import AuthenticateDTO
from app.infrastructure.repositories.auth_repository import AuthRepository
from app.infrastructure.services.auth_service import AuthService
from tests.factories.user import UserFactory, DEFAULT_PASSWORD


def _make_input(**overrides) -> AuthenticateDTO:
    defaults = {
        "email": "joao@example.com",
        "password": DEFAULT_PASSWORD,
    }
    defaults.update(overrides)
    return AuthenticateDTO(**defaults)


@pytest_asyncio.fixture
async def user_on_db(session: AsyncSession):
    user = UserFactory.build(email="joao@example.com")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def use_case(session: AsyncSession) -> AuthenticateUser:
    return AuthenticateUser(
        repository=AuthRepository(session),
        service=AuthService(),
    )


class TestAuthenticateIntegration:
    @pytest.mark.asyncio
    async def test_returns_token(self, use_case: AuthenticateUser, user_on_db):
        result = await use_case.execute(_make_input())

        assert result.token is not None
        assert isinstance(result.token, str)

    @pytest.mark.asyncio
    async def test_raises_when_email_not_found(
        self, use_case: AuthenticateUser, user_on_db
    ):
        with pytest.raises(BadRequestError, match="Credenciais inválidas"):
            await use_case.execute(_make_input(email="naoexiste@example.com"))

    @pytest.mark.asyncio
    async def test_raises_when_password_wrong(
        self, use_case: AuthenticateUser, user_on_db
    ):
        with pytest.raises(BadRequestError, match="Credenciais inválidas"):
            await use_case.execute(_make_input(password="SenhaErrada@123"))

    @pytest.mark.asyncio
    async def test_token_contains_user_data(
        self, use_case: AuthenticateUser, user_on_db
    ):
        import jwt
        from app.infrastructure.config.settings import get_settings

        config = get_settings()
        result = await use_case.execute(_make_input())
        payload = jwt.decode(
            result.token, config.JWT_KEY, algorithms=[config.JWT_ALGORITHM]
        )

        assert payload["sub"] == str(user_on_db.id)
        assert payload["email"] == "joao@example.com"
