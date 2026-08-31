"""Tests d'integration du socle P0 (FastAPI TestClient + PostgreSQL reelle).

Couvre, conformement a la consigne P0 (etapes 1-2, 19-20) :
- Parcours client : creation, lecture, liste, mise a jour
- Parcours application : creation, lecture, liste, lifecycle (transitions)
- Isolation multi-tenant : les donnees d'une institution ne sont pas
  visibles par une autre institution (etape 20)
- RBAC : un role sans permission recoit 403 / un utilisateur sans
  institution recoit 401 (etape 19, section 67)

Chaque test est isole : les tables sont tronquees avant chaque cas.
L'institution provient du contexte authentifie (JWT), jamais du body.
"""

import sys
import uuid
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.api.middleware.auth import create_access_token  # noqa: E402
from src.db.session import SessionLocal  # noqa: E402
from src.main import app  # noqa: E402

INST_A = uuid.uuid4()
INST_B = uuid.uuid4()

# Toutes les tables (P0 + historiques). CASCADE gere les FK lors du truncate.
_TRUNCATE_TABLES = (
    "institutions",
    "roles",
    "permissions",
    "users",
    "clients",
    "applications",
    "application_data",
    "data_sources",
    "consents",
    "data_lineage",
    "information_profiles",
    "feature_definitions",
    "feature_sets",
    "feature_snapshots",
    "model_versions",
    "calibration_versions",
    "predictions",
    "uncertainty_assessments",
    "decision_policies",
    "decisions",
    "reviews",
    "decision_overrides",
    "audit_events",
    "loan_outcomes",
    "audit_log",
    "customers",
)


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _clean_tables(client):  # noqa: ARG001
    """Nettoie les tables metier avant chaque test pour l'isolation."""
    db = SessionLocal()
    try:
        db.execute(text(f"TRUNCATE {', '.join(_TRUNCATE_TABLES)} CASCADE"))
        db.commit()
    finally:
        db.close()
    yield


@pytest.fixture(autouse=True)
def _seed_institutions(client):  # noqa: ARG001
    """Insere les institutions A/B pour respecter les FK (multi-tenancy P0)."""
    db = SessionLocal()
    try:
        db.execute(
            text(
                "INSERT INTO institutions (institution_id, name, code, status) "
                "VALUES (:a, 'Inst A', 'INSTA', 'ACTIVE'), "
                "(:b, 'Inst B', 'INSTB', 'ACTIVE') "
                "ON CONFLICT (institution_id) DO NOTHING"
            ),
            {"a": INST_A, "b": INST_B},
        )
        db.commit()
    finally:
        db.close()
    yield


def admin_headers(institution_id: str | None = str(INST_A)) -> dict:
    """Token JWT d'un ADMIN appartenant a l'institution donnee."""
    token = create_access_token(
        subject="admin-user",
        role="ADMIN",
        institution_id=institution_id,
    )
    return {"Authorization": f"Bearer {token}"}


def auditor_headers(institution_id: str | None = str(INST_A)) -> dict:
    """Token JWT d'un AUDITOR (lecture seule)."""
    token = create_access_token(
        subject="auditor-user",
        role="AUDITOR",
        institution_id=institution_id,
    )
    return {"Authorization": f"Bearer {token}"}


def client_payload() -> dict:
    return {
        "external_ref": "EXT-0001",
        "first_name": "Awa",
        "last_name": "Diallo",
        "gender": "F",
    }


def application_payload(client_id: str) -> dict:
    return {
        "client_id": client_id,
        "product_id": "PROD-01",
        "requested_amount": 750000.0,
        "currency": "XOF",
        "requested_term": 12,
        "purpose": "Renovation",
    }


# --------------------------------------------------------- Securite / RBAC --


def test_create_client_without_token_returns_401(client):
    response = client.post("/v1/clients", json=client_payload())
    assert response.status_code == 401


def test_auditor_cannot_create_client_returns_403(client):
    response = client.post(
        "/v1/clients", json=client_payload(), headers=auditor_headers()
    )
    assert response.status_code == 403
    body = response.json()
    assert body["error"]["code"] == "FORBIDDEN"


def test_user_without_institution_returns_401(client):
    response = client.post(
        "/v1/clients", json=client_payload(), headers=admin_headers(None)
    )
    assert response.status_code == 401


