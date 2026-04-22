from pydantic import UUID8, BaseModel, ConfigDict


class GenerateEmbeddingResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    study_note_id: UUID8
    embedded: bool = True
