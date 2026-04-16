from pydantic import Field

from app.domain.entities.base import Entity


class Question(Entity):
    statement: str = Field(..., min_length=4, max_length=2000)
    exam_id: UUID8
    correct: Alternative  # "A" | "B" | "C" | "D"
    alternative_a: str = Field(..., min_length=1, max_length=1000)
    alternative_b: str = Field(..., min_length=1, max_length=1000)
    alternative_c: str = Field(..., min_length=1, max_length=1000)
    alternative_d: str = Field(..., min_length=1, max_length=1000)