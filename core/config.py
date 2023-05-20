from pydantic import BaseSettings, EmailStr
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str

    JWT_SECRET_KEY: str
    JWT_HASH_ALGORITHM: str
    ACCESS_TOKEN_EXPIRATION_MINS: int = 60*24*7

    DATABASE_URI: str
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    class Config:
        env_file = '../.env'


@lru_cache(maxsize=1)
def get_settings():
    return Settings()
