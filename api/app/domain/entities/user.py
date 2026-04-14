from datetime import datetime, UTC
from uuid import uuid8

from pydantic import BaseModel, Field, UUID8, EmailStr, StrictBool

from app.domain.value_objects.name import Name


class User(BaseModel):
    id: UUID8 = Field(default_factory=uuid8)
    name: Name = Field(default_factory=Name)
    email: EmailStr
    password: Password
    is_active: StrictBool
    create_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(UTC))