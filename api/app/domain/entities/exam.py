from datetime import date

from pydantic import Field

from app.domain.entities.base import Entity


class Exam(Entity):
    """Exame (ex: Exame de Ordem Unificado - OAB).

    :ivar name: Nome do exame (ex: "XL Exame de Ordem Unificado").
    :ivar edition: Número da edição (ex: 40).
    :ivar year: Ano de aplicação.
    :ivar board: Banca examinadora (ex: "FGV").
    :ivar first_phase_date: Data da prova objetiva (1ª fase).
    :ivar second_phase_date: Data da prova prático-profissional (2ª fase).
    """

    name: str = Field(..., min_length=4, max_length=150)
    edition: int = Field(..., gt=0)
    year: int = Field(..., ge=2000, le=2100)
    board: str = Field(..., min_length=2, max_length=100)
    first_phase_date: date | None = None
    second_phase_date: date | None = None

    @classmethod
    def create(
        cls,
        name: str,
        edition: int,
        year: int,
        board: str,
        first_phase_date: date | None = None,
        second_phase_date: date | None = None,
    ) -> "Exam":
        return cls(
            name=name,
            edition=edition,
            year=year,
            board=board,
            first_phase_date=first_phase_date,
            second_phase_date=second_phase_date,
        )
