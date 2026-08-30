"""Routes de controle de sante de l'API.

Endpoints publics (sans authentification) :
- GET /health        -> etat global
- GET /health/live   -> liveness probe (processus vivant)
- GET /health/ready  -> readiness probe (modele charge + base accessible)
"""

from fastapi import APIRouter, Request
from sqlalchemy import text

from src.api.middleware.rate_limit import get_limit, limiter
from src.config.settings import Settings
from src.db.session import engine
from src.models.predictor import Predictor

router = APIRouter(tags=["health"])

settings = Settings()

# Le predictor n'est pas charge ici si le modele est indisponible :
# le readiness probe signale `model_loaded=False` au lieu de crasher.
try:
    _predictor = Predictor(settings.model_path)
except Exception:  # noqa: BLE001 - pragma: no cover - environnement sans modele
    _predictor = None


def _db_connected() -> bool:
    try:
        with engine.connect() as conn:
            return conn.execute(text("SELECT 1")).scalar() == 1
    except Exception:  # noqa: BLE001 - sante: toute erreur = base injoignable
        return False


@router.get("/health")
@limiter.limit(get_limit("rate_health"))
async def health(request: Request) -> dict:
    """Etat de sante global du service."""
    return {"status": "healthy", "version": settings.app_version}


@router.get("/health/live")
async def liveness(request: Request) -> dict:
    """Liveness probe : repond tant que le processus est vivant."""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness(request: Request) -> dict:
    """Readiness probe : modele charge et base de donnees accessible."""
    return {
        "status": "ready" if (_predictor and _predictor.is_loaded() and _db_connected()) else "unready",
        "model_loaded": bool(_predictor and _predictor.is_loaded()),
        "db_connected": _db_connected(),
    }