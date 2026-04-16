from datetime import datetime
from uuid import UUID, uuid8

import pytest
from pydantic import ValidationError

from app.domain.entities.study_note import StudyNote


def _user_id() -> UUID:
    return uuid8()


class TestCreateStudyNote:
    def test_creates_with_all_fields(self):
        user_id = _user_id()
        note = StudyNote.create(
            user_id=user_id,
            title="Minhas anotações",
            description="Descrição de estudo",
            content="Conteúdo completo",
            tags=["python", "fastapi"],
        )

        assert note.user_id == user_id
        assert note.title == "Minhas anotações"
        assert note.description == "Descrição de estudo"
        assert note.content == "Conteúdo completo"
        assert note.tags == ["python", "fastapi"]

    def test_creates_with_only_required_fields(self):
        note = StudyNote.create(
            user_id=_user_id(),
            title="Apenas título",
        )

        assert note.description is None
        assert note.content is None
        assert note.tags == []

    def test_creates_with_description_only(self):
        note = StudyNote.create(
            user_id=_user_id(),
            title="Título",
            description="Só descrição",
        )

        assert note.description == "Só descrição"
        assert note.content is None
        assert note.tags == []

    def test_creates_with_content_only(self):
        note = StudyNote.create(
            user_id=_user_id(),
            title="Título",
            content="Só conteúdo",
        )

        assert note.content == "Só conteúdo"
        assert note.description is None
        assert note.tags == []

    def test_creates_with_tags_only(self):
        note = StudyNote.create(
            user_id=_user_id(),
            title="Título",
            tags=["tag1", "tag2"],
        )

        assert note.tags == ["tag1", "tag2"]
        assert note.description is None
        assert note.content is None

    def test_tags_none_becomes_empty_list(self):
        note = StudyNote.create(
            user_id=_user_id(),
            title="Título",
            tags=None,
        )

        assert note.tags == []


class TestStudyNoteDefaults:
    def test_generates_id_automatically(self):
        note = StudyNote.create(user_id=_user_id(), title="Título")

        assert isinstance(note.id, UUID)

    def test_each_note_has_unique_id(self):
        note_a = StudyNote.create(user_id=_user_id(), title="Título A")
        note_b = StudyNote.create(user_id=_user_id(), title="Título B")

        assert note_a.id != note_b.id

    def test_sets_created_at_and_updated_at(self):
        note = StudyNote.create(user_id=_user_id(), title="Título")

        assert isinstance(note.created_at, datetime)
        assert isinstance(note.updated_at, datetime)


class TestStudyNoteTitleValidation:
    def test_title_too_short_raises(self):
        with pytest.raises(ValidationError):
            StudyNote.create(user_id=_user_id(), title="abc")

    def test_title_too_long_raises(self):
        with pytest.raises(ValidationError):
            StudyNote.create(user_id=_user_id(), title="a" * 101)

    def test_title_at_min_length_is_valid(self):
        note = StudyNote.create(user_id=_user_id(), title="abcd")
        assert note.title == "abcd"

    def test_title_at_max_length_is_valid(self):
        title = "a" * 100
        note = StudyNote.create(user_id=_user_id(), title=title)
        assert note.title == title


class TestStudyNoteDescriptionValidation:
    def test_description_too_short_raises(self):
        with pytest.raises(ValidationError):
            StudyNote.create(
                user_id=_user_id(),
                title="Título",
                description="abc",
            )

    def test_description_too_long_raises(self):
        with pytest.raises(ValidationError):
            StudyNote.create(
                user_id=_user_id(),
                title="Título",
                description="a" * 501,
            )

    def test_description_at_max_length_is_valid(self):
        description = "a" * 500
        note = StudyNote.create(
            user_id=_user_id(),
            title="Título",
            description=description,
        )
        assert note.description == description


class TestStudyNoteContentValidation:
    def test_content_too_long_raises(self):
        with pytest.raises(ValidationError):
            StudyNote.create(
                user_id=_user_id(),
                title="Título",
                content="a" * 5001,
            )

    def test_content_at_max_length_is_valid(self):
        content = "a" * 5000
        note = StudyNote.create(
            user_id=_user_id(),
            title="Título",
            content=content,
        )
        assert note.content == content

    def test_empty_content_is_valid(self):
        note = StudyNote.create(
            user_id=_user_id(),
            title="Título",
            content="",
        )
        assert note.content == ""


class TestStudyNoteUserIdValidation:
    def test_invalid_user_id_raises(self):
        with pytest.raises(ValidationError):
            StudyNote.create(user_id="not-a-uuid", title="Título")

    def test_missing_user_id_raises(self):
        with pytest.raises(ValidationError):
            StudyNote(title="Título")  # type: ignore[call-arg]
