"""Route de rapport de drift du modele.

Endpoints :
- GET /v1/reports/drift -> rapport de suivi du drift (Evidently/MLflow).
"""

from fastapi import APIRouter, Request

from src.api.middleware.rate_limit import get_limit, limiter
from src.config.settings import Settings

router = APIRouter(tags=["reports"])

settings = Settings()


@router.get("/v1/reports/drift", response_model=dict)
@limiter.limit(get_limit("rate_drift"))
async def get_drift_report(request: Request) -> dict:
    """Rapport de drift.

    Retourne l'etat du suivi de drift. Le calcul des metriques de drift
    (Evidently) est branche a la collecte des predictions en production ;
    tant qu'aucune reference n'est configuree, le statut indique
    `monitoring_configurable`.
    """
    return {
        "status": "declarations",
        "message": (
            "Monitoring de drift configurable : connecter Evidently a la "
            "reference de production pour produire des metriques."
        ),
        "model_version": settings.app_version,
    }