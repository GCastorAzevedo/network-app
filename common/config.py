from pydantic_settings import BaseSettings
from pydantic import PostgresDsn


class Settings(BaseSettings):
    DATABASE_URI: PostgresDsn = PostgresDsn(
        "postgresql://postgres:postgres@localhost:5432/postgres"
    )


settings = Settings()  # type: ignore
