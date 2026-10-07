from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    app_name: str = "Roh Support API"
    agent_name: str = "Roh"
    database_url: str
    secret_key: str
    groq_api_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    model_config = SettingsConfigDict(env_file=ENV_FILE)


settings = Settings()