from pydantic import UUID8, BaseModel, ConfigDict


class StudyNoteListItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID8
    title: str
    has_embedding: bool


class ListStudyNotesResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: list[StudyNoteListItem]
