from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WikiAI API"
    app_env: str = "development"
    cors_origin: str = "http://localhost:3000"
    database_url: str = "sqlite:///./wikiai.db"
    session_ttl_hours: int = 12
    max_sessions_per_user: int = 5

    @field_validator("cors_origin")
    @classmethod
    def reject_wildcard_cors(cls, value: str) -> str:
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        if "*" in origins:
            raise ValueError("WIKIAI_CORS_ORIGIN must not contain '*'")
        return ",".join(origins)

    @property
    def cors_origins(self) -> list[str]:
        origins = [origin for origin in self.cors_origin.split(",") if origin]
        if self.app_env == "development":
            for local_origin in ("http://localhost:3000", "http://127.0.0.1:3000"):
                if local_origin not in origins:
                    origins.append(local_origin)
        else:
            origins = [
                origin
                for origin in origins
                if not origin.startswith(("http://localhost", "http://127.0.0.1"))
            ]
        return origins

    model_config = SettingsConfigDict(env_prefix="WIKIAI_", extra="ignore")


settings = Settings()
