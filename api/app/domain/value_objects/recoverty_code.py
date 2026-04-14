import secrets
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, ConfigDict, Field


class RecoveryCode(BaseModel):
    """Recuperação de senha"""
    model_config = ConfigDict(frozen=True)

    code: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=1)
    )

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at

    def verify(self, code: str) -> bool:
        if self.is_expired:
            raise ValueError("Código expirado.")
        return secrets.compare_digest(self.code, code)

