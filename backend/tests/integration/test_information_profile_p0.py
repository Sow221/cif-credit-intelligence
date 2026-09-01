"""Tests d'integration de l'information profiler (P0, etape 8).

Couvre la route POST /v1/applications/{id}/profile : le profil d'information
est produit a partir des donnees ingerees et le resultat est persiste.
"""

import sys
import uuid
from pathlib import Path
from typing import Generator

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient
from sqlalchemy import text

from src.api.middleware.auth import create_access_token  # noqa: E402
from src.db.session import SessionLocal  # noqa: E402
from src.main import app  # noqa: E402

INST_A = uuid.uuid4()
SOURCE_ID = uuid.uuid4()

_TRUNCATE_TABLES = (
    "institutions",
    "clients",
    "applications",
    "application_data",
    "data_sources",
    "consents",
    "information_profiles",
    "audit_events",
    "data_lineage",
)


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _clean(client):  # noqa: ARG001
    db = SessionLocal()
    try:
        db.execute(text(f"TRUNCATE {', '.join(_TRUNCATE_TABLES)} CASCADE"))
        db.commit()
        db.execute(
            text(
                "INSERT INTO institutions (institution_id, name, code, status) "
                "VALUES (:a, 'Inst A', 'INSTA', 'ACTIVE') "
                "ON CONFLICT (institution_id) DO NOTHING"
            ),
            {"a": INST_A},
        )
        db.execute(
            text(
                "INSERT INTO data_sources (source_id, code, type, name, active) "
                "VALUES (:s, 'BANK_STATEMENT', 'BANK', 'Etat bancaire', TRUE) "
                "ON CONFLICT (source_id) DO NOTHING"
            ),
            {"s": SOURCE_ID},
        )
        # Consommation des types par le profiler : source BUSINESS pour compléter.
        db.execute(
            text(
                "INSERT INTO data_sources (source_id, code, type, name, active) "
                "VALUES (:b, 'BUSINESS_REG', 'BUSINESS', 'Registre activite', TRUE) "
                "ON CONFLICT (source_id) DO NOTHING"
            ),
            {"b": uuid.uuid4()},
        )
        db.commit()
    finally:
        db.close()
    yield


def admin_headers(institution_id: str | None = str(INST_A)) -> dict:
    token = create_access_token(subject="admin-user", role="ADMIN", institution_id=institution_id)
    return {"Authorization": f"Bearer {token}"}


def _create_application(client) -> str:
    client_id = client.post(
        "/v1/clients", json={"first_name": "Awa", "last_name": "Diallo"},
        headers=admin_headers(),
    ).json()["client_id"]
    app = client.post(
        "/v1/applications",
        json={"client_id": client_id, "product_id": "PROD-01",
              "requested_amount": 500000.0, "requested_term": 12},
        headers=admin_headers(),
    ).json()
    return app["application_id"]


def _ingest(client, app_id, source_code="BANK_STATEMENT"):
    response = client.post(
        f"/v1/applications/{app_id}/data",
        json={"entries": [
            {"field_name": "monthly_income", "field_value": 250000.0,
             "source_code": source_code}
        ]},
        headers=admin_headers(),
    )
    assert response.status_code == 201


def test_profile_created_with_data(client):
    """Un dossier avec donnees produit un profil persiste."""
    app_id = _create_application(client)
    _ingest(client, app_id)

    response = client.post(f"/v1/applications/{app_id}/profile", headers=admin_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["credit_depth"] in ("NONE", "LOW", "MEDIUM", "HIGH")
    assert body["financial_depth"] == "LOW"  # une seule source financiere = LOW
    assert body["information_state"] in ("NO_FILE", "THIN_FILE", "FULL_FILE",
                                         "DATA_POOR", "UNKNOWN")
    assert body["profile_version"] == "1.0"
    assert body["applicant_status"] in ("NEW_TO_INSTITUTION", "NEW_TO_CREDIT",
                                        "EXISTING", "UNKNOWN")

    # Le profil est bien persiste en base.
    db = SessionLocal()
    row = db.execute(
        text("SELECT profile_id FROM information_profiles LIMIT 1")
    ).fetchone()
    assert row is not None
    db.close()


def test_profile_without_data_unknown_state(client):
    """Sans donnee, l'etat d'information reste non-fichier/inconnu."""
    app_id = _create_application(client)

    response = client.post(f"/v1/applications/{app_id}/profile", headers=admin_headers())
    assert response.status_code == 200
    body = response.json()
    # Pas de donnees -> pas de fichier de credit ni etat plein.
    assert body["credit_depth"] == "NONE"
    assert body["information_state"] in ("UNKNOWN", "NO_FILE")


def test_profile_business_source_adds_business_depth(client):
    """Une source BUSINESS contribue a la profondeur business."""
    app_id = _create_application(client)
    _ingest(client, app_id, source_code="BUSINESS_REG")

    response = client.post(f"/v1/applications/{app_id}/profile", headers=admin_headers())
    assert response.status_code == 200
    body = response.json()
    assert body["business_depth"] != "NONE"


def test_profile_tenant_isolation(client):
    """L'institution B ne voit pas une application de A (404)."""
    app_id = _create_application(client)
    _ingest(client, app_id)

    response = client.post(
        f"/v1/applications/{app_id}/profile",
        headers=admin_headers(str(uuid.uuid4())),
    )
    assert response.status_code == 404
