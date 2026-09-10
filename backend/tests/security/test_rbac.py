from __future__ import annotations

from src.api.dependencies.permissions import ROLE_PERMISSIONS, VALID_ROLES


def test_all_roles_defined():
    assert VALID_ROLES == {"ADMIN", "CREDIT_OFFICER", "CREDIT_MANAGER", "RISK_MANAGER", "AUDITOR"}


def test_admin_has_all_permissions():
    assert "*" in ROLE_PERMISSIONS["ADMIN"]


def test_credit_officer_cannot_manage_models():
    assert "models:write" not in ROLE_PERMISSIONS["CREDIT_OFFICER"]


def test_auditor_read_only():
    perms = ROLE_PERMISSIONS["AUDITOR"]
    write_perms = [p for p in perms if ":write" in p]
    assert len(write_perms) == 0


def test_risk_manager_can_manage_policies():
    assert "policies:write" in ROLE_PERMISSIONS["RISK_MANAGER"]
