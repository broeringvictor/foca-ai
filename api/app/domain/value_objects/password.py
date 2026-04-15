import datetime

from argon2.exceptions import VerifyMismatchError
from pydantic import BaseModel, ConfigDict, StrictBool, Field

from app.infrastructure.config.settings import get_settings

_hasher = get_settings().password_hasher

class Password(BaseModel):
    """Senha do usuário.

    Armazena o hash da senha e fornece métodos para criação e verificação.
    Utiliza Argon2 como algoritmo de hashing.

    Atributos:
        hashed_value: Hash da senha gerado pelo Argon2.
    """
    model_config = ConfigDict(frozen=True)
    hashed_value: str = Field(description="Hash da senha gerado pelo Argon2")

    @classmethod
    def create(cls, plain: str) -> Password:
        """Cria uma nova senha a partir do texto plano.

        Args:
            plain: Senha em texto plano.

        Returns:
            Instância de Password com o hash gerado.

        Raises:
            ValueError: Se a senha não atender aos requisitos de tamanho.
        """
        plain = plain.strip()

        if len(plain) < 8:
            raise ValueError("Senha deve ter ao menos 8 caracteres.")
        if len(plain) > 50:
            raise ValueError("Senha deve ter no máximo 50 caracteres.")

        return cls(hashed_value=_hasher.hash(plain))

    def verify(self, plain: str) -> StrictBool:
        """Verifica se o texto plano corresponde ao hash armazenado.

        Args:
            plain: Senha em texto plano para comparação.

        Returns:
            True se a senha corresponder, False caso contrário.
        """
        try:
            return _hasher.verify(self.hashed_value, plain)
        except VerifyMismatchError:
            return False

    @classmethod
    def from_hash(cls, hashed_value: str) -> "Password":
        """Reconstrói o VO a partir de um hash já existente (ex: leitura do banco).

        Args:
            hashed_value: Hash previamente gerado.

        Returns:
            Instância de Password com o hash fornecido.
        """
        return cls(hashed_value=hashed_value)


