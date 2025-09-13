# backend/app/config.py
from __future__ import annotations

from typing import List, Optional

# Try to use the pydantic v2 settings package if available; otherwise fall back to pydantic v1 style.
try:  # pydantic v2 + pydantic-settings
    from pydantic_settings import BaseSettings as _BaseSettings  # type: ignore
    from pydantic_settings import SettingsConfigDict as _PSettingsConfigDict  # type: ignore
    _USE_PYDANTIC_V2_SETTINGS = True
except Exception:  # pydantic v1
    from pydantic import BaseSettings as _BaseSettings  # type: ignore
    _USE_PYDANTIC_V2_SETTINGS = False


class Settings(_BaseSettings):
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

    # Pydantic settings configuration per version
    if _USE_PYDANTIC_V2_SETTINGS:
        model_config = _PSettingsConfigDict(  # type: ignore[call-arg]
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )
    else:
        class Config:  # type: ignore[no-redef]
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
