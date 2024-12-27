import json
from typing import Optional, List

from pydantic import field_validator, Field
from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=['.env', '../.env', '../../.env', '../../../.env', '../prism/.env'],
                                      extra='ignore',
                                      env_file_encoding="utf-8")

    HOST: str = "0.0.0.0"
    PORT: int = 8080
    APP_NAME: str = "prism"
    OTEL_ENABLED: bool = True
    OTEL_TRACE_UPLOAD_ENABLED: bool = False
    OTEL_TRACE_UPLOAD_URL: str = "http://127.0.0.1:4318/v1/traces"
    OPENAI_API_KEY: Optional[str] = None
    X_BEARER_TOKEN: Optional[str] = None
    SEARCHAPI_API_KEY: Optional[str] = None
    API_KEYS: List[str] = Field(default_factory=list)
    CMC_PRO_API_KEY: Optional[str] = None

    @field_validator('API_KEYS', mode='before')
    def validator_api_keys(cls, v):
        if isinstance(v, str):
            v_list = json.loads(v)
            if isinstance(v_list, list):
                return v_list
        return v


SETTINGS = Settings()
