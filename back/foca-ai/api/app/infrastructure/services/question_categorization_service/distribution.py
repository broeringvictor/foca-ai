from collections import Counter
from collections.abc import Iterable

from app.domain.enums.law_area import LawArea
from app.domain.value_objects.classified_question import (
    ClassifiedQuestion,
    DistributionSnapshot,
)

# Faixas estimadas para a OAB 1a fase (80 questoes).
# Propósito: detectar desequilíbrios grossos (ex.: 14 em CIVIL enquanto CIVIL_PROCEDURE
# tem 2). Não impõe distribuição rígida — prova real varia ano a ano.
AREA_RANGES: dict[LawArea, tuple[int, int]] = {
    LawArea.ETHICS: (6, 10),
    LawArea.CIVIL: (5, 10),
    LawArea.CIVIL_PROCEDURE: (5, 10),
    LawArea.CONSTITUTIONAL: (4, 8),
    LawArea.CRIMINAL: (4, 8),
    LawArea.CRIMINAL_PROCEDURE: (4, 8),
    LawArea.LABOR: (4, 8),
    LawArea.LABOR_PROCEDURE: (2, 6),
    LawArea.ADMINISTRATIVE: (3, 7),
    LawArea.TAX: (3, 7),
    LawArea.BUSINESS: (2, 6),
    LawArea.CONSUMER: (1, 5),
    LawArea.CHILD_AND_ADOLESCENT: (0, 4),
    LawArea.ENVIRONMENTAL: (0, 4),
    LawArea.INTERNATIONAL: (1, 5),
    LawArea.HUMAN_RIGHTS: (1, 5),
    LawArea.SOCIAL_SECURITY: (0, 4),
    LawArea.FINANCIAL: (0, 3),
    LawArea.PHILOSOPHY_OF_LAW: (1, 4),
}


def build_snapshot(
    assignments: Iterable[ClassifiedQuestion],
) -> DistributionSnapshot:
    items = list(assignments)
    counts: Counter[LawArea] = Counter(item.area for item in items)

    excess: list[LawArea] = []
    deficit: list[LawArea] = []

    for area, (min_expected, max_expected) in AREA_RANGES.items():
        observed = counts.get(area, 0)
        if observed > max_expected:
            excess.append(area)
        elif observed < min_expected:
            deficit.append(area)

    return DistributionSnapshot(
        counts_by_area=dict(counts),
        total_questions=len(items),
        excess_areas=excess,
        deficit_areas=deficit,
    )
