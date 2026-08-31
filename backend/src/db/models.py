"""Modeles ORM SQLAlchemy du socle Adaptive Credit Decision Engine.

Le module unifie :
  * le socle multi-tenant / RBAC (institutions, roles, users)
  * le domaine de credit (clients, applications, data, consent, lineage)
  * l'information / features (profils, definitions, sets, snapshots)
  * le risque ML (model_versions, calibration, predictions, uncertainty)
  * la decision (policies, decisions, reviews, overrides)
  * l'audit et l'outcome

Compatibilite : les tables historiques (customers, predictions, audit_log,
model_versions) sont conservees avec leurs colonnes, enrichies de colonnes
autorisees nullables pour ne pas casser l'API existante (consigne : ne pas
casser le socle).
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.db.session import Base


# ---------------------------------------------------------------------------
# Socle multi-tenant / RBAC
# ---------------------------------------------------------------------------


class Institution(Base):
    __tablename__ = "institutions"

    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="ACTIVE"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class Permission(Base):
    __tablename__ = "permissions"

    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.role_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.permission_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("institutions.institution_id"), nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.role_id"), nullable=False
    )
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(200))
    password_hash: Mapped[str | None] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# ---------------------------------------------------------------------------
# Tables historiques conservees (compatibilite API /v1)
# ---------------------------------------------------------------------------


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    age: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Age valide entre 18 et 100"
    )
    seniority_months: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class ModelVersion(Base):
    __tablename__ = "model_versions"

    version_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    mlflow_run_id: Mapped[str | None] = mapped_column(String(100))
    roc_auc: Mapped[float | None] = mapped_column(Float)
    pr_auc: Mapped[float | None] = mapped_column(Float)
    brier_score: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="REGISTERED", nullable=False)
    deployed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    # Enrichissements P0 (autorise nullables)
    model_id: Mapped[str | None] = mapped_column(String(100))
    name: Mapped[str | None] = mapped_column(String(200))
    version: Mapped[str | None] = mapped_column(String(50))
    model_type: Mapped[str | None] = mapped_column(String(50))
    dataset_version: Mapped[str | None] = mapped_column(String(50))
    feature_set_id: Mapped[str | None] = mapped_column(String(50))
    training_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metrics_json: Mapped[dict | None] = mapped_column(JSONB)
    fairness_metrics_json: Mapped[dict | None] = mapped_column(JSONB)
    calibration_version: Mapped[str | None] = mapped_column(String(50))
    artifact_uri: Mapped[str | None] = mapped_column(String(255))
    checksum: Mapped[str | None] = mapped_column(String(128))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[str | None] = mapped_column(String(100))


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    customer_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("customers.customer_id"), nullable=True, index=True
    )
    pd_score: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Probability of default dans [0, 1]"
    )
    confidence_level: Mapped[str] = mapped_column(String(10), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(20), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    features_used: Mapped[dict | None] = mapped_column(JSONB)
    request_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )
    # Enrichissements P0 (autorise nullables)
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.application_id"), index=True
    )
    pd_raw: Mapped[float | None] = mapped_column(Float)
    pd_calibrated: Mapped[float | None] = mapped_column(Float)
    calibration_version: Mapped[str | None] = mapped_column(String(50))
    feature_set_id: Mapped[str | None] = mapped_column(String(50))
    feature_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("feature_snapshots.feature_snapshot_id")
    )
    information_profile_version: Mapped[str | None] = mapped_column(String(50))
    policy_version: Mapped[str | None] = mapped_column(String(50))
    model_version_full: Mapped[str | None] = mapped_column(String(100))
    prediction_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditLog(Base):
    __tablename__ = "audit_log"

    audit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    prediction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("predictions.prediction_id"), index=True
    )
    agent_id: Mapped[str | None] = mapped_column(String(50))
    agent_decision: Mapped[str | None] = mapped_column(String(20))
    agent_justification: Mapped[str | None] = mapped_column(String)
    is_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )


# ---------------------------------------------------------------------------
# Domaine de credit (P0)
# ---------------------------------------------------------------------------


class Client(Base):
    __tablename__ = "clients"

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("institutions.institution_id"), nullable=False
    )
    external_ref: Mapped[str | None] = mapped_column(String(100))
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime)
    gender: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Application(Base):
    __tablename__ = "applications"

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("institutions.institution_id"), nullable=False
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.client_id"), nullable=False, index=True
    )
    product_id: Mapped[str] = mapped_column(String(50), nullable=False)
    requested_amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="XOF")
    requested_term: Mapped[int | None] = mapped_column(Integer)
    purpose: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="DRAFT"
    )
    application_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DataSource(Base):
    __tablename__ = "data_sources"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Consent(Base):
    __tablename__ = "consents"

    consent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.client_id"), nullable=False
    )
    institution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("institutions.institution_id"), nullable=False
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_sources.source_id")
    )
    purpose: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="UNKNOWN")
    version: Mapped[str] = mapped_column(String(20), default="1", nullable=False)
    granted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ApplicationData(Base):
    __tablename__ = "application_data"

    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.application_id"),
        nullable=False,
        index=True,
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_sources.source_id")
    )
    field_name: Mapped[str] = mapped_column(String(200), nullable=False)
    field_value: Mapped[dict | None] = mapped_column(JSONB)
    data_type: Mapped[str | None] = mapped_column(String(50))
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    consent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("consents.consent_id")
    )
    quality_status: Mapped[str | None] = mapped_column(String(20))
    availability_status: Mapped[str | None] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class DataLineage(Base):
    __tablename__ = "data_lineage"

    lineage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.application_id"), nullable=False
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_sources.source_id")
    )
    raw_field: Mapped[str | None] = mapped_column(String(200))
    transformation: Mapped[str | None] = mapped_column(String(200))
    feature: Mapped[str | None] = mapped_column(String(200))
    model_version: Mapped[str | None] = mapped_column(String(50))
    prediction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("predictions.prediction_id")
    )
    decision_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("decisions.decision_id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# ---------------------------------------------------------------------------
# Information / Features (P0)
# ---------------------------------------------------------------------------


class InformationProfile(Base):
    __tablename__ = "information_profiles"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.application_id"), nullable=False
    )
    applicant_status: Mapped[str | None] = mapped_column(String(30))
    credit_depth: Mapped[str] = mapped_column(String(20), nullable=False, default="NONE")
    financial_depth: Mapped[str] = mapped_column(String(20), nullable=False, default="NONE")
    business_depth: Mapped[str] = mapped_column(String(20), nullable=False, default="NONE")
    relationship_depth: Mapped[str] = mapped_column(String(20), nullable=False, default="NONE")
    data_quality: Mapped[str] = mapped_column(String(20), nullable=False, default="UNKNOWN")
    information_state: Mapped[str] = mapped_column(String(20), nullable=False, default="UNKNOWN")
    profile_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    details_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class FeatureDefinition(Base):
    __tablename__ = "feature_definitions"

    feature_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    data_type: Mapped[str | None] = mapped_column(String(50))
    unit: Mapped[str | None] = mapped_column(String(50))
    feature_group: Mapped[str | None] = mapped_column(String(50))
    source: Mapped[str | None] = mapped_column(String(100))
    formula_reference: Mapped[str | None] = mapped_column(Text)
    availability_rule: Mapped[str | None] = mapped_column(Text)
    sensitivity_class: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="PROPOSED", nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1", nullable=False)


class FeatureSet(Base):
    __tablename__ = "feature_sets"

    feature_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1")
    schema_version: Mapped[str] = mapped_column(String(20), default="1", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="EXPERIMENTAL", nullable=False)
    features_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class FeatureSnapshot(Base):
    __tablename__ = "feature_snapshots"

    feature_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.application_id"), nullable=False
    )
    feature_set_id: Mapped[str | None] = mapped_column(String(50))
    feature_schema_version: Mapped[str | None] = mapped_column(String(20))
    features_json: Mapped[dict | None] = mapped_column(JSONB)
    input_snapshot_hash: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# ---------------------------------------------------------------------------
# Risque ML (P0)
# ---------------------------------------------------------------------------


class CalibrationVersion(Base):
    __tablename__ = "calibration_versions"

    calibration_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    model_version_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("model_versions.version_id")
    )
    method: Mapped[str] = mapped_column(String(20), nullable=False)  # PLATT / ISOTONIC
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1")
    validation_metrics: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), default="EXPERIMENTAL", nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class UncertaintyAssessment(Base):
    __tablename__ = "uncertainty_assessments"

    uncertainty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    prediction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("predictions.prediction_id"), nullable=False
    )
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1")
    score: Mapped[float | None] = mapped_column(Float)
    # LOW / MEDIUM / HIGH / UNKNOWN
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="UNKNOWN")
    factors_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# ---------------------------------------------------------------------------
# Decision (P0)
# ---------------------------------------------------------------------------


class DecisionPolicy(Base):
    __tablename__ = "decision_policies"

    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("institutions.institution_id")
    )
    product_id: Mapped[str | None] = mapped_column(String(50))
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1")
    eligibility_rules: Mapped[dict | None] = mapped_column(JSONB)
    approve_rule: Mapped[dict | None] = mapped_column(JSONB)
    review_rule: Mapped[dict | None] = mapped_column(JSONB)
    decline_rule: Mapped[dict | None] = mapped_column(JSONB)
    fallback_rules: Mapped[dict | None] = mapped_column(JSONB)
    effective_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="DRAFT", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[str | None] = mapped_column(String(100))


class Decision(Base):
    __tablename__ = "decisions"

    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.application_id"), nullable=False
    )
    prediction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("predictions.prediction_id")
    )
    policy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("decision_policies.policy_id")
    )
    # APPROVE / REVIEW / DECLINE
    recommendation: Mapped[str] = mapped_column(String(20), nullable=False)
    final_decision: Mapped[str | None] = mapped_column(String(20))
    reason_codes_json: Mapped[dict | None] = mapped_column(JSONB)
    actor_id: Mapped[str | None] = mapped_column(String(100))
    made_by: Mapped[str | None] = mapped_column(String(30))
    requested_amount: Mapped[float | None] = mapped_column(Float)
    approved_amount: Mapped[float | None] = mapped_column(Float)
    proposed_terms_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Review(Base):
    __tablename__ = "reviews"

    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.application_id"), nullable=False
    )
    assigned_to: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_reason: Mapped[str | None] = mapped_column(String(200))
    # APPROVE / DECLINE / REQUEST_INFORMATION
    final_action: Mapped[str | None] = mapped_column(String(30))


class DecisionOverride(Base):
    __tablename__ = "decision_overrides"

    override_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("decisions.decision_id"), nullable=False
    )
    original_recommendation: Mapped[str] = mapped_column(String(20), nullable=False)
    final_decision: Mapped[str] = mapped_column(String(20), nullable=False)
    override_reason: Mapped[str] = mapped_column(Text, nullable=False)
    actor_id: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# ---------------------------------------------------------------------------
# Audit & Outcome (P0)
# ---------------------------------------------------------------------------


class AuditEvent(Base):
    __tablename__ = "audit_events"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    institution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("institutions.institution_id")
    )
    actor_id: Mapped[str | None] = mapped_column(String(100))
    event: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(50))
    entity_id: Mapped[str | None] = mapped_column(String(100))
    request_id: Mapped[str | None] = mapped_column(String(100))
    details_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )


class LoanOutcome(Base):
    __tablename__ = "loan_outcomes"

    outcome_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.application_id"), nullable=False
    )
    loan_id: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str | None] = mapped_column(String(30))
    outcome_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    days_past_due: Mapped[int | None] = mapped_column(Integer)
    default_status: Mapped[bool | None] = mapped_column(Boolean)
    recovery_amount: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
