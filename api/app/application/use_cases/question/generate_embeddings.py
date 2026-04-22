from uuid import UUID
from loguru import logger
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

        processed_count = 0
        errors_count = 0
        
        # 3. Gerar embeddings
        for question in to_process:
            vector = await self._embedding_service.embed_query(question.statement)
            if vector:
                question.embedding = vector
                await self._repository.update(question)
                processed_count += 1
            else:
                # Se o embedding falhou (ex: 401 Unauthorized), incrementamos erros e paramos 
                # se houver erros persistentes para não inundar o log com 80 falhas iguais.
                errors_count += 1
                if errors_count >= 1: # Se o primeiro falhar em lote, provavelmente a chave está errada.
                    logger.error("generate_embeddings: aborting due to persistent embedding failure")
                    break
        
        # 4. Commit parcial do que foi processado
        if processed_count > 0:
            await self._session.commit()
        
        status = "success" if errors_count == 0 else "partial_failure_or_aborted"
        if processed_count == 0 and errors_count > 0:
            status = "failed"
            
        return {
            "processed": processed_count,
            "total": len(questions),
            "remaining_without_embedding": len(to_process) - processed_count,
            "status": status
        }
