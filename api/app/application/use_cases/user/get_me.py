from app.api.errors.exceptions import NotFoundError
from app.application.dto.user.get_me_dto import GetMeResponse
from app.domain.repositories.user_repository import IUserRepository


class GetMe:

    def __init__(self, repository: IUserRepository) -> None:
        self._repo = repository

    async def execute(self, user_id: str) -> GetMeResponse:
        user = await self._repo.find_by_id(user_id)
        if user is None:
            raise NotFoundError("Usuário não encontrado", field="user_id", source="token")

        return GetMeResponse(
            user_id=user.id,
            name=user.name,
            email=user.email,
            is_active=user.is_active,
            create_at=user.create_at,
            modified_at=user.modified_at,
        )
