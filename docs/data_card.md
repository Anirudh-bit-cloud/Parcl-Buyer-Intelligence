# Data Card: Parcl Buyer Intelligence Platform

**Target Enterprise**: Parcl Co. Limited  
**Program Sponsor**: Unified Mentor  
**Date**: November 2, 2026  
**Reference Parquet Files**:
* Clients: `data/processed/clients_clean.parquet` (2,000 unique buyers)
* Transactions: `data/processed/transactions_clean.parquet` (7,305 historical sold units)
* Live Inventory: `data/processed/available_properties.parquet` (313 deduplicated currently available units)

---

## 1. Physical Properties & Inventory Temporal Lineage

### 1.1 Total Footprint & Towers
* **Towers**: The development portfolio contains exactly **20 towers** (Tower 1 through Tower 20).
* **Total Listing Records**: The raw `data/raw/properties.csv` contains 10,000 event records spanning from 2024-01 to 2025-12.
* **Status Distribution**:
  * `Sold`: 7,305 records (joined to client buyer profiles).
  * `Available`: 2,695 event rows.

### 1.2 Inventory Deduplication Assumption
* **Empirical Reality of Raw "Available" Rows**:
  * The 2,695 raw "Available" records represent historical monthly listing snapshots, **not** 2,695 distinct unsold physical units.
  * In the raw data, there are only **932 distinct `(tower_number, unit_number)` pairs** ever listed as "Available".
  * Exactly **2,243 of those available event rows have a subsequent `Sold` record** for the exact same physical unit at a later transaction date.
  * For example, Listings `130272` (March 2025) and `130273` (January 2025) both represent Tower 13, Unit 32. This physical unit was subsequently sold in December 2025 (Listing `130276`).
* **Current Inventory Definition**:
  * **Core Assumption**: Current available inventory is defined as the **latest record per physical unit `(tower_number, unit_number)` in temporal sequence** where `listing_status == 'Available'`.
  * Units whose latest temporal record is `Sold` have already been acquired and are excluded from active inventory.
  * Applying this deduplication yields exactly **313 currently available physical units** across the 20 towers (264 Apartments, 49 Offices).
  * Downstream matching engines (Opportunity Finder, NBO Engine) operate strictly on this live deduplicated inventory of 313 units.

---

## 2. Client Demographics, Accounting Currency & Referral Channels

* **Cohort Size**: 2,000 unique buyers (`C0001` through `C2000`).
* **Accounting Currency Standard (₹ INR) & Raw Data Relabeling**:
  * In Phase 1 ingestion, raw property and transaction values carrying a leading dollar symbol (e.g. `300,385.62`) were stripped to numeric floats.
  * Under sponsor instruction from Parcl Co. Limited and Unified Mentor, all monetary amounts are relabeled directly in **Indian Rupees (₹)** with standard Indian digit grouping (lakh/crore).
  * *Assumption Notice*: Currency is an accounting and display labeling convention and is independent of client geographic provenance (`country: "USA"` and regional attributes remain unchanged). No foreign exchange (FX) conversion has been applied.
* **Age Calculation & Single Reference Date**:
  * Computed as completed integer age relative to the single configured reference date **`2025-12-31`**.
  * DOB sensitivity analysis confirms 0 age-band switches (0.00%) between slash and dash format interpretations.
* **Referral Channels & Empirical Benchmarks**:
  * **Website**: 1,103 buyers (55.15%), Mean sales: ₹12,74,771, **Median sales: ₹12,38,163**, Mean units: 3.68, Loan rate: 36.63%.
  * **Agency**: 705 buyers (35.25%), Mean sales: ₹12,43,489, **Median sales: ₹12,10,176**, Mean units: 3.61, Loan rate: 36.60%.
  * **Client (Referral)**: 192 buyers (9.60%), Mean sales: ₹12,39,682, **Median sales: ₹12,23,339**, Mean units: 3.63, Loan rate: 38.54%.
* **Satisfaction Score**: Marginal distribution is consistent with discrete uniform across {1, 2, 3, 4, 5} (χ² = 1.990, p = 0.7376 across category counts `[395, 379, 404, 417, 405]`). Exhibits no detectable association with acquisition purpose, loan application, referral channel, or total spend.

---

## 3. Client C0001 Provenance & Baseline Record

To establish complete provenance and eliminate hand-written discrepancy:

### Raw Ingestion Record (`data/raw/clients.csv`)
```json
{
  "client_id": "C0001",
  "client_type": "Individual",
  "first_name": "Kareem",
  "last_name": "Liu",
  "date_of_birth": "05-11-1968",
  "gender": "F",
  "country": "USA",
  "region": "California",
  "acquisition_purpose": "Home",
  "satisfaction_score": 4,
  "loan_applied": "Yes",
  "referral_channel": "Website"
}
```

### Cleaned Feature Record (`data/processed/clients_clean.parquet`)
```json
{
  "client_id": "C0001",
  "client_type": "INDIVIDUAL",
  "first_name": "Kareem",
  "last_name": "Liu",
  "date_of_birth": "1968-11-05",
  "gender": "Female",
  "country": "USA",
  "region": "California",
  "age": 57,
  "satisfaction_score": 4,
  "loan_applied": true,
  "referral_channel": "Website",
  "n_units": 4,
  "total_spend": 1246764.72,
  "assigned_cluster": 0,
  "cluster_name": "Emerging Multi-Tower Accumulators"
}
```

### Audit Notes on C0001
1. **Name and Origin**: The authentic client identity in the underlying data has always been **Kareem Liu, USA, California**.
2. **Age Derivation**: On configured reference date `2025-12-31`, with date of birth `1968-11-05`, the client has lived 20,875 days. Dividing by 365.2425 yields completed integer age **57**. (The legacy Phase 5 walkthrough reference to age 49 was an error caused by evaluating age relative to 2017: 2017 - 1968 = 49).
