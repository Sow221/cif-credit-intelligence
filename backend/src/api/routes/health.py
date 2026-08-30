"""Route de controle de sante de l'API."""

import time

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Retourne l'etat de sante courant du service."""
    return {
        "status": "ok",
        "service": "cif-credit-intelligence-backend",
        "timestamp": time.time(),
    }
