from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_URL: str = Field(
        default="http://127.0.0.1:8000",
        title="Base URL for the API",
        description="Base URL for the API, used for making requests to the backend service.",
        examples=["http://127.0.0.1:8000",
                  "http://backend:8000"]
    )

    model_config = SettingsConfigDict(
        env_file=Path.cwd() / ".env",
        env_file_encoding='utf-8',
    )


@lru_cache
def get_settings() -> Settings:
    """Returns the settings for the application.
    This function uses the `lru_cache` decorator to cache the settings object,
    so that it is only loaded once and reused for subsequent calls.

    :return: Settings object containing the application settings.
    :rtype: Settings
    """
    return Settings()  # type: ignore


settings: Settings = get_settings()
SettingsDependency = Annotated[Settings, Depends(get_settings)]
