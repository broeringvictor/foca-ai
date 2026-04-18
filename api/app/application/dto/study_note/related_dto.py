from pydantic import UUID8, BaseModel, ConfigDict, Field


class RelatedStudyNoteItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID8
    title: str
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    score: float = Field(..., ge=0.0, le=1.0)


class FindRelatedStudyNotesResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    question_id: UUID8
    items: list[RelatedStudyNoteItem] = Field(default_factory=list)


class FindRelatedStudyNotesToNoteResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    study_note_id: UUID8
    items: list[RelatedStudyNoteItem] = Field(default_factory=list)
