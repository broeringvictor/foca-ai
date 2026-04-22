from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.question import Question
from app.domain.enums.alternatives import Alternative
from app.domain.enums.law_area import LawArea
from app.infrastructure.model.question_model import QuestionModel


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

    async def find_all_by_exam_id(self, exam_id: UUID) -> list[Question]:
        stmt = select(QuestionModel).where(QuestionModel.exam_id == exam_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    # ── mapeamento ────────────────────────────────────────────────────────────

    @staticmethod
    def _to_entity(model: QuestionModel) -> Question:
        return Question(
            id=model.id,
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
            source=model.source,
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
            source=question.source,
            created_at=question.created_at,
            updated_at=question.updated_at,
        )