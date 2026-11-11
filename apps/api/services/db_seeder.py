"""Database seeding service populating relational tables from audited Parquet artifacts."""

import logging

import pandas as pd
from sqlalchemy.orm import Session

from apps.api.config import api_settings
from apps.api.db import (
    ClientEntity,
    ClientFeaturesEntity,
    PropertyEntity,
    SessionLocal,
    init_db,
)

logger = logging.getLogger(__name__)


def seed_database_from_parquet(force: bool = False) -> dict[str, int]:
    """Seed relational database from clean Parquet tables for both full and sample scopes."""
    init_db()
    session: Session = SessionLocal()

    counts = {"clients": 0, "properties": 0, "client_features": 0}

    try:
        # Check if already seeded
        existing_clients = session.query(ClientEntity).count()
        if existing_clients > 0 and not force:
            logger.info("Database already seeded (%d clients present). Skipping.", existing_clients)
            return {
                "clients": existing_clients,
                "properties": session.query(PropertyEntity).count(),
                "client_features": session.query(ClientFeaturesEntity).count(),
            }

        if force:
            session.query(ClientFeaturesEntity).delete()
            session.query(PropertyEntity).delete()
            session.query(ClientEntity).delete()
            session.commit()

        # 1. Seed Full Production Dataset
        full_dir = api_settings.processed_dir
        if (full_dir / "clients_clean.parquet").exists():
            df_clients = pd.read_parquet(full_dir / "clients_clean.parquet")
            for _, r in df_clients.iterrows():
                session.add(
                    ClientEntity(
                        client_id=str(r["client_id"]),
                        client_type=str(r["client_type"]),
                        first_name=str(r["first_name"]),
                        last_name=str(r["last_name"]),
                        date_of_birth=str(r["date_of_birth"]),
                        gender=str(r["gender"]),
                        country=str(r["country"]),
                        region=str(r["region"]),
                        acquisition_purpose=str(r["acquisition_purpose"]),
                        satisfaction_score=int(r["satisfaction_score"]),
                        loan_applied=bool(r["loan_applied"]),
                        referral_channel=str(r["referral_channel"]),
                        age=int(r["age"]),
                        dataset_scope="full",
                    )
                )

        if (full_dir / "transactions_clean.parquet").exists():
            df_trans = pd.read_parquet(full_dir / "transactions_clean.parquet")
            for _, r in df_trans.iterrows():
                session.add(
                    PropertyEntity(
                        listing_id=int(r["listing_id"]),
                        tower_number=int(r["tower_number"]),
                        transaction_date=str(r["transaction_date"]),
                        unit_category=str(r["unit_category"]),
                        unit_number=int(r["unit_number"]),
                        floor_area_sqft=float(r["floor_area_sqft"]),
                        sale_price=float(r["sale_price"]),
                        listing_status="Sold",
                        client_ref=str(r["client_ref"]),
                        dataset_scope="full",
                    )
                )

        if (full_dir / "available_properties.parquet").exists():
            df_avail = pd.read_parquet(full_dir / "available_properties.parquet")
            for _, r in df_avail.iterrows():
                session.add(
                    PropertyEntity(
                        listing_id=int(r["listing_id"]),
                        tower_number=int(r["tower_number"]),
                        transaction_date=str(r["transaction_date"]),
                        unit_category=str(r["unit_category"]),
                        unit_number=int(r["unit_number"]),
                        floor_area_sqft=float(r["floor_area_sqft"]),
                        sale_price=float(r["sale_price"]),
                        listing_status="Available",
                        client_ref=None,
                        dataset_scope="full",
                    )
                )

        if (full_dir / "client_features.parquet").exists():
            df_feat = pd.read_parquet(full_dir / "client_features.parquet")
            # Load cluster assignments from joblib if not present in parquet
            if "cluster" not in df_feat.columns:
                import joblib

                bundle = joblib.load(api_settings.models_dir / "cluster_models.joblib")
                df_feat["cluster"] = bundle["labels"]
                if "soft_probabilities" in bundle:
                    soft_probs = bundle["soft_probabilities"]
                    for i in range(soft_probs.shape[1]):
                        df_feat[f"soft_prob_cluster_{i}"] = soft_probs[:, i]

            for _, r in df_feat.iterrows():
                session.add(
                    ClientFeaturesEntity(
                        client_id=str(r["client_id"]),
                        client_type=str(r["client_type"]),
                        country=str(r["country"]),
                        region=str(r["region"]),
                        acquisition_purpose=str(r["acquisition_purpose"]),
                        referral_channel=str(r["referral_channel"]),
                        age=int(r["age"]),
                        n_units=int(r["n_units"]),
                        total_spend=float(r["total_spend"]),
                        avg_price=float(r["avg_price"]),
                        max_price=float(r["max_price"]),
                        avg_floor_area=float(r["avg_floor_area"]),
                        price_per_sqft=float(r["price_per_sqft"]),
                        n_towers=int(r["n_towers"]),
                        office_share=float(r["office_share"]),
                        apartment_share=float(r["apartment_share"]),
                        portfolio_towers_hhi=float(r["portfolio_towers_hhi"]),
                        first_purchase_month=str(r["first_purchase_month"]),
                        last_purchase_month=str(r["last_purchase_month"]),
                        purchase_span_months=float(r["purchase_span_months"]),
                        is_multi_unit=bool(r["is_multi_unit"]),
                        spend_percentile=float(r["spend_percentile"]),
                        age_band=str(r["age_band"]),
                        cluster=int(r["cluster"]),
                        soft_prob_cluster_0=float(r.get("soft_prob_cluster_0", 0.0)),
                        soft_prob_cluster_1=float(r.get("soft_prob_cluster_1", 0.0)),
                        soft_prob_cluster_2=float(r.get("soft_prob_cluster_2", 0.0)),
                        soft_prob_cluster_3=float(r.get("soft_prob_cluster_3", 0.0)),
                        dataset_scope="full",
                    )
                )

        session.commit()
        counts["clients"] = session.query(ClientEntity).count()
        counts["properties"] = session.query(PropertyEntity).count()
        counts["client_features"] = session.query(ClientFeaturesEntity).count()
        logger.info("Database seeding completed successfully: %s", counts)
        return counts

    except Exception as exc:
        session.rollback()
        logger.error("Database seeding failed: %s", exc)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    res = seed_database_from_parquet(force=True)
    print("Seeding result:", res)
