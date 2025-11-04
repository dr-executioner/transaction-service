from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    REDIS_URL: str = "redis://localhost:6379/0"

    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set broker/backend from REDIS_URL if not provided
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = self.REDIS_URL
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
