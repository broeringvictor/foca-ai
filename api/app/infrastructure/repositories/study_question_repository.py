from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.study_question import StudyQuestion
from app.domain.value_objects.sm2_progress import Sm2Progress
from app.infrastructure.model.study_question_model import StudyQuestionModel


class StudyQuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, study_question: StudyQuestion) -> None:
        model = self._to_model(study_question)
        self._session.add(model)

    async def update(self, study_question: StudyQuestion) -> None:
        model = await self._session.get(StudyQuestionModel, study_question.id)
        if model is None:
            return
        model.review_progress = study_question.review_progress.model_dump(mode='json')
        model.updated_at = study_question.updated_at

    async def find_by_user_and_question(self, user_id: UUID, question_id: UUID) -> StudyQuestion | None:
        stmt = select(StudyQuestionModel).where(
            StudyQuestionModel.user_id == user_id,
            StudyQuestionModel.question_id == question_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_all_by_user_id(self, user_id: UUID) -> list[StudyQuestion]:
        stmt = select(StudyQuestionModel).where(StudyQuestionModel.user_id == user_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def find_due_by_user_id(self, user_id: UUID, limit: int = 20) -> list[StudyQuestion]:
        from datetime import date
        today = date.today()
        
        stmt = (
            select(StudyQuestionModel)
            .where(
                StudyQuestionModel.user_id == user_id,
                StudyQuestionModel.review_progress["next_review_date"].astext <= today.isoformat()
            )
            .order_by(StudyQuestionModel.review_progress["next_review_date"].astext.asc())
            .limit(limit)
        )
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def find_high_error_by_user_id(self, user_id: UUID, limit: int = 10) -> list[StudyQuestion]:
        import sqlalchemy as sa
        # Ordenar por maior número de erros (wrong_count dentro do JSONB)
        stmt = (
            select(StudyQuestionModel)
            .where(StudyQuestionModel.user_id == user_id)
            .order_by(sa.cast(StudyQuestionModel.review_progress["wrong_count"].astext, sa.Integer).desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_entity(model: StudyQuestionModel) -> StudyQuestion:
        return StudyQuestion(
            id=model.id,
            user_id=model.user_id,
            question_id=model.question_id,
            review_progress=Sm2Progress.model_validate(model.review_progress),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(study_question: StudyQuestion) -> StudyQuestionModel:
        return StudyQuestionModel(
            id=study_question.id,
            user_id=study_question.user_id,
            question_id=study_question.question_id,
            review_progress=study_question.review_progress.model_dump(mode='json'),
            created_at=study_question.created_at,
            updated_at=study_question.updated_at,
        )
