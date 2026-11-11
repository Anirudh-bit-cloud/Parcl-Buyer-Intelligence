import duckdb

con = duckdb.connect()
df = con.execute("SELECT referral_channel, avg(total_spend) as mean_spend, count(*) as cnt, sum(total_spend) as tot_spend FROM read_parquet('data/processed/client_features.parquet') GROUP BY referral_channel ORDER BY referral_channel").df()

for _, r in df.iterrows():
    print(r["referral_channel"], "mean_spend:", repr(r["mean_spend"]), "tot_spend:", repr(r["tot_spend"]))

w_mean = df.loc[df["referral_channel"] == "Website", "mean_spend"].values[0]
a_mean = df.loc[df["referral_channel"] == "Agency", "mean_spend"].values[0]
c_mean = df.loc[df["referral_channel"] == "Client", "mean_spend"].values[0]

# Unrounded clients:
w_clients = 50000.0 / 1200.0
a_clients = 35000.0 / 3500.0
c_clients = 15000.0 / 1800.0

print("\n=== Raw product: clients * unrounded mean ===")
gmv_w_unrounded = w_clients * w_mean
gmv_a_unrounded = a_clients * a_mean
gmv_c_unrounded = c_clients * c_mean
tot_unrounded = gmv_w_unrounded + gmv_a_unrounded + gmv_c_unrounded
print("Website GMV:", repr(gmv_w_unrounded), f"{gmv_w_unrounded:.2f}")
print("Agency GMV:", repr(gmv_a_unrounded), f"{gmv_a_unrounded:.2f}")
print("Client GMV:", repr(gmv_c_unrounded), f"{gmv_c_unrounded:.2f}")
print("Total GMV:", repr(tot_unrounded), f"{tot_unrounded:.2f}")

print("\n=== Product: clients * rounded mean (to 2 decimal places) ===")
w_mean_round = round(w_mean, 2)
a_mean_round = round(a_mean, 2)
c_mean_round = round(c_mean, 2)
gmv_w_round = w_clients * w_mean_round
gmv_a_round = a_clients * a_mean_round
gmv_c_round = c_clients * c_mean_round
tot_round = gmv_w_round + gmv_a_round + gmv_c_round
print("Website GMV:", repr(gmv_w_round), f"{gmv_w_round:.2f}")
print("Agency GMV:", repr(gmv_a_round), f"{gmv_a_round:.2f}")
print("Client GMV:", repr(gmv_c_round), f"{gmv_c_round:.2f}")
print("Total GMV:", repr(tot_round), f"{tot_round:.2f}")
