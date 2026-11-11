# Security & Privacy Governance (DPDP India 2023 & GDPR Privacy Posture)

## 1. Privacy Posture Architecture
The Parcl Buyer Intelligence Platform is engineered to align with:
- India's **Digital Personal Data Protection Act (DPDP Act, 2023)**
- EU **General Data Protection Regulation (GDPR)**
- Institutional investment privacy posture and confidential client identity standards.

## 2. PII Masking & Data Minimization
- **Viewer / Analyst Roles**: Buyer first and last names are deterministically masked at the serialization layer:
  - Example: `John Doe` -> `J*** D***`
  - National identifiers and dates of birth are never exposed across analytical endpoints.
  - Calculated integer ages are anchored to a static reference audit date (`2025-12-31`).
- **Admin Role**: Unmasked access is restricted strictly to users with the `admin` role who possess verified admin keys.

## 3. Cryptographic Token Specifications
- Authentication utilizes HMAC SHA-256 (HS256) JWT access tokens with short lifetimes paired with refresh token rotation.
- Public demo token endpoint `/api/v1/auth/demo-token` is gated behind `PARCL_API_DEMO_AUTH_ENABLED=false` in production.
- Generic OIDC single sign-on integration supported via configurable identity providers.

## 4. Tamper-Evident Append-Only Audit Trail
Every mutative action, dataset context switch, and bulk data export is recorded into the relational `audit_logs` table:
- **Captured Attributes**: `id`, `timestamp` (UTC), `user_id`, `role`, `action`, `resource`, `details`, `ip_address`, `prev_hash`, and `entry_hash`.
- **Cryptographic Chaining**: Each record contains a SHA-256 hash pointer to the previous record (`entry_hash = SHA256(prev_hash + ...)`); verified via `/api/v1/export/audit-logs/verify`.
- **Database & ORM Immutability**: SQLAlchemy listeners strictly prohibit `UPDATE` and `DELETE` on the `audit_logs` table.
- **Query Access**: Restricted strictly to `admin` and `auditor` roles.

## 5. Network & HTTP Defenses
- Explicit CORS whitelist (no wildcard `*` allowed outside local development).
- Rate limiting: Redis-backed sliding window with local in-memory fallback (120 req/min per IP).
- Privacy headers: `Vary: Authorization`, `Cache-Control: private, max-age=60`, role-salted SHA-256 ETags preventing cross-role cache contamination.
