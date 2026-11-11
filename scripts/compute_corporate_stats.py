import duckdb
import numpy as np
from scipy import stats

con = duckdb.connect()
cf = con.execute("SELECT * FROM read_parquet('data/processed/client_features.parquet')").df()

ind = cf[cf["client_type"] == "INDIVIDUAL"]["n_units"]
corp = cf[cf["client_type"] == "COMPANY"]["n_units"]

print("=== CORPORATE-BUYER TEST (FULL PRECISION) ===")
print(f"Individual: count={len(ind)}, mean={ind.mean():.8f}, std={ind.std():.8f}, var={ind.var():.8f}")
print(f"Company:    count={len(corp)}, mean={corp.mean():.8f}, std={corp.std():.8f}, var={corp.var():.8f}")

print("\nValue counts for Individual (n_units):")
print(ind.value_counts().sort_index())

print("\nValue counts for Company (n_units):")
print(corp.value_counts().sort_index())

# Scipy calls
t_pooled, p_pooled = stats.ttest_ind(ind, corp, equal_var=True)
t_welch, p_welch = stats.ttest_ind(ind, corp, equal_var=False)
f_val, p_f = stats.f_oneway(ind, corp)
kw_stat, kw_p = stats.kruskal(ind, corp)

# Degrees of freedom
df_pooled = len(ind) + len(corp) - 2
# Welch df formula
s1, s2 = ind.var(), corp.var()
n1, n2 = len(ind), len(corp)
df_welch = (s1/n1 + s2/n2)**2 / ((s1/n1)**2 / (n1 - 1) + (s2/n2)**2 / (n2 - 1))

print(f"\nPooled t-test: t = {t_pooled:.10f}, df = {df_pooled}, p = {p_pooled:.10f}")
print(f"Welch t-test:  t = {t_welch:.10f}, df = {df_welch:.10f}, p = {p_welch:.10f}")
print(f"One-way ANOVA: F = {f_val:.10f}, df = (1, {df_pooled}), p = {p_f:.10f}")
print(f"Kruskal-Wallis: H = {kw_stat:.10f}, p = {kw_p:.10f}")

print("\nUnrounded comparison to 1/3 and -1/sqrt(3):")
print(f"F_val = {f_val:.8f} vs 1/3 = {1/3:.8f} (diff = {f_val - 1/3:+.8f})")
print(f"t_val = {t_pooled:.8f} vs -1/sqrt(3) = {-1/np.sqrt(3):.8f} (diff = {t_pooled - (-1/np.sqrt(3)):+.8f})")
print(f"p_val = {p_pooled:.8f} vs 2/3 = {2/3:.8f} (diff = {p_pooled - 2/3:+.8f})")
