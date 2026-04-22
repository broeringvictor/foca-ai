from pydantic import BaseModel, Field

from app.domain.enums.law_area import LawArea


class ClassificationResult(BaseModel):
    """Uma entrada do array retornada pelo LLM em structured output."""

    question_number: int = Field(
        ..., gt=0, description="Numero da questao no caderno (1-80)."
    )
    area: LawArea = Field(
        ..., description="Area juridica principal da questao (enum LawArea)."
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="0.9+ quando a area esta clara; 0.5-0.7 quando ambiguo; <0.5 chute.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Lista de 3 a 5 tags ou assuntos especificos relacionados a questao. Cada tag deve ter no maximo 50 caracteres (ex: 'reclamacao trabalhista', 'verbas rescisorias').",
    )
    reasoning: str = Field(
        default="",
        max_length=300,
        description="Justificativa curta (1 frase) para a area escolhida.",
    )


class ClassificationBatch(BaseModel):
    """Wrapper para structured output — o LLM retorna um batch por invocacao."""

    results: list[ClassificationResult] = Field(default_factory=list)
