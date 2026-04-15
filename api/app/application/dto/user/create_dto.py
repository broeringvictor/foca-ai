from pydantic import BaseModel, EmailStr, ConfigDict, UUID8, Field

from app.domain.value_objects.name import Name


class CreateUserInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    first_name: str = Field(..., min_length=3, max_length=50, examples=["Gentil João"])
    last_name: str = Field(..., min_length=3, max_length=50, examples=["da Silva"])
    email: EmailStr = Field(..., min_length=4, max_length=255, examples=["email@exemple.com"])
    password: str = Field(
        ...,
        min_length=8,
        max_length=50,
        examples=["Senha@1234"],
        description="A senha deve conter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais.",
    )
    password_confirm: str


class CreateUserOutput(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: UUID8
    name: Name
    email: EmailStr
