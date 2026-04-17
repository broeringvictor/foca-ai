import json
import math
from collections import Counter
from uuid import uuid8

from app.domain.entities.question import Question
from app.domain.enums.alternatives import Alternative
from app.domain.enums.law_area import LawArea
from app.domain.services.question_categorization_service import (
    IChatModel,
    IQuestionCategorizationService,
)
from app.domain.value_objects.raw_exam import RawExam, RawQuestion


class QuestionCategorizationService(IQuestionCategorizationService):
    INITIAL_BATCH_SIZE = 12
    REVIEW_BATCH_SIZE = 6
    MAX_REVIEW_CYCLES = 2
    Z_THRESHOLD = 2.0

    # Weights are normalized at runtime to model a prior OAB distribution.
    DISTRIBUTION_WEIGHTS = {
        LawArea.ETHICS: 10,
        LawArea.CIVIL: 9,
        LawArea.CONSTITUTIONAL: 8,
        LawArea.CIVIL_PROCEDURE: 8,
        LawArea.CRIMINAL: 8,
        LawArea.CRIMINAL_PROCEDURE: 8,
        LawArea.LABOR: 8,
        LawArea.LABOR_PROCEDURE: 6,
        LawArea.ADMINISTRATIVE: 6,
        LawArea.TAX: 6,
        LawArea.BUSINESS: 5,
        LawArea.CONSUMER: 4,
        LawArea.CHILD_AND_ADOLESCENT: 3,
        LawArea.ENVIRONMENTAL: 3,
        LawArea.INTERNATIONAL: 3,
        LawArea.HUMAN_RIGHTS: 3,
        LawArea.SOCIAL_SECURITY: 3,
        LawArea.FINANCIAL: 3,
        LawArea.PHILOSOPHY_OF_LAW: 2,
    }

    def __init__(self, llm: IChatModel) -> None:
        self.llm = llm

    def classify(self, raw_exam: RawExam) -> list[Question]:
        if not raw_exam.questions:
            return []

        assignments = self._initial_classification(raw_exam)

        for _ in range(self.MAX_REVIEW_CYCLES):
            report = self._distribution_report(assignments)
            if not report["distorted_areas"]:
                break

            review_numbers = self._select_review_numbers(assignments, report)
            if not review_numbers:
                break

            reviewed = self._review_numbers_tool(raw_exam, review_numbers, report)
            assignments.update(reviewed)

        return self._build_questions(raw_exam, assignments)

    def _initial_classification(self, raw_exam: RawExam) -> dict[int, dict]:
        assignments: dict[int, dict] = {}
        all_questions = sorted(raw_exam.questions, key=lambda q: q.number)

        for i in range(0, len(all_questions), self.INITIAL_BATCH_SIZE):
            batch = all_questions[i : i + self.INITIAL_BATCH_SIZE]
            payload = [
                {
                    "number": q.number,
                    "statement": q.statement,
                    "alternative_a": q.alternative_a,
                    "alternative_b": q.alternative_b,
                    "alternative_c": q.alternative_c,
                    "alternative_d": q.alternative_d,
                }
                for q in batch
            ]
            prompt = (
                "Classifique cada questao na area juridica principal da OAB. "
                "Retorne JSON valido no formato: "
                "[{\"question_number\": int, \"area\": str, \"confidence\": float}]. "
                "Use apenas valores de area do enum LawArea em snake_case.\n"
                f"Questoes: {json.dumps(payload, ensure_ascii=False)}"
            )

            parsed = self._invoke_json(prompt)
            for item in parsed:
                number = int(item.get("question_number", 0))
                if not number:
                    continue
                assignments[number] = {
                    "area": self._parse_area(item.get("area")),
                    "confidence": self._parse_confidence(item.get("confidence")),
                    "source": "initial",
                }

        # Fallback guarantees a complete list even with partial/malformed model output.
        for q in all_questions:
            assignments.setdefault(
                q.number,
                {"area": LawArea.CIVIL, "confidence": 0.01, "source": "fallback"},
            )

        return assignments

    def _distribution_report(self, assignments: dict[int, dict]) -> dict:
        counts = Counter(item["area"] for item in assignments.values())
        total = max(len(assignments), 1)

        total_weight = sum(self.DISTRIBUTION_WEIGHTS.values())
        distorted_areas: list[LawArea] = []
        deficits: list[LawArea] = []
        z_scores: dict[LawArea, float] = {}

        for area in LawArea:
            expected_prob = self.DISTRIBUTION_WEIGHTS.get(area, 1) / total_weight
            expected = total * expected_prob
            observed = counts.get(area, 0)
            variance = max(total * expected_prob * (1 - expected_prob), 1e-9)
            z_score = (observed - expected) / math.sqrt(variance)
            z_scores[area] = z_score

            if abs(z_score) > self.Z_THRESHOLD:
                distorted_areas.append(area)
                if z_score < 0:
                    deficits.append(area)

        return {
            "counts": counts,
            "z_scores": z_scores,
            "distorted_areas": distorted_areas,
            "deficits": deficits,
        }

    def _select_review_numbers(self, assignments: dict[int, dict], report: dict) -> list[int]:
        excessive = {
            area for area in report["distorted_areas"] if report["z_scores"][area] > 0
        }
        if not excessive:
            return []

        candidates = [
            (number, data)
            for number, data in assignments.items()
            if data["area"] in excessive or data["confidence"] < 0.65
        ]

        candidates.sort(key=lambda pair: pair[1]["confidence"])
        return [number for number, _ in candidates[: self.REVIEW_BATCH_SIZE * 2]]

    def _review_numbers_tool(
        self,
        raw_exam: RawExam,
        question_numbers: list[int],
        report: dict,
    ) -> dict[int, dict]:
        """Tool coordinator: receives only numbers and resolves full text internally."""
        to_review = self._get_questions_by_numbers(raw_exam, question_numbers)
        if not to_review:
            return {}

        deficits = [area.value for area in report["deficits"]]
        snapshot = {
            area.value: round(report["z_scores"][area], 3)
            for area in report["distorted_areas"]
        }

        reviewed: dict[int, dict] = {}
        for i in range(0, len(to_review), self.REVIEW_BATCH_SIZE):
            batch = to_review[i : i + self.REVIEW_BATCH_SIZE]
            payload = [
                {
                    "number": q.number,
                    "statement": q.statement,
                    "alternative_a": q.alternative_a,
                    "alternative_b": q.alternative_b,
                    "alternative_c": q.alternative_c,
                    "alternative_d": q.alternative_d,
                }
                for q in batch
            ]

            prompt = (
                "Revisor de distribuicao da OAB: voce recebeu APENAS questoes candidatas. "
                "Tente reduzir distorcao de distribuicao sem inventar numero. "
                "Retorne JSON valido: "
                "[{\"question_number\": int, \"area\": str, \"confidence\": float}].\n"
                f"Deficits: {json.dumps(deficits, ensure_ascii=False)}\n"
                f"Snapshot z-scores: {json.dumps(snapshot, ensure_ascii=False)}\n"
                f"Questoes candidatas: {json.dumps(payload, ensure_ascii=False)}"
            )

            parsed = self._invoke_json(prompt)
            for item in parsed:
                number = int(item.get("question_number", 0))
                if number not in question_numbers:
                    continue

                reviewed[number] = {
                    "area": self._parse_area(item.get("area")),
                    "confidence": self._parse_confidence(item.get("confidence")),
                    "source": "review",
                }

        return reviewed

    @staticmethod
    def _get_questions_by_numbers(raw_exam: RawExam, numbers: list[int]) -> list[RawQuestion]:
        allowed = set(numbers)
        return [q for q in raw_exam.questions if q.number in allowed]

    def _build_questions(self, raw_exam: RawExam, assignments: dict[int, dict]) -> list[Question]:
        exam_id = uuid8()
        result: list[Question] = []

        for raw in sorted(raw_exam.questions, key=lambda q: q.number):
            data = assignments.get(raw.number, {})
            confidence = self._parse_confidence(data.get("confidence", 0.01))
            source = str(data.get("source", "fallback"))
            area = data.get("area", LawArea.CIVIL)
            if not isinstance(area, LawArea):
                area = LawArea.CIVIL

            result.append(
                Question.create(
                    exam_id=exam_id,
                    statement=raw.statement[:1500],
                    area=area,
                    correct=Alternative.A,
                    alternative_a=raw.alternative_a[:1000],
                    alternative_b=raw.alternative_b[:1000],
                    alternative_c=raw.alternative_c[:1000],
                    alternative_d=raw.alternative_d[:1000],
                    tags=[
                        "auto-categorized",
                        f"question_number:{raw.number}",
                        f"confidence:{confidence:.2f}",
                        f"source:{source}",
                    ],
                )
            )

        return result

    def _invoke_json(self, prompt: str) -> list[dict]:
        response = self.llm.invoke(prompt)

        if isinstance(response, list):
            return [item for item in response if isinstance(item, dict)]
        if isinstance(response, dict):
            return [response]

        content = getattr(response, "content", response)
        if isinstance(content, list):
            content = "\n".join(str(item) for item in content)

        if not isinstance(content, str):
            return []

        payload = content.strip()
        if payload.startswith("```"):
            payload = payload.strip("`")
            payload = payload.replace("json", "", 1).strip()

        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            return []

        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        if isinstance(parsed, dict):
            return [parsed]
        return []

    @staticmethod
    def _parse_area(value: object) -> LawArea:
        if isinstance(value, LawArea):
            return value

        normalized = str(value or "").strip().lower()
        if not normalized:
            return LawArea.CIVIL

        alias_map = {
            "constitucional": LawArea.CONSTITUTIONAL,
            "direito constitucional": LawArea.CONSTITUTIONAL,
            "etica": LawArea.ETHICS,
            "ética": LawArea.ETHICS,
            "penal": LawArea.CRIMINAL,
            "processo penal": LawArea.CRIMINAL_PROCEDURE,
            "processo civil": LawArea.CIVIL_PROCEDURE,
            "trabalho": LawArea.LABOR,
            "processo do trabalho": LawArea.LABOR_PROCEDURE,
            "empresarial": LawArea.BUSINESS,
            "tributario": LawArea.TAX,
            "tributário": LawArea.TAX,
            "administrativo": LawArea.ADMINISTRATIVE,
        }
        if normalized in alias_map:
            return alias_map[normalized]

        for area in LawArea:
            if normalized == area.value:
                return area

        return LawArea.CIVIL

    @staticmethod
    def _parse_confidence(value: object) -> float:
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return 0.01
        return min(max(parsed, 0.0), 1.0)
