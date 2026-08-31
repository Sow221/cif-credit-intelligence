"""Package schemas : contrats d'entree/sortie (Pydantic) du socle P0."""

from src.schemas.client import (
    ClientCreate,
    ClientResponse,
    ClientUpdate,
)
from src.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatus,
)

__all__ = [
    "ClientCreate",
    "ClientResponse",
    "ClientUpdate",
    "ApplicationCreate",
    "ApplicationResponse",
    "ApplicationStatus",
]
