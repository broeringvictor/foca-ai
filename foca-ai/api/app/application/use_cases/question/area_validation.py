import math
from collections import Counter

from app.application.dto.question.area_validation_dto import AreaDistributionValidation
from app.domain.entities.question import Question
from app.domain.enums.law_area import LawArea

# Approximate prior distribution weights for OAB 1a fase.
_DISTRIBUTION_WEIGHTS = {
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

_Z_THRESHOLD = 2.0


def build_area_validation(questions: list[Question]) -> AreaDistributionValidation:
    total = len(questions)
    counts = Counter(question.area for question in questions)
    total_weight = sum(_DISTRIBUTION_WEIGHTS.values())

    distorted: list[str] = []
    for area in LawArea:
        expected_prob = _DISTRIBUTION_WEIGHTS.get(area, 1) / total_weight
        expected = total * expected_prob
        observed = counts.get(area, 0)
        variance = max(total * expected_prob * (1 - expected_prob), 1e-9)
        z_score = (observed - expected) / math.sqrt(variance)
        if abs(z_score) > _Z_THRESHOLD:
            distorted.append(area.value)

    counts_by_area = {area.value: int(counts.get(area, 0)) for area in LawArea}

    return AreaDistributionValidation(
        counts_by_area=counts_by_area,
        total_questions=total,
        distorted_areas=distorted,
        is_within_expected_distribution=not distorted,
    )

