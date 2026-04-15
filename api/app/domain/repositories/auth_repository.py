from typing import Protocol

from app.domain.entities.user import User


class IUserRepository(Protocol):
    async def find_by_email_for_auth(self, email: str) -> User | None: ...