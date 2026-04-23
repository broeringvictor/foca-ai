from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app.domain.entities.question import Question
from app.domain.enums.alternatives import Alternative
from app.domain.enums.law_area import LawArea
from app.infrastructure.model.question_model import QuestionModel

_COLS_WITHOUT_EMBEDDING = load_only(
    QuestionModel.id,
    QuestionModel.exam_id,
    QuestionModel.number,
    QuestionModel.statement,
    QuestionModel.area,
    QuestionModel.correct,
    QuestionModel.alternative_a,
    QuestionModel.alternative_b,
    QuestionModel.alternative_c,
    QuestionModel.alternative_d,
    QuestionModel.tags,
    QuestionModel.confidence,
    QuestionModel.priority_score,
    QuestionModel.source,
    QuestionModel.created_at,
    QuestionModel.updated_at,
)


class QuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── persistência ──────────────────────────────────────────────────────────

    async def save(self, question: Question) -> None:
        model = self._to_model(question)
        self._session.add(model)

    async def update(self, question: Question) -> None:
        model = await self._session.get(QuestionModel, question.id)
        if model is None:
            return

        model.exam_id = question.exam_id
        model.number = question.number
        model.statement = question.statement
        model.area = question.area.value
        model.correct = question.correct.value
        model.alternative_a = question.alternative_a
        model.alternative_b = question.alternative_b
        model.alternative_c = question.alternative_c
        model.alternative_d = question.alternative_d
        model.tags = list(question.tags)
        model.confidence = question.confidence
        model.source = question.source
        model.embedding = question.embedding
        model.updated_at = question.updated_at

    async def delete(self, question_id: UUID) -> None:
        stmt = delete(QuestionModel).where(QuestionModel.id == question_id)
        await self._session.execute(stmt)

    async def delete_all_by_exam_id(self, exam_id: UUID) -> int:
        stmt = delete(QuestionModel).where(QuestionModel.exam_id == exam_id)
        result = await self._session.execute(stmt)
        return int(result.rowcount or 0)

    # ── busca ─────────────────────────────────────────────────────────────────

    async def find_by_id(self, question_id: UUID) -> Question | None:
        stmt = select(QuestionModel).where(QuestionModel.id == question_id)
        result = await self._session.execute(stmt)
        model: QuestionModel | None = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def find_by_ids(self, question_ids: list[UUID]) -> list[Question]:
        if not question_ids:
            return []
        stmt = select(QuestionModel).where(QuestionModel.id.in_(question_ids))
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def find_all_by_exam_id(self, exam_id: UUID) -> list[Question]:
        stmt = select(QuestionModel).where(QuestionModel.exam_id == exam_id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def find_by_area(self, area: LawArea, limit: int = 5) -> list[Question]:
        stmt = (
            select(QuestionModel)
            .options(_COLS_WITHOUT_EMBEDDING)
            .where(QuestionModel.area == area.value)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def find_one_by_exam_id_at_index(
        self, exam_id: UUID, index: int
    ) -> Question | None:
        stmt = (
            select(QuestionModel)
            .where(QuestionModel.exam_id == exam_id)
            .order_by(QuestionModel.number)
            .offset(index)
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def count_by_exam_id(self, exam_id: UUID) -> int:
        from sqlalchemy import func

        stmt = select(func.count(QuestionModel.id)).where(
            QuestionModel.exam_id == exam_id
        )
        result = await self._session.execute(stmt)
        return int(result.scalar_one() or 0)

    async def find_top_rated_not_answered(
        self, user_id: UUID, limit: int = 10
    ) -> list[Question]:
        from app.infrastructure.model.study_question_model import StudyQuestionModel
        
        # Subquery para questões que o usuário já respondeu (tem progresso)
        answered_stmt = select(StudyQuestionModel.question_id).where(
            StudyQuestionModel.user_id == user_id
        )
        
        stmt = (
            select(QuestionModel)
            .options(_COLS_WITHOUT_EMBEDDING)
            .where(QuestionModel.id.not_in(answered_stmt))
            .order_by(QuestionModel.priority_score.desc())
            .limit(limit)
        )
        
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def find_low_rated_not_answered(
        self, user_id: UUID, limit: int = 10
    ) -> list[Question]:
        from app.infrastructure.model.study_question_model import StudyQuestionModel
        
        answered_stmt = select(StudyQuestionModel.question_id).where(
            StudyQuestionModel.user_id == user_id
        )
        
        # Ordem ascendente para pegar as notas mais baixas
        stmt = (
            select(QuestionModel)
            .options(_COLS_WITHOUT_EMBEDDING)
            .where(QuestionModel.id.not_in(answered_stmt))
            .order_by(QuestionModel.priority_score.asc())
            .limit(limit)
        )
        
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def find_by_embedding_similarity(
        self,
        query_vector: list[float],
        limit: int,
        exam_id: UUID | None = None,
    ) -> list[tuple[Question, float]]:
        distance_expr = QuestionModel.embedding.cosine_distance(query_vector)
        stmt = (
            select(QuestionModel, distance_expr.label("distance"))
            .where(QuestionModel.embedding.is_not(None))
        )

        if exam_id:
            stmt = stmt.where(QuestionModel.exam_id == exam_id)

        stmt = stmt.order_by(distance_expr).limit(limit)

        result = await self._session.execute(stmt)
        rows = result.all()
        return [
            (self._to_entity(model), 1.0 - float(distance))
            for model, distance in rows
        ]

    # ── mapeamento ────────────────────────────────────────────────────────────

    @staticmethod
    def _to_entity(model: QuestionModel) -> Question:
        from sqlalchemy import inspect
        insp = inspect(model)

        embedding = None
        if "embedding" not in insp.unloaded:
            embedding = _coerce_embedding(model.embedding)

        return Question(            id=model.id,
            exam_id=model.exam_id,
            number=model.number,
            statement=model.statement,
            area=LawArea(model.area),
            correct=Alternative(model.correct),
            alternative_a=model.alternative_a,
            alternative_b=model.alternative_b,
            alternative_c=model.alternative_c,
            alternative_d=model.alternative_d,
            tags=list(model.tags or []),
            confidence=model.confidence,
            priority_score=model.priority_score,
            source=model.source,
            embedding=embedding,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(question: Question) -> QuestionModel:
        return QuestionModel(
            id=question.id,
            exam_id=question.exam_id,
            number=question.number,
            statement=question.statement,
            area=question.area.value,
            correct=question.correct.value,
            alternative_a=question.alternative_a,
            alternative_b=question.alternative_b,
            alternative_c=question.alternative_c,
            alternative_d=question.alternative_d,
            tags=list(question.tags),
            confidence=question.confidence,
            priority_score=question.priority_score,
            source=question.source,
            embedding=question.embedding,
            created_at=question.created_at,
            updated_at=question.updated_at,
        )


def _coerce_embedding(value: object) -> list[float] | None:
    """Normalize HalfVector / Vector / JSON / numpy results into list[float] | None."""
    if value is None:
        return None
    if isinstance(value, list):
        return [float(v) for v in value]

    # Handle pgvector/numpy objects that might have to_list, tolist, or are iterable
    for method in ("to_list", "tolist"):
        if hasattr(value, method):
            return [float(v) for v in getattr(value, method)()]

    try:
        return [float(v) for v in value]  # type: ignore
    except (TypeError, ValueError):
        return None
