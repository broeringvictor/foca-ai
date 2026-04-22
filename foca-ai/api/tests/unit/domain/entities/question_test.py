from uuid import UUID, uuid8

import pytest
from pydantic import ValidationError

from app.domain.entities.question import Question
from app.domain.enums.alternatives import Alternative
from app.domain.enums.law_area import LawArea


def _exam_id() -> UUID:
    return uuid8()


class TestCreateQuestion:
    def test_creates_with_all_fields(self):
        exam_id = _exam_id()
        question = Question.create(
            exam_id=exam_id,
            number=1,
            statement="Qual a cor do cavalo branco de Napoleão?",
            area=LawArea.ETHICS,
            correct=Alternative.A,
            alternative_a="Branco",
            alternative_b="Preto",
            alternative_c="Marrom",
            alternative_d="Cinza",
            tags=["história", "curiosidades"],
        )

        assert question.exam_id == exam_id
        assert question.statement == "Qual a cor do cavalo branco de Napoleão?"
        assert question.area == LawArea.ETHICS
        assert question.correct == Alternative.A
        assert question.alternative_a == "Branco"
        assert question.alternative_b == "Preto"
        assert question.alternative_c == "Marrom"
        assert question.alternative_d == "Cinza"
        assert question.tags == ["história", "curiosidades"]

    def test_creates_with_only_required_fields(self):
        question = Question.create(
            exam_id=_exam_id(),
            number=1,
            statement="Enunciado de teste",
            area=LawArea.CONSTITUTIONAL,
            correct=Alternative.B,
            alternative_a="Alt A",
            alternative_b="Alt B",
            alternative_c="Alt C",
            alternative_d="Alt D",
        )

        assert question.tags == []

    def test_tags_none_becomes_empty_list(self):
        question = Question.create(
            exam_id=_exam_id(),
            number=1,
            statement="Enunciado de teste",
            area=LawArea.CONSTITUTIONAL,
            correct=Alternative.B,
            alternative_a="Alt A",
            alternative_b="Alt B",
            alternative_c="Alt C",
            alternative_d="Alt D",
            tags=None,
        )

        assert question.tags == []


class TestQuestionValidation:
    def test_statement_too_short_raises(self):
        with pytest.raises(ValidationError):
            Question.create(
                exam_id=_exam_id(),
            number=1,
                statement="abc",
                area=LawArea.ETHICS,
                correct=Alternative.A,
                alternative_a="A",
                alternative_b="B",
                alternative_c="C",
                alternative_d="D",
            )

    def test_statement_too_long_raises(self):
        with pytest.raises(ValidationError):
            Question.create(
                exam_id=_exam_id(),
            number=1,
                statement="a" * 1501,
                area=LawArea.ETHICS,
                correct=Alternative.A,
                alternative_a="A",
                alternative_b="B",
                alternative_c="C",
                alternative_d="D",
            )

    def test_alternative_too_long_raises(self):
        with pytest.raises(ValidationError):
            Question.create(
                exam_id=_exam_id(),
            number=1,
                statement="Pergunta?",
                area=LawArea.ETHICS,
                correct=Alternative.A,
                alternative_a="a" * 1001,
                alternative_b="B",
                alternative_c="C",
                alternative_d="D",
            )

    def test_invalid_exam_id_raises(self):
        with pytest.raises(ValidationError):
            Question.create(
                exam_id="not-a-uuid",
                number=1,
                statement="Pergunta?",
                area=LawArea.ETHICS,
                correct=Alternative.A,
                alternative_a="A",
                alternative_b="B",
                alternative_c="C",
                alternative_d="D",
            )

