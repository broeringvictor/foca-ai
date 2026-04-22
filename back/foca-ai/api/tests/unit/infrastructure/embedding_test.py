from app.infrastructure.config.settings import Settings
from app.infrastructure.embedding import get_embedding_model


class TestGetEmbeddingModel:
    def test_builds_model_with_explicit_settings(self, monkeypatch):
        captured: dict[str, object] = {}

        class _FakeOpenAIEmbeddings:
            def __init__(self, **kwargs):
                captured.update(kwargs)

        settings = Settings(
            POSTGRES_PASSWORD="test",
            JWT_KEY="test",
            ANTHROPIC_API_KEY="test",
            OPENAI_API_KEY="openai-key",
            embedding={
                "model": "text-embedding-3-small",
                "dimensions": 1024,
                "timeout": 10,
                "max_retries": 2,
            },
        )

        monkeypatch.setattr("app.infrastructure.embedding.OpenAIEmbeddings", _FakeOpenAIEmbeddings)

        model = get_embedding_model(settings)

        assert isinstance(model, _FakeOpenAIEmbeddings)
        assert captured["model"] == "text-embedding-3-small"
        assert captured["api_key"] == "openai-key"
        assert captured["dimensions"] == 1024
        assert captured["timeout"] == 10
        assert captured["max_retries"] == 2

    def test_uses_get_settings_when_settings_not_provided(self, monkeypatch):
        captured: dict[str, object] = {}

        class _FakeOpenAIEmbeddings:
            def __init__(self, **kwargs):
                captured.update(kwargs)

        settings = Settings(
            POSTGRES_PASSWORD="test",
            JWT_KEY="test",
            ANTHROPIC_API_KEY="test",
            OPENAI_API_KEY="fallback-key",
            embedding={
                "model": "text-embedding-3-large",
                "dimensions": 3072,
                "timeout": 30,
                "max_retries": 6,
            },
        )

        monkeypatch.setattr("app.infrastructure.embedding.OpenAIEmbeddings", _FakeOpenAIEmbeddings)
        monkeypatch.setattr("app.infrastructure.embedding.get_settings", lambda: settings)

        model = get_embedding_model()

        assert isinstance(model, _FakeOpenAIEmbeddings)
        assert captured["api_key"] == "fallback-key"
        assert captured["dimensions"] == 3072

