import duckdb

con = duckdb.connect()
c1 = con.execute("""
    SELECT tower_number, unit_number, transaction_date, sale_price
    FROM read_parquet('data/processed/transactions_clean.parquet')
    WHERE client_ref = 'C0001'
    ORDER BY transaction_date
""").df()

print(c1.to_string(index=False))
print('Exact Sum:', f"{c1['sale_price'].sum():.2f}")
