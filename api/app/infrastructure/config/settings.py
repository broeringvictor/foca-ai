from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from argon2 import PasswordHasher
from sqlalchemy.engine import URL

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # CONFIG MAP
    ## 1. db
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "foca-ai"
    POSTGRES_USER: str = "admin"

    ## 2. SECURITY
    ### Password
    argon2_time_cost: int = 3  # iterações
    argon2_memory_cost: int = 65536  # (64 MB)
    argon2_parallelism: int = 2  # threads

    ### JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30


    # SECRETS MAP
    POSTGRES_PASSWORD: str
    JWT_KEY: str

    @property
    def password_hasher(self) -> PasswordHasher:
        return PasswordHasher(
            time_cost=self.argon2_time_cost,
            memory_cost=self.argon2_memory_cost,
            parallelism=self.argon2_parallelism,
        )

    @property
    def database_url(self) -> str:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        ).render_as_string(hide_password=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()