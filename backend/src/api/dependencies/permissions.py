from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends

from src.api.dependencies.auth import get_current_user
from src.core.exceptions import ForbiddenError
from src.models.database import User

VALID_ROLES = {"ADMIN", "CREDIT_OFFICER", "CREDIT_MANAGER", "RISK_MANAGER", "AUDITOR"}

ROLE_PERMISSIONS = {
    "ADMIN": {"*"},
    "CREDIT_OFFICER": {"clients:read", "applications:read", "applications:write", "decisions:read"},
    "CREDIT_MANAGER": {
        "clients:read",
        "applications:read",
        "applications:write",
        "reviews:read",
        "reviews:write",
        "decisions:read",
        "decisions:override",
    },
    "RISK_MANAGER": {
        "models:read",
        "models:write",
        "monitoring:read",
        "policies:read",
        "policies:write",
        "applications:read",
        "reviews:read",
    },
    "AUDITOR": {"audit:read", "clients:read", "applications:read", "models:read"},
}


def require_permission(permission: str) -> Callable[[Any], Any]:
    async def _check(user: User = Depends(get_current_user)) -> User:
        user_permissions = ROLE_PERMISSIONS.get(user.role, set())
        if "*" not in user_permissions and permission not in user_permissions:
            raise ForbiddenError(f"Permission requise: {permission}")
        return user

    return _check
