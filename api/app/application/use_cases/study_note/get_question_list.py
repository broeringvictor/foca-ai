from uuid import UUID

from app.api.errors.exceptions import NotFoundError
from app.application.dto.question.get_dto import GetQuestionsListResponse, QuestionListItem
from app.domain.repositories.question_repository import IQuestionRepository
from app.domain.repositories.study_note_repository import IStudyNoteRepository


class GetStudyNoteQuestionList:
    def __init__(
        self,
        study_note_repository: IStudyNoteRepository,
        question_repository: IQuestionRepository,
    ) -> None:
        self._study_note_repo = study_note_repository
        self._question_repo = question_repository

    async def execute(self, study_note_id: UUID) -> GetQuestionsListResponse:
        note = await self._study_note_repo.find_by_id(study_note_id)
        if note is None:
            raise NotFoundError("Nota de estudo não encontrada")

        questions = await self._question_repo.find_by_ids(list(note.questions))

        items = [
            QuestionListItem(
                id=q.id,
                statement=q.statement,
                alternative_a=q.alternative_a,
                alternative_b=q.alternative_b,
                alternative_c=q.alternative_c,
                alternative_d=q.alternative_d,
            )
            for q in questions
        ]

        return GetQuestionsListResponse(questions=items)
