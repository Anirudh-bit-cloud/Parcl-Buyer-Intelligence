"""Generate synthetic sample dataset for Parcl Buyer Intelligence Platform.

Produces:
- data/sample/clients_sample.csv (200 buyers, all >= 3 units)
- data/sample/properties_sample.csv (~867 properties, 20 towers 1..20)
- data/sample/processed/clients_clean.parquet
- data/sample/processed/transactions_clean.parquet
- data/sample/processed/available_properties.parquet
- data/sample/processed/client_features.parquet (scored with production saved model B3, NO retraining)

Features identical columns, types, and constraints to Pandera Raw schemas,
with entirely synthetic/anonymized values.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from parcl_core.cleaning import clean_clients, clean_properties
from parcl_core.config import settings
from parcl_core.encoding import (
    MODEL_B_BASE_NUMERICS,
    MODEL_B_BOOLEANS,
    MODEL_B_CATEGORICALS,
)
from parcl_core.features import engineer_client_features
from scipy.special import softmax

ROOT_DIR = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT_DIR / "data" / "sample"
SAMPLE_PROCESSED_DIR = SAMPLE_DIR / "processed"

FIRST_NAMES = [
    "Aarav", "Aditi", "Alexander", "Amara", "Carlos", "Chloe", "David", "Elena",
    "Fatima", "Gabriel", "Hannah", "Hiroshi", "Isaac", "Jasmine", "Kavita", "Liam",
    "Maya", "Noah", "Olivia", "Priya", "Rahul", "Sara", "Tariq", "Uma", "Vikram",
    "William", "Xavier", "Yuki", "Zoe", "Arthur", "Beatrice", "Caleb", "Daphne",
    "Ethan", "Freja", "George", "Helena", "Ian", "Julia", "Kai", "Leila", "Marcus",
    "Nadia", "Oscar", "Penelope", "Quinn", "Rohan", "Sophia", "Thomas", "Victoria"
]

LAST_NAMES = [
    "Anderson", "Bhatia", "Chen", "Dubois", "Espinoza", "Fischer", "Gupta", "Hansen",
    "Ivanov", "Johansson", "Kapoor", "Larsson", "Mendoza", "Nakamura", "O'Connor", "Patel",
    "Qureshi", "Rossi", "Sharma", "Tanaka", "Underwood", "Venkatesh", "Watanabe", "Xu",
    "Yamamoto", "Zhang", "Adler", "Bennett", "Costa", "Dumont", "Eriksson", "Ferreira",
    "Gomez", "Hoffman", "Iqbal", "Jensen", "Kowalski", "Lombardi", "Moreau", "Novak",
    "Olsen", "Petrov", "Ricci", "Schmidt", "Torres", "Ueda", "Vogel", "Weber", "Yilmaz", "Zimmerman"
]

COUNTRY_REGIONS = {
    "USA": ["California", "Texas", "New York", "Florida", "Illinois", "Washington", "Nevada", "Colorado"],
    "UK": ["England", "Scotland", "Wales", "Northern Ireland", "Greater London"],
    "Canada": ["Ontario", "Quebec", "British Columbia", "Alberta"],
    "Germany": ["Bavaria", "Berlin", "Hesse", "North Rhine-Westphalia", "Baden-Wurttemberg"],
    "France": ["Ile-de-France", "Provence-Alpes-Cote d'Azur", "Auvergne-Rhone-Alpes", "Occitanie"],
    "Belgium": ["Flanders", "Wallonia", "Brussels-Capital"],
    "Mexico": ["Mexico City", "Jalisco", "Nuevo Leon", "Quintana Roo"],
    "Australia": ["New South Wales", "Victoria", "Queensland", "Western Australia"],
    "Russia": ["Central Federal District", "Northwestern Federal District", "Volga Federal District"],
    "Denmark": ["Capital Region", "Central Denmark", "Region of Southern Denmark"],
}

COUNTRIES = list(COUNTRY_REGIONS.keys())


def generate_sample_datasets() -> tuple[Path, Path]:
    random.seed(42)
    np.random.seed(42)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    clients_path = SAMPLE_DIR / "clients_sample.csv"
    properties_path = SAMPLE_DIR / "properties_sample.csv"

    # 1. Generate 200 Clients targeted across the 4 quadrant profiles
    clients_rows: list[dict[str, Any]] = []
    properties_rows: list[dict[str, Any]] = []
    listing_id_counter = 1001

    for i in range(1, 201):
        cid = f"C{i:04d}"
        group = (i - 1) % 4
        if group == 0:  # Cluster 0: Emerging Multi-Tower Accumulators (units > 3.5, age <= 56.5)
            dob = date(1983, 5, 10) + timedelta(days=random.randint(-400, 400))  # age ~42
            n_units = random.choice([4, 5])
            office_prob = 0.15
        elif group == 1:  # Cluster 1: Concentrated Residential (units <= 3.5, office_share == 0)
            dob = date(1971, 3, 15) + timedelta(days=random.randint(-400, 400))  # age ~54
            n_units = 3
            office_prob = 0.0
        elif group == 2:  # Cluster 2: Commercial Office Diversifiers (units <= 3.5, office_share > 0.01)
            dob = date(1976, 8, 20) + timedelta(days=random.randint(-400, 400))  # age ~49
            n_units = 3
            office_prob = 0.65
        else:  # Cluster 3: Established Senior Estate Investors (units > 3.5, age > 56.5)
            dob = date(1956, 4, 12) + timedelta(days=random.randint(-400, 400))  # age ~69
            n_units = random.choice([4, 5, 6])
            office_prob = 0.15

        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        country = random.choice(COUNTRIES)
        region = random.choice(COUNTRY_REGIONS[country])

        # ~5% Company, ~95% Individual
        client_type = "Company" if random.random() < 0.05 else "Individual"
        # ~69% Home, ~31% Investment
        acquisition_purpose = "Home" if random.random() < 0.69 else "Investment"
        satisfaction_score = random.randint(1, 5)
        loan_applied = "Yes" if random.random() < 0.35 else "No"
        referral_channel = random.choices(
            ["Website", "Agency", "Client"],
            weights=[0.55, 0.30, 0.15],
            k=1,
        )[0]

        clients_rows.append({
            "client_id": cid,
            "client_type": client_type,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": dob.strftime("%m/%d/%Y"),
            "gender": random.choice(["M", "F"]),
            "country": country,
            "region": region,
            "acquisition_purpose": acquisition_purpose,
            "satisfaction_score": satisfaction_score,
            "loan_applied": loan_applied,
            "referral_channel": referral_channel,
        })

        # Generate sold units across towers 1..20
        for u in range(n_units):
            lid = listing_id_counter
            listing_id_counter += 1
            tower_number = ((i * 3 + u) % 20) + 1  # 1 to 20

            if group == 1:
                unit_cat = "Apartment"
            elif group == 2:
                unit_cat = "Office" if (u == 0 or random.random() < office_prob) else "Apartment"
            else:
                unit_cat = "Office" if random.random() < office_prob else "Apartment"

            sqft = round(random.uniform(550.0, 2200.0), 2)
            price = round(sqft * random.uniform(220.0, 420.0), 2)
            sale_price_str = f"${price:,.2f}"

            properties_rows.append({
                "listing_id": lid,
                "tower_number": tower_number,
                "transaction_date": "06-15-2024",
                "unit_category": unit_cat,
                "unit_number": random.randint(10, 99),
                "floor_area_sqft": sqft,
                "sale_price": sale_price_str,
                "listing_status": "Sold",
                "client_ref": cid,
            })

    # Available properties across all 20 towers (5 available units per tower = 100 available units)
    for t in range(1, 21):
        for u in range(5):
            lid = listing_id_counter
            listing_id_counter += 1
            sqft = round(random.uniform(550.0, 2200.0), 2)
            price = round(sqft * random.uniform(220.0, 420.0), 2)
            sale_price_str = f"${price:,.2f}"

            properties_rows.append({
                "listing_id": lid,
                "tower_number": t,
                "transaction_date": "12-01-2025",
                "unit_category": "Office" if u == 0 else "Apartment",
                "unit_number": 100 + u,
                "floor_area_sqft": sqft,
                "sale_price": sale_price_str,
                "listing_status": "Available",
                "client_ref": "",
            })

    # Write CSV files
    with open(clients_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "client_id", "client_type", "first_name", "last_name", "date_of_birth",
            "gender", "country", "region", "acquisition_purpose", "satisfaction_score",
            "loan_applied", "referral_channel",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clients_rows)

    with open(properties_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "listing_id", "tower_number", "transaction_date", "unit_category",
            "unit_number", "floor_area_sqft", "sale_price", "listing_status", "client_ref",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(properties_rows)

    # 3. Clean, engineer features, and score with saved production model (NO retraining)
    df_c = pd.DataFrame(clients_rows)
    df_p = pd.DataFrame(properties_rows)

    clean_c = clean_clients(df_c, dob_dash_format=settings.dob_dash_format)
    trans_clean, avail_clean = clean_properties(df_p)
    feat = engineer_client_features(clean_c, trans_clean)

    # Load production model
    models_path = ROOT_DIR / "data" / "models" / "cluster_models.joblib"
    bundle = joblib.load(models_path)
    preprocessor = bundle["preprocessor"]
    kmeans = bundle["kmeans"]
    centroids = kmeans.cluster_centers_

    # Transform with saved production preprocessor
    X = preprocessor.transform(feat)
    cat_encoder = preprocessor.named_transformers_["core_cat"]
    n_core_cat = cat_encoder.transform(feat[MODEL_B_CATEGORICALS]).shape[1]
    n_prev = len(MODEL_B_BASE_NUMERICS) + 1 + len(MODEL_B_BOOLEANS) + n_core_cat
    X[:, n_prev:] = X[:, n_prev:] * 0.5

    # Predict cluster and compute softmax probabilities with temperature beta = 1.12
    dists = np.linalg.norm(X[:, np.newaxis, :] - centroids[np.newaxis, :, :], axis=2)
    soft_probs = softmax(-1.12 * dists, axis=1)
    preds = np.argmin(dists, axis=1)

    feat["cluster"] = preds
    for i in range(4):
        feat[f"soft_prob_cluster_{i}"] = soft_probs[:, i]

    # Save processed parquet files
    clean_c.to_parquet(SAMPLE_PROCESSED_DIR / "clients_clean.parquet", index=False)
    trans_clean.to_parquet(SAMPLE_PROCESSED_DIR / "transactions_clean.parquet", index=False)
    avail_clean.to_parquet(SAMPLE_PROCESSED_DIR / "available_properties.parquet", index=False)
    feat.to_parquet(SAMPLE_PROCESSED_DIR / "client_features.parquet", index=False)

    return clients_path, properties_path


if __name__ == "__main__":
    c_p, p_p = generate_sample_datasets()
    with open(c_p, encoding="utf-8") as f_c:
        n_c = sum(1 for _ in f_c) - 1
    with open(p_p, encoding="utf-8") as f_p:
        n_p = sum(1 for _ in f_p) - 1
    print(f"Generated clients sample: {c_p} ({n_c} rows)")
    print(f"Generated properties sample: {p_p} ({n_p} rows)")

    feat_sample = pd.read_parquet(SAMPLE_PROCESSED_DIR / "client_features.parquet")
    print("Scored sample features cluster counts:")
    counts = feat_sample["cluster"].value_counts().sort_index()
    for cid, cnt in counts.items():
        print(f"  Cluster {cid}: {cnt} buyers ({cnt / len(feat_sample) * 100:.1f}%)")
