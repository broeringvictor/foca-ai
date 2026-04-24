import json
from uuid import uuid8

from langchain_core.language_models import BaseChatModel
from loguru import logger
from pydantic import UUID8, ValidationError

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
    """

    INITIAL_BATCH_SIZE = 6
    REVIEW_BATCH_SIZE = 6
    LOW_CONFIDENCE_THRESHOLD = 0.65
    MAX_REVIEW_CANDIDATES = 18

    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm
        self._structured_llm = llm.with_structured_output(ClassificationBatch)

    def classify(
        self, raw_exam: RawExam, exam_id: UUID8 | None = None
    ) -> list[Question]:
        if not raw_exam.questions:
            logger.info("categorization: no_questions edition={}", raw_exam.edition)
            return []

        logger.info(
            "categorization: start edition={} total={}",
            raw_exam.edition,
            len(raw_exam.questions),
        )

        assignments = self._initial_classification(raw_exam)
        snapshot = build_snapshot(assignments.values())

        if snapshot.excess_areas and snapshot.deficit_areas:
            assignments = self._review_imbalances(raw_exam, assignments, snapshot)

        return self._build_questions(raw_exam, assignments, exam_id=exam_id)

    def recategorize(
        self,
        questions: list[Question],
        format_statement: bool = True,
        categorize_tags: bool = True,
        categorize_law_area: bool = True,
    ) -> list[Question]:
        """
        Recategoriza questões existentes.
        """
        if not questions:
            logger.warning("categorization.recategorize: No questions provided")
            return []

        # Converte entidades para RawExam para reutilizar lógica de classificação
        try:
            raw_exam = RawExam(
                edition=1,
                name="Recategorization",
                exam_type=1,
                color="Unknown",
                questions=[self._to_raw(q) for q in questions],
            )
        except ValidationError as e:
            logger.error("categorization.recategorize: RawExam validation failed. Data: {}", e.errors())
            raise

        logger.info("categorization.recategorize: start total={} format={} tags={} area={}", 
                    len(questions), format_statement, categorize_tags, categorize_law_area)

        # Executa classificação inicial
        assignments = self._initial_classification(raw_exam)
        
        if len(assignments) == 0:
            logger.error("categorization.recategorize: No assignments returned from LLM")

        # Para recategorização pontual ou de um exame completo, 
        # opcionalmente rodamos o rebalanceamento se houver muitas questões
        if len(questions) >= 10:
            snapshot = build_snapshot(assignments.values())
            if snapshot.excess_areas and snapshot.deficit_areas:
                assignments = self._review_imbalances(raw_exam, assignments, snapshot)

        results = self._build_updated_questions(
            questions, 
            assignments, 
            format_statement, 
            categorize_tags, 
            categorize_law_area
        )
        
        logger.info("categorization.recategorize: done total={}", len(results))
        return results

    def _initial_classification(
        self, raw_exam: RawExam
    ) -> dict[int, ClassifiedQuestion]:
        sorted_questions = sorted(raw_exam.questions, key=lambda q: q.number)
        assignments: dict[int, ClassifiedQuestion] = {}
        classify_chain = CLASSIFY_PROMPT | self._structured_llm

        for offset in range(0, len(sorted_questions), self.INITIAL_BATCH_SIZE):
            batch = sorted_questions[offset : offset + self.INITIAL_BATCH_SIZE]
            payload = [self._to_payload(q) for q in batch]
            questions_json = json.dumps(payload, ensure_ascii=False)

            logger.info("categorization: calling LLM for batch offset={} size={}", offset, len(batch))
            
            results = []
            try:
                batch_result = classify_chain.invoke({"questions_json": questions_json})
                
                # Extração robusta do campo 'results'
                if isinstance(batch_result, dict):
                    results = batch_result.get('results', [])
                else:
                    results = getattr(batch_result, 'results', [])

                # Caso o LLM tenha retornado o JSON como string dentro do campo
                if isinstance(results, str):
                    try:
                        results = json.loads(results)
                    except Exception:
                        logger.warning("categorization: results field was a string but not valid JSON")
                        results = []
                
                logger.info("categorization: LLM returned {} results", len(results))
            except Exception as exc:
                logger.error("categorization: classify_chain_failed error={}. Trying fallback manual parse.", exc)
                # O fallback manual poderia ser uma chamada sem formatador, 
                # mas por ora vamos tentar extrair o que for possível do erro se for ValidationError
                if "input_value='" in str(exc):
                    # Tenta extrair o valor que falhou (técnica suja mas eficaz para debug/emergência)
                    try:
                        import re
                        json_match = re.search(r"input_value='(\[.*\])'", str(exc), re.DOTALL)
                        if json_match:
                            results = json.loads(json_match.group(1))
                            logger.info("categorization: Recovered {} results from validation error string", len(results))
                    except Exception:
                        pass

            for item in results:
                # Mapeamento seguro (aceita objeto ou dict)
                def get_val(obj, key, default=None):
                    if isinstance(obj, dict): return obj.get(key, default)
                    return getattr(obj, key, default)

                q_num = get_val(item, 'question_number')
                q_area = get_val(item, 'area')
                q_formatted = get_val(item, 'formatted_statement')
                q_conf = get_val(item, 'confidence', 0.0)
                q_tags = get_val(item, 'tags', [])

                if q_num is not None:
                    assignments[q_num] = ClassifiedQuestion(
                        number=q_num,
                        area=q_area,
                        formatted_statement=q_formatted,
                        confidence=q_conf,
                        source="initial",
                        tags=q_tags,
                    )
                    logger.debug("categorization: question {} classified as {}", q_num, q_area)
        
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
                    "current_confidence": round(assignments[raw.number].confidence, 2),
                }
                for raw in batch
            ]

            results = []
            try:
                batch_result = review_chain.invoke({
                    "distribution_summary": distribution_summary,
                    "excess_areas": str(excess_names),
                    "deficit_areas": str(deficit_names),
                    "questions_json": json.dumps(payload, ensure_ascii=False)
                })
                
                if isinstance(batch_result, dict):
                    results = batch_result.get('results', [])
                else:
                    results = getattr(batch_result, 'results', [])
                
                if isinstance(results, str):
                    results = json.loads(results)
                    
            except Exception as exc:
                logger.error("categorization: review_chain_failed error={}", exc)

            for item in results:
                def get_val(obj, key, default=None):
                    if isinstance(obj, dict): return obj.get(key, default)
                    return getattr(obj, key, default)

                q_num = get_val(item, 'question_number')
                if q_num not in by_number:
                    continue
                
                q_area = get_val(item, 'area')
                q_formatted = get_val(item, 'formatted_statement')
                q_conf = get_val(item, 'confidence', 0.0)
                q_tags = get_val(item, 'tags', [])

                existing = assignments.get(q_num)
                new_formatted = q_formatted or (existing.formatted_statement if existing else None)
                
                assignments[q_num] = ClassifiedQuestion(
                    number=q_num,
                    area=q_area,
                    formatted_statement=new_formatted,
                    confidence=q_conf,
                    source="review",
                    tags=q_tags,
                )
                logger.debug("categorization.review: question {} re-classified as {}", q_num, q_area)
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
        exam_id: UUID8 | None = None,
    ) -> list[Question]:
        exam_id = exam_id or uuid8()
        result: list[Question] = []
        for raw in sorted(raw_exam.questions, key=lambda q: q.number):
            data = assignments.get(raw.number)
            area = data.area if data else LawArea.CIVIL
            confidence = data.confidence if data else 0.0
            source = data.source if data else "unclassified"
            tags = data.tags if data else []
            statement = (data.formatted_statement if data else None) or raw.statement

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

    def _build_updated_questions(
        self,
        original_questions: list[Question],
        assignments: dict[int, ClassifiedQuestion],
        format_statement: bool,
        categorize_tags: bool,
        categorize_law_area: bool,
    ) -> list[Question]:
        updated: list[Question] = []
        for q in original_questions:
            data = assignments.get(q.number)
            if not data:
                logger.warning("categorization: No classification data for question {}", q.number)
                updated.append(q)
                continue
            
            new_area = data.area if categorize_law_area else q.area
            new_statement = (data.formatted_statement if format_statement and data.formatted_statement else q.statement)
            new_tags = data.tags if categorize_tags else q.tags
            
            logger.debug("categorization: Updating question {}. New area: {}, Statement length: {}, Tags count: {}", 
                         q.number, new_area, len(new_statement), len(new_tags))

            try:
                updated_q = Question(
                    id=q.id,
                    exam_id=q.exam_id,
                    number=q.number,
                    statement=new_statement,
                    area=new_area,
                    correct=q.correct,
                    alternative_a=q.alternative_a,
                    alternative_b=q.alternative_b,
                    alternative_c=q.alternative_c,
                    alternative_d=q.alternative_d,
                    tags=new_tags,
                    confidence=data.confidence,
                    source=data.source,
                    created_at=q.created_at,
                    updated_at=q.updated_at,
                    embedding=q.embedding
                )
                updated.append(updated_q)
            except ValidationError as e:
                logger.error("categorization: Failed to build updated question {}: {}", q.number, e.errors())
                updated.append(q)
                
        return updated

    @staticmethod
    def _to_raw(q: Question) -> RawQuestion:
        return RawQuestion(
            number=q.number,
            statement=q.statement,
            alternative_a=q.alternative_a,
            alternative_b=q.alternative_b,
            alternative_c=q.alternative_c,
            alternative_d=q.alternative_d,
        )

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
