from pydantic import BaseModel, EmailStr, ConfigDict, UUID8
from sqlalchemy import UUID

from app.domain.value_objects.name import Name


class CreateUserInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    first_name: str
    last_name: str
    email: EmailStr
    password: str
    password_confirm: str


class CreateUserOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: UUID8
    name: Name
    email: EmailStr
