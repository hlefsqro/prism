from typing import Optional

from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=['.env', '../.env', '../../.env', '../../../.env'], extra='ignore',
                                      env_file_encoding="utf-8")
    OPENAI_API_KEY: Optional[str] = None


SETTINGS = Settings()
