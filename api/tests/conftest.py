import pytest
import pytest_asyncio
from typing import AsyncGenerator

from fastapi.testclient import TestClient
from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from app.api.dependecies.embeddings import get_embedding_service_dependency
from app.domain.services.embedding_service import IEmbeddingService
from app.infrastructure.model import table_registry
from app.infrastructure.session import get_session
from tests.factories.user import UserFactory

EMBEDDING_DIMENSIONS = 3072


class FakeEmbeddingService(IEmbeddingService):
    """Deterministic stand-in for OpenAIEmbeddingService used across tests."""

    def __init__(self, dimensions: int = EMBEDDING_DIMENSIONS) -> None:
        self._dimensions = dimensions

    async def embed_query(self, text: str) -> list[float] | None:
        if not text or not text.strip():
            return None
        return self._vector_for(text)

    async def embed_documents(
        self, texts: list[str]
    ) -> list[list[float] | None]:
        return [
            self._vector_for(t) if t and t.strip() else None for t in texts
        ]

    def _vector_for(self, text: str) -> list[float]:
        # Simple hash-based seed so equal inputs return equal vectors.
        seed = sum(ord(c) for c in text) or 1
        base = (seed % 97) / 97.0
        return [base] * self._dimensions

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
def fake_embedding_service() -> FakeEmbeddingService:
    return FakeEmbeddingService()


@pytest.fixture(scope="function")
def client(setup_db, fake_embedding_service):
    async def get_session_override():
        async with TestingSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_embedding_service_dependency] = (
        lambda: fake_embedding_service
    )

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
