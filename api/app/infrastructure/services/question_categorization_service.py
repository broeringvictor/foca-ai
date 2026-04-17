from app.domain.entities.question import Question
from app.domain.services.question_categorization_service import (
    IChatModel,
    IQuestionCategorizationService,
)
from app.domain.value_objects.raw_exam import RawExam


class QuestionCategorizationService:
    def __init__(self, llm: IChatModel) -> None:
        self.llm = llm

    def classify(self, raw_exam: RawExam) -> list[Question]:
        prompt = (
            "Classifique as questoes da OAB por area do direito e dificuldade. "
            f"Edicao: {raw_exam.edition}. Total de questoes: {len(raw_exam.questions)}"
        )
        self.llm.invoke(prompt)
        raise NotImplementedError("Implement mapping from LLM output to list[Question]")

