"""Dependances d'autorisation RBAC (P0, etape 19).

require_permission(permission) retourne une dependance FastAPI qui verifie
que le role de l'utilisateur courant possede la permission requise, sinon
FORBIDDEN.
"""

from typing import Callable

from fastapi import Depends

from src.api.dependencies.auth import CurrentUser, get_current_user
from src.core.exceptions import ForbiddenError
from src.core.security import Permission, role_has_permission


def require_permission(permission: Permission) -> Callable:
    """Fabrique une dependance FastAPI verifiant une permission RBAC."""

    def _checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role is None or not role_has_permission(
            current_user.role, permission
        ):
            raise ForbiddenError(
                "Permission insuffisante",
                details={"permission": permission.value},
            )
        return current_user

    return _checker
