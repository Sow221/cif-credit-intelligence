"""Point d'entree de l'API CIF Credit Intelligence.

Assemble l'application FastAPI, les middlewares (identification de requete,
authentification JWT) et les routers (sante, prediction).
"""

from fastapi import FastAPI

from src.api.middleware.auth import AuthMiddleware
from src.api.middleware.request_id import RequestIDMiddleware
from src.api.routes import health, predict

app = FastAPI(
    title="CIF Credit Intelligence - API",
    version="1.0.0",
    description=(
        "API de decision de risque de credit : feature store, prediction de "
        "defaut (PD), confiance et recommandation reglementee."
    ),
)

# Ordre des middlewares : le dernier ajoute est le plus externe.
# RequestID est externe -> defini le request_id avant l'authentification.
app.add_middleware(AuthMiddleware)
app.add_middleware(RequestIDMiddleware)

app.include_router(health.router)
app.include_router(predict.router)
