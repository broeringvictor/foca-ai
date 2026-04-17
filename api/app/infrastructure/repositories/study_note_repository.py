from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app.domain.entities.study_note import StudyNote
from app.infrastructure.model.study_note_model import StudyNoteModel


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
        stmt = (
            select(StudyNoteModel)
            .options(
                load_only(
                    StudyNoteModel.id,
                    StudyNoteModel.user_id,
                    StudyNoteModel.title,
                    StudyNoteModel.description,
                    StudyNoteModel.created_at,
                    StudyNoteModel.updated_at,
                )
            )
            .where(StudyNoteModel.user_id == user_id)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

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
            created_at=study_note.created_at,
            updated_at=study_note.updated_at,
        )
