"""Compute exact country breakdowns, statistical tests, and cohort figures directly from Parquet tables."""

import sys

import numpy as np
import pandas as pd
from scipy import stats

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 1. Load clean datasets
cf = pd.read_parquet("data/processed/client_features.parquet")
tx = pd.read_parquet("data/processed/transactions_clean.parquet")

print("=== 1. COUNTRY BREAKDOWN ===")
country_groups = []
for country, grp in cf.groupby("country"):
    cnt = len(grp)
    tot_spend = grp["total_spend"].sum()
    mean_spend = grp["total_spend"].mean()
    tot_units = grp["n_units"].sum()
    mean_units = grp["n_units"].mean()
    country_groups.append({
        "country": country,
        "buyer_count": cnt,
        "total_spend_inr": tot_spend,
        "mean_spend_inr": mean_spend,
        "total_units": int(tot_units),
        "mean_units": mean_units,
    })

df_country = pd.DataFrame(country_groups).sort_values("buyer_count", ascending=False)
for _, r in df_country.iterrows():
    print(f"Country: {r['country']:<15} Buyers: {r['buyer_count']:<6} Total Spend: ₹{r['total_spend_inr']:>17,.2f} Mean Spend: ₹{r['mean_spend_inr']:>13,.2f} Total Units: {r['total_units']:<6} Mean Units: {r['mean_units']:.2f}")

total_buyers = df_country["buyer_count"].sum()
total_spend = df_country["total_spend_inr"].sum()
total_units = df_country["total_units"].sum()
print("-" * 80)
print(f"COHORT TOTAL:   Buyers: {total_buyers:<6} Total Spend: ₹{total_spend:>17,.2f} Mean Spend: ₹{total_spend/total_buyers:>13,.2f} Total Units: {total_units}")

# 2. USA vs International Breakdown
print("\n=== 2. USA VS INTERNATIONAL (PRD_H1) ===")
usa_mask = cf["country"] == "USA"
usa_grp = cf[usa_mask]
intl_grp = cf[~usa_mask]

n_usa = len(usa_grp)
n_intl = len(intl_grp)
usa_spend_sum = usa_grp["total_spend"].sum()
intl_spend_sum = intl_grp["total_spend"].sum()
usa_mean = usa_grp["total_spend"].mean()
intl_mean = intl_grp["total_spend"].mean()
spend_diff = usa_mean - intl_mean
premium_pct = (spend_diff / intl_mean) * 100.0

# Two-sample t-test on spend
t_stat, t_pval = stats.ttest_ind(usa_grp["total_spend"], intl_grp["total_spend"], equal_var=False)

# Cohen's d
pooled_std = np.sqrt(
    ((n_usa - 1) * usa_grp["total_spend"].var() + (n_intl - 1) * intl_grp["total_spend"].var())
    / (n_usa + n_intl - 2)
)
cohen_d = spend_diff / pooled_std

print(f"USA Buyers: {n_usa} ({(n_usa/2000)*100:.2f}%)")
print(f"USA Total Spend: ₹{usa_spend_sum:,.2f}")
print(f"USA Mean Spend: ₹{usa_mean:,.2f}")
print(f"International Buyers: {n_intl} ({(n_intl/2000)*100:.2f}%)")
print(f"International Total Spend: ₹{intl_spend_sum:,.2f}")
print(f"International Mean Spend: ₹{intl_mean:,.2f}")
print(f"USA Spend Premium: ₹{spend_diff:,.2f} ({premium_pct:.2f}%)")
print(f"Two-sample Welch's t-test: t = {t_stat:.4f}, p = {t_pval:.4f}")
print(f"Cohen's d = {cohen_d:.4f}")
implied_cohort_mean = (n_usa * usa_mean + n_intl * intl_mean) / 2000.0
print(f"Implied Cohort Mean: ₹{implied_cohort_mean:,.2f} (matches cohort: {implied_cohort_mean == total_spend/2000.0})")

