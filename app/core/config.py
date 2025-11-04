from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = Field(default_factory=lambda: "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = REDIS_URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
