# Operations & Deployment Runbook

## 1. Quickstart (Docker Compose)
To launch the complete enterprise production stack in under 5 minutes:

```bash
# 1. Clone repository
git clone https://github.com/organization/parcl-buyer-intelligence.git
cd parcl-buyer-intelligence

# 2. Build and start containers (API, Web SPA, PostgreSQL 16, Redis 7, Prometheus)
docker compose up -d --build

# 3. Verify health status
curl -f http://localhost:8000/health/ready
```

Dashboard access: `http://localhost:8000/app` (or `http://localhost:5173` in local dev).

## 2. Health & Liveness Probes
- **Liveness Probe**: `GET /health/live` (returns HTTP 200 `{"status": "alive"}`).
- **Readiness Probe**: `GET /health/ready` (checks PostgreSQL/SQLite connectivity, Redis ping, and client feature record counts).
- **Prometheus Metrics**: `GET /metrics` (scrapes OpenMetrics application counters and latency histograms).

## 3. Database Management & Seeding
```bash
# Seed or migrate relational schema
python -m apps.api.services.db_seeder

# Connect to PostgreSQL directly
docker exec -it parcl_postgres psql -U parcl_user -d parcl_db
```

## 4. Drift Monitoring Routine
A scheduled cron or Kubernetes CronJob triggers live drift evaluation:
```bash
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/v1/governance/drift
```
- If `max_psi >= 0.25`: Alert desk engineers for model retraining.
- If `0.10 <= max_psi < 0.25`: Moderate drift warning; monitor incoming quarterly cohorts.

## 5. Backup & Disaster Recovery
```bash
# Backup PostgreSQL Database
docker exec -t parcl_postgres pg_dumpall -c -U parcl_user > backup_$(date +%Y%m%d).sql

# Restore PostgreSQL Database
cat backup_20261110.sql | docker exec -i parcl_postgres psql -U parcl_user -d parcl_db
```
