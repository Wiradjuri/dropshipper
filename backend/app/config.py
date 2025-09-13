# backend/app/config.py
from __future__ import annotations

from typing import List, Optional

# Try to use the pydantic v2 settings package if available; otherwise fall back to pydantic v1 style.
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
    _USE_PYDANTIC_V2_SETTINGS = True
except Exception:
    from pydantic import BaseSettings  # type: ignore
    _USE_PYDANTIC_V2_SETTINGS = False


if _USE_PYDANTIC_V2_SETTINGS:
    class Settings(BaseSettings):
        # --- Core ---
        DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

        # CORS
        FRONTEND_ORIGIN: str = "http://localhost:3000"
        ALLOWED_ORIGINS: Optional[str] = None  # comma-separated list

        # Dev convenience (never true in prod)
        DISABLE_AUTH: bool = False

        # Integrations (placeholders ok)
        STRIPE_SECRET_KEY: Optional[str] = None
        STRIPE_WEBHOOK_SECRET: Optional[str] = None

        # Pydantic v2 settings
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )

        @property
        def allowed_origins(self) -> List[str]:
            if self.ALLOWED_ORIGINS:
                return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
            return [self.FRONTEND_ORIGIN]
else:
    class Settings(BaseSettings):
        # --- Core ---
        DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

        # CORS
        FRONTEND_ORIGIN: str = "http://localhost:3000"
        ALLOWED_ORIGINS: Optional[str] = None  # comma-separated list

        # Dev convenience (never true in prod)
        DISABLE_AUTH: bool = False

        # Integrations (placeholders ok)
        STRIPE_SECRET_KEY: Optional[str] = None
        STRIPE_WEBHOOK_SECRET: Optional[str] = None

        # Pydantic v1-compatible settings
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False
            extra = "ignore"

        @property
        def allowed_origins(self) -> List[str]:
            if self.ALLOWED_ORIGINS:
                return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
            return [self.FRONTEND_ORIGIN]


# Export a settings instance for the app to use
settings = Settings()
