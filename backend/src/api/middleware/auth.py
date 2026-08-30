"""Authentification JWT.

Cree et valide les jetons d'acces a l'API. Le middleware protege les routes
metier (ex. /predict) tout en laissant publiques les routes de sante et de
documentation.
"""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.config.settings import Settings

PUBLIC_PATHS = {
    "/health",
    "/health/live",
    "/health/ready",
    "/docs",
    "/redoc",
    "/openapi.json",
}

settings = Settings()


def create_access_token(
    subject: str,
    secret: str | None = None,
    algorithm: str | None = None,
    expires_minutes: int | None = None,
) -> str:
    """Cree un jeton JWT signe pour le sujet donne."""
    secret = secret or settings.jwt_secret
    algorithm = algorithm or settings.jwt_algorithm
    expires_minutes = expires_minutes or settings.jwt_expiry_minutes
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_token(
    token: str,
    secret: str | None = None,
    algorithm: str | None = None,
) -> dict:
    """Decode et valide un jeton JWT, leve jwt.PyJWTError en cas d'invalidite."""
    secret = secret or settings.jwt_secret
    algorithm = algorithm or settings.jwt_algorithm
    return jwt.decode(token, secret, algorithms=[algorithm])


class AuthMiddleware(BaseHTTPMiddleware):
    """Valide le Bearer token sur les routes protegees."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        authorization = request.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Jeton d'acces manquant ou invalide"},
            )

        try:
            payload = decode_token(token)
            request.state.user = payload.get("sub")
        except jwt.PyJWTError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Jeton d'acces expire ou invalide"},
            )

        return await call_next(request)
