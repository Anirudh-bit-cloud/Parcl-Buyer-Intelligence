from pathlib import Path

# 1. Update task_list.md
task_list_path = Path("C:/Users/saini/.gemini/antigravity/brain/09ff63e0-3793-4725-abed-f1fde3c4c041/task_list.md")
task_text = task_list_path.read_text(encoding="utf-8")

# Fix Phase 5 header
task_text = task_text.replace(
    "## Phase 5: FastAPI Backend Service (`apps/api`) (COMPLETED)",
    "## Phase 5: FastAPI Backend Service (`apps/api`) (awaiting approval)"
)

# Fix 5.2 predict line
task_text = task_text.replace(
    "- [x] 18. `POST /api/v1/predict/segment` - Real-time inference with out-of-fold agreement log-likelihood centroid-softmax probabilities",
    "- [x] 18. `POST /api/v1/predict/segment` - Real-time inference with centroid-softmax probabilities (β chosen by out-of-fold agreement log-likelihood)"
)

# Fix 2017 explanation in 5.6
task_text = task_text.replace(
    "old age 49 documented as 2017 artifact",
    "old age 49 documented as hand-typed in the original sample; no recoverable reference date"
)

# Fix rounding in 5.7
task_text = task_text.replace("13.40% office, age 42.10", "13.38% office, age 42.05")
task_text = task_text.replace("age 54.10", "age 54.11")

# Fix section 3.3 canonical mapping table
old_s33 = """    - *Note on raw Phase 3 cluster indexing vs production*: The raw K-Means fit in Phase 3 indexed the 3-unit, 0% office segment as raw index 0 and the 4.05-unit accumulator segment as raw index 1. In production (Phase 5 Model B3), canonical cluster IDs map directly to empirical surrogate rules so Cluster 0 is `Emerging Multi-Tower Accumulators` and Cluster 1 is `Concentrated Residential Buyers`, without contradicting data card ground truth.
    - Canonical Mapping Table:
      | Phase 3 Model B3 Raw Index | Production Cluster ID | Canonical Segment Name | Defining Microdata Conditions |
      |:---:|:---:|:---|:---|
      | Raw Index 0 | **Cluster 1** | Concentrated Residential Buyers | 3.00 units, 0.00% office, age 54.10, HHI 0.3333 |
      | Raw Index 1 | **Cluster 0** | Emerging Multi-Tower Accumulators | 4.06 units, 13.40% office, age 42.10, HHI 0.2518 |
      | Raw Index 2 | **Cluster 2** | Commercial Office Diversifiers | 3.00 units, 37.84% office, age 55.20, HHI 0.3333 |
      | Raw Index 3 | **Cluster 3** | Established Senior Estate Investors | 4.39 units, 15.80% office, age 69.20, HHI 0.2416 |"""

new_s33 = """    - *Note on raw Phase 3 cluster indexing vs production*: In production Model B3 (`cluster_models.joblib`), raw K-Means labels and production cluster IDs are completely identical ($[0, 1, 2, 3] \\to [0, 1, 2, 3]$). The earlier Amendment 2 table mistakenly inverted the names for Cluster 0 and Cluster 1; this was corrected in Amendment 3 with verified 100% concordance.
    - Canonical Mapping Table:
      | Raw K-Means Index (`cluster_models.joblib`) | Production Cluster ID | Canonical Segment Name | Defining Microdata Conditions |
      |:---:|:---:|:---|:---|
      | Raw Index 0 | **Cluster 0** | Emerging Multi-Tower Accumulators | 4.06 units, 13.38% office, age 42.05, HHI 0.2518 |
      | Raw Index 1 | **Cluster 1** | Concentrated Residential Buyers | 3.00 units, 0.00% office, age 54.11, HHI 0.3333 |
      | Raw Index 2 | **Cluster 2** | Commercial Office Diversifiers | 3.00 units, 37.78% office, age 55.19, HHI 0.3333 |
      | Raw Index 3 | **Cluster 3** | Established Senior Estate Investors | 4.39 units, 15.80% office, age 69.21, HHI 0.2416 |"""

task_text = task_text.replace(old_s33, new_s33)

# Remove "Produced `walkthrough_phase_5_amendment_3.md` artifact." or keep as file reference
task_text = task_text.replace(
    "- [x] Produced `walkthrough_phase_5_amendment_3.md` artifact.",
    "- [ ] Walkthrough file delivery (`walkthrough_phase_5_amendment_3.md`) awaiting transmission."
)

task_list_path.write_text(task_text, encoding="utf-8")
print("Updated task_list.md")

# 2. Update docs/data_card.md
data_card_path = Path("docs/data_card.md")
dc_text = data_card_path.read_text(encoding="utf-8")
old_dc_age = "(The legacy Phase 5 walkthrough reference to age 49 was an error caused by evaluating age relative to 2017: 2017 - 1968 = 49)."
new_dc_age = "(The legacy Phase 5 walkthrough reference to age 49 was hand-typed in the original sample; no recoverable reference date)."
if old_dc_age in dc_text:
    dc_text = dc_text.replace(old_dc_age, new_dc_age)
    data_card_path.write_text(dc_text, encoding="utf-8")
    print("Updated docs/data_card.md age explanation")
else:
    print("Could not find old_dc_age in docs/data_card.md")
