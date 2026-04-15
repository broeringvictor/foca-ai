import pytest
import pytest_asyncio
from typing import AsyncGenerator

from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.infrastructure.model import table_registry
from app.infrastructure.session import get_session
from tests.factories.user import UserFactory

logger.disable("app")


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def session(setup_db) -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
def client(setup_db):
    async def get_session_override():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user_on_db(session):
    user = UserFactory.build()

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user
