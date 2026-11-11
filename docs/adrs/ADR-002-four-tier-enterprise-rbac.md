# ADR-002: Four-Tier Enterprise Role-Based Access Control (RBAC)

## Status
Accepted (v2.0.0)

## Context
Enterprise institutional clients require granular data segregation to comply with GDPR and India's Digital Personal Data Protection (DPDP) Act 2023. Capstone had basic Analyst vs Admin roles.

## Decision
We established a strict 4-tier RBAC matrix:
1. `viewer`: Read-only access to high-level executive dashboards and segment aggregates. PII fully masked. Cannot export data.
2. `analyst`: Full analytical access to Behavior Lab, Geo Intelligence, Tower Heatmap, NBO, and Campaign Simulator. Client names masked (`J*** D***`). Cannot export bulk raw microdata.
3. `admin`: Unrestricted operational control: dataset switching, unmasked PII inspection, synchronous and asynchronous bulk data export, and system configuration. Requires administrative API key to issue tokens.
4. `auditor`: Compliance role granting read access to the immutable security audit trail (`audit_logs`), model cards, data quality lineage, and asynchronous export logs.

## Consequences
- Guaranteed compliance with institutional security and privacy standards.
- Cryptographically signed JWT tokens with short TTLs and role claims.
