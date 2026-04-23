from datetime import UTC, datetime

import pytest

from app.domain.entities.study_note import StudyNote
from app.domain.enums.law_area import LawArea
from app.infrastructure.repositories.study_note_repository import StudyNoteRepository
from tests.factories.study_note import StudyNoteFactory


class TestStudyNoteRepository:
    @pytest.mark.asyncio
    async def test_save_and_find_by_id(self, session, user_on_db):
        repo = StudyNoteRepository(session)
        note = StudyNote.create(
            user_id=user_on_db.id,
            area=LawArea.CONSTITUTIONAL,
            title="Resumo de Constitucional",
            description="Pontos sobre controle de constitucionalidade",
            content="# Resumo\n\nConteudo",
            tags=["constitucional", "revisao"],
        )

        await repo.save(note)
        await session.commit()

        saved = await repo.find_by_id(note.id)

        assert saved is not None
        assert saved.id == note.id
        assert saved.area == LawArea.CONSTITUTIONAL
        assert saved.title == "Resumo de Constitucional"
        assert saved.tags == ["constitucional", "revisao"]

    @pytest.mark.asyncio
    async def test_update_persists_changes(self, session, user_on_db):
        repo = StudyNoteRepository(session)
        model = StudyNoteFactory.build(
            user_id=user_on_db.id,
            area=LawArea.CIVIL.value,
            title="Titulo antigo",
            description="Descricao antiga",
            tags=["antiga"],
        )
        session.add(model)
        await session.commit()

        note = await repo.find_by_id(model.id)
        assert note is not None

        updated_at = datetime.now(UTC)
        updated = note.model_copy(
            update={
                "title": "Titulo novo",
                "description": "Descricao nova",
                "content": "Conteudo novo",
                "tags": ["nova", "atualizada"],
                "updated_at": updated_at,
            }
        )

        await repo.update(updated)
        await session.commit()

        persisted = await repo.find_by_id(model.id)
        assert persisted is not None
        assert persisted.title == "Titulo novo"
        assert persisted.description == "Descricao nova"
        assert persisted.content == "Conteudo novo"
        assert persisted.tags == ["nova", "atualizada"]
        assert persisted.updated_at == updated_at

    @pytest.mark.asyncio
    async def test_find_summaries_returns_embedding_flag(self, session, user_on_db):
        repo = StudyNoteRepository(session)
        without_embedding = StudyNoteFactory.build(user_id=user_on_db.id, title="Sem embedding")
        with_embedding = StudyNoteFactory.build(user_id=user_on_db.id, title="Com embedding")

        session.add(without_embedding)
        session.add(with_embedding)
        await session.commit()

        await repo.update_embedding(with_embedding.id, [0.2] * 3072)
        await session.commit()

        summaries = await repo.find_summaries_by_user_id(user_on_db.id)
        by_id = {note_id: has_embedding for note_id, _, has_embedding in summaries}

        assert by_id[without_embedding.id] is False
        assert by_id[with_embedding.id] is True

    @pytest.mark.asyncio
    async def test_delete_removes_study_note(self, session, user_on_db):
        repo = StudyNoteRepository(session)
        model = StudyNoteFactory.build(user_id=user_on_db.id)
        session.add(model)
        await session.commit()

        await repo.delete(model.id)
        await session.commit()

        deleted = await repo.find_by_id(model.id)
        assert deleted is None
