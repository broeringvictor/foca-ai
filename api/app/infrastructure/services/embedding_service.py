from langchain_openai import OpenAIEmbeddings
from loguru import logger

from app.domain.services.embedding_service import IEmbeddingService


class OpenAIEmbeddingService(IEmbeddingService):
    """OpenAI-backed implementation of `IEmbeddingService`.

    Wraps `langchain_openai.OpenAIEmbeddings` with structured logging and
    graceful degradation: upstream failures return None so callers can persist
    the entity without an embedding instead of aborting the whole request.
    """

    def __init__(self, client: OpenAIEmbeddings) -> None:
        self._client = client

    async def embed_query(self, text: str) -> list[float] | None:
        if not text or not text.strip():
            return None

        try:
            vector = await self._client.aembed_query(text)
        except Exception as exc:
            logger.warning("embedding: embed_query_failed error={}", exc)
            return None

        logger.info("embedding: embed_query_done dims={}", len(vector))
        return vector

    async def embed_documents(
        self, texts: list[str]
    ) -> list[list[float] | None]:
        if not texts:
            return []

        valid_indices = [i for i, t in enumerate(texts) if t and t.strip()]
        if not valid_indices:
            return [None] * len(texts)

        inputs = [texts[i] for i in valid_indices]
        try:
            vectors = await self._client.aembed_documents(inputs)
        except Exception as exc:
            logger.warning(
                "embedding: embed_documents_failed batch={} error={}",
                len(inputs),
                exc,
            )
            return [None] * len(texts)

        logger.info(
            "embedding: embed_documents_done batch={} dims={}",
            len(inputs),
            len(vectors[0]) if vectors else 0,
        )

        result: list[list[float] | None] = [None] * len(texts)
        for idx, vec in zip(valid_indices, vectors, strict=True):
            result[idx] = vec
        return result
