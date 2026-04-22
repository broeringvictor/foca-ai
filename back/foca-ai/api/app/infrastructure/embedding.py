from langchain_openai import OpenAIEmbeddings

from app.infrastructure.config.settings import Settings, get_settings


def get_embedding_model(settings: Settings | None = None) -> OpenAIEmbeddings:
    s = settings or get_settings()
    return OpenAIEmbeddings(
        model=s.embedding.model,
        api_key=s.OPENAI_API_KEY,
        dimensions=s.embedding.dimensions,
        timeout=s.embedding.timeout,
        max_retries=s.embedding.max_retries,
    )
