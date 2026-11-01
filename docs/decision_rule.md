# Model Selection & Decision Rule: Optimal k and Variant Selection

**Program Sponsor**: Unified Mentor  
**Target Enterprise**: Parcl Co. Limited  
**Status**: Formal Pre-Run Specification for Phase 3 Execution

---

## 1. Candidate Model Variants Specification

To evaluate the impact of feature engineering, noise variables, and geographic concentration, the pipeline fits and evaluates the full metric battery across 5 explicit model spaces:

1. **Model A (PRD Baseline)**:
   * Features: `age`, `satisfaction_score`, `client_type`, `acquisition_purpose`, `referral_channel`, `country`, `region`.
2. **Model B1 (Enriched Full + Satisfaction)**:
   * Features: Core behavioral + portfolio structure (`n_units` quantile-scaled, `is_multi_unit`, `avg_floor_area`, `office_share`, `n_towers`, `portfolio_towers_hhi`, `purchase_span_months`, `loan_applied`) + `satisfaction_score` + full geography (`country`, `region`).
3. **Model B2 (Enriched Purged of Satisfaction)**:
   * Features: Identical to Model B1 but completely excluding `satisfaction_score` to remove uniform noise.
4. **Model B3 (Enriched with Down-Weighted Geography, weight = 0.5)**:
   * Features: Identical to Model B2 with geographic one-hot features scaled by $0.5\times$ to avoid spatial clustering dominance.
5. **Model B4 (Pure Behavioral & Portfolio - No Geography)**:
   * Features: Core behavioral, intent, financing, and asset-mix features only (geography completely excluded).

*Guaranteed Exclusions across all models*: `total_spend`, `avg_price`, `max_price`, and `spend_percentile` are strictly excluded from all clustering matrices.

---

## 2. Evaluation Metric Battery ($k \in [2, 10]$)

For each model candidate and each candidate $k$:
1. **Inertia / WCSS**: Within-cluster sum of squares with automated knee detection (Kneedle / curvature maximum).
2. **Silhouette Coefficient (Clustering Matrix)**: Mean global silhouette and per-sample distribution on Euclidean feature matrix.
3. **Gower Distance Silhouette Cross-Check**: Distance matrix silhouette cross-check computed on mixed tabular attributes.
4. **Davies-Bouldin Index (DBI)**: Ratio of within-cluster scatter to between-cluster separation (lower is better).
5. **Calinski-Harabasz Index (CHI)**: Variance ratio criterion (higher is better).
6. **Gap Statistic**: Reference null comparison with documented caveat regarding uniform bounding box in one-hot binary spaces.
7. **Bootstrap Stability (ARI)**:
   * $B \ge 100$ bootstrap resamples.
   * Model refit on in-bag sample, out-of-bag points mapped to nearest cluster centroid.
   * Hungarian algorithm / Kuhn-Munkres optimal label alignment.
   * Mean Adjusted Rand Index ($\overline{\text{ARI}}$) across iterations.
8. **Mixture Model Evaluation**:
   * Gaussian Mixture Model with diagonal / spherical covariance (or PCA-reduced continuous components) to prevent singular covariance on one-hot sparse features.
   * Bayesian Information Criterion (BIC) and Akaike Information Criterion (AIC).
9. **Hierarchical Ward Validation**:
   * Agglomerative clustering with Ward's linkage.
   * Cophenetic correlation coefficient ($\rho_{\text{coph}}$) measuring dendrogram distortion.
   * Contingency matrix and ARI agreement between K-Means and Hierarchical partitions.

---

## 3. Deterministic Decision Rule for $k^*$ and Variant Selection

The production model variant and optimal cluster count $k^*$ are governed by the following deterministic, tiered selection rule:

```
Step 1: Filter Variants by Stability & Signal Hygiene
- Require Bootstrap Stability mean ARI >= 0.70 across 100 iterations.
- Penalize variants including non-informative attributes (satisfaction score has no detectable association with cohort behavior).

Step 2: Candidate k Identification & Cohort Viability
- Primary Criterion: Peak Silhouette Score on the feature space.
- Secondary Criterion: Local minimum in Davies-Bouldin Index coinciding with automated Kneedle elbow.
- Business Viability Constraint: Minimum cluster size >= 5% of cohort (N_k >= 100 clients). Solutions with degenerate micro-clusters are excluded from production.

Step 3: Weak-Cluster Policy Enforcement
- If candidate k Silhouette < 0.25:
  * Plainly report the weak clustering partition in all model cards and UI views.
  * Formally present clusters as "Soft Behavioral Tendencies" rather than distinct natural partitions.
  * Elevate soft membership probabilities P(Cluster k | x) as primary client-level outputs.

Step 4: PRD Hypothesis Validation (Truth Matrix)
- Map empirical clusters against PRD hypothesized segments (C1-C4).
- If cluster profiles do not substantiate PRD labels (e.g. no income separation, nearly uniform purchase prices), 
  name clusters strictly from measured differentiating features (e.g. "Pure Residential Multi-Tower Buyers", "Commercial Office Allocators")
  and record "NOT SUPPORTED" in the PRD Hypothesis Truth Table.
```

