import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors.exceptions import NotFoundError
from app.application.use_cases.user.get_me import GetMe
from app.infrastructure.repositories.user_repository import UserRepository
from tests.factories.user import UserFactory


@pytest_asyncio.fixture
async def user_on_db(session: AsyncSession):
    user = UserFactory.build()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def use_case(session: AsyncSession) -> GetMe:
    return GetMe(repository=UserRepository(session))


class TestGetMeIntegration:
    @pytest.mark.asyncio
    async def test_returns_user_data(self, use_case: GetMe, user_on_db):
        result = await use_case.execute(str(user_on_db.id))

        assert result.user_id == user_on_db.id
        assert result.email == user_on_db.email
        assert result.name.first_name == user_on_db.first_name
        assert result.name.last_name == user_on_db.last_name
        assert result.is_active is True

    @pytest.mark.asyncio
    async def test_returns_timestamps(self, use_case: GetMe, user_on_db):
        result = await use_case.execute(str(user_on_db.id))

        assert result.create_at is not None
        assert result.modified_at is not None

    @pytest.mark.asyncio
    async def test_raises_when_user_not_found(self, use_case: GetMe):
        with pytest.raises(NotFoundError, match="Usuário não encontrado"):
            await use_case.execute("00000000-0000-0000-0000-000000000000")
