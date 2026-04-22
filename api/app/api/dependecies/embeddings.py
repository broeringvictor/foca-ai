from app.domain.services.embedding_service import IEmbeddingService
from app.infrastructure.embeddings import get_embeddings_client
from app.infrastructure.services.embedding_service import OpenAIEmbeddingService


def get_embedding_service_dependency() -> IEmbeddingService:
    # Composition root: build the OpenAI client once per request and wrap it.
    return OpenAIEmbeddingService(client=get_embeddings_client())
