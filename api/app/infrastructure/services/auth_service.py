from jwt import ExpiredSignatureError, InvalidTokenError

from app.api.errors.exceptions import BadRequestError, NotFoundError
from app.domain.entities.user import User
from app.domain.repositories.user_repository import IUserRepository
from app.infrastructure.security.jwt import create_access_token, decode_access_token


class AuthService:

    def __init__(self, repository: IUserRepository) -> None:
        self._repo = repository

    @staticmethod
    def generate_token(user_id: str) -> str:
        return create_access_token(sub=user_id)

    async def get_current_user(self, token: str) -> User:
        try:
            payload = decode_access_token(token)
        except ExpiredSignatureError:
            raise BadRequestError("Token expirado", field="token", source="header")
        except InvalidTokenError:
            raise BadRequestError("Token inválido", field="token", source="header")

        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise BadRequestError("Token inválido", field="token", source="header")

        user = await self._repo.find_by_id(user_id)
        if user is None:
            raise NotFoundError("Usuário não encontrado", field="user_id", source="token")

        return user
