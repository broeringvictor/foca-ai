from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.exam import Exam
from app.infrastructure.model.exam_model import ExamModel


class ExamRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── persistência ──────────────────────────────────────────────────────────

    async def save(self, exam: Exam) -> None:
        model = self._to_model(exam)
        self._session.add(model)

    async def update(self, exam: Exam) -> None:
        model = await self._session.get(ExamModel, exam.id)
        if model is None:
            return

        model.name = exam.name
        model.edition = exam.edition
        model.year = exam.year
        model.board = exam.board
        model.first_phase_date = exam.first_phase_date
        model.second_phase_date = exam.second_phase_date
        model.updated_at = exam.updated_at

    async def delete(self, exam_id: UUID) -> None:
        stmt = delete(ExamModel).where(ExamModel.id == exam_id)
        await self._session.execute(stmt)

    # ── busca ─────────────────────────────────────────────────────────────────

    async def find_by_id(self, exam_id: UUID) -> Exam | None:
        stmt = select(ExamModel).where(ExamModel.id == exam_id)
        result = await self._session.execute(stmt)
        model: ExamModel | None = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def find_all(self) -> list[Exam]:
        stmt = select(ExamModel)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    # ── mapeamento ────────────────────────────────────────────────────────────

    @staticmethod
    def _to_entity(model: ExamModel) -> Exam:
        return Exam(
            id=model.id,
            name=model.name,
            edition=model.edition,
            year=model.year,
            board=model.board,
            first_phase_date=model.first_phase_date,
            second_phase_date=model.second_phase_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(exam: Exam) -> ExamModel:
        return ExamModel(
            id=exam.id,
            name=exam.name,
            edition=exam.edition,
            year=exam.year,
            board=exam.board,
            first_phase_date=exam.first_phase_date,
            second_phase_date=exam.second_phase_date,
            created_at=exam.created_at,
            updated_at=exam.updated_at,
        )
