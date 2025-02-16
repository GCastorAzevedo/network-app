from pydantic_settings import BaseSettings
from pydantic import PostgresDsn


class Settings(BaseSettings):
    DATABASE_URI: PostgresDsn


settings = Settings()  # type: ignore
