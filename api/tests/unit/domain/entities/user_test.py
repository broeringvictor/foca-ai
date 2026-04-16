from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.domain.entities.user import User
from app.domain.value_objects.name import Name
from app.domain.value_objects.password import Password
from app.domain.value_objects.recoverty_code import RecoveryCode


VALID_PASSWORD = "Senha@1234"


class TestCreateUser:
    def test_creates_with_valid_data(self):
        user = User.create(
            first_name="João",
            last_name="Silva",
            password=VALID_PASSWORD,
            email="joao@example.com",
        )

        assert isinstance(user.name, Name)
        assert user.name.first_name == "João"
        assert user.name.last_name == "Silva"
        assert user.email == "joao@example.com"
        assert isinstance(user.password, Password)
        assert user.is_active is True

    def test_password_is_hashed_not_stored_plain(self):
        user = User.create(
            first_name="João",
            last_name="Silva",
            password=VALID_PASSWORD,
            email="joao@example.com",
        )

        assert user.password.hashed_value != VALID_PASSWORD
        assert user.password.verify(VALID_PASSWORD) is True

    def test_generates_recovery_code_automatically(self):
        user = User.create(
            first_name="João",
            last_name="Silva",
            password=VALID_PASSWORD,
            email="joao@example.com",
        )

        assert isinstance(user.recovery_code, RecoveryCode)
        assert user.recovery_code.code
        assert user.recovery_code.is_expired is False

    def test_generates_id_automatically(self):
        user = User.create(
            first_name="João",
            last_name="Silva",
            password=VALID_PASSWORD,
            email="joao@example.com",
        )

        assert isinstance(user.id, UUID)

    def test_each_user_has_unique_id(self):
        user_a = User.create(
            first_name="João",
            last_name="Silva",
            password=VALID_PASSWORD,
            email="joao@example.com",
        )
        user_b = User.create(
            first_name="Maria",
            last_name="Costa",
            password=VALID_PASSWORD,
            email="maria@example.com",
        )

        assert user_a.id != user_b.id

    def test_sets_timestamps(self):
        user = User.create(
            first_name="João",
            last_name="Silva",
            password=VALID_PASSWORD,
            email="joao@example.com",
        )

        assert isinstance(user.create_at, datetime)
        assert isinstance(user.modified_at, datetime)

    def test_is_active_default_true(self):
        user = User.create(
            first_name="João",
            last_name="Silva",
            password=VALID_PASSWORD,
            email="joao@example.com",
        )

        assert user.is_active is True


class TestUserEmailNormalization:
    def test_email_is_lowercased(self):
        user = User.create(
            first_name="João",
            last_name="Silva",
            password=VALID_PASSWORD,
            email="Joao@Example.COM",
        )

        assert user.email == "joao@example.com"

    def test_email_is_stripped(self):
        user = User.create(
            first_name="João",
            last_name="Silva",
            password=VALID_PASSWORD,
            email="  joao@example.com  ",
        )

        assert user.email == "joao@example.com"


class TestUserEmailValidation:
    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            User.create(
                first_name="João",
                last_name="Silva",
                password=VALID_PASSWORD,
                email="nao-e-email",
            )

    def test_email_without_domain_raises(self):
        with pytest.raises(ValidationError):
            User.create(
                first_name="João",
                last_name="Silva",
                password=VALID_PASSWORD,
                email="joao@",
            )


class TestUserNameValidation:
    def test_invalid_first_name_raises(self):
        with pytest.raises(ValueError):
            User.create(
                first_name="J",
                last_name="Silva",
                password=VALID_PASSWORD,
                email="joao@example.com",
            )

    def test_invalid_last_name_raises(self):
        with pytest.raises(ValueError):
            User.create(
                first_name="João",
                last_name="",
                password=VALID_PASSWORD,
                email="joao@example.com",
            )


class TestUserPasswordValidation:
    def test_short_password_raises(self):
        with pytest.raises(ValueError, match="ao menos 8 caracteres"):
            User.create(
                first_name="João",
                last_name="Silva",
                password="Abc@1",
                email="joao@example.com",
            )

    def test_long_password_raises(self):
        with pytest.raises(ValueError, match="no máximo 50 caracteres"):
            User.create(
                first_name="João",
                last_name="Silva",
                password="A" * 51,
                email="joao@example.com",
            )


class TestUserIsActiveValidation:
    def test_is_active_must_be_strict_bool(self):
        with pytest.raises(ValidationError):
            User(
                name=Name(first_name="João", last_name="Silva"),
                email="joao@example.com",
                password=Password.create(VALID_PASSWORD),
                is_active="yes",  # type: ignore[arg-type]
            )

    def test_is_active_missing_raises(self):
        with pytest.raises(ValidationError):
            User(
                name=Name(first_name="João", last_name="Silva"),
                email="joao@example.com",
                password=Password.create(VALID_PASSWORD),
            )  # type: ignore[call-arg]
