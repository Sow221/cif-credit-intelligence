"""Configuration centralisee (Pydantic Settings)."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Parametres applicatifs du backend."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Modele ---
    model_path: str = str(
        Path(__file__).resolve().parents[3]
        / "mlops"
        / "artifacts"
        / "MODEL_OFFICIAL.joblib"
    )
    isocal_path: Optional[str] = None

    # --- Securite / Auth ---
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60

    # --- Base de donnees ---
    database_url: str = "postgresql+psycopg2://cif:cif@localhost:5432/cif"
    redis_url: str = "redis://localhost:6379/0"

    # --- Rate limits ---
    rate_predict: int = 60
    rate_decisions: int = 30
    rate_audit: int = 30
    rate_models: int = 60
    rate_drift: int = 5
    rate_health: int = 120
    rate_override: int = 10

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parents[3]
