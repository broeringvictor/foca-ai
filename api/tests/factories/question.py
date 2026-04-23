from uuid import uuid8
import factory as factory_boy
from faker import Faker
from app.domain.entities.question import Question
from app.domain.enums.law_area import LawArea
from app.domain.enums.alternatives import Alternative
from app.infrastructure.model.question_model import QuestionModel

_faker = Faker("pt_BR")

class QuestionFactory(factory_boy.Factory):
    class Meta:
        model = QuestionModel

    id = factory_boy.LazyFunction(uuid8)
    exam_id = factory_boy.LazyFunction(uuid8)
    statement = factory_boy.LazyFunction(lambda: _faker.text(max_nb_chars=500))
    area = LawArea.CIVIL
    correct = Alternative.A
    alternative_a = factory_boy.LazyFunction(lambda: _faker.sentence())
    alternative_b = factory_boy.LazyFunction(lambda: _faker.sentence())
    alternative_c = factory_boy.LazyFunction(lambda: _faker.sentence())
    alternative_d = factory_boy.LazyFunction(lambda: _faker.sentence())

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        # We need to use the domain entity to ensure validation if needed, 
        # but here we can just map to the model
        return model_class(
            id=kwargs.pop("id", uuid8()),
            exam_id=kwargs.pop("exam_id", uuid8()),
            statement=kwargs.pop("statement", _faker.text(max_nb_chars=500)),
            area=kwargs.pop("area", LawArea.CIVIL).value,
            correct=kwargs.pop("correct", Alternative.A).value,
            alternative_a=kwargs.pop("alternative_a", _faker.sentence()),
            alternative_b=kwargs.pop("alternative_b", _faker.sentence()),
            alternative_c=kwargs.pop("alternative_c", _faker.sentence()),
            alternative_d=kwargs.pop("alternative_d", _faker.sentence()),
            number=kwargs.pop("number", 1),
            confidence=kwargs.pop("confidence", 1.0),
            source=kwargs.pop("source", "initial"),
            embedding=kwargs.pop("embedding", None)
        )

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._build(model_class, *args, **kwargs)
