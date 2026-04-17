from typing import Protocol

from app.domain.entities.user import User


class IAuthRepository(Protocol):
    async def find_by_email_for_auth(self, email: str) -> User | None: ...
