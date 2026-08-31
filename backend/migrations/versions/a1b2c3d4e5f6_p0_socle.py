"""P0 - socle Adaptive Credit Decision Engine

Introduit les tables du cœur métier : multi-tenancy/RBAC, domaine de
crédit, information/features, calibration/uncertainty, décision, audit et
outcome. Enrichit prescriptions et model_versions de colonnes autorisées
nullables (compatibilité API /v1 conservée).

Revision ID: a1b2c3d4e5f6
Revises: 4802eb20ba6b
Create Date: 2026-08-31 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "4802eb20ba6b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Multi-tenancy / RBAC ---
    op.create_table(
        "institutions",
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("institution_id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "roles",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("role_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "permissions",
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("permission_id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.permission_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.role_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )
    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=200), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.institution_id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.role_id"]),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("username"),
    )

    # --- Domaine de crédit ---
    op.create_table(
        "clients",
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_ref", sa.String(length=100), nullable=True),
        sa.Column("first_name", sa.String(length=100), nullable=True),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("date_of_birth", sa.DateTime(), nullable=True),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.institution_id"]),
        sa.PrimaryKeyConstraint("client_id"),
    )
    op.create_table(
        "applications",
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", sa.String(length=50), nullable=False),
        sa.Column("requested_amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("requested_term", sa.Integer(), nullable=True),
        sa.Column("purpose", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("application_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.institution_id"]),
        sa.PrimaryKeyConstraint("application_id"),
    )
    op.create_index(
        op.f("ix_applications_client_id"), "applications", ["client_id"], unique=False
    )
    op.create_table(
        "data_sources",
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("source_id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "consents",
        sa.Column("consent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purpose", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["client_id"], ["clients.client_id"]),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.institution_id"]),
        sa.ForeignKeyConstraint(["source_id"], ["data_sources.source_id"]),
        sa.PrimaryKeyConstraint("consent_id"),
    )
    op.create_table(
        "application_data",
        sa.Column("entry_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("field_name", sa.String(length=200), nullable=False),
        sa.Column("field_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("data_type", sa.String(length=50), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("quality_status", sa.String(length=20), nullable=True),
        sa.Column("availability_status", sa.String(length=30), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["application_id"], ["applications.application_id"]),
        sa.ForeignKeyConstraint(["consent_id"], ["consents.consent_id"]),
        sa.ForeignKeyConstraint(["source_id"], ["data_sources.source_id"]),
        sa.PrimaryKeyConstraint("entry_id"),
    )
    op.create_index(
        op.f("ix_application_data_application_id"),
        "application_data",
        ["application_id"],
        unique=False,
    )

    # --- Information / features ---
    op.create_table(
        "information_profiles",
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("applicant_status", sa.String(length=30), nullable=True),
        sa.Column("credit_depth", sa.String(length=20), nullable=False),
        sa.Column("financial_depth", sa.String(length=20), nullable=False),
        sa.Column("business_depth", sa.String(length=20), nullable=False),
        sa.Column("relationship_depth", sa.String(length=20), nullable=False),
        sa.Column("data_quality", sa.String(length=20), nullable=False),
        sa.Column("information_state", sa.String(length=20), nullable=False),
        sa.Column("profile_version", sa.String(length=50), nullable=False),
        sa.Column("details_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["application_id"], ["applications.application_id"]),
        sa.PrimaryKeyConstraint("profile_id"),
    )
    op.create_table(
        "feature_definitions",
        sa.Column("feature_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("data_type", sa.String(length=50), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("feature_group", sa.String(length=50), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("formula_reference", sa.Text(), nullable=True),
        sa.Column("availability_rule", sa.Text(), nullable=True),
        sa.Column("sensitivity_class", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("feature_id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "feature_sets",
        sa.Column("feature_set_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.Column("schema_version", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("features_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("feature_set_id"),
        sa.UniqueConstraint("code"),
    )

    # --- Enrichissement model_versions et predictions (compatibles) ---
    op.add_column(
        "model_versions",
        sa.Column("model_id", sa.String(length=100), nullable=True),
    )
    op.add_column("model_versions", sa.Column("name", sa.String(length=200), nullable=True))
    op.add_column("model_versions", sa.Column("version", sa.String(length=50), nullable=True))
    op.add_column(
        "model_versions", sa.Column("model_type", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "model_versions", sa.Column("dataset_version", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "model_versions", sa.Column("feature_set_id", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "model_versions", sa.Column("training_date", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "model_versions",
        sa.Column("metrics_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "model_versions",
        sa.Column("fairness_metrics_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "model_versions", sa.Column("calibration_version", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "model_versions", sa.Column("artifact_uri", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "model_versions", sa.Column("checksum", sa.String(length=128), nullable=True)
    )
    op.add_column(
        "model_versions", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "model_versions", sa.Column("approved_by", sa.String(length=100), nullable=True)
    )

    op.create_table(
        "calibration_versions",
        sa.Column("calibration_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_version_id", sa.Integer(), nullable=True),
        sa.Column("method", sa.String(length=20), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.Column(
            "validation_metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.version_id"]),
        sa.PrimaryKeyConstraint("calibration_id"),
    )
    op.create_table(
        "feature_snapshots",
        sa.Column("feature_snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("feature_set_id", sa.String(length=50), nullable=True),
        sa.Column("feature_schema_version", sa.String(length=20), nullable=True),
        sa.Column("features_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("input_snapshot_hash", sa.String(length=128), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["application_id"], ["applications.application_id"]),
        sa.PrimaryKeyConstraint("feature_snapshot_id"),
    )
    op.add_column("predictions", sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("predictions", sa.Column("pd_raw", sa.Float(), nullable=True))
    op.add_column("predictions", sa.Column("pd_calibrated", sa.Float(), nullable=True))
    op.add_column(
        "predictions", sa.Column("calibration_version", sa.String(length=50), nullable=True)
    )
    op.add_column("predictions", sa.Column("feature_set_id", sa.String(length=50), nullable=True))
    op.add_column("predictions", sa.Column("feature_snapshot_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column(
        "predictions", sa.Column("information_profile_version", sa.String(length=50), nullable=True)
    )
    op.add_column("predictions", sa.Column("policy_version", sa.String(length=50), nullable=True))
    op.add_column("predictions", sa.Column("model_version_full", sa.String(length=100), nullable=True))
    op.add_column(
        "predictions", sa.Column("prediction_timestamp", sa.DateTime(timezone=True), nullable=True)
    )
    op.create_foreign_key(
        "fk_predictions_application", "predictions", "applications", ["application_id"], ["application_id"]
    )
    op.create_index(
        op.f("ix_predictions_application_id"), "predictions", ["application_id"], unique=False
    )
    op.create_foreign_key(
        "fk_predictions_snapshot",
        "predictions",
        "feature_snapshots",
        ["feature_snapshot_id"],
        ["feature_snapshot_id"],
    )
    op.create_table(
        "uncertainty_assessments",
        sa.Column("uncertainty_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prediction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("method", sa.String(length=50), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("factors_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["prediction_id"], ["predictions.prediction_id"]),
        sa.PrimaryKeyConstraint("uncertainty_id"),
    )

    # --- Décision ---
    op.create_table(
        "decision_policies",
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", sa.String(length=50), nullable=True),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.Column("eligibility_rules", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("approve_rule", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("review_rule", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("decline_rule", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("fallback_rules", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.institution_id"]),
        sa.PrimaryKeyConstraint("policy_id"),
    )
    op.create_table(
        "decisions",
        sa.Column("decision_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prediction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("recommendation", sa.String(length=20), nullable=False),
        sa.Column("final_decision", sa.String(length=20), nullable=True),
        sa.Column("reason_codes_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("actor_id", sa.String(length=100), nullable=True),
        sa.Column("made_by", sa.String(length=30), nullable=True),
        sa.Column("requested_amount", sa.Float(), nullable=True),
        sa.Column("approved_amount", sa.Float(), nullable=True),
        sa.Column("proposed_terms_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["application_id"], ["applications.application_id"]),
        sa.ForeignKeyConstraint(["policy_id"], ["decision_policies.policy_id"]),
        sa.ForeignKeyConstraint(["prediction_id"], ["predictions.prediction_id"]),
        sa.PrimaryKeyConstraint("decision_id"),
    )
    op.create_table(
        "reviews",
        sa.Column("review_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_to", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_reason", sa.String(length=200), nullable=True),
        sa.Column("final_action", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(["application_id"], ["applications.application_id"]),
        sa.PrimaryKeyConstraint("review_id"),
    )
    op.create_table(
        "decision_overrides",
        sa.Column("override_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("original_recommendation", sa.String(length=20), nullable=False),
        sa.Column("final_decision", sa.String(length=20), nullable=False),
        sa.Column("override_reason", sa.Text(), nullable=False),
        sa.Column("actor_id", sa.String(length=100), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["decision_id"], ["decisions.decision_id"]),
        sa.PrimaryKeyConstraint("override_id"),
    )
    op.create_table(
        "data_lineage",
        sa.Column("lineage_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("raw_field", sa.String(length=200), nullable=True),
        sa.Column("transformation", sa.String(length=200), nullable=True),
        sa.Column("feature", sa.String(length=200), nullable=True),
        sa.Column("model_version", sa.String(length=50), nullable=True),
        sa.Column("prediction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("decision_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["application_id"], ["applications.application_id"]),
        sa.ForeignKeyConstraint(["decision_id"], ["decisions.decision_id"]),
        sa.ForeignKeyConstraint(["prediction_id"], ["predictions.prediction_id"]),
        sa.ForeignKeyConstraint(["source_id"], ["data_sources.source_id"]),
        sa.PrimaryKeyConstraint("lineage_id"),
    )

    # --- Audit & Outcome ---
    op.create_table(
        "audit_events",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_id", sa.String(length=100), nullable=True),
        sa.Column("event", sa.String(length=50), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=True),
        sa.Column("entity_id", sa.String(length=100), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("details_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.institution_id"]),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index(
        op.f("ix_audit_events_created_at"), "audit_events", ["created_at"], unique=False
    )
    op.create_table(
        "loan_outcomes",
        sa.Column("outcome_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("loan_id", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("outcome_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("days_past_due", sa.Integer(), nullable=True),
        sa.Column("default_status", sa.Boolean(), nullable=True),
        sa.Column("recovery_amount", sa.Float(), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["application_id"], ["applications.application_id"]),
        sa.PrimaryKeyConstraint("outcome_id"),
    )


def downgrade() -> None:
    """Downgrade schema P0."""
    op.drop_table("loan_outcomes")
    op.drop_index(op.f("ix_audit_events_created_at"), table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_table("data_lineage")
    op.drop_table("decision_overrides")
    op.drop_table("reviews")
    op.drop_table("decisions")
    op.drop_table("decision_policies")
    op.drop_table("uncertainty_assessments")
    op.drop_constraint("fk_predictions_snapshot", "predictions", type_="foreignkey")
    op.drop_index(op.f("ix_predictions_application_id"), table_name="predictions")
    op.drop_constraint("fk_predictions_application", "predictions", type_="foreignkey")
    op.drop_column("predictions", "prediction_timestamp")
    op.drop_column("predictions", "model_version_full")
    op.drop_column("predictions", "policy_version")
    op.drop_column("predictions", "information_profile_version")
    op.drop_column("predictions", "feature_snapshot_id")
    op.drop_column("predictions", "feature_set_id")
    op.drop_column("predictions", "calibration_version")
    op.drop_column("predictions", "pd_calibrated")
    op.drop_column("predictions", "pd_raw")
    op.drop_column("predictions", "application_id")
    op.drop_table("feature_snapshots")
    op.drop_table("calibration_versions")
    op.drop_column("model_versions", "approved_by")
    op.drop_column("model_versions", "approved_at")
    op.drop_column("model_versions", "checksum")
    op.drop_column("model_versions", "artifact_uri")
    op.drop_column("model_versions", "calibration_version")
    op.drop_column("model_versions", "fairness_metrics_json")
    op.drop_column("model_versions", "metrics_json")
    op.drop_column("model_versions", "training_date")
    op.drop_column("model_versions", "feature_set_id")
    op.drop_column("model_versions", "dataset_version")
    op.drop_column("model_versions", "model_type")
    op.drop_column("model_versions", "version")
    op.drop_column("model_versions", "name")
    op.drop_column("model_versions", "model_id")
    op.drop_table("feature_sets")
    op.drop_table("feature_definitions")
    op.drop_table("information_profiles")
    op.drop_index(op.f("ix_application_data_application_id"), table_name="application_data")
    op.drop_table("application_data")
    op.drop_table("consents")
    op.drop_table("data_sources")
    op.drop_index(op.f("ix_applications_client_id"), table_name="applications")
    op.drop_table("applications")
    op.drop_table("clients")
    op.drop_table("users")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("institutions")
