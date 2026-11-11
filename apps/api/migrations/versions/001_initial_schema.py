"""001_initial_schema

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-11-10 18:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. clients table
    op.create_table(
        "clients",
        sa.Column("client_id", sa.String(length=32), primary_key=True, index=True),
        sa.Column("client_type", sa.String(length=32), nullable=False, index=True),
        sa.Column("first_name", sa.String(length=64), nullable=False),
        sa.Column("last_name", sa.String(length=64), nullable=False),
        sa.Column("date_of_birth", sa.String(length=32), nullable=False),
        sa.Column("gender", sa.String(length=16), nullable=False),
        sa.Column("country", sa.String(length=64), nullable=False, index=True),
        sa.Column("region", sa.String(length=64), nullable=False, index=True),
        sa.Column("acquisition_purpose", sa.String(length=32), nullable=False, index=True),
        sa.Column("satisfaction_score", sa.Integer(), nullable=False),
        sa.Column("loan_applied", sa.Boolean(), nullable=False),
        sa.Column("referral_channel", sa.String(length=32), nullable=False, index=True),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("dataset_scope", sa.String(length=16), server_default="full", index=True),
    )

    # 2. properties table
    op.create_table(
        "properties",
        sa.Column("listing_id", sa.Integer(), primary_key=True, index=True),
        sa.Column("tower_number", sa.Integer(), nullable=False, index=True),
        sa.Column("transaction_date", sa.String(length=32), nullable=False, index=True),
        sa.Column("unit_category", sa.String(length=32), nullable=False, index=True),
        sa.Column("unit_number", sa.Integer(), nullable=False),
        sa.Column("floor_area_sqft", sa.Float(), nullable=False),
        sa.Column("sale_price", sa.Float(), nullable=False),
        sa.Column("listing_status", sa.String(length=32), nullable=False, index=True),
        sa.Column("client_ref", sa.String(length=32), nullable=True, index=True),
        sa.Column("dataset_scope", sa.String(length=16), server_default="full", index=True),
    )

    # 3. client_features table
    op.create_table(
        "client_features",
        sa.Column("client_id", sa.String(length=32), primary_key=True, index=True),
        sa.Column("client_type", sa.String(length=32), nullable=False),
        sa.Column("country", sa.String(length=64), nullable=False),
        sa.Column("region", sa.String(length=64), nullable=False),
        sa.Column("acquisition_purpose", sa.String(length=32), nullable=False),
        sa.Column("referral_channel", sa.String(length=32), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("n_units", sa.Integer(), nullable=False),
        sa.Column("total_spend", sa.Float(), nullable=False),
        sa.Column("avg_price", sa.Float(), nullable=False),
        sa.Column("max_price", sa.Float(), nullable=False),
        sa.Column("avg_floor_area", sa.Float(), nullable=False),
        sa.Column("price_per_sqft", sa.Float(), nullable=False),
        sa.Column("n_towers", sa.Integer(), nullable=False),
        sa.Column("office_share", sa.Float(), nullable=False),
        sa.Column("apartment_share", sa.Float(), nullable=False),
        sa.Column("portfolio_towers_hhi", sa.Float(), nullable=False),
        sa.Column("first_purchase_month", sa.String(length=16), nullable=False),
        sa.Column("last_purchase_month", sa.String(length=16), nullable=False),
        sa.Column("purchase_span_months", sa.Float(), nullable=False),
        sa.Column("is_multi_unit", sa.Boolean(), nullable=False),
        sa.Column("spend_percentile", sa.Float(), nullable=False),
        sa.Column("age_band", sa.String(length=32), nullable=False),
        sa.Column("cluster", sa.Integer(), nullable=False, index=True),
        sa.Column("soft_prob_cluster_0", sa.Float(), nullable=True),
        sa.Column("soft_prob_cluster_1", sa.Float(), nullable=True),
        sa.Column("soft_prob_cluster_2", sa.Float(), nullable=True),
        sa.Column("soft_prob_cluster_3", sa.Float(), nullable=True),
        sa.Column("dataset_scope", sa.String(length=16), server_default="full", index=True),
    )

    # 4. audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("user_id", sa.String(length=64), nullable=False, index=True),
        sa.Column("role", sa.String(length=32), nullable=False, index=True),
        sa.Column("action", sa.String(length=64), nullable=False, index=True),
        sa.Column("resource", sa.String(length=128), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("prev_hash", sa.String(length=64), nullable=True),
        sa.Column("entry_hash", sa.String(length=64), nullable=True, index=True),
    )

    # 5. export_jobs table
    op.create_table(
        "export_jobs",
        sa.Column("job_id", sa.String(length=64), primary_key=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False, index=True),
        sa.Column("format", sa.String(length=16), nullable=False),
        sa.Column("filter_params", sa.Text(), nullable=True),
        sa.Column("record_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("file_path", sa.String(length=256), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("export_jobs")
    op.drop_table("audit_logs")
    op.drop_table("client_features")
    op.drop_table("properties")
    op.drop_table("clients")