# 3. Investment Share Contingency Table (PRD_H1)
print("\n=== 3. INVESTMENT SHARE CONTINGENCY TABLE (PRD_H1) ===")
# Purpose: HOME vs INVESTMENT
contingency = pd.crosstab(cf["country"] == "USA", cf["acquisition_purpose"])
contingency.index = ["International", "USA"]
print(contingency)
chi2_stat, chi2_pval, dof, expected = stats.chi2_contingency(contingency, correction=False)
print(f"Chi-Square test of independence: chi2 = {chi2_stat:.4f}, p = {chi2_pval:.4f}, dof = {dof}")
usa_inv_rate = (usa_grp["acquisition_purpose"] == "INVESTMENT").mean() * 100.0
intl_inv_rate = (intl_grp["acquisition_purpose"] == "INVESTMENT").mean() * 100.0
print(f"USA Investment Share: {usa_inv_rate:.2f}%")
print(f"International Investment Share: {intl_inv_rate:.2f}%")

# 4. Individuals vs Companies (PRD_H3)
print("\n=== 4. INDIVIDUALS VS COMPANIES (PRD_H3) ===")
ind_grp = cf[cf["client_type"] == "INDIVIDUAL"]
com_grp = cf[cf["client_type"] == "COMPANY"]
n_ind = len(ind_grp)
n_com = len(com_grp)
ind_units_mean = ind_grp["n_units"].mean()
com_units_mean = com_grp["n_units"].mean()

# One-way ANOVA / Two-sample t-test
f_stat, f_pval = stats.f_oneway(ind_grp["n_units"], com_grp["n_units"])
t_stat_type, t_pval_type = stats.ttest_ind(ind_grp["n_units"], com_grp["n_units"], equal_var=True)
print(f"Individual Buyers: {n_ind} ({n_ind/2000*100:.2f}%), Mean Units: {ind_units_mean:.4f}")
print(f"Company Buyers: {n_com} ({n_com/2000*100:.2f}%), Mean Units: {com_units_mean:.4f}")
print(f"One-Way ANOVA on units: F(1, {n_ind + n_com - 2}) = {f_stat:.4f}, p = {f_pval:.4f}")
print(f"Two-Sample t-test: t({n_ind + n_com - 2}) = {t_stat_type:.4f}, p = {t_pval_type:.4f} (Note: F = t^2: {t_stat_type**2:.4f} == {f_stat:.4f})")

# 5. Campaign Scenario Formulas and Live Values
print("\n=== 5. CAMPAIGN SCENARIO LIVE FORMULA & ROW VALUES ===")
total_budget = 100000.0
channels = ["Website", "Agency", "Client"]
shares = {"Website": 0.50, "Agency": 0.35, "Client": 0.15}
cpas = {"Website": 1200.0, "Agency": 3500.0, "Client": 1800.0}

row_clients = {}
row_sales = {}
for ch in channels:
    alloc_budget = total_budget * shares[ch]
    cpa = cpas[ch]
    n_clients = alloc_budget / cpa
    sub_cf = cf[cf["referral_channel"] == ch]
    mean_sales = sub_cf["total_spend"].mean()
    gmv = n_clients * mean_sales
    row_clients[ch] = (alloc_budget, cpa, n_clients, mean_sales, gmv)
    print(f"Channel {ch:<8}: Allocated=₹{alloc_budget:,.2f}, CPA=₹{cpa:,.2f}, Clients={n_clients:.4f}, HistMean=₹{mean_sales:,.4f}, GMV=₹{gmv:,.4f}")

tot_sim_clients = sum(r[2] for r in row_clients.values())
tot_sim_gmv = sum(r[4] for r in row_clients.values())
print(f"Total Modeled Clients: {tot_sim_clients:.4f}")
print(f"Total Modeled GMV:     ₹{tot_sim_gmv:,.4f}")
