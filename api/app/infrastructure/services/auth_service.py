from app.infrastructure.security.jwt import create_access_token


class AuthService:

    def generate_token_jwt(self, user_id: str, email: str, name: str) -> str:
        return create_access_token(
            sub=user_id,
            extra={"email": email, "name": name},
        )
