import datetime

from argon2.exceptions import VerifyMismatchError
from pydantic import BaseModel, ConfigDict, StrictBool, Field

from app.infrastructure.config.settings import get_settings

_hasher = get_settings().password_hasher

class Password(BaseModel):
    model_config = ConfigDict(frozen=True)
    hashed_value: str

    @classmethod
    def create(cls, plain: str) -> Password:
        plain = plain.strip()

        if len(plain) < 8:
            raise ValueError("Senha deve ter ao menos 8 caracteres.")
        if len(plain) > 50:
            raise ValueError("Senha deve ter no máximo 50 caracteres.")

        return cls(hashed_value=_hasher.hash(plain))

    def verify(self, plain: str) -> StrictBool:
        """Retorna True se o texto plano corresponde ao hash armazenado."""
        try:
            return _hasher.verify(self.hashed_value, plain)
        except VerifyMismatchError:
            return False

    @classmethod
    def from_hash(cls, hashed_value: str) -> "Password":
        """Reconstrói o VO a partir de um hash já existente (ex: leitura do banco)."""
        return cls(hashed_value=hashed_value)


