from loguru import logger

from app.domain.entities.user import User
from app.domain.repositories.user_repository import IUserRepository
from app.application.dto.user.create_dto import CreateUserInput, CreateUserOutput

class CreateUser:

    def __init__(self, repository: IUserRepository) -> None:
        self._repo = repository

    async def execute(self, input_data: CreateUserInput) -> CreateUserOutput:

        # Verifica a senha antes do e-mail para não gastar processamento.
        if input_data.password != input_data.password_confirm:
            raise ValueError("As senhas são divergentes")

        # 2 - busca pelo e-mail
        if await self._repo.find_by_email(input_data.email):
            raise ValueError(f"Email {input_data.email} já está em uso.")

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

        return CreateUserOutput(
            email=user.email,
            user_id=user.id,
            name=user.name,
        )





