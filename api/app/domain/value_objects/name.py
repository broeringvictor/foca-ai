import re

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class Name(BaseModel):
    """Nome completo do usuário.

    Valida e formata o nome e sobrenome, garantindo regras de tamanho
    e caracteres permitidos.

    Atributos:
        first_name: Primeiro nome.
        last_name: Sobrenome.
        value: Nome completo formatado (campo computado).
    """

    model_config = ConfigDict(frozen=True)

    first_name: str = Field(description="Primeiro nome do usuário")
    last_name: str = Field(description="Sobrenome do usuário")

    @computed_field
    @property
    def value(self) -> str:
        """Nome completo formatado."""
        return f"{self.first_name} {self.last_name}"

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_required_names(cls, v, info):
        campos = {"first_name": "Nome", "last_name": "Sobrenome"}
        campo = campos[info.field_name]

        if not v:
            raise ValueError(f"{campo} não pode ser vazio.")
        if len(v) < 2:
            raise ValueError(f"{campo} deve ter ao menos 2 caracteres.")
        if len(v) > 48:
            raise ValueError(f"{campo} deve ter no máximo 48 caracteres.")
        if not re.match(r"^[a-zA-ZÀ-ÿ\s'\-]+$", v):
            raise ValueError(f"{campo} contém caracteres inválidos.")
        if re.search(r"[\s'\-]{2,}", v):
            raise ValueError(f"{campo} não pode ter caracteres especiais consecutivos.")
        if v[0] in " '-" or v[-1] in " '-":
            raise ValueError(
                f"{campo} não pode começar ou terminar com caractere especial."
            )

        return v.title()

    def __str__(self) -> str:
        return self.value
