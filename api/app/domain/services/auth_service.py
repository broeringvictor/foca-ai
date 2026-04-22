from typing import Protocol


class IAuthService(Protocol):
    def generate_token_jwt(self, user_id: str, email: str, name: str) -> str: ...
