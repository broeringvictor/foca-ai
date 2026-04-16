from app.api.errors.exceptions import BadRequestError
from app.application.dto.auth.authenticate_dto import AuthenticateDTO, AuthenticateResponse
from app.domain.repositories.auth_repository import IAuthRepository
from app.domain.services.auth_service import IAuthService


class AuthenticateUser:
    def __init__(
        self,
        repository: IAuthRepository,
        service: IAuthService,
    ) -> None:
        self._repo = repository
        self._service = service

    async def execute(self, input_data: AuthenticateDTO) -> AuthenticateResponse:
        user = await self._repo.find_by_email_for_auth(input_data.email)
        if not user:
            raise BadRequestError("Credenciais inválidas", field="email/password", source="body")

        if not user.is_active:
            raise BadRequestError("Usuário inativo", field="email", source="body")

        if not user.password.verify(input_data.password):
            raise BadRequestError("Credenciais inválidas", field="email/password", source="body")

        token = self._service.generate_token_jwt(
            user_id=str(user.id),
            email=user.email,
            name=str(user.name),
        )

        return AuthenticateResponse(token=token)
