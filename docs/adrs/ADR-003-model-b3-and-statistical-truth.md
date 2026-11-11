# ADR-003: Model B3 Selection, Surrogate Tree Classification Metrics, and Statistical Truth

## Status
Accepted (v2.0.0)

## Context
During Phase 0 audit, three methodological issues were identified:
1. Surrogate decision tree was evaluated using regression $R^2$, which is mathematically invalid for multi-class classification.
2. Centroid softmax temperature calibration ($\beta = 1.12$) was tuned against K-Means pseudo-labels and required explicit labeling as a "membership score".
3. Silhouette score is 0.1211, representing overlapping behavioral regimes, not isolated clusters.

## Decision
1. Replaced $R^2$ with Classification Fidelity Accuracy (96.55%), Macro-F1 (0.965), and a complete $4 \times 4$ confusion matrix.
2. Formally labeled softmax probabilities as calibrated "membership scores", with out-of-fold cross-validation and temporal holdout tests.
3. Updated all customer-facing documentation and UI to characterize clusters as "distinct but overlapping behavioral regimes".
4. Integrated continuous drift monitoring via Population Stability Index (PSI) and Kolmogorov-Smirnov two-sample tests.

## Consequences
- 100% adherence to zero-fabrication and statistical rigor rules.
- Fully transparent model cards and governance disclosures.
