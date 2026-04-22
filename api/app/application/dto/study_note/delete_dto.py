from pydantic import UUID8, BaseModel, ConfigDict


class DeleteStudyNoteResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    study_note_id: UUID8
