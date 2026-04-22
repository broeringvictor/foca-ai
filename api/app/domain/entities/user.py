from pydantic import Field, EmailStr, StrictBool, field_validator

from app.domain.entities.base import Entity
from app.domain.value_objects.name import Name
from app.domain.value_objects.password import Password
from app.domain.value_objects.recoverty_code import RecoveryCode


class User(Entity):
    """Entidade de usuário do sistema.

    :ivar name: first name + last name (Value Object Name).
    :ivar email: E-mail válido e normalizado em minúsculas.
    :ivar password: Argon2 (Value Object Password).
    :ivar is_active: Indica se o usuário está ativo.
    :ivar recovery_code: Recuperação de senha, code + expires_at (Value Object RecoveryCode).
    """

    name: Name = Field(default_factory=Name)
    email: EmailStr
    password: Password
    is_active: StrictBool

    # TODO: IMPLEMENTAR O ENVIO DO CÓDIGO POR E-MAIL COM A URL DO FRONT
    recovery_code: RecoveryCode = Field(default_factory=RecoveryCode)

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
        """Único ponto de criação válido para um novo usuário."""
        return cls(
            name=Name(first_name=first_name, last_name=last_name),
            password=Password.create(password),
            email=email,
            is_active=True,
        )
