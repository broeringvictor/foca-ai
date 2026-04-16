import factory as factory_boy
from faker import Faker

from app.domain.entities.user import User
from app.infrastructure.model.user_model import UserModel

_faker = Faker("pt_BR")

DEFAULT_PASSWORD = "DefaultP@ssw0rd!"


class UserFactory(factory_boy.Factory):
    class Meta:
        model = UserModel

    first_name = factory_boy.LazyFunction(lambda: _faker.first_name())
    last_name = factory_boy.LazyFunction(lambda: _faker.last_name())
    email = factory_boy.LazyFunction(lambda: _faker.email())

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        user = User.create(
            first_name=str(kwargs.pop("first_name")),
            last_name=str(kwargs.pop("last_name")),
            email=str(kwargs.pop("email", _faker.email())),
            password=DEFAULT_PASSWORD,
        )
        return model_class(
            id=user.id,
            first_name=user.name.first_name,
            last_name=user.name.last_name,
            email=user.email,
            hashed_password=user.password.hashed_value,
            code=user.recovery_code.code,
            expires_at=user.recovery_code.expires_at,
            create_at=user.create_at,
            modified_at=user.modified_at,
            is_active=user.is_active,
        )

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._build(model_class, *args, **kwargs)
