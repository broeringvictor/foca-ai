from uuid import UUID

from fastapi import APIRouter, Depends, Form, Query, status

from app.api.dependecies.auth import get_current_user_id
from app.api.dependecies.markdown import get_markdown_content, parse_tags
from app.api.dependecies.study_note import (
    get_create_study_note_dependency,
    get_find_related_questions_to_note_dependency,
    get_find_related_study_notes_to_note_dependency,
)
from app.api.errors.schemas import ErrorResponse
from app.application.dto.question.related_dto import FindRelatedQuestionsToNoteResponse
from app.application.dto.study_note.create_dto import (
    CreateStudyNoteDTO,
    CreateStudyNoteResponse,
)
from app.application.dto.study_note.related_dto import FindRelatedStudyNotesToNoteResponse
from app.application.use_cases.study_note.create import CreateStudyNote
from app.application.use_cases.study_note.find_related_questions import (
    FindRelatedQuestionsToNote,
)
from app.application.use_cases.study_note.find_related_to_note import (
    FindRelatedStudyNotesToNote,
)

router = APIRouter(
    prefix="/study-notes",
    tags=["study-notes"],
    dependencies=[Depends(get_current_user_id)],
)


@router.post(
    "/",
    summary="create",
    description=(
        "Cria uma nova nota de estudo a partir de um arquivo Markdown.\n\n"
        "**Como enviar:**\n"
        "- `title` e `description` via formulário.\n"
        "- `content_file` opcional com arquivo `.md` ou `.markdown`.\n"
        "- `tags` opcionais para categorização."
    ),
    response_model=CreateStudyNoteResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Entrada inválida"},
        422: {"model": ErrorResponse, "description": "Erro de validação"},
    },
)
async def create_study_note(
    title: str = Form(...),
    description: str | None = Form(None),
    tags: list[str] = Depends(parse_tags),
    markdown_content: str | None = Depends(get_markdown_content),
    user_id: UUID = Depends(get_current_user_id),
    use_case: CreateStudyNote = Depends(get_create_study_note_dependency),
) -> CreateStudyNoteResponse:
    dto = CreateStudyNoteDTO(
        user_id=user_id,
        title=title,
        description=description,
        content=markdown_content,
        tags=tags,
    )
    return await use_case.execute(dto)


@router.get(
    "/{study_note_id}/related",
    summary="related study notes",
    description=(
        "Busca notas de estudo similares a uma nota específica do usuário "
        "usando busca semântica (k-NN via embeddings)."
    ),
    response_model=FindRelatedStudyNotesToNoteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Nota sem embedding"},
        404: {"model": ErrorResponse, "description": "Nota não encontrada"},
    },
)
async def get_related_study_notes(
    study_note_id: UUID,
    limit: int = Query(5, ge=1, le=20),
    user_id: UUID = Depends(get_current_user_id),
    use_case: FindRelatedStudyNotesToNote = Depends(
        get_find_related_study_notes_to_note_dependency
    ),
) -> FindRelatedStudyNotesToNoteResponse:
    return await use_case.execute(
        user_id=user_id, study_note_id=study_note_id, limit=limit
    )


@router.get(
    "/{study_note_id}/questions",
    summary="related questions",
    description=(
        "Busca questões de exames similares a uma nota específica do usuário "
        "usando busca semântica (k-NN via embeddings).\n\n"
        "É possível filtrar as questões por um exame específico usando `exam_id`."
    ),
    response_model=FindRelatedQuestionsToNoteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Nota sem embedding"},
        404: {"model": ErrorResponse, "description": "Nota não encontrada"},
    },
)
async def get_related_questions(
    study_note_id: UUID,
    limit: int = Query(5, ge=1, le=20),
    exam_id: UUID | None = Query(None),
    use_case: FindRelatedQuestionsToNote = Depends(
        get_find_related_questions_to_note_dependency
    ),
) -> FindRelatedQuestionsToNoteResponse:
    return await use_case.execute(
        study_note_id=study_note_id, limit=limit, exam_id=exam_id
    )
