"""Securite / RBAC (P0, etape 19).

Roles obligatoires :
    ADMIN, CREDIT_OFFICER, CREDIT_MANAGER, RISK_MANAGER, AUDITOR

Chaque requete verifie : identite + permission + institution_scope.
Le multi-tenancy est impose au niveau backend (etape 20).
"""

from enum import Enum
from typing import Dict, FrozenSet


class Role(str, Enum):
    ADMIN = "ADMIN"
    CREDIT_OFFICER = "CREDIT_OFFICER"
    CREDIT_MANAGER = "CREDIT_MANAGER"
    RISK_MANAGER = "RISK_MANAGER"
    AUDITOR = "AUDITOR"


class Permission(str, Enum):
    # Clients / applications
    CLIENT_CREATE = "client:create"
    CLIENT_READ = "client:read"
    CLIENT_UPDATE = "client:update"
    APPLICATION_CREATE = "application:create"
    APPLICATION_READ = "application:read"
    APPLICATION_UPDATE = "application:update"
    APPLICATION_SUBMIT = "application:submit"
    APPLICATION_SCORE = "application:score"
    # Decision
    DECISION_RECOMMEND = "decision:recommend"
    DECISION_MAKE = "decision:make"
    DECISION_OVERRIDE = "decision:override"
    REVIEW_READ = "review:read"
    REVIEW_ACTION = "review:action"
    # Gouvernance / audit
    CONSENT_MANAGE = "consent:manage"
    AUDIT_READ = "audit:read"
    POLICY_MANAGE = "policy:manage"
    POLICY_READ = "policy:read"
    # Modèles / admin
    MODEL_MANAGE = "model:manage"
    MODEL_READ = "model:read"
    ADMIN_ALL = "admin:all"


# Matrice des permissions par role (P0 minimal, extensible).
ROLE_PERMISSIONS: Dict[Role, FrozenSet[Permission]] = {
    Role.ADMIN: frozenset(p for p in Permission),
    Role.CREDIT_OFFICER: frozenset(
        {
            Permission.CLIENT_CREATE,
            Permission.CLIENT_READ,
            Permission.CLIENT_UPDATE,
            Permission.APPLICATION_CREATE,
            Permission.APPLICATION_READ,
            Permission.APPLICATION_SUBMIT,
            Permission.REVIEW_READ,
            Permission.REVIEW_ACTION,
            Permission.DECISION_MAKE,
            Permission.CONSENT_MANAGE,
        }
    ),
    Role.CREDIT_MANAGER: frozenset(
        {
            Permission.CLIENT_READ,
            Permission.APPLICATION_READ,
            Permission.APPLICATION_SUBMIT,
            Permission.APPLICATION_SCORE,
            Permission.DECISION_RECOMMEND,
            Permission.DECISION_MAKE,
            Permission.DECISION_OVERRIDE,
            Permission.REVIEW_READ,
            Permission.REVIEW_ACTION,
            Permission.AUDIT_READ,
            Permission.POLICY_READ,
        }
    ),
    Role.RISK_MANAGER: frozenset(
        {
            Permission.CLIENT_READ,
            Permission.APPLICATION_READ,
            Permission.APPLICATION_SCORE,
            Permission.DECISION_RECOMMEND,
            Permission.MODEL_READ,
            Permission.POLICY_READ,
            Permission.POLICY_MANAGE,
            Permission.AUDIT_READ,
        }
    ),
    Role.AUDITOR: frozenset(
        {Permission.CLIENT_READ, Permission.APPLICATION_READ, Permission.AUDIT_READ}
    ),
}


def role_has_permission(role: Role, permission: Permission) -> bool:
    """Verifie qu'un role possede une permission (fallback ADMIN)."""
    return permission in ROLE_PERMISSIONS.get(role, frozenset())
