from datetime import datetime

from pydantic import BaseModel, ConfigDict, UUID8, EmailStr

from app.domain.value_objects.name import Name


class GetMeResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    user_id: UUID8
    name: Name
    email: EmailStr
    is_active: bool
    create_at: datetime
    modified_at: datetime
