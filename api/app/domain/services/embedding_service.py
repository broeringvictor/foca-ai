from typing import Protocol


class IEmbeddingService(Protocol):
    async def embed_query(self, text: str) -> list[float] | None: ...
    async def embed_documents(
        self, texts: list[str]
    ) -> list[list[float] | None]: ...
