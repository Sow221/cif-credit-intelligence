"""Exposition des metriques Prometheus pour Grafana Cloud.

Endpoint public : GET /metrics (format Prometheus text). Metriques exposees :
- `cif_predictions_total`  : compteur de predictions traitees
- `cif_model_loaded`       : 1 si le modele est charge, 0 sinon
- `cif_requests_total`     : compteur de requetes HTTP

La librairie `prometheus-client` est requise (ajoutee aux dependances du
backend). Les compteurs sont des singletons partages avec le module de routes.
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest

logger = logging.getLogger(__name__)

router = APIRouter(tags=["metrics"])

# --- Metriques (singletons disponibles pour les autres routes) ---
predictions_total = Counter(
    "cif_predictions_total",
    "Nombre total de predictions de defaut traitees",
)
requests_total = Counter(
    "cif_requests_total",
    "Nombre total de requetes HTTP recues",
)
model_loaded_gauge = Gauge(
    "cif_model_loaded",
    "1 si le modele est charge, 0 sinon",
)


def set_model_loaded(value: bool) -> None:
    """Met a jour la jauge d'etat du modele."""
    model_loaded_gauge.set(1 if value else 0)


def inc_prediction() -> None:
    """Incremente le compteur de predictions."""
    predictions_total.inc()


def inc_request() -> None:
    """Incremente le compteur de requetes HTTP."""
    requests_total.inc()


@router.get("/metrics", include_in_schema=False)
async def metrics(_: Request) -> Response:
    """Metriques au format Prometheus (scrape par Prometheus / Grafana)."""
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
