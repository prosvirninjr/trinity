import pathlib
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent


# Настройки приложения
class AppSettings(BaseSettings):
    BOT_TOKEN: str
    REDIS_HOST: str
    LOCALHOST: bool
    LOCAL_SERVER_URL: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / '.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


@lru_cache(maxsize=1)
def load_settings():
    return AppSettings()  # type: ignore
