from pydantic import BaseModel, ConfigDict, Field


class AreaDistributionValidation(BaseModel):
    model_config = ConfigDict(frozen=True)

    counts_by_area: dict[str, int] = Field(default_factory=dict)
    total_questions: int = Field(..., ge=0, examples=[80])
    distorted_areas: list[str] = Field(default_factory=list)
    is_within_expected_distribution: bool = Field(default=True)

