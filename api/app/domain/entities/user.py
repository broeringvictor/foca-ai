from datetime import datetime, UTC
from uuid import uuid8

from pydantic import BaseModel, Field, UUID8, EmailStr, StrictBool, field_validator

from app.domain.value_objects.name import Name
from app.domain.value_objects.password import Password
from app.domain.value_objects.recoverty_code import RecoveryCode


class User(BaseModel):
    """Entidade de usuário do sistema.

    :ivar id: UUID8.
    :ivar name: first name + last name(Value Object Name).
    :ivar email: E-mail válido e normalizado em minúsculas.
    :ivar password: Argon2 (Value Object Password).
    :ivar is_active: Indica se o usuário está ativo.
    :ivar recovery_code: Recuperação de senha, code + expired_at (Value Object RecoveryCode).
    :ivar create_at: UTC.
    :ivar modified_at: UTC.
    """

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
        """Único ponto de criação válido para um novo usuário.

        Args:
            first_name: Primeiro nome (2-48 caracteres, apenas letras e acentos).
            last_name: Sobrenome (2-48 caracteres, apenas letras e acentos).
            password: Senha em texto plano (8-50 caracteres).
            email: E-mail válido (será normalizado para minúsculas).

        Returns:
            Instância de User com id, recovery_code e timestamps gerados automaticamente.
        """
        return cls(
            name=Name(first_name=first_name, last_name=last_name),
            password=Password.create(password),
            email=email,
            is_active=True,
        )