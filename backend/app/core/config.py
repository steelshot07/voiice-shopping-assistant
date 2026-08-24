from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    debug: bool = False

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            # HTTP (legacy / LAN HTTP access)
            "http://localhost:8081",
            "http://localhost:19006",
            "http://localhost:5173",
            "http://172.22.27.121:5173",
            "http://172.22.27.121:8081",
            # HTTPS (Vite basicSsl dev server — required for Web Speech API on phone)
            "https://localhost:5173",
            "https://172.22.27.121:5173",
        ]
    )

    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("JWT_SECRET_KEY must contain at least 32 characters")

        return value


settings = Settings()
