from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app.domain.entities.study_note import StudyNote
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
            title=model.title,
            description=model.description,
            content=model.content,
            tags=model.tags,
            embedding=_coerce_embedding(model.embedding),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(study_note: StudyNote) -> StudyNoteModel:
        return StudyNoteModel(
            id=study_note.id,
            user_id=study_note.user_id,
            title=study_note.title,
            description=study_note.description,
            content=study_note.content,
            tags=study_note.tags,
            embedding=study_note.embedding,
            created_at=study_note.created_at,
            updated_at=study_note.updated_at,
        )
