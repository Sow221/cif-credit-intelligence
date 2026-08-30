"""Point d'entree de l'API CIF Credit Intelligence.

Assemble l'application FastAPI, les middlewares (identification de requete,
authentification JWT, rate limiting) et tous les routers (sante, prediction,
decisions, audit, modeles, rapports).
"""

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.api.middleware.auth import AuthMiddleware
from src.api.middleware.rate_limit import limiter
from src.api.middleware.request_id import RequestIDMiddleware
from src.api.routes import audit, decisions, health, models, predict, reports

app = FastAPI(
    title="CIF Credit Intelligence - API",
    version="1.0.0",
    description=(
        "API de decision de risque de credit : feature store, prediction de "
        "defaut (PD), confiance et recommandation reglementee."
    ),
)

# Application du rate limiting (slowapi).
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Ordre des middlewares : le dernier ajoute est le plus externe.
# RequestID est externe -> defini le request_id avant l'authentification.
app.add_middleware(AuthMiddleware)
app.add_middleware(RequestIDMiddleware)

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(decisions.router)
app.include_router(audit.router)
app.include_router(models.router)
app.include_router(reports.router)