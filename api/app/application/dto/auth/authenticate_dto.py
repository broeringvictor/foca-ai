from pydantic import BaseModel, EmailStr, Field, ConfigDict, UUID8

from app.domain.value_objects.name import Name


class AuthenticateDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    email: EmailStr = Field(..., min_length=4, max_length=255, examples=["email@exemple.com"])
    password: str = Field(
        ...,
        min_length=8,
        max_length=50,
        examples=["Senha@1234"],
        description="A senha deve conter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais.",
    )

class AuthenticateResponse(BaseModel):
    model_config = ConfigDict(frozen=True)
    token: str = Field(..., examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."])