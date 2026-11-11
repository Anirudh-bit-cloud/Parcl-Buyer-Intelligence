# Parcl Buyer Intelligence Platform v2.0.0

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19.3-61dafb.svg)](https://react.dev/)
[![TypeScript 7](https://img.shields.io/badge/TypeScript-7.0-3178c6.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-4.3-38bdf8.svg)](https://tailwindcss.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7+-dc382d.svg)](https://redis.io/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-e6522c.svg)](https://prometheus.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: 103 Pytest](https://img.shields.io/badge/Pytest-103%20passed-success.svg)](packages/core/tests)
[![Tests: 32 Vitest](https://img.shields.io/badge/Vitest-32%20passed-success.svg)](apps/web/src/test)

Production-grade buyer segmentation, portfolio intelligence, and property allocation platform for **Parcl Co. Limited** (in collaboration with **Unified Mentor**). Grounded on empirical multi-unit buyer records, audited Model B3 cluster inference, and enterprise governance standards.

---

## 📖 Executive Abstract

Real estate development platforms often suffer from uniform, one-size-fits-all customer targeting due to unobserved heterogeneity across demographic, financial, and geographic buyer behaviors. This platform implements an unsupervised machine learning architecture (**Model B3**) over an empirical multi-unit portfolio cohort (2,000 unique buyers across 7,305 transacted units in 20 development towers).

The enterprise system integrates:
1. **Relational Persistence**: PostgreSQL 16+ (SQLAlchemy 2.0 + Alembic) with zero-configuration SQLite local fallback (`data/parcl.db`).
2. **Four-Tier RBAC**: `viewer`, `analyst` (masked PII), `admin` (unmasked microdata & export), and `auditor` (governance & audit trail).
3. **Auditability & Security**: Tamper-evident append-only SHA-256 hash-chained `audit_logs` tracking sensitive exports, aligned with DPDP (India 2023) and GDPR privacy posture.
4. **Observability**: Prometheus `/metrics` scraping, Kubernetes `/health/live` and `/health/ready` probes, OpenTelemetry distributed tracing, and RFC 7807 `application/problem+json` error semantics.
5. **Continuous MLOps**: Live Population Stability Index (PSI) and Kolmogorov-Smirnov drift monitoring, descriptive disparity reports on age and geography, and Model Card auto-generation.
6. **Campaign Simulator v2**: Diminishing returns saturating response curves, channel capacity caps, Monte-Carlo 95% confidence intervals, and side-by-side scenario comparison (A vs B).
7. **Enterprise Frontend**: React 19 + TypeScript + Tailwind with 8 data-visualization palettes (Okabe-Ito default), Light/Dark/High-Contrast modes (WCAG 2.2 AA compliant, with AAA-contrast theme available), i18n localization (English, plus Hindi, German, Arabic RTL machine-translated, pending native linguistic review), and one-click PDF Board Pack export.

---

## 🏛️ System Architecture

```
parcl-buyer-intelligence/
├── packages/core/              # Core ML Engine & Analytics Suite
│   ├── parcl_core/
│   │   ├── cleaning.py         # Dual-format DOB parsing & deterministic age
│   │   ├── features.py         # 84-feature extraction, portfolio HHI, tenure
│   │   ├── schemas.py          # Pandera strict DataFrame validation schemas
│   │   ├── encoding.py         # ColumnTransformer with 0.5x geo downweighting
│   │   ├── recommend.py        # Cosine NBO, campaign simulator v2, CLV baseline
│   │   ├── drift.py            # PSI, Kolmogorov-Smirnov, cluster-mix drift
│   │   ├── registry.py         # Model card generator, dataset hashing, fairness
│   │   ├── clustering/         # KMeans, Ward Hierarchical, GMM diagnostics
│   │   └── explain.py          # Surrogate tree classification metrics & TreeSHAP
│   └── tests/                  # Core mathematical & invariant tests
├── apps/api/                   # Production FastAPI REST Backend
│   ├── main.py                 # FastAPI app, RFC 7807, CORS, ETag, OpenTelemetry
│   ├── db.py                   # SQLAlchemy 2.0 schema, PostgreSQL/SQLite engine
│   ├── auth.py                 # JWT authentication & 4-tier RBAC
│   ├── middleware.py           # Request-ID, Structured JSON logger, Rate-limiting
│   ├── routers/                # 15 REST routers (Health, Export, Audit, Governance...)
│   └── tests/                  # 68 API contract, security & invariant tests
├── apps/web/                   # Enterprise B2B Analytics SPA
│   ├── src/
│   │   ├── components/         # Design system: ChartCard, KPICard, DataTable...
│   │   ├── design/             # Tokens, 8 palettes, Light/Dark/High-Contrast
│   │   ├── pages/              # 12 modules (Overview, Segments, Model Lab...)
│   │   ├── stores/             # Zustand stores (Theme, Auth, Dataset, Currency)
│   │   ├── utils/              # i18n (en, hi, de, ar-RTL), Currency & formatters
│   │   └── test/               # 32 Vitest tests + axe-core accessibility suite
├── data/
│   ├── raw/                    # Audited production baseline CSVs & prd.pdf
│   ├── processed/              # Cleaned Parquet tables & client features
│   ├── models/                 # Serialized cluster_models.joblib
│   └── parcl.db                # Relational SQLite local fallback database
├── docker-compose.yml          # Production multi-container orchestration
├── Dockerfile                  # Multi-stage production container build
└── docs/                       # Architecture C4 diagrams, ADRs, runbook, security note
```

---

## 🎯 Discovered Buyer Archetypes (Model B3)

| Cluster | Archetype Name | Population Share | Defining Profile | Strategic Action |
|:---:|---|:---:|---|---|
| **C0** | **Emerging Multi-Tower Accumulators** | **27.5%** | Younger (mean age 42.1), 4.1 units, multi-tower footprint, mixed portfolio. | Target pre-launch towers, multi-unit bulk incentives. |
| **C1** | **Concentrated Residential Buyers** | **25.0%** | Exactly 3.0 units, 0.0% office share (100% residential), mean age 54.1. | Pitch residential suites; zero commercial targeting. |
| **C2** | **Commercial Office Diversifiers** | **25.0%** | High commercial focus (37.8% office share), 3.0 units, yield-seeking. | Target premium commercial office inventory. |
| **C3** | **Established Senior Estate Investors** | **22.5%** | Senior (mean age 69.2), 4.4 units, largest total spend, long hold periods. | High-value estate preservation and luxury assets. |

---

## 🚀 Quickstart & Deployment

### Option 1: Docker Compose (Recommended Enterprise Production)
Runs the complete stack with API, Web UI, PostgreSQL 16, Redis 7, and Prometheus:
```bash
docker compose up -d --build
```
Access the dashboard at `http://localhost:8000/app` or inspect API documentation at `http://localhost:8000/docs`.

### Option 2: Local Developer Mode
```bash
# 1. Install Python packages
pip install -e packages/core
pip install -e apps/api

# 2. Seed database
python -m apps.api.services.db_seeder

# 3. Start Backend
uvicorn apps.api.main:app --reload --port 8000

# 4. Start Frontend
cd apps/web
npm install
npm run dev
```

---

## 🧪 Verification & Test Battery

```bash
# Backend Pytest Suite (68 API + 38 Core tests)
python -m pytest

# Frontend Vitest Suite (32 tests + axe-core accessibility)
cd apps/web && npm test -- --run

# TypeScript Typecheck & Vite Production Build
cd apps/web && npx tsc --noEmit && npm run build
```

---

## 🔒 Governance, Disclosures & Standards
- **Zero Fabrication**: All figures displayed are mathematically computed from data or explicitly labeled heuristic assumptions.
- **Currency Standards**: Conforms to Indian Rupees (**₹ INR**) by default with Lakh/Crore digit grouping. Live mathematical FX conversion (₹83.50/USD) is configurable in the top-bar. When unscaled relabeling is active, a mandatory disclosure banner is rendered.
- **Accessibility**: Validated against WCAG 2.2 AA standards with automated axe-core CI assertions.
