from uuid import UUID

from fastapi import APIRouter, Depends, Form, status

from app.api.dependecies.auth import get_current_user_id
from app.api.dependecies.markdown import get_markdown_content, parse_tags
from app.api.dependecies.study_note import get_create_study_note_dependency
from app.api.errors.schemas import ErrorResponse
from app.application.dto.study_note.create_dto import (
    CreateStudyNoteDTO,
    CreateStudyNoteResponse,
)
from app.application.use_cases.study_note.create import CreateStudyNote

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
