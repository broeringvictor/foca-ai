from langchain_openai import OpenAIEmbeddings

from app.infrastructure.config.settings import Settings, get_settings


def get_embeddings_client(settings: Settings | None = None) -> OpenAIEmbeddings:
    """Build and return the OpenAI embeddings client used by infrastructure services."""
    current_settings = settings or get_settings()
    return OpenAIEmbeddings(
        model=current_settings.embedding.model,
        api_key=current_settings.OPENAI_API_KEY,
        dimensions=current_settings.embedding.dimensions,
        timeout=current_settings.embedding.timeout,
        max_retries=current_settings.embedding.max_retries,
    )
