import secrets
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, ConfigDict, Field


class RecoveryCode(BaseModel):
    """Código de recuperação de senha.

    Gera um token seguro com validade de 1 hora para redefinição de senha.

    Atributos:
        code: Token seguro gerado automaticamente.
        expires_at: Data e hora de expiração do código (UTC).
    """
    model_config = ConfigDict(frozen=True)

    code: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Token seguro para recuperação de senha",
    )
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=1),
        description="Data e hora de expiração do código em UTC",
    )

    @property
    def is_expired(self) -> bool:
        """Verifica se o código de recuperação está expirado."""
        return datetime.now(timezone.utc) >= self.expires_at

    def verify(self, code: str) -> bool:
        """Verifica se o código informado é válido.

        Args:
            code: Código a ser verificado.

        Returns:
            True se o código for válido.

        Raises:
            ValueError: Se o código estiver expirado.
        """
        if self.is_expired:
            raise ValueError("O código de recuperação expirou.")
        return secrets.compare_digest(self.code, code)



