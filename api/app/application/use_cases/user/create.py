from loguru import logger

from app.api.errors.exceptions import BadRequestError, ConflictError
from app.domain.entities.user import User
from app.domain.repositories.user_repository import IUserRepository
from app.application.dto.user.create_dto import CreateUserDTO, CreateUserResponse

class CreateUser:

    def __init__(self, repository: IUserRepository) -> None:
        self._repo = repository

    async def execute(self, input_data: CreateUserDTO) -> CreateUserResponse:

        # Verifica a senha antes do e-mail para não gastar processamento.
        if input_data.password != input_data.password_confirm:
            raise BadRequestError(
                "As senhas são divergentes",
                field="password_confirm",
                source="body",
            )

        # 2 - busca pelo e-mail
        if await self._repo.find_by_email(input_data.email):
            raise ConflictError(
                f"Email {input_data.email} já está em uso.",
                field="email",
                source="body",
            )

        user = User.create(
            first_name=input_data.first_name,
            last_name=input_data.last_name,
            email=input_data.email,
            password=input_data.password,
        )

        try:
            await self._repo.save(user)
        except Exception as e:
            logger.exception(f"Erro ao salvar usuário: {e}")
            raise

        return CreateUserResponse(
            email=user.email,
            user_id=user.id,
            name=user.name,
        )





