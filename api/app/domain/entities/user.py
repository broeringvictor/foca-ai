from datetime import datetime, UTC
from uuid import uuid8

from pydantic import BaseModel, Field, UUID8, EmailStr, StrictBool, field_validator

from app.domain.value_objects.name import Name
from app.domain.value_objects.password import Password
from app.domain.value_objects.recoverty_code import RecoveryCode


class User(BaseModel):
    id: UUID8 = Field(default_factory=uuid8)
    name: Name = Field(default_factory=Name)
    email: EmailStr
    password: Password
    is_active: StrictBool

    #TODO: IMPLEMENTAR O ENVIO DO CÓDIGO POR E-MAIL COM A URL DO FRONT
    recovery_code: RecoveryCode = Field(default_factory=RecoveryCode)

    create_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()

    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        password: str,
        email: str,
    ) -> "User":
        """Único ponto de criação válido."""
        return cls(
            name=Name(first_name=first_name, last_name=last_name),
            password=Password.create(password),
            email=email,
            is_active=True,
        )