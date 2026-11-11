"""Unit and integration tests for Append-Only Audit Log, SHA-256 Hash Chaining, and Immutability Guards."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.api.db import (
    AuditLogEntity,
    Base,
    compute_audit_entry_hash,
    verify_audit_log_chain,
)


@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_audit_hash_chain_computes_valid_hashes(memory_db):
    """Verify sequential entries form an unbroken cryptographic chain."""
    prev_hash = "GENESIS"
    for i in range(5):
        now_dt = datetime.now(UTC)
        entry_hash = compute_audit_entry_hash(
            prev_hash=prev_hash,
            timestamp=now_dt,
            user_id=f"user-{i}",
            role="analyst",
            action="EXPORT_INITIATED",
            resource=f"/api/v1/export/cohort-{i}",
            details="format=csv",
        )
        entry = AuditLogEntity(
            timestamp=now_dt,
            user_id=f"user-{i}",
            role="analyst",
            action="EXPORT_INITIATED",
            resource=f"/api/v1/export/cohort-{i}",
            details="format=csv",
            prev_hash=prev_hash,
            entry_hash=entry_hash,
        )
        memory_db.add(entry)
        memory_db.commit()
        prev_hash = entry_hash

    # Verify chain integrity
    res = verify_audit_log_chain(memory_db)
    assert res["status"] == "valid"
    assert res["total_records"] == 5
    assert res["tampered"] is False


def test_audit_hash_chain_detects_tampered_record(memory_db):
    """Modifying or tampering with a recorded audit entry must be flagged as tampered."""
    # Insert 3 legitimate entries
    prev_hash = "GENESIS"
    for i in range(3):
        now_dt = datetime.now(UTC)
        entry_hash = compute_audit_entry_hash(
            prev_hash=prev_hash,
            timestamp=now_dt,
            user_id=f"user-{i}",
            role="analyst",
            action="VIEW_OVERVIEW",
            resource="/api/v1/overview",
        )
        entry = AuditLogEntity(
            timestamp=now_dt,
            user_id=f"user-{i}",
            role="analyst",
            action="VIEW_OVERVIEW",
            resource="/api/v1/overview",
            prev_hash=prev_hash,
            entry_hash=entry_hash,
        )
        memory_db.add(entry)
        memory_db.commit()
        prev_hash = entry_hash

    # Manually tamper with entry 2 in raw SQL bypassing ORM listeners
    memory_db.execute(
        AuditLogEntity.__table__.update()
        .where(AuditLogEntity.id == 2)
        .values(action="TAMPERED_ACTION_FORGERY")
    )
    memory_db.commit()

    # Integrity verification must detect corruption
    res = verify_audit_log_chain(memory_db)
    assert res["status"] == "tampered"
    assert res["tampered"] is True
    assert res["broken_at_id"] == 2


def test_audit_entity_orm_immutability_guard(memory_db):
    """SQLAlchemy ORM listener must strictly prohibit UPDATE and DELETE on AuditLogEntity."""
    entry = AuditLogEntity(
        timestamp=datetime.now(UTC),
        user_id="auditor-1",
        role="auditor",
        action="INSPECT_LOGS",
        resource="/api/v1/export/audit-logs",
        prev_hash="GENESIS",
        entry_hash="hash123",
    )
    memory_db.add(entry)
    memory_db.commit()

    # Attempting UPDATE via ORM must raise RuntimeError
    entry.action = "ALTERED_ACTION"
    with pytest.raises(RuntimeError, match="AuditLogEntity is append-only: UPDATE operations are strictly prohibited"):
        memory_db.commit()

    memory_db.rollback()

    # Attempting DELETE via ORM must raise RuntimeError
    entry_to_delete = memory_db.query(AuditLogEntity).first()
    memory_db.delete(entry_to_delete)
    with pytest.raises(RuntimeError, match="AuditLogEntity is append-only: DELETE operations are strictly prohibited"):
        memory_db.commit()
