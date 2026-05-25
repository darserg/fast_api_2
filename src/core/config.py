from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    ENVIRONMENT: str = "local"
    LOG_LEVEL: str = "INFO"

    SQLITE_DB_PATH: str = "app.db"
    DATABASE_URL: str = ""
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "app"
    POSTGRES_USER: str = "app"
    POSTGRES_PASSWORD: str = "app"

    # JWT settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Storage
    S3_ENABLED: bool = False
    S3_ENDPOINT_URL: str = ""
    S3_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "media"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_PUBLIC_BASE_URL: str = ""
    S3_PRESIGNED_EXPIRES_SECONDS: int = 3600

    # Observability
    SENTRY_DSN: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    OTEL_ENABLED: bool = False

    @computed_field
    @property
    def sqlite_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"

    @computed_field
    @property
    def postgres_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.POSTGRES_HOST:
            return self.postgres_url
        return self.sqlite_url


settings = Settings()
