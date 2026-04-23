from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.study_note import StudyNote
from app.domain.enums.law_area import LawArea
from app.domain.value_objects.sm2_progress import Sm2Progress
from app.infrastructure.model.study_note_model import StudyNoteModel


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


class StudyNoteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── persistência ──────────────────────────────────────────────────────────

    async def save(self, study_note: StudyNote) -> None:
        model = self._to_model(study_note)
        self._session.add(model)

    async def update(self, study_note: StudyNote) -> None:
        model = await self._session.get(StudyNoteModel, study_note.id)
        if model is None:
            return
        model.title = study_note.title
        model.description = study_note.description
        model.content = study_note.content
        model.tags = list(study_note.tags)
        model.embedding = study_note.embedding
        model.questions = [str(qid) for qid in study_note.questions]
        model.review_progress = study_note.review_progress.model_dump(mode='json')
        model.updated_at = study_note.updated_at

    async def update_embedding(self, study_note_id: UUID, embedding: list[float]) -> None:
        model = await self._session.get(StudyNoteModel, study_note_id)
        if model is None:
            return
        model.embedding = embedding

    async def delete(self, study_note_id: UUID) -> None:
        from sqlalchemy import delete as sa_delete
        stmt = sa_delete(StudyNoteModel).where(StudyNoteModel.id == study_note_id)
        await self._session.execute(stmt)

    # ── busca ──────────────────────────────────────────────────────────────────

    async def find_by_id(self, study_note_id: UUID) -> StudyNote | None:
        stmt = select(StudyNoteModel).where(StudyNoteModel.id == study_note_id)
        result = await self._session.execute(stmt)
        model: StudyNoteModel | None = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def find_all_by_user_id(self, user_id: UUID) -> list[StudyNote]:
        # Carregamos todos os campos necessários para a entidade StudyNote
        stmt = (
            select(StudyNoteModel)
            .where(StudyNoteModel.user_id == user_id)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def find_due_by_user_id(self, user_id: UUID) -> list[StudyNote]:
        today = datetime.now(timezone.utc).date()
        
        # Filtra por user_id e next_review_date <= hoje
        stmt = (
            select(StudyNoteModel)
            .where(
                StudyNoteModel.user_id == user_id,
                cast(StudyNoteModel.review_progress["next_review_date"].astext, Date) <= today
            )
        )
        
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def find_summaries_by_user_id(self, user_id: UUID) -> list[tuple[UUID, str, bool]]:
        notes = await self.find_all_by_user_id(user_id)
        return [
            (note.id, note.title, note.embedding is not None)
            for note in notes
        ]

    async def find_by_embedding_similarity(
        self,
        user_id: UUID,
        query_vector: list[float],
        limit: int,
    ) -> list[tuple[StudyNote, float]]:
        distance_expr = StudyNoteModel.embedding.cosine_distance(query_vector)
        # Removido load_only para evitar erro de lazy loading em sessão assíncrona
        stmt = (
            select(StudyNoteModel, distance_expr.label("distance"))
            .where(
                StudyNoteModel.user_id == user_id,
                StudyNoteModel.embedding.is_not(None),
            )
            .order_by(distance_expr)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        rows = result.all()
        return [(self._to_entity(model), 1.0 - float(distance)) for model, distance in rows]

    # ── mapeamento ────────────────────────────────────────────────────────────

    @staticmethod
    def _to_entity(model: StudyNoteModel) -> StudyNote:
        return StudyNote(
            id=model.id,
            user_id=model.user_id,
            area=LawArea(model.area),
            title=model.title,
            description=model.description,
            content=model.content,
            tags=model.tags,
            embedding=_coerce_embedding(model.embedding),
            questions=[UUID(qid) for qid in (model.questions or [])],
            review_progress=Sm2Progress.model_validate(model.review_progress),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(study_note: StudyNote) -> StudyNoteModel:
        return StudyNoteModel(
            id=study_note.id,
            user_id=study_note.user_id,
            area=study_note.area.value,
            title=study_note.title,
            description=study_note.description,
            content=study_note.content,
            tags=study_note.tags,
            embedding=study_note.embedding,
            questions=[str(qid) for qid in study_note.questions],
            review_progress=study_note.review_progress.model_dump(mode='json'),
            created_at=study_note.created_at,
            updated_at=study_note.updated_at,
        )
