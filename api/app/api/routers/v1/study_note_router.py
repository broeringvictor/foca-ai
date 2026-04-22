from uuid import UUID

from fastapi import APIRouter, Depends, Form, status

from app.api.dependecies.auth import get_current_user_id
from app.api.dependecies.markdown import get_markdown_content, parse_tags
from app.api.dependecies.study_note import (
    get_create_study_note_dependency,
    get_delete_study_note_dependency,
    get_generate_embedding_dependency,
    get_get_study_note_dependency,
    get_list_study_notes_dependency,
    get_update_study_note_dependency,
)
from app.api.errors.schemas import ErrorResponse
from app.application.dto.study_note.create_dto import (
    CreateStudyNoteDTO,
    CreateStudyNoteResponse,
)
from app.application.dto.study_note.delete_dto import DeleteStudyNoteResponse
from app.application.dto.study_note.embedding_dto import GenerateEmbeddingResponse
from app.application.dto.study_note.get_dto import GetStudyNoteResponse
from app.application.dto.study_note.list_dto import ListStudyNotesResponse
from app.application.dto.study_note.update_dto import UpdateStudyNoteDTO, UpdateStudyNoteResponse
from app.application.use_cases.study_note.create import CreateStudyNote
from app.application.use_cases.study_note.delete import DeleteStudyNote
from app.application.use_cases.study_note.generate_embedding import GenerateStudyNoteEmbedding
from app.application.use_cases.study_note.get import GetStudyNote
from app.application.use_cases.study_note.list import ListStudyNotes
from app.application.use_cases.study_note.update import UpdateStudyNote

router = APIRouter(
    prefix="/study-notes",
    tags=["study-notes"],
    dependencies=[Depends(get_current_user_id)],
)


@router.get(
    "/",
    summary="list",
    description="Lista as notas de estudo do usuário autenticado.",
    response_model=ListStudyNotesResponse,
    status_code=status.HTTP_200_OK,
)
async def list_study_notes(
    user_id: UUID = Depends(get_current_user_id),
    use_case: ListStudyNotes = Depends(get_list_study_notes_dependency),
) -> ListStudyNotesResponse:
    return await use_case.execute(user_id)


@router.get(
    "/{study_note_id}",
    summary="get by id",
    description="Retorna os detalhes de uma nota de estudo pelo ID.",
    response_model=GetStudyNoteResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Nota não encontrada"}},
)
async def get_study_note(
    study_note_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    use_case: GetStudyNote = Depends(get_get_study_note_dependency),
) -> GetStudyNoteResponse:
    return await use_case.execute(study_note_id, user_id)


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


@router.patch(
    "/{study_note_id}",
    summary="update",
    description=(
        "Atualiza campos de uma nota de estudo. Apenas os campos enviados são alterados.\n\n"
        "- `content_file` opcional para substituir o conteúdo Markdown."
    ),
    response_model=UpdateStudyNoteResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Nota não encontrada"}},
)
async def update_study_note(
    study_note_id: UUID,
    title: str | None = Form(None),
    description: str | None = Form(None),
    tags: list[str] = Depends(parse_tags),
    markdown_content: str | None = Depends(get_markdown_content),
    use_case: UpdateStudyNote = Depends(get_update_study_note_dependency),
) -> UpdateStudyNoteResponse:
    dto = UpdateStudyNoteDTO(
        title=title,
        description=description,
        content=markdown_content,
        tags=tags if tags else None,
    )
    return await use_case.execute(study_note_id, dto)


@router.delete(
    "/{study_note_id}",
    summary="delete",
    description="Remove uma nota de estudo pelo ID.",
    response_model=DeleteStudyNoteResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Nota não encontrada"}},
)
async def delete_study_note(
    study_note_id: UUID,
    use_case: DeleteStudyNote = Depends(get_delete_study_note_dependency),
) -> DeleteStudyNoteResponse:
    return await use_case.execute(study_note_id)


@router.post(
    "/{study_note_id}/embeddings",
    summary="generate embedding",
    description=(
        "Gera e armazena o embedding vetorial de uma nota de estudo usando OpenAI.\n\n"
        "O campo `has_embedding` na listagem será `true` após esta operação."
    ),
    response_model=GenerateEmbeddingResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse, "description": "Nota não encontrada"}},
)
async def generate_study_note_embedding(
    study_note_id: UUID,
    use_case: GenerateStudyNoteEmbedding = Depends(get_generate_embedding_dependency),
) -> GenerateEmbeddingResponse:
    return await use_case.execute(study_note_id)
