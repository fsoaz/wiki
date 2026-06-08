from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WikiAI API"
    app_env: str = "development"
    cors_origin: str = "http://localhost:3000"
    database_url: str = "sqlite:///./wikiai.db"

    model_config = SettingsConfigDict(env_prefix="WIKIAI_", extra="ignore")


settings = Settings()
