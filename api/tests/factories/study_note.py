from datetime import UTC, datetime
from uuid import uuid8

import factory as factory_boy
from faker import Faker

from app.domain.entities.study_note import StudyNote
from app.domain.enums.law_area import LawArea
from app.infrastructure.model.study_note_model import StudyNoteModel

_faker = Faker("pt_BR")


class StudyNoteFactory(factory_boy.Factory):
    class Meta:
        model = StudyNoteModel

    user_id = factory_boy.LazyFunction(uuid8)
    area = LawArea.ETHICS
    title = factory_boy.LazyFunction(lambda: (_faker.sentence(nb_words=4).strip(". ") or "Resumo")[:100])
    description = factory_boy.LazyFunction(lambda: (_faker.sentence(nb_words=8).strip() or "Descricao")[:200])
    content = factory_boy.LazyFunction(lambda: f"# {_faker.word()}\n\n{_faker.text(max_nb_chars=200)}")
    tags = factory_boy.LazyFunction(lambda: ["estudo", "revisao"])

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        area = kwargs.pop("area", LawArea.ETHICS)
        note = StudyNote.create(
            user_id=kwargs.pop("user_id", uuid8()),
            area=area,
            title=kwargs.pop("title", (_faker.sentence(nb_words=4).strip(". ") or "Resumo")[:100]),
            description=kwargs.pop("description", (_faker.sentence(nb_words=8).strip() or "Descricao")[:200]),
            content=kwargs.pop("content", f"# {_faker.word()}\n\n{_faker.text(max_nb_chars=200)}"),
            tags=kwargs.pop("tags", ["estudo", "revisao"]),
        )

        created_at = kwargs.pop("created_at", note.created_at)
        updated_at = kwargs.pop("updated_at", datetime.now(UTC))
        review_progress = kwargs.pop("review_progress", note.review_progress.model_dump(mode='json'))

        return model_class(
            id=kwargs.pop("id", note.id),
            user_id=note.user_id,
            area=note.area.value,
            title=note.title,
            description=note.description,
            content=note.content,
            tags=list(note.tags),
            created_at=created_at,
            updated_at=updated_at,
            review_progress=review_progress
        )

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._build(model_class, *args, **kwargs)
