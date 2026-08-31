"""Handlers d'exception FastAPI conformes au contrat d'erreur standard.

Convertit les StandardError metier en reponse HTTP au corps :
    { "error": { "code", "message", "details" } }
(consigne sections 40, 41, 67).
"""

from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.exceptions import StandardError


def register_exception_handlers(app: FastAPI) -> None:
    """Enregistre les handlers d'exception sur l'application FastAPI."""

    @app.exception_handler(StandardError)
    async def standard_error_handler(
        request: Request, exc: StandardError
    ) -> JSONResponse:
        payload = exc.to_dict()
        if exc.request_id:
            payload["error"]["details"]["request_id"] = exc.request_id
        return JSONResponse(status_code=exc.status_code, content=payload)
