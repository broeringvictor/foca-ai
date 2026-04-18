from functools import lru_cache
from pathlib import Path

from argon2 import PasswordHasher
from pydantic import BaseModel, Field, NonNegativeFloat, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class LLMSettings(BaseModel):
    temperature: NonNegativeFloat = 0.7
    timeout: PositiveInt = 30
    max_tokens: PositiveInt = 1000
    max_retries: PositiveInt = 6


class EmbeddingSettings(BaseModel):
    model: str = "text-embedding-3-large"
    dimensions: PositiveInt = 3072
    timeout: PositiveInt = 30
    max_retries: PositiveInt = 6


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

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

    ## 3. UPLOAD
    ### Markdown
    MAX_FILENAME_LEN: int = 255
    MAX_MARKDOWN_CONTENT_LEN: int = 20_000
    MAX_MARKDOWN_BYTES: int = 120_000

    ## 4. LLM
    llm: LLMSettings = Field(default_factory=LLMSettings)

    ## 5. EMBEDDING
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)

    # SECRETS MAP
    POSTGRES_PASSWORD: str
    JWT_KEY: str
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str

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
