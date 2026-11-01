# Workspace Rule: No Hardcoded Metrics & Zero Hallucination

## Core Mandates
1. **Never fabricate or hardcode numbers**: Every metric, count, lift, silhouette score, p-value, or dollar figure displayed in the UI, Streamlit dashboard, Research Paper, or README must be dynamically computed from the underlying data (`clients.csv`, `properties.csv`) by code residing in this repository.
2. **Grounding in Evidence**: If the data contradicts a PRD assumption (e.g. uniform satisfaction score, weak cluster separation, lack of income field), explicitly document and state the empirical finding. Never force the data to match preconceived hypotheses.
3. **No Phantom Referral Channels or Yields**: Only use the empirical referral channels (`Website`, `Agency`, `Client`). Do not invent expected yield percentages or ROI figures without explicit assumptions labeled as such.
4. **Observed Spend vs Income**: All financial figures must be designated as "Observed Spend". Never claim or imply true household/corporate income.
