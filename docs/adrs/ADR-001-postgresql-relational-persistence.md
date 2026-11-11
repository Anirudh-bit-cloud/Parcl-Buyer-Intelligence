# ADR-001: Migration to PostgreSQL with SQLAlchemy 2.0 and SQLite Dual Engine

## Status
Accepted (v2.0.0)

## Context
The capstone system relied on ephemeral flat parquet and CSV files loaded in-memory on application start. While high performance for analytical queries, institutional enterprise deployment requires:
1. ACID-compliant relational persistence for multi-tenant data management.
2. Immutable audit logging of administrative exports and sensitive PII access.
3. Asynchronous idempotent export job tracking.
4. Production zero-downtime database migrations via Alembic.

## Decision
We adopted SQLAlchemy 2.0 with a dual-engine architecture:
- Primary Engine: PostgreSQL 16+ via `psycopg2` / `asyncpg` connection pool.
- Local Fallback Engine: SQLite (`data/parcl.db`) enabling zero-configuration developer onboarding and offline execution.
- Parquet remains the high-throughput interchange and batch ingestion format.

## Consequences
- Clean separation between transactional relational state and analytical query caches.
- Complete auditability of every data export and model change.
