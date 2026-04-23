from unittest.mock import AsyncMock
from uuid import uuid8

import pytest

from app.application.use_cases.study_note.get import GetStudyNote
from app.domain.entities.study_note import StudyNote
from app.domain.enums.law_area import LawArea


class TestGetStudyNote:
    @pytest.mark.asyncio
    async def test_execute_serializes_question_ids_as_strings(self):
        user_id = uuid8()
        question_id = uuid8()
        note = StudyNote.create(
            user_id=user_id,
            area=LawArea.CIVIL_PROCEDURE,
            title="Resumo de Processo Civil",
            description="Resumo",
            content="# Titulo",
            tags=["civil"],
        )
        note.questions = [question_id]

        repository = AsyncMock()
        repository.find_by_id.return_value = note
        use_case = GetStudyNote(repository=repository)

        response = await use_case.execute(note.id, user_id)

        assert response.questions == [str(question_id)]