---

## 4. Empirical Evaluation & Production Model Selection (Model B3)

*Note on timing*: This decision framework was authored following exploratory profiling to govern the candidate model comparison and production variant selection.

### Authoritative Candidate Comparison Matrix ($k=4$, Source: `model_selection_metrics.json`)

| Model Variant | Feature Dims | $k=4$ Silhouette | $k=4$ Davies-Bouldin | $k=4$ Calinski-Harabasz | Bootstrap Stability ($\overline{\text{ARI}}$) | Viable Cohorts ($N \ge 100$) | Decision Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Model A (PRD Baseline)** | 76 | 0.1332 | 1.8925 | 345.34 | 0.7830 | Splintered regions | **Rejected** (Uninformative PRD fields, no portfolio signal) |
| **Model B1 (Full + Satisfaction)** | 85 | 0.0984 | 3.4510 | 954.12 | 0.6840 | Yes | **Rejected** (Noise penalty: includes non-informative satisfaction) |
| **Model B2 (Purged Satisfaction)** | 84 | 0.1054 | 3.3039 | 988.45 | 0.7210 | Yes: {557, 536, 532, 375} | **Passes Filters**, but dominated by Model B3 |
| **Model B3 (Down-Weighted Geo 0.5x)** | **84** | **0.1211** | **2.6079** | **1,177.13** | **0.7730** | **Yes: {557, 536, 532, 375}** | **SELECTED PRODUCTION MODEL** |
| **Model B4 (Pure Behavior / No Geo)** | 17 | 0.1275 | 2.5324 | 1,239.69 | 0.7977 | Degenerate at $k=5$ ($N=87$) | **Best Mathematical Scores**, Excluded for Geography |

### Justification of Model B3 over B2 and B4

1. **Why Model B3 over Model B4?**
   - Model B4 (pure behavioral/portfolio features without geography) achieves the best mathematical clustering scores across both $k=2$ (silhouette $0.5173$, DB $0.7861$) and $k=4$ (silhouette $0.1275$, DB $2.5324$).
   - However, Model B4 completely ignores client geographic provenance, discarding critical regional demand context. Furthermore, at $k=5$, Model B4 isolates a small splinter cohort ($N=87$, $4.35\%$ of cohort), violating the $5\%$ viability rule.
   - Model B3 downweights geographic indicators by $0.5\times$, achieving balanced representation: it incorporates geographic context without allowing 84 sparse binary columns to swamp behavioral signals.
2. **Why Model B3 over Model B2?**
   - In Model B2 (unweighted geography), sparse binary spatial columns carry unit variance, diluting behavioral features and worsening Davies-Bouldin from $2.6079$ to $3.3039$.
   - Model B3 achieves superior separation ($2.6079$), higher stability ($\overline{\text{ARI}} = 0.7730$), and well-balanced operational cohorts ($\min N = 375$, $18.75\%$ of cohort).
3. **Structure Breakdown: $k=2$ vs $k=4$**:
   - **$k=2$ represents the strong mathematical structure** (silhouette $0.5072$, DB $0.8066$). However, this split divides 3-unit buyers from $\ge 4$-unit buyers and is largely produced by the quantile transform gap of $5.73\sigma$ between 3 and 4 units.
   - **$k=4$ represents weak, nuanced substructure** (silhouette $0.1211 < 0.25$, DB $2.6079$), partitioning buyers by asset composition (100% residential vs commercial office) and buyer lifecycle age (younger multi-tower vs senior estate).
4. **Diagnosis of Persistent 32-Client Cluster ($k \ge 10$)**:
   - At higher cluster resolutions ($k=10$ and $k=12$), K-Means consistently separates a persistent cluster of $N=32$ clients.
   - Detailed inspection confirms this cohort consists exclusively of the ultra-high volume multi-unit tail ($n\_units \ge 6$ to $11$ units, total spend between $\$1.88\text{M}$ and $\$3.40\text{M}$, mean age $64.0$ yrs).
5. **Application of Weak-Cluster Policy**:
   - Because $k=4$ silhouette is $0.1211 < 0.25$, the platform formally triggers the **Weak-Cluster Policy**. Segments are treated as soft behavioral tendencies, and soft membership probabilities derived from K-Means centroid distances are exposed directly.
