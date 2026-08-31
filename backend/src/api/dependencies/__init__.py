"""Package dependencies FastAPI (P0) : auth, tenant, permissions."""

from src.api.dependencies.auth import (
    CurrentUser,
    decode_user_from_token,
    get_current_user,
)
from src.api.dependencies.permissions import require_permission

__all__ = [
    "CurrentUser",
    "decode_user_from_token",
    "get_current_user",
    "require_permission",
]
