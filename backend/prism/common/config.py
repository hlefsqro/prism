from typing import Optional

from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=['.env', '../.env', '../../.env', '../../../.env'], extra='ignore',
                                      env_file_encoding="utf-8")

    HOST: str = "0.0.0.0"
    PORT: int = 8080
    APP_NAME: str = "prism"
    OTEL_ENABLED: bool = True
    OTEL_TRACE_UPLOAD_ENABLED: bool = False
    OTEL_TRACE_UPLOAD_URL: str = "http://127.0.0.1:4318/v1/traces"
    OPENAI_API_KEY: Optional[str] = None


SETTINGS = Settings()
