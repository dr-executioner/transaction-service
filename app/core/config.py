from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "transactions_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    REDIS_URL: str = "redis://localhost:6379/0"

    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
