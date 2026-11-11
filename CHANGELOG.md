# Changelog

All notable changes to the Parcl Buyer Intelligence Platform will be documented in this file.

## [2.0.0] - 2026-11-10 - Enterprise Production Hardening

### Added
- **Relational Persistence**: PostgreSQL 16+ support with SQLAlchemy 2.0 and SQLite local development fallback.
- **Enterprise RBAC**: 4-tier role-based access control (`viewer`, `analyst`, `admin`, `auditor`).
- **Security Audit Trail**: Tamper-evident append-only SHA-256 hash-chained `audit_logs` tracking user queries, dataset switches, and bulk exports.
- **Observability**: Prometheus `/metrics` endpoint, Kubernetes `/health/live` and `/health/ready` probes, OpenTelemetry distributed tracing, and RFC 7807 `application/problem+json` error responses.
- **Asynchronous Export Engine**: Idempotent async export jobs with status polling and secure artifact downloads.
- **MLOps & Drift Monitoring**: Population Stability Index (PSI) and Kolmogorov-Smirnov continuous feature drift tests, cluster-mix $\chi^2$ divergence monitoring.
- **Campaign Simulator v2**: Diminishing returns saturating response curves, channel capacity caps, Monte-Carlo 95% confidence intervals, and side-by-side scenario comparison (A vs B).
- **Enterprise Design System**: High-contrast accessibility theme (WCAG 2.2 AA compliant, with AAA-contrast theme available), 8 data-visualization palettes (Okabe-Ito default, Tableau 10, Viridis, Plasma, Coolwarm, Monochrome, Emerald Tech, Oceanic).
- **Internationalization (i18n)**: English (`en`), Hindi (`hi`), German (`de`), and Arabic (`ar` with bidirectional RTL layout engine; non-English machine-translated pending native linguistic review).
- **Accounting Currency Standards**: Configurable INR, USD, EUR with configured conversion rates toggle (as of 2026-11-10) and Lakh/Crore vs Million/Billion number formatting.
- **Export Board Pack**: One-click high-resolution executive print stylesheet for PDF exports.

### Changed
- **Surrogate Decision Tree Metrics**: Deprecated and replaced regression $R^2$ with classification fidelity accuracy (96.55%), macro-F1 (0.965), and $4 \times 4$ empirical confusion matrix.
- **Cluster Overlap Terminology**: Scientifically revised cluster wording from "non-overlapping" to "distinct but overlapping behavioral regimes" with per-cluster silhouette breakdown and Euclidean centroid distance matrices.
- **Currency Disclosure**: Added visible amber notice banner when figures are unscaled relabeled without FX conversion.

### Fixed
- Fixed authentication header preservation in RFC 7807 exception handler ensuring `WWW-Authenticate: Bearer` headers are maintained on 401 Unauthorized responses.
- Fixed database multi-thread SQLite connections during unit testing.
