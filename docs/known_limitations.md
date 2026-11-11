# Known Limitations & Methodological Disclosures

## 1. Currency Relabeling vs Mathematical Conversion
- **Raw Transaction Currency**: Underlying property transactions in the source dataset were denominated in US Dollars.
- **Relabeling Default**: The default application setting treats the numbers as unscaled relabeled INR figures (₹).
- **Remedy**: When `apply_fx_conversion=False`, the UI and API explicitly display an amber disclosure banner: *"Values relabeled directly without foreign exchange conversion."* Users can toggle configured mathematical conversion rate (₹83.50/USD, as of 2026-11-10) in the top-bar localization menu.

## 2. Customer Satisfaction Scores
- **Discrete Uniform Distribution**: Historical customer satisfaction scores (1 to 5) fail the null hypothesis of non-uniformity ($\chi^2 = 1.990, p = 0.7376$).
- **Lack of Correlation**: Satisfaction scores have near-zero correlation with buyer spend ($r = 0.041, p = 0.0639$) and property price per sqft ($F = 0.409, p = 0.8018$).
- **Remedy**: Satisfaction scores were completely purged from Model B3 feature matrices to avoid introducing random noise.

## 3. Gaussian Mixture Models in High Dimensions
- **Structural Collapse**: Full-covariance GMM fails in 84 continuous dimensions, collapsing into 2 macro-components rather than separating the 4 distinct behavioral archetypes.
- **Remedy**: GMM is formally deprecated for production inference in favor of K-Means with temperature-scaled membership score ($\beta = 1.12$).

## 4. Silhouette Score Interpretation
- **Moderate Substructure**: The overall silhouette score of Model B3 is 0.1211.
- **Remedy**: Rather than claiming "non-overlapping isolated clusters", clusters are scientifically characterized as "distinct but overlapping behavioral regimes".

## 5. Machine-Translated Internationalization
- **Translation Fidelity**: Non-English translations (Hindi, German, Arabic RTL) are generated via machine translation pipelines and remain pending native institutional linguistic review.
