from datetime import datetime, timedelta, timezone

import jwt

from app.infrastructure.config.settings import get_settings

config = get_settings()


def create_access_token(sub: str, extra: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": now,
        "exp": now + timedelta(minutes=config.JWT_EXPIRE_MINUTES),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, config.JWT_KEY, algorithm=config.JWT_ALGORITHM, https_only=True)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, config.JWT_KEY, algorithms=[config.JWT_ALGORITHM])
