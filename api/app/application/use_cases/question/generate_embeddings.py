from uuid import UUID
from app.domain.repositories.question_repository import IQuestionRepository
from app.domain.services.embedding_service import IEmbeddingService
from sqlalchemy.ext.asyncio import AsyncSession

class GenerateEmbeddingsForExam:
    def __init__(
        self,
        repository: IQuestionRepository,
        embedding_service: IEmbeddingService,
        session: AsyncSession,
    ) -> None:
        self._repository = repository
        self._embedding_service = embedding_service
        self._session = session

    async def execute(self, exam_id: UUID) -> dict:
        # 1. Buscar todas as questões do exame
        questions = await self._repository.find_all_by_exam_id(exam_id)
        
        # 2. Filtrar apenas as que não têm embedding
        to_process = [q for q in questions if q.embedding is None]
        
        if not to_process:
            return {"processed": 0, "total": len(questions), "status": "already_up_to_date"}

        # 3. Gerar embeddings (poderia ser feito em batch, mas vamos um a um por segurança/limite de tokens)
        for question in to_process:
            vector = await self._embedding_service.embed_query(question.statement)
            if vector:
                question.embedding = vector
                await self._repository.update(question)
        
        # 4. Commit final
        await self._session.commit()
        
        return {
            "processed": len(to_process),
            "total": len(questions),
            "status": "success"
        }
