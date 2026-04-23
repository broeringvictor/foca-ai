import json
from uuid import uuid8

from langchain_core.language_models import BaseChatModel
from loguru import logger
from pydantic import UUID8

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
from app.infrastructure.services.question_categorization_service.distribution import build_snapshot
from app.infrastructure.services.question_categorization_service.prompts import (
    CLASSIFY_PROMPT,
    REVIEW_PROMPT,
)
from app.infrastructure.services.question_categorization_service.schemas import ClassificationBatch


class QuestionCategorizationService(IQuestionCategorizationService):
    """
    Pipeline deterministico: classifica em batches -> snapshot -> revisa desequilibrios.

    This service uses a Large Language Model (LLM) to classify a batch of parsed OAB questions
    into one of the standard `LawArea` values. The classification runs in two steps:
    1. Initial classification in fixed-size batches using structured LLM output.
    2. Imbalance review: if some legal areas have statistically anomalous distributions (excess or deficit),
       the model selectively reviews low-confidence or potentially misclassified candidates to rebalance
       the tags without forcing incorrect results.
    """

    INITIAL_BATCH_SIZE = 6
    REVIEW_BATCH_SIZE = 6
    LOW_CONFIDENCE_THRESHOLD = 0.65
    MAX_REVIEW_CANDIDATES = 18

    def __init__(self, llm: BaseChatModel) -> None:
        """
        Initializes the QuestionCategorizationService.

        Args:
            llm (BaseChatModel): A LangChain chat model capable of generating structured output
                                 matching the `ClassificationBatch` schema.
        """
        self._structured_llm = llm.with_structured_output(ClassificationBatch)

    def classify(
        self, raw_exam: RawExam, exam_id: UUID8 | None = None
    ) -> list[Question]:
        """
        Classifies the questions included in a `RawExam` payload.

        Constructs a complete set of application `Question` entities by iterating
        over the initial predictions, performing distribution gap analysis via snapshots,
        and conditionally running a review batch step for edge cases.

        Args:
            raw_exam (RawExam): The parsed exam payload containing unclassified raw questions.
            exam_id (UUID8 | None): Optional exam ID to associate with the questions.

        Returns:
            list[Question]: A list of Domain `Question` entities containing their matched `LawArea` and descriptive tags.
        """

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

        questions = self._build_questions(raw_exam, assignments, exam_id=exam_id)
        logger.info("categorization: done questions={}", len(questions))
        return questions

    def _initial_classification(
        self, raw_exam: RawExam
    ) -> dict[int, ClassifiedQuestion]:
        """
        Executes the initial baseline classification loop for all questions.

        Chunks the complete sorted list of questions into blocks of `INITIAL_BATCH_SIZE` to
        safeguard token usage limitations and maps the predictions to `ClassifiedQuestion` objects.

        Args:
            raw_exam (RawExam): The parsed raw exam payload.

        Returns:
            dict[int, ClassifiedQuestion]: A dictionary mapping the question ID/number to its
                                           resolved classification data.
        """
        sorted_questions = sorted(raw_exam.questions, key=lambda q: q.number)
        assignments: dict[int, ClassifiedQuestion] = {}

        classify_chain = CLASSIFY_PROMPT | self._structured_llm

        for offset in range(0, len(sorted_questions), self.INITIAL_BATCH_SIZE):
            batch = sorted_questions[offset : offset + self.INITIAL_BATCH_SIZE]
            payload = [self._to_payload(q) for q in batch]

            logger.info("categorization: classify_batch offset={} size={} total={}", offset, len(batch), len(sorted_questions))

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
                    formatted_statement=getattr(item, 'formatted_statement', None),
                    confidence=item.confidence,
                    source="initial",
                    tags=getattr(item, 'tags', []),
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
        """
        Submits candidates back to the LLM when there are anomalies in distribution logic.

        Identifies questions mapped to skewed categories or those flagged with low-confidence
        scores and delegates them to the `REVIEW_PROMPT` chain. Overwrites assignments for
        approved reclassifications.

        Args:
            raw_exam (RawExam): The parsed raw exam payload.
            assignments (dict[int, ClassifiedQuestion): The currently resolved map of questions.
            snapshot (DistributionSnapshot): A domain value holding statistical distribution analysis.

        Returns:
            dict[int, ClassifiedQuestion]: An updated dictionary of classifications mapping containing
                                           the newly reviewed overrides.
        """
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

            logger.info("categorization.review: review_batch offset={} size={} total={}", offset, len(batch), len(to_review))

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
                
                # Preserva o enunciado formatado se já existir e o novo não vier (ou se for o mesmo)
                existing = assignments.get(item.question_number)
                new_formatted = getattr(item, 'formatted_statement', None) or (existing.formatted_statement if existing else None)

                assignments[item.question_number] = ClassifiedQuestion(
                    number=item.question_number,
                    area=item.area,
                    formatted_statement=new_formatted,
                    confidence=item.confidence,
                    source="review",
                    tags=getattr(item, 'tags', []),
                )

        return assignments

    def _select_review_candidates(
        self,
        assignments: dict[int, ClassifiedQuestion],
        snapshot: DistributionSnapshot,
    ) -> list[int]:
        """
        Filters and selects priority items for the categorization review round based on target capacity.

        Fetches candidates configured either in excessive distribution buckets or whose initial
        model conviction fell under the `LOW_CONFIDENCE_THRESHOLD`, bounded by `MAX_REVIEW_CANDIDATES`.

        Args:
            assignments (dict[int, ClassifiedQuestion]): Current classification mappings.
            snapshot (DistributionSnapshot): Information containing the `excess_areas`.

        Returns:
            list[int]: A deterministic list of sorted candidate question numbers.
        """
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
        exam_id: UUID8 | None = None,
    ) -> list[Question]:
        """
        Creates fully populated `Question` domain entities from categorizations.

        Combines original `RawQuestion` values alongside their generated metadata such as
        LawArea classifications, sources, and statistical confidence levels stored under standard tags.
        Will default to a fallback state if unclassified data falls through the gaps.

        Args:
            raw_exam (RawExam): The pristine parsed payload.
            assignments (dict[int, ClassifiedQuestion]): The established output mapping.
            exam_id (UUID8 | None): Optional exam ID to associate with the questions.

        Returns:
            list[Question]: Clean entity components ready for downstream processing.
        """
        exam_id = exam_id or uuid8()
        result: list[Question] = []

        for raw in sorted(raw_exam.questions, key=lambda q: q.number):
            data = assignments.get(raw.number)
            if data is None:
                area = LawArea.CIVIL
                confidence = 0.0
                source = "unclassified"
                tags = []
                statement = raw.statement
            else:
                area = data.area
                confidence = data.confidence
                source = data.source
                tags = data.tags
                statement = data.formatted_statement or raw.statement

            result.append(
                Question.create(
                    exam_id=exam_id,
                    number=raw.number,
                    statement=statement[:2000],
                    area=area,
                    correct=Alternative.A,
                    alternative_a=raw.alternative_a[:1000],
                    alternative_b=raw.alternative_b[:1000],
                    alternative_c=raw.alternative_c[:1000],
                    alternative_d=raw.alternative_d[:1000],
                    tags=tags,
                    confidence=confidence,
                    source=source,
                )
            )

        return result

    @staticmethod
    def _to_payload(raw: RawQuestion) -> dict:
        """
        Formats a unclassified Question down to a lightweight LLM mapping payload.

        Args:
            raw (RawQuestion): The model context object.

        Returns:
            dict: Simplified dictionary ready to be strictly converted to a JSON layout.
        """
        return {
            "number": raw.number,
            "statement": raw.statement,
            "alternative_a": raw.alternative_a,
            "alternative_b": raw.alternative_b,
            "alternative_c": raw.alternative_c,
            "alternative_d": raw.alternative_d,
        }
