from pathlib import Path
import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── DATABASE ─────────────────────────────
    DATABASE_URL: str | None = None
    DATABASE_URL_SYNC: str | None = None

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "school_master"

    # ── JWT ──────────────────────────────────
    JWT_PRIVATE_KEY_PATH: str
    JWT_PUBLIC_KEY_PATH: str

    @property
    def JWT_PRIVATE_KEY(self):
        return Path(self.JWT_PRIVATE_KEY_PATH).read_text()

    @property
    def JWT_PUBLIC_KEY(self):
        return Path(self.JWT_PUBLIC_KEY_PATH).read_text()

    # ── AUTH ─────────────────────────────────
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── REDIS ────────────────────────────────
    REDIS_URL: str | None = None

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # ── BUSINESS RULES ───────────────────────
    FREQUENCIA_MINIMA: float = 75.0
    MEDIA_APROVADO: float = 7.0
    MEDIA_RECUPERACAO: float = 5.0

    # ── RABBITMQ ─────────────────────────────
    RABBITMQ_URL: str | None = None

    RABBIT_HOST: str = "localhost"
    RABBIT_PORT: int = 5672
    RABBIT_USER: str = "guest"
    RABBIT_PASSWORD: str = "guest"
    
    # ── SMTP ─────────────────────────────
    SMTP_HOST:     str = "smtp.gmail.com"
    SMTP_PORT:     int = 587
    SMTP_USER:     str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM:     str = SMTP_USER

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}"
            f"/{self.DB_NAME}"
        )

    @property
    def redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL

        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def rabbitmq_url(self) -> str:
        if self.RABBITMQ_URL:
            return self.RABBITMQ_URL

        return (
            f"amqp://{self.RABBIT_USER}:{self.RABBIT_PASSWORD}"
            f"@{self.RABBIT_HOST}:{self.RABBIT_PORT}/"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()