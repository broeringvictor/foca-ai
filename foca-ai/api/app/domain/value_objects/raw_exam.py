from pydantic import BaseModel, ConfigDict, Field


class RawQuestion(BaseModel):
    """Questão parseada do PDF, ainda sem gabarito, área ou tags."""

    model_config = ConfigDict(frozen=True)

    number: int = Field(..., gt=0, description="Número da questão no caderno (1-80)")
    statement: str = Field(..., min_length=4, description="Enunciado")
    alternative_a: str = Field(..., min_length=1)
    alternative_b: str = Field(..., min_length=1)
    alternative_c: str = Field(..., min_length=1)
    alternative_d: str = Field(..., min_length=1)


class RawExam(BaseModel):
    """Prova completa extraída do PDF: cabeçalho + questões parseadas."""

    model_config = ConfigDict(frozen=True)

    edition: int = Field(..., gt=0)
    name: str = Field(..., min_length=4)
    exam_type: int = Field(..., gt=0)
    color: str = Field(..., min_length=2)
    questions: list[RawQuestion] = Field(default_factory=list)


class ExtractionOptions(BaseModel):
    """Parâmetros de corte do layout para o extrator.

    Os valores padrão foram calibrados para os PDFs da FGV (OAB).
    """

    model_config = ConfigDict(frozen=True)

    header_height: int = Field(default=65, gt=0, le=500)
    footer_height: int = Field(default=60, gt=0, le=500)
    column_split: int = Field(default=298, gt=0, le=2000)