def test_extra_fields_rejected(client):
    payload = client_payload()
    payload["institution_id"] = str(INST_B)  # tenant dans le body => refus
    response = client.post(
        "/v1/clients", json=payload, headers=admin_headers()
    )
    assert response.status_code == 422


# ------------------------------------------------------------- Parcours client --


def test_create_and_read_client(client):
    created = client.post("/v1/clients", json=client_payload(), headers=admin_headers())
    assert created.status_code == 201
    body = created.json()
    assert body["first_name"] == "Awa"
    assert body["institution_id"] == str(INST_A)  # multi-tenancy injecte cote backend
    assert body["status"] == "ACTIVE"

    listed = client.get("/v1/clients", headers=admin_headers())
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/v1/clients/{body['client_id']}", headers=admin_headers())
    assert fetched.status_code == 200
    assert fetched.json()["last_name"] == "Diallo"


def test_update_client(client):
    created = client.post("/v1/clients", json=client_payload(), headers=admin_headers()).json()
    updated = client.patch(
        f"/v1/clients/{created['client_id']}",
        json={"last_name": "Ndiaye", "status": "ACTIVE"},
        headers=admin_headers(),
    )
    assert updated.status_code == 200
    assert updated.json()["last_name"] == "Ndiaye"


def test_get_missing_client_returns_404(client):
    response = client.get(f"/v1/clients/{uuid.uuid4()}", headers=admin_headers())
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


# ------------------------------------------------------- Isolation multi-tenant --


def test_tenant_isolation(client):
    a = client.post("/v1/clients", json=client_payload(), headers=admin_headers(str(INST_A)))
    assert a.status_code == 201

    # L'institution B ne voit pas le client de A...
    b_list = client.get("/v1/clients", headers=admin_headers(str(INST_B)))
    assert b_list.status_code == 200
    assert b_list.json() == []

    # ... et ne peut pas le lire (6564: acces rendu 404 ou 403).
    a_client_id = a.json()["client_id"]
    b_get = client.get(f"/v1/clients/{a_client_id}", headers=admin_headers(str(INST_B)))
    assert b_get.status_code in (403, 404)


# -------------------------------------------------------- Parcours application --


def test_application_lifecycle(client):
    client_id = client.post(
        "/v1/clients", json=client_payload(), headers=admin_headers()
    ).json()["client_id"]

    created = client.post(
        "/v1/applications",
        json=application_payload(client_id),
        headers=admin_headers(),
    )
    assert created.status_code == 201
    app = created.json()
    assert app["status"] == "DRAFT"
    assert app["institution_id"] == str(INST_A)

    # DRAFT -> SUBMITTED -> DATA_VALIDATION
    r1 = client.post(
        f"/v1/applications/{app['application_id']}/transition?to_status=SUBMITTED",
        headers=admin_headers(),
    )
    assert r1.status_code == 200
    assert r1.json()["status"] == "SUBMITTED"

    r2 = client.post(
        f"/v1/applications/{app['application_id']}/transition?to_status=DATA_VALIDATION",
        headers=admin_headers(),
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "DATA_VALIDATION"


def test_application_invalid_transition_returns_409(client):
    client_id = client.post(
        "/v1/clients", json=client_payload(), headers=admin_headers()
    ).json()["client_id"]
    app = client.post(
        "/v1/applications",
        json=application_payload(client_id),
        headers=admin_headers(),
    ).json()

    # DIRECT: DRAFT -> DECIDED est interdit (etape 2, ALLOWED_TRANSITIONS).
    response = client.post(
        f"/v1/applications/{app['application_id']}/transition?to_status=DECIDED",
        headers=admin_headers(),
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_STATE_TRANSITION"


def test_application_tenant_isolation(client):
    client_id = client.post(
        "/v1/clients", json=client_payload(), headers=admin_headers()
    ).json()["client_id"]
    app = client.post(
        "/v1/applications",
        json=application_payload(client_id),
        headers=admin_headers(str(INST_A)),
    ).json()

    b_list = client.get("/v1/applications", headers=admin_headers(str(INST_B)))
    assert b_list.status_code == 200
    assert b_list.json() == []
