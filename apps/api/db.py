"""SQLAlchemy 2.0 Database Models and Engine Management."""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Generator
from datetime import UTC, datetime
from typing import Any, cast

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from apps.api.config import api_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Declarative Base for all Parcl persistence entities."""
    pass


class ClientEntity(Base):
    """Clean multi-unit client buyer entity."""

    __tablename__ = "clients"

    client_id = Column(String(32), primary_key=True, index=True)
    client_type = Column(String(32), nullable=False, index=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    date_of_birth = Column(String(32), nullable=False)
    gender = Column(String(16), nullable=False)
    country = Column(String(64), nullable=False, index=True)
    region = Column(String(64), nullable=False, index=True)
    acquisition_purpose = Column(String(32), nullable=False, index=True)
    satisfaction_score = Column(Integer, nullable=False)
    loan_applied = Column(Boolean, nullable=False)
    referral_channel = Column(String(32), nullable=False, index=True)
    age = Column(Integer, nullable=False)
    dataset_scope = Column(String(16), default="full", index=True)  # 'full' or 'sample'


class PropertyEntity(Base):
    """Property inventory entity spanning both Sold and Available inventory."""

    __tablename__ = "properties"

    listing_id = Column(Integer, primary_key=True, index=True)
    tower_number = Column(Integer, nullable=False, index=True)
    transaction_date = Column(String(32), nullable=False, index=True)
    unit_category = Column(String(32), nullable=False, index=True)
    unit_number = Column(Integer, nullable=False)
    floor_area_sqft = Column(Float, nullable=False)
    sale_price = Column(Float, nullable=False)
    listing_status = Column(String(32), nullable=False, index=True)  # 'Sold' or 'Available'
    client_ref = Column(String(32), nullable=True, index=True)
    dataset_scope = Column(String(16), default="full", index=True)


class ClientFeaturesEntity(Base):
    """84-dimension derived behavioral features and Model B3 cluster assignments."""

    __tablename__ = "client_features"

    client_id = Column(String(32), primary_key=True, index=True)
    client_type = Column(String(32), nullable=False)
    country = Column(String(64), nullable=False)
    region = Column(String(64), nullable=False)
    acquisition_purpose = Column(String(32), nullable=False)
    referral_channel = Column(String(32), nullable=False)
    age = Column(Integer, nullable=False)
    n_units = Column(Integer, nullable=False)
    total_spend = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    avg_floor_area = Column(Float, nullable=False)
    price_per_sqft = Column(Float, nullable=False)
    n_towers = Column(Integer, nullable=False)
    office_share = Column(Float, nullable=False)
    apartment_share = Column(Float, nullable=False)
    portfolio_towers_hhi = Column(Float, nullable=False)
    first_purchase_month = Column(String(16), nullable=False)
    last_purchase_month = Column(String(16), nullable=False)
    purchase_span_months = Column(Float, nullable=False)
    is_multi_unit = Column(Boolean, nullable=False)
    spend_percentile = Column(Float, nullable=False)
    age_band = Column(String(32), nullable=False)
    cluster = Column(Integer, nullable=False, index=True)
    soft_prob_cluster_0 = Column(Float, nullable=True)
    soft_prob_cluster_1 = Column(Float, nullable=True)
    soft_prob_cluster_2 = Column(Float, nullable=True)
    soft_prob_cluster_3 = Column(Float, nullable=True)
    dataset_scope = Column(String(16), default="full", index=True)


class AuditLogEntity(Base):
    """Immutable, append-only, tamper-evident audit trail with SHA-256 hash chaining."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    role = Column(String(32), nullable=False, index=True)
    action = Column(String(64), nullable=False, index=True)
    resource = Column(String(128), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)
    prev_hash = Column(String(64), nullable=True)
    entry_hash = Column(String(64), nullable=True, index=True)


@event.listens_for(AuditLogEntity, "before_update")
def block_audit_log_update(mapper: Any, connection: Any, target: Any) -> None:
    """Enforce append-only constraint: prevent any updates to audit log entries."""
    raise RuntimeError("AuditLogEntity is append-only: UPDATE operations are strictly prohibited.")


@event.listens_for(AuditLogEntity, "before_delete")
def block_audit_log_delete(mapper: Any, connection: Any, target: Any) -> None:
    """Enforce append-only constraint: prevent deletion of audit log entries."""
    raise RuntimeError("AuditLogEntity is append-only: DELETE operations are strictly prohibited.")


def _format_audit_timestamp(ts: datetime | str | None) -> str:
    """Format timestamp consistently across SQLite and PostgreSQL."""
    if isinstance(ts, datetime):
        return ts.strftime("%Y-%m-%dT%H:%M:%S")
    return str(ts or "")[:19].replace(" ", "T")


def compute_audit_entry_hash(
    prev_hash: str | None,
    timestamp: datetime | str | None,
    user_id: str,
    role: str,
    action: str,
    resource: str,
    details: str | None = None,
) -> str:
    """Compute SHA-256 hash for tamper-evident audit chaining."""
    ts_str = _format_audit_timestamp(timestamp)
    seed = f"{prev_hash or 'GENESIS'}|{ts_str}|{user_id}|{role}|{action}|{resource}|{details or ''}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def verify_audit_log_chain(session: Session) -> dict[str, Any]:
    """Verify cryptographic integrity of audit log hash chain."""
    entries = session.query(AuditLogEntity).order_by(AuditLogEntity.id.asc()).all()
    if not entries:
        return {"status": "valid", "total_records": 0, "tampered": False}

    prev_hash = "GENESIS"
    for entry in entries:
        if entry.prev_hash != prev_hash:
            return {
                "status": "tampered",
                "tampered": True,
                "broken_at_id": entry.id,
                "reason": "Previous hash pointer mismatch",
                "expected_prev_hash": prev_hash,
                "actual_prev_hash": entry.prev_hash,
            }
        expected_hash = compute_audit_entry_hash(
            str(prev_hash),
            cast(Any, entry.timestamp),
            str(entry.user_id),
            str(entry.role),
            str(entry.action),
            str(entry.resource),
            str(entry.details) if entry.details is not None else None,
        )
        if entry.entry_hash and entry.entry_hash != expected_hash:
            return {
                "status": "tampered",
                "tampered": True,
                "broken_at_id": int(entry.id),
                "reason": "Entry hash signature invalid",
                "expected_hash": expected_hash,
                "actual_hash": str(entry.entry_hash),
            }
        prev_hash = str(entry.entry_hash or expected_hash)

    return {"status": "valid", "total_records": len(entries), "tampered": False}


class ExportJobEntity(Base):
    """Asynchronous and idempotent export job tracker."""

    __tablename__ = "export_jobs"

    job_id = Column(String(64), primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    user_id = Column(String(64), nullable=False)
    role = Column(String(32), nullable=False)
    status = Column(String(32), default="pending", nullable=False, index=True)  # pending, completed, failed
    format = Column(String(16), nullable=False)  # csv, parquet, excel
    filter_params = Column(Text, nullable=True)
    record_count = Column(Integer, default=0)
    file_path = Column(String(256), nullable=True)
    error_message = Column(Text, nullable=True)


# Database Engine and Session Factory
connect_args = {"check_same_thread": False} if api_settings.database_url.startswith("sqlite") else {}
engine = create_engine(
    api_settings.database_url,
    echo=api_settings.database_echo,
    connect_args=connect_args,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully via SQLAlchemy.")
    except Exception as exc:
        logger.error("Failed to initialize database tables: %s", exc)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
