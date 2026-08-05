from pydantic import model_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT token
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # Default user credentials (seeded on database creation)
    SEED_USER_USERNAME: str
    SEED_USER_PASSWORD: str

    # Comma-separated list of allowed frontend origins.
    # Local dev: http://localhost:5173
    # Cloud Run: https://<frontend-service-url>.run.app  (each service resource has its own URL)
    CORS_ORIGINS: str = "http://localhost:5173"

    # Cookie behavior. More information in .env.example
    COOKIE_SAMESITE: str = "lax"
    COOKIE_SECURE: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @model_validator(mode="after")
    def validate_cookie_config(self):
        # SameSite=None cookies are rejected by browsers unless Secure is set.
        if self.COOKIE_SAMESITE == "none" and not self.COOKIE_SECURE:
            raise ValueError(
                "COOKIE_SAMESITE='none' requires COOKIE_SECURE=true "
                "(browsers reject SameSite=None cookies without the Secure attribute)."
            )
        return self

    class Config:
        env_file = ".env"

settings = Settings()