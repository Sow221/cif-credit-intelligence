"""Point d'entree de l'API CIF Credit Intelligence.

Assemble l'application FastAPI, les middlewares (identification de requete,
authentification JWT, rate limiting) et tous les routers (sante, prediction,
decisions, audit, modeles, rapports).
"""

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.api.errors import register_exception_handlers
from src.api.middleware.auth import AuthMiddleware
from src.api.middleware.rate_limit import limiter
from src.api.middleware.request_id import RequestIDMiddleware
from src.api.routes import (
    application_data,
    applications,
    audit,
    clients,
    consents,
    decisions,
    eligibility,
    health,
    metrics,
    models,
    predict,
    reports,
)

app = FastAPI(
    title="CIF Credit Intelligence - API",
    version="1.0.0",
    description=(
        "API de decision de risque de credit : feature store, prediction de "
        "defaut (PD), confiance et recommandation reglementee."
    ),
)

# Conversion des erreurs metier en contrat d'erreur standard (P0).
register_exception_handlers(app)

# Application du rate limiting (slowapi).
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Ordre des middlewares : le dernier ajoute est le plus externe.
# RequestID est externe -> defini le request_id avant l'authentification.
app.add_middleware(AuthMiddleware)
app.add_middleware(RequestIDMiddleware)

app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(predict.router)
app.include_router(decisions.router)
app.include_router(audit.router)
app.include_router(models.router)
app.include_router(reports.router)
app.include_router(clients.router)
app.include_router(applications.router)
app.include_router(application_data.router)
app.include_router(eligibility.router)
app.include_router(consents.router)