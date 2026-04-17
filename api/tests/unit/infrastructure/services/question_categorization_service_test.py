import json

from app.domain.enums.law_area import LawArea
from app.domain.value_objects.raw_exam import RawExam, RawQuestion
from app.infrastructure.services.question_categorization_service import (
    QuestionCategorizationService,
)


class _FakeResponse:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeLLM:
    def __init__(self, responses: list[str] | None = None, default: str = "[]") -> None:
        self._responses = responses or []
        self._default = default
        self.prompts: list[str] = []

    def invoke(self, input, **kwargs):
        self.prompts.append(str(input))
        if self._responses:
            return _FakeResponse(self._responses.pop(0))
        return _FakeResponse(self._default)


def _make_raw_exam() -> RawExam:
    return RawExam(
        edition=45,
        name="45 EXAME DE ORDEM UNIFICADO",
        exam_type=1,
        color="BRANCA",
        questions=[
            RawQuestion(
                number=1,
                statement="Questao 1 de direito civil.",
                alternative_a="A1",
                alternative_b="B1",
                alternative_c="C1",
                alternative_d="D1",
            ),
            RawQuestion(
                number=2,
                statement="Questao 2 de direito penal.",
                alternative_a="A2",
                alternative_b="B2",
                alternative_c="C2",
                alternative_d="D2",
            ),
            RawQuestion(
                number=3,
                statement="Questao 3 de direito do trabalho.",
                alternative_a="A3",
                alternative_b="B3",
                alternative_c="C3",
                alternative_d="D3",
            ),
        ],
    )


class TestQuestionCategorizationService:
    def test_review_tool_uses_only_selected_numbers(self):
        fake_llm = _FakeLLM(
            responses=[
                json.dumps(
                    [
                        {"question_number": 2, "area": "criminal", "confidence": 0.9},
                        {"question_number": 1, "area": "civil", "confidence": 0.8},
                    ]
                )
            ]
        )
        service = QuestionCategorizationService(llm=fake_llm)
        raw_exam = _make_raw_exam()
        report = {
            "counts": {},
            "z_scores": {LawArea.CIVIL: 2.5},
            "distorted_areas": [LawArea.CIVIL],
            "deficits": [LawArea.CRIMINAL],
        }

        reviewed = service._review_numbers_tool(raw_exam, [2], report)

        assert list(reviewed.keys()) == [2]
        assert reviewed[2]["area"] == LawArea.CRIMINAL

        prompt = fake_llm.prompts[0]
        assert '"number": 2' in prompt
        assert '"number": 1' not in prompt

    def test_classify_returns_all_questions_with_fallback(self):
        fake_llm = _FakeLLM(default="not-json")
        service = QuestionCategorizationService(llm=fake_llm)

        result = service.classify(_make_raw_exam())

        assert len(result) == 3
        assert all(question.area == LawArea.CIVIL for question in result)
        assert all(any(tag.startswith("source:") for tag in question.tags) for question in result)

