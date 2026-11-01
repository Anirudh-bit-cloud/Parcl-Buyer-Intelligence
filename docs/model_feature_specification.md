# Phase 2 Feature Specification: Model A and Model B Feature Sets

**Program Sponsor**: Unified Mentor  
**Target Enterprise**: Parcl Co. Limited  
**Status**: Guardrails Enforced (Prior to Phase 2 Code Execution)

---

## 1. Explicit Exclusions & Anti-Circularity Guardrails

Per strict business & data science guardrails:
1. **Total Spend Excluded from Clustering**: `total_spend` is strictly excluded from clustering features.
2. **Unit Pricing Excluded from Clustering**: `avg_price`, `max_price`, and `min_price` are strictly excluded from clustering features.
3. **Usage of Financial Metrics**: Total spend and unit prices are reserved exclusively for **orthogonal profiling, lifetime-value analysis, and validation tables**.
4. **Transformation Policy**: `n_units` is transformed via QuantileTransformer / log1p to mitigate positive skew without distorting centroid distances.

---

## 2. Model A Feature List (Exact PRD Step 2 Baseline)

Model A replicates the exact feature set articulated in PRD Step 2 & 3:

| # | Feature Name | Raw Source | Type | Encoding / Scaling Policy |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `age` | `date_of_birth` | Continuous | `StandardScaler` (Integer age at 2025-12-31) |
| 2 | `satisfaction_score` | `satisfaction_score` | Numeric / Ordinal | `StandardScaler` (1–5 scale) |
| 3 | `client_type` | `client_type` | Nominal | One-Hot Encoded (`INDIVIDUAL`, `COMPANY`) |
| 4 | `acquisition_purpose` | `acquisition_purpose`| Nominal | One-Hot Encoded (`HOME`, `INVESTMENT`) |
| 5 | `referral_channel` | `referral_channel` | Nominal | One-Hot Encoded (`Website`, `Agency`, `Client`) |
| 6 | `country` | `country` | Nominal | One-Hot Encoded (Top countries, rare to 'Other') |
| 7 | `region` | `region` | Nominal | Grouped One-Hot Encoded |

*Total Feature Dimensions (post-encoding)*: ~25 sparse binary and standard-scaled dimensions.

---

## 3. Model B Feature List (Enriched Behavioral & Portfolio Model)

Model B enriches client representation using behavioral intent, asset-type preferences, and portfolio structure while strictly barring monetary spend variables:

### Core Behavioral & Structural Features
| # | Feature Name | Description | Type | Transformation Policy |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `age` | Integer age at 2025-12-31 | Continuous | `StandardScaler` |
| 2 | `loan_applied` | Financing reliance indicator | Binary | Boolean flag (0 / 1) |
| 3 | `client_type` | Corporate vs. Individual entity | Nominal | One-Hot Encoded |
| 4 | `acquisition_purpose`| Investment vs. Home purchase intent | Nominal | One-Hot Encoded |
| 5 | `referral_channel` | Acquisition source (Website/Agency/Client) | Nominal | One-Hot Encoded |
| 6 | `n_units` | Portfolio volume of purchased properties | Count | `QuantileTransformer(output_distribution='normal')` or `log1p` |
| 7 | `is_multi_unit` | Indicator for buyer with $\ge 2$ units | Binary | Boolean flag (0 / 1) |
| 8 | `office_share` | Proportion of portfolio units in Office category | Continuous | Ratio $\in [0, 1]$ (`StandardScaler`) |
| 9 | `avg_floor_area` | Mean floor area across purchased units (sqft) | Continuous | `StandardScaler` |
| 10 | `price_per_sqft` | Mean price per square foot across purchases | Continuous | `StandardScaler` (unit-level density proxy, not total wealth) |
| 11 | `n_towers` | Distinct count of towers purchased across | Count | Scaled integer |
| 12 | `portfolio_towers_hhi`| Herfindahl-Hirschman Index of tower concentration | Continuous | $HHI = \sum s_i^2 \in [0.05, 1.0]$ |
| 13 | `purchase_span_months`| Months elapsed between first and last purchase | Count | Scaled non-negative integer |

### Model B Variants & Geographic Ablation Matrix
To satisfy Phase 2 guardrails, Model B is fitted across four explicit variants:
1. **Model B1 (Full with Satisfaction)**: Features 1–13 + `satisfaction_score` + Full Geographic hierarchy (`country` + `region`).
2. **Model B2 (Without Satisfaction)**: Features 1–13 + Full Geographic hierarchy (`satisfaction_score` removed to evaluate impact of uniform noise).
3. **Model B3 (Geographic Down-Weighted)**: Features 1–13 + Geography scaled with a 0.5 weight factor to prevent USA (76.9%) from dominating clusters.
4. **Model B4 (Geographic Removed)**: Features 1–13 with purely behavioral, intent, and portfolio variables (evaluating pure buyer persona separation).

---

## 4. Orthogonal Profiling & Validation Features (Non-Clustering)

Computed and persisted in `client_features.parquet` solely for downstream business intelligence:
* `total_spend`: Cumulative transaction volume ($).
* `avg_price`: Mean unit transaction price ($).
* `max_price`: Peak unit transaction price ($).
* `spend_percentile`: Global cohort spend ranking $\in [0, 100]$.
* `first_purchase_month` & `last_purchase_month`: Activity window.
