from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums.law_area import LawArea


class ClassifiedQuestion(BaseModel):
    """Resultado interno da categorização de uma questão antes da construção da entidade."""

    model_config = ConfigDict(frozen=True)

    number: int = Field(..., gt=0)
    area: LawArea
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: str = Field(default="initial", max_length=40)
    tags: list[str] = Field(default_factory=list)


class DistributionSnapshot(BaseModel):
    """Retrato da distribuição de áreas em um conjunto de questões classificadas."""

    model_config = ConfigDict(frozen=True)

    counts_by_area: dict[LawArea, int] = Field(default_factory=dict)
    total_questions: int = Field(..., ge=0)
    excess_areas: list[LawArea] = Field(default_factory=list)
    deficit_areas: list[LawArea] = Field(default_factory=list)

    @property
    def is_balanced(self) -> bool:
        return not self.excess_areas and not self.deficit_areas
