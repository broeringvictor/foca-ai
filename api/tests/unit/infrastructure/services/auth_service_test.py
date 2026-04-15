import pytest
from unittest.mock import patch

import jwt

from app.infrastructure.services.auth_service import AuthService
from app.infrastructure.config.settings import get_settings

config = get_settings()


class TestGenerateTokenJwt:
    def test_returns_string(self):
        token = AuthService.generate_token_jwt(
            user_id="123", email="joao@example.com", name="João Silva"
        )

        assert isinstance(token, str)

    def test_token_contains_sub(self):
        token = AuthService.generate_token_jwt(
            user_id="123", email="joao@example.com", name="João Silva"
        )

        payload = jwt.decode(token, config.JWT_KEY, algorithms=[config.JWT_ALGORITHM])
        assert payload["sub"] == "123"

    def test_token_contains_email(self):
        token = AuthService.generate_token_jwt(
            user_id="123", email="joao@example.com", name="João Silva"
        )

        payload = jwt.decode(token, config.JWT_KEY, algorithms=[config.JWT_ALGORITHM])
        assert payload["email"] == "joao@example.com"

    def test_token_contains_name(self):
        token = AuthService.generate_token_jwt(
            user_id="123", email="joao@example.com", name="João Silva"
        )

        payload = jwt.decode(token, config.JWT_KEY, algorithms=[config.JWT_ALGORITHM])
        assert payload["name"] == "João Silva"

    def test_token_contains_exp(self):
        token = AuthService.generate_token_jwt(
            user_id="123", email="joao@example.com", name="João Silva"
        )

        payload = jwt.decode(token, config.JWT_KEY, algorithms=[config.JWT_ALGORITHM])
        assert "exp" in payload

    def test_token_contains_iat(self):
        token = AuthService.generate_token_jwt(
            user_id="123", email="joao@example.com", name="João Silva"
        )

        payload = jwt.decode(token, config.JWT_KEY, algorithms=[config.JWT_ALGORITHM])
        assert "iat" in payload

    def test_token_is_decodable_with_correct_key(self):
        token = AuthService.generate_token_jwt(
            user_id="123", email="joao@example.com", name="João Silva"
        )

        payload = jwt.decode(token, config.JWT_KEY, algorithms=[config.JWT_ALGORITHM])
        assert payload["sub"] == "123"

    def test_token_fails_with_wrong_key(self):
        token = AuthService.generate_token_jwt(
            user_id="123", email="joao@example.com", name="João Silva"
        )

        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, "chave-errada", algorithms=[config.JWT_ALGORITHM])
