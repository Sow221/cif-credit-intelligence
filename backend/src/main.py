from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes import applications, audit, clients, decisions, reviews, scoring
from src.core.config import get_settings
from src.core.exceptions import StandardError

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clients.router, prefix=settings.API_V1_PREFIX)
app.include_router(applications.router, prefix=settings.API_V1_PREFIX)
app.include_router(scoring.router, prefix=settings.API_V1_PREFIX)
app.include_router(decisions.router, prefix=settings.API_V1_PREFIX)
app.include_router(reviews.router, prefix=settings.API_V1_PREFIX)
app.include_router(audit.router, prefix=settings.API_V1_PREFIX)


@app.exception_handler(StandardError)
async def standard_error_handler(request: Request, exc: StandardError) -> JSONResponse:
    return JSONResponse(status_code=400, content=exc.to_dict())


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok"}
