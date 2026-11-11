# ADR-004: Multilingual Support, Accounting Currency, and Foreign Exchange Standards

## Status
Accepted (v2.0.0)

## Context
Phase 0 audit identified that raw USD values from property transactions were directly relabeled with the Indian Rupee symbol (₹) without currency conversion.

## Decision
1. Introduced configurable currency standards (`INR`, `USD`, `EUR`) and live foreign exchange conversion (`fx_rate_usd_to_inr = 83.50`).
2. Added `apply_fx_conversion` boolean setting (default `False`). When `False`, values remain unscaled and a mandatory disclosure badge is displayed in the UI: *"Values relabeled directly without foreign exchange conversion."*
3. Number grouping supports both Indian Lakh/Crore (`12,74,771`) and International Million/Billion (`1,274,771`).
4. Multilingual support for English (`en`), Hindi (`hi`), German (`de`), and Arabic (`ar`) with bidirectional RTL layout engine.

## Consequences
- Complete transparency regarding accounting and currency conventions.
- Frictionless deployment for global institutional investment desks.
