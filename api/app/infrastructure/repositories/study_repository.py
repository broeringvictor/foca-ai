from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.study import Study
from app.domain.enums.law_area import LawArea
from app.domain.value_objects.sm2_progress import Sm2Progress
from app.infrastructure.model.study_model import StudyModel


class StudyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, study: Study) -> None:
        model = self._to_model(study)
        self._session.add(model)

    async def update(self, study: Study) -> None:
        model = await self._session.get(StudyModel, study.id)
        if model is None:
            return
        model.review_progress = study.review_progress.model_dump(mode='json')
        model.updated_at = study.updated_at

    async def find_by_user_and_area(self, user_id: UUID, area: LawArea) -> Study | None:
        stmt = select(StudyModel).where(
            StudyModel.user_id == user_id,
            StudyModel.area == area.value
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_all_by_user_id(self, user_id: UUID) -> list[Study]:
        stmt = select(StudyModel).where(StudyModel.user_id == user_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def find_due_by_user_id(self, user_id: UUID) -> list[Study]:
        today = datetime.now(timezone.utc).date()
        # Filtro direto no banco via JSONB extraction para usar o índice funcional
        stmt = (
            select(StudyModel)
            .where(
                StudyModel.user_id == user_id,
                StudyModel.review_progress["next_review_date"].astext <= today.isoformat()
            )
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    @staticmethod
    def _to_entity(model: StudyModel) -> Study:
        return Study(
            id=model.id,
            user_id=model.user_id,
            area=LawArea(model.area),
            review_progress=Sm2Progress.model_validate(model.review_progress),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(study: Study) -> StudyModel:
        return StudyModel(
            id=study.id,
            user_id=study.user_id,
            area=study.area.value,
            review_progress=study.review_progress.model_dump(mode='json'),
            created_at=study.created_at,
            updated_at=study.updated_at,
        )
