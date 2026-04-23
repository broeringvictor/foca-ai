from uuid import UUID
from pydantic import BaseModel, Field
from app.domain.enums.law_area import LawArea
from app.domain.enums.answer_quality import AnswerQuality
from app.domain.enums.alternatives import Alternative
from app.domain.value_objects.sm2_progress import Sm2Progress

from app.application.dto.question.get_dto import QuestionListItem

class QuestionWithProgressDTO(BaseModel):
    id: UUID
    statement: str
    alternative_a: str
    alternative_b: str
    alternative_c: str
    alternative_d: str
    has_embedding: bool
    progress: Sm2Progress | None = None

class StudyAreaProgressDTO(BaseModel):
    area: LawArea
    progress: Sm2Progress | None
    questions: list[QuestionWithProgressDTO] = Field(default_factory=list)

class ListStudyProgressResponse(BaseModel):
    items: list[StudyAreaProgressDTO]

class SubmitAreaReviewDTO(BaseModel):
    question_id: UUID = Field(..., description="ID da questão respondida")
    response: Alternative = Field(..., description="Alternativa escolhida pelo usuário (A, B, C ou D)")
    quality: AnswerQuality = Field(
        ..., 
        description=(
            "Qualidade da resposta (SM-2):\n"
            "0: AGAIN (Errou ou esqueceu - Reinicia o aprendizado)\n"
            "3: HARD (Acertou com muita dificuldade)\n"
            "4: GOOD (Acertou com esforço normal)\n"
            "5: EASY (Acertou com facilidade)\n\n"
            "**Nota:** Em caso de resposta incorreta (`is_correct: false`), "
            "o sistema recomenda enviar a qualidade 0 (AGAIN)."
        )
    )

class SubmitAreaReviewResponse(BaseModel):
    area: LawArea
    is_correct: bool
    correct_alternative: Alternative
    new_progress: Sm2Progress
