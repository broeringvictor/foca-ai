from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, UUID8


class CreateStudyNoteDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: UUID8 = Field(..., examples=["01965354-a47f-816a-a4ce-f4fa7f87f617"])
    title: str = Field(
        ...,
        min_length=4,
        max_length=100,
        examples=["Resumo de SQLAlchemy Async"],
    )
    description: str | None = Field(
        None,
        min_length=4,
        max_length=500,
        examples=["Notas principais sobre sessão assíncrona e transações."],
    )
    content: str | None = Field(
        None,
        max_length=5000,
        examples=["# SQLAlchemy Async\n\n- Use `AsyncSession`\n- Controle commit no `get_session`"],
    )
    tags: list[str] = Field(default_factory=list, examples=[["python", "sqlalchemy"]])


class CreateStudyNoteResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    study_note_id: UUID8 = Field(..., examples=["01965366-a7bf-8c8d-b791-b2fef0ddf742"])
    title: str = Field(..., examples=["Resumo de SQLAlchemy Async"])
    created_at: datetime = Field(..., examples=["2026-04-16T20:30:00Z"])
