from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "KBC LMS Prototype"
    api_prefix: str = "/api"
    secret_key: str = "super-secret-change-me"
    access_token_expire_minutes: int = 60 * 12
    sql_database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/lms"
    mongo_database_url: str = "mongodb://mongodb:27017"
    mongo_database_name: str = "lms"
    admin_email: str = "admin@kbc-lms.local"
    admin_password: str = "Admin123!"
    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
