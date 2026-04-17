import json
from uuid import uuid8

from langchain_core.language_models import BaseChatModel
from loguru import logger

from app.domain.entities.question import Question
from app.domain.enums.alternatives import Alternative
from app.domain.enums.law_area import LawArea
from app.domain.services.question_categorization_service import (
    IQuestionCategorizationService,
)
from app.domain.value_objects.classified_question import (
    ClassifiedQuestion,
    DistributionSnapshot,
)
from app.domain.value_objects.raw_exam import RawExam, RawQuestion
from app.infrastructure.services.categorization.distribution import build_snapshot
from app.infrastructure.services.categorization.prompts import (
    CLASSIFY_PROMPT,
    REVIEW_PROMPT,
)
from app.infrastructure.services.categorization.schemas import ClassificationBatch


class QuestionCategorizationService(IQuestionCategorizationService):
    """Pipeline deterministico: classifica em batches -> snapshot -> revisa desequilibrios."""

    INITIAL_BATCH_SIZE = 6
    REVIEW_BATCH_SIZE = 6
    LOW_CONFIDENCE_THRESHOLD = 0.65
    MAX_REVIEW_CANDIDATES = 18

    def __init__(self, llm: BaseChatModel) -> None:
        self._structured_llm = llm.with_structured_output(ClassificationBatch)

    def classify(self, raw_exam: RawExam) -> list[Question]:
        if not raw_exam.questions:
            logger.info("categorization: no_questions edition={}", raw_exam.edition)
            return []

        logger.info(
            "categorization: start edition={} type={} color={} total={}",
            raw_exam.edition,
            raw_exam.exam_type,
            raw_exam.color,
            len(raw_exam.questions),
        )

        assignments = self._initial_classification(raw_exam)
        snapshot = build_snapshot(assignments.values())
        logger.info(
            "categorization: initial_done excess={} deficit={}",
            [area.value for area in snapshot.excess_areas],
            [area.value for area in snapshot.deficit_areas],
        )

        if snapshot.excess_areas and snapshot.deficit_areas:
            assignments = self._review_imbalances(raw_exam, assignments, snapshot)
            snapshot = build_snapshot(assignments.values())
            logger.info(
                "categorization: post_review excess={} deficit={}",
                [area.value for area in snapshot.excess_areas],
                [area.value for area in snapshot.deficit_areas],
            )

        questions = self._build_questions(raw_exam, assignments)
        logger.info("categorization: done questions={}", len(questions))
        return questions

    def _initial_classification(
        self, raw_exam: RawExam
    ) -> dict[int, ClassifiedQuestion]:
        sorted_questions = sorted(raw_exam.questions, key=lambda q: q.number)
        assignments: dict[int, ClassifiedQuestion] = {}

        classify_chain = CLASSIFY_PROMPT | self._structured_llm

        for offset in range(0, len(sorted_questions), self.INITIAL_BATCH_SIZE):
            batch = sorted_questions[offset : offset + self.INITIAL_BATCH_SIZE]
            payload = [self._to_payload(q) for q in batch]

            try:
                batch_result = classify_chain.invoke({
                    "questions_json": json.dumps(payload, ensure_ascii=False)
                })
            except Exception as exc:
                logger.warning("categorization: classify_chain_failed error={}", exc)
                batch_result = ClassificationBatch(results=[])

            for item in getattr(batch_result, 'results', []):
                assignments[item.question_number] = ClassifiedQuestion(
                    number=item.question_number,
                    area=item.area,
                    confidence=item.confidence,
                    source="initial",
                )

        missing = [q.number for q in sorted_questions if q.number not in assignments]
        if missing:
            logger.warning("categorization: initial_missing={}", missing)

        return assignments

    def _review_imbalances(
        self,
        raw_exam: RawExam,
        assignments: dict[int, ClassifiedQuestion],
        snapshot: DistributionSnapshot,
    ) -> dict[int, ClassifiedQuestion]:
        review_numbers = self._select_review_candidates(assignments, snapshot)
        if not review_numbers:
            return assignments

        logger.info("categorization.review: candidates={}", review_numbers)

        by_number = {q.number: q for q in raw_exam.questions}
        to_review = [by_number[number] for number in review_numbers if number in by_number]

        distribution_summary = ", ".join(
            f"{area.value}={count}"
            for area, count in sorted(
                snapshot.counts_by_area.items(), key=lambda kv: -kv[1]
            )
        )
        excess_names = [area.value for area in snapshot.excess_areas]
        deficit_names = [area.value for area in snapshot.deficit_areas]

        review_chain = REVIEW_PROMPT | self._structured_llm

        for offset in range(0, len(to_review), self.REVIEW_BATCH_SIZE):
            batch = to_review[offset : offset + self.REVIEW_BATCH_SIZE]
            payload = [
                {
                    **self._to_payload(raw),
                    "current_area": assignments[raw.number].area.value,
                    "current_confidence": round(
                        assignments[raw.number].confidence, 2
                    ),
                }
                for raw in batch
            ]

            try:
                batch_result = review_chain.invoke({
                    "distribution_summary": distribution_summary,
                    "excess_areas": str(excess_names),
                    "deficit_areas": str(deficit_names),
                    "questions_json": json.dumps(payload, ensure_ascii=False)
                })
            except Exception as exc:
                logger.warning("categorization: review_chain_failed error={}", exc)
                batch_result = ClassificationBatch(results=[])

            for item in getattr(batch_result, 'results', []):
                if item.question_number not in by_number:
                    continue
                assignments[item.question_number] = ClassifiedQuestion(
                    number=item.question_number,
                    area=item.area,
                    confidence=item.confidence,
                    source="review",
                )

        return assignments

    def _select_review_candidates(
        self,
        assignments: dict[int, ClassifiedQuestion],
        snapshot: DistributionSnapshot,
    ) -> list[int]:
        excess_set = set(snapshot.excess_areas)
        candidates = [
            item
            for item in assignments.values()
            if item.area in excess_set
            or item.confidence < self.LOW_CONFIDENCE_THRESHOLD
        ]
        candidates.sort(key=lambda item: item.confidence)
        return [item.number for item in candidates[: self.MAX_REVIEW_CANDIDATES]]

    def _build_questions(
        self,
        raw_exam: RawExam,
        assignments: dict[int, ClassifiedQuestion],
    ) -> list[Question]:
        exam_id = uuid8()
        result: list[Question] = []

        for raw in sorted(raw_exam.questions, key=lambda q: q.number):
            data = assignments.get(raw.number)
            if data is None:
                area = LawArea.CIVIL
                confidence = 0.0
                source = "unclassified"
            else:
                area = data.area
                confidence = data.confidence
                source = data.source

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

    @staticmethod
    def _to_payload(raw: RawQuestion) -> dict:
        return {
            "number": raw.number,
            "statement": raw.statement,
            "alternative_a": raw.alternative_a,
            "alternative_b": raw.alternative_b,
            "alternative_c": raw.alternative_c,
            "alternative_d": raw.alternative_d,
        }
