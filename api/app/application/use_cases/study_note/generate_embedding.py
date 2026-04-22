from uuid import UUID

from langchain_openai import OpenAIEmbeddings
from loguru import logger

from app.api.errors.exceptions import NotFoundError
from app.application.dto.study_note.embedding_dto import GenerateEmbeddingResponse
from app.domain.repositories.study_note_repository import IStudyNoteRepository


class GenerateStudyNoteEmbedding:
    def __init__(self, repository: IStudyNoteRepository, embeddings: OpenAIEmbeddings) -> None:
        self._repo = repository
        self._embeddings = embeddings

    async def execute(self, study_note_id: UUID) -> GenerateEmbeddingResponse:
        note = await self._repo.find_by_id(study_note_id)
        if note is None:
            raise NotFoundError("study note not found", field="study_note_id", source="path")

        text = f"{note.title}\n\n{note.content or ''}".strip()
        logger.info("study_note.embedding: generating id={} text_len={}", study_note_id, len(text))

        vector = await self._embeddings.aembed_query(text)
        await self._repo.update_embedding(study_note_id, vector)

        logger.info("study_note.embedding: done id={} dims={}", study_note_id, len(vector))
        return GenerateEmbeddingResponse(study_note_id=study_note_id)
