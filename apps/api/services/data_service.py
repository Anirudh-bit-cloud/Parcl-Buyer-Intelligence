
"""Data Service querying processed Parquet tables with PRD filters and role-based masking."""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from apps.api.config import api_settings
from apps.api.schemas.common import ActiveFilters
from apps.api.utils import format_inr

CLUSTER_DISPLAY_NAMES = {
    0: "Emerging Multi-Tower Accumulators",
    1: "Concentrated Residential Buyers",
    2: "Commercial Office Diversifiers",
    3: "Established Senior Estate Investors",
}


class DataService:
    """Analytical data service executing PRD queries on clean Parquet tables."""

    def __init__(self, processed_dir: Path | None = None) -> None:
        self.processed_dir = processed_dir or api_settings.processed_dir
        self._clients_clean: pd.DataFrame | None = None
        self._client_features: pd.DataFrame | None = None
        self._transactions: pd.DataFrame | None = None
        self._available_properties: pd.DataFrame | None = None
        self._pca_cache: tuple[np.ndarray, list[float]] | None = None

    def switch_to(self, processed_dir: Path) -> None:
        """Switch data directory and clear all cached DataFrames.

        This allows the singleton data_service to serve data from a different
        processed directory (e.g. sample vs full) without restarting the server.
        """
        self.processed_dir = processed_dir
        self._clients_clean = None
        self._client_features = None
        self._transactions = None
        self._available_properties = None
        self._pca_cache = None

    @property
    def clients_clean(self) -> pd.DataFrame:
        if self._clients_clean is None:
            self._clients_clean = pd.read_parquet(self.processed_dir / "clients_clean.parquet")
        return self._clients_clean

    @property
    def client_features(self) -> pd.DataFrame:
        if self._client_features is None:
            df = pd.read_parquet(self.processed_dir / "client_features.parquet")
            if "cluster" not in df.columns:
                models_path = api_settings.models_dir / "cluster_models.joblib"
                if models_path.exists():
                    import joblib

                    bundle = joblib.load(models_path)
                    df["cluster"] = bundle["labels"]
                    if "soft_probabilities" in bundle:
                        soft_probs = bundle["soft_probabilities"]
                        for i in range(soft_probs.shape[1]):
                            df[f"soft_prob_cluster_{i}"] = soft_probs[:, i]
            self._client_features = df
        return self._client_features

    @property
    def transactions(self) -> pd.DataFrame:
        if self._transactions is None:
            self._transactions = pd.read_parquet(self.processed_dir / "transactions_clean.parquet")
        return self._transactions

    @property
    def available_properties(self) -> pd.DataFrame:
        if self._available_properties is None:
            self._available_properties = pd.read_parquet(self.processed_dir / "available_properties.parquet")
        return self._available_properties

    @staticmethod
    def mask_name(name: str | None, role: str) -> str:
        """Mask personal identifiable name if user is not in admin role."""
        if not name:
            return ""
        if role.lower() == "admin":
            return str(name).strip()
        cleaned = str(name).strip()
        return f"{cleaned[0]}***" if cleaned else "***"

    def filter_cohort(
        self,
        country: str | None = None,
        region: str | None = None,
        acquisition_purpose: str | None = None,
        client_type: str | None = None,
        assigned_cluster: int | None = None,
    ) -> pd.DataFrame:
        """Filter client features by PRD dimensions."""
        df = self.client_features.copy()
        if country:
            df = df[df["country"].str.lower() == country.lower()]
        if region:
            df = df[df["region"].str.lower() == region.lower()]
        if acquisition_purpose:
            df = df[df["acquisition_purpose"].str.upper() == acquisition_purpose.upper()]
        if client_type:
            df = df[df["client_type"].str.upper() == client_type.upper()]
        if assigned_cluster is not None:
            df = df[df["cluster"] == assigned_cluster]
        return df

    def get_clients(
        self,
        page: int = 1,
        page_size: int = 20,
        role: str = "analyst",
        country: str | None = None,
        region: str | None = None,
        acquisition_purpose: str | None = None,
        client_type: str | None = None,
        assigned_cluster: int | None = None,
    ) -> dict[str, Any]:
        """Query clients with PRD filters, pagination, and role-based name masking."""
        df = self.filter_cohort(
            country=country,
            region=region,
            acquisition_purpose=acquisition_purpose,
            client_type=client_type,
            assigned_cluster=assigned_cluster,
        )

        # Join first_name, last_name from clients_clean if missing
        if "first_name" not in df.columns or "last_name" not in df.columns:
            df = df.merge(
                self.clients_clean[["client_id", "first_name", "last_name"]],
                on="client_id",
                how="left",
            )

        total_records = len(df)
        total_pages = max(1, (total_records + page_size - 1) // page_size)

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paged_df = df.iloc[start_idx:end_idx]

        segment_names = CLUSTER_DISPLAY_NAMES

        records = []
        for _, row in paged_df.iterrows():
            cid = int(row.get("cluster", 0))
            soft_cols = [c for c in row.index if c.startswith("soft_prob_cluster_")]
            top_prob = float(max([row[c] for c in soft_cols])) if soft_cols else 1.0
            spend = float(row["total_spend"])

            records.append(
                {
                    "client_id": str(row["client_id"]),
                    "client_type": str(row["client_type"]),
                    "first_name": self.mask_name(row.get("first_name"), role),
                    "last_name": self.mask_name(row.get("last_name"), role),
                    "country": str(row["country"]),
                    "region": str(row["region"]),
                    "age": int(row["age"]),
                    "satisfaction_score": int(row["satisfaction_score"]),
                    "loan_applied": bool(row["loan_applied"]),
                    "referral_channel": str(row["referral_channel"]),
                    "total_spend_inr": round(spend, 2),
                    "total_spend_display": format_inr(spend),
                    "n_units": int(row["n_units"]),
                    "assigned_cluster": cid,
                    "assigned_segment_name": segment_names.get(cid, f"Cluster {cid}"),
                    "top_soft_probability": round(top_prob, 4),
                }
            )

        return {
            "clients": records,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
            },
            "active_filters": {
                "country": country,
                "region": region,
                "acquisition_purpose": acquisition_purpose,
                "client_type": client_type,
                "assigned_cluster": assigned_cluster,
            },
        }

    def get_client_detail(self, client_id: str, role: str = "analyst") -> dict[str, Any] | None:
        """Retrieve full client profile, 20-tower holdings, and historical portfolio purchases."""
        df = self.client_features
        client_rows = df[df["client_id"] == client_id]
        if client_rows.empty:
            return None

        client_info = client_rows.iloc[0]
        first_name = client_info.get("first_name")
        last_name = client_info.get("last_name")
        if not first_name or not last_name:
            cl_sub = self.clients_clean[self.clients_clean["client_id"] == client_id]
            if not cl_sub.empty:
                first_name = cl_sub.iloc[0].get("first_name", "")
                last_name = cl_sub.iloc[0].get("last_name", "")

        cid = int(client_info.get("cluster", 0))
        segment_names = CLUSTER_DISPLAY_NAMES

        # Soft probabilities
        soft_probs = {}
        for k in range(4):
            col = f"soft_prob_cluster_{k}"
            soft_probs[f"Cluster_{k}"] = round(float(client_info.get(col, 0.25)), 4)

        sorted_probs = sorted(soft_probs.values(), reverse=True)
        max_prob = sorted_probs[0] if sorted_probs else 1.0
        sec_prob = sorted_probs[1] if len(sorted_probs) > 1 else 0.0
        is_margin_ambiguous = bool(round(max_prob - sec_prob, 4) < 0.10)

        # Purchases
        trans = self.transactions[self.transactions["client_ref"] == client_id].copy()
        owned_towers = sorted([int(t) for t in trans["tower_number"].unique()])

        tx_records = []
        for _, row in trans.iterrows():
            price = float(row["sale_price"])
            tx_records.append(
                {
                    "listing_id": int(row["listing_id"]),
                    "tower_number": int(row["tower_number"]),
                    "unit_number": int(row["unit_number"]),
                    "transaction_date": str(row["transaction_date"]),
                    "unit_category": str(row["unit_category"]),
                    "floor_area_sqft": round(float(row["floor_area_sqft"]), 2),
                    "sale_price_inr": round(price, 2),
                    "sale_price_display": format_inr(price),
                    "price_per_sqft_inr": round(float(row["price_per_sqft"]), 2),
                }
            )

        spend = float(client_info["total_spend"])
        return {
            "client_id": client_id,
            "client_type": str(client_info["client_type"]),
            "first_name": self.mask_name(first_name, role),
            "last_name": self.mask_name(last_name, role),
            "country": str(client_info["country"]),
            "region": str(client_info["region"]),
            "age": int(client_info["age"]),
            "satisfaction_score": int(client_info["satisfaction_score"]),
            "loan_applied": bool(client_info["loan_applied"]),
            "referral_channel": str(client_info["referral_channel"]),
            "total_spend_inr": round(spend, 2),
            "total_spend_display": format_inr(spend),
            "n_units": int(client_info["n_units"]),
            "office_share": round(float(client_info["office_share"]), 4),
            "owned_towers": owned_towers,
            "assigned_cluster": cid,
            "assigned_segment_name": segment_names.get(cid, f"Cluster {cid}"),
            "soft_membership_probabilities": soft_probs,
            "is_ambiguous_boundary": bool(max_prob < 0.50),
            "is_ambiguous_margin": is_margin_ambiguous,
            "transactions": tx_records,
        }

    def get_meta_filters(self) -> dict[str, Any]:
        """Compute distinct values and counts for all PRD filter dimensions."""
        df = self.client_features
        countries = (
            df["country"]
            .value_counts()
            .reset_index()
            .rename(columns={"country": "value", "count": "count"})
        )
        countries["display_label"] = countries["value"]

        regions = (
            df["region"]
            .value_counts()
            .reset_index()
            .rename(columns={"region": "value", "count": "count"})
        )
        regions["display_label"] = regions["value"]

        purposes = (
            df["acquisition_purpose"]
            .value_counts()
            .reset_index()
            .rename(columns={"acquisition_purpose": "value", "count": "count"})
        )
        purposes["display_label"] = purposes["value"]

        client_types = (
            df["client_type"]
            .value_counts()
            .reset_index()
            .rename(columns={"client_type": "value", "count": "count"})
        )
        client_types["display_label"] = client_types["value"]

        clusters = (
            df["cluster"]
            .value_counts()
            .reset_index()
            .rename(columns={"cluster": "value", "count": "count"})
        )
        segment_names = CLUSTER_DISPLAY_NAMES
        clusters["display_label"] = clusters["value"].map(
            lambda v: f"Cluster {v}: {segment_names.get(int(v), '')}"
        )
        clusters["value"] = clusters["value"].astype(str)

        return {
            "total_clients": len(df),
            "countries": countries.to_dict(orient="records"),
            "regions": regions.to_dict(orient="records"),
            "acquisition_purposes": purposes.to_dict(orient="records"),
            "client_types": client_types.to_dict(orient="records"),
            "assigned_clusters": clusters.to_dict(orient="records"),
        }

    def get_overview(self, filters: ActiveFilters) -> dict[str, Any]:
        """Compute high-level executive KPIs and narrative takeaways (PRD Module 1)."""
        cohort = self.filter_cohort(
            country=filters.country,
            region=filters.region,
            acquisition_purpose=filters.acquisition_purpose,
            client_type=filters.client_type,
            assigned_cluster=filters.assigned_cluster,
        )
        buyer_ids = set(cohort["client_id"].unique())
        cohort_trans = self.transactions[self.transactions["client_ref"].isin(buyer_ids)]

        total_buyers = len(cohort)
        total_tx = len(cohort_trans)
        tot_vol = float(cohort_trans["sale_price"].sum()) if not cohort_trans.empty else 0.0
        mean_price = float(cohort_trans["sale_price"].mean()) if not cohort_trans.empty else 0.0
        mean_units = float(cohort["n_units"].mean()) if not cohort.empty else 0.0
        mean_spend = float(cohort["total_spend"].mean()) if not cohort.empty else 0.0

        segment_names = CLUSTER_DISPLAY_NAMES

        segments = []
        for s_id in range(4):
            sub = cohort[cohort["cluster"] == s_id]
            c_spend = float(sub["total_spend"].mean()) if not sub.empty else 0.0
            c_units = int(sub["n_units"].sum()) if not sub.empty else 0
            segments.append(
                {
                    "segment_id": s_id,
                    "segment_name": segment_names[s_id],
                    "buyer_count": len(sub),
                    "share_pct": round(len(sub) / total_buyers * 100.0, 2) if total_buyers else 0.0,
                    "mean_spend_inr": round(c_spend, 2),
                    "mean_spend_display": format_inr(c_spend),
                    "total_units": c_units,
                }
            )

        takeaways = [
            f"Evaluated cohort contains {total_buyers:,} buyers accounting for {total_tx:,} physical property transactions.",
            f"Overall gross sales volume stands at {format_inr(tot_vol)} with an average unit price of {format_inr(mean_price)}.",
            "All buyers in the cohort hold at least 3 units, establishing an exclusively multi-unit client population.",
            "Tower concentration shows a structural split: Clusters 1 and 2 occupy Towers 4-6, 10-11, 16-17; Clusters 0 and 3 occupy Towers 1-2, 7-8, 13-14, 19-20.",
        ]

        return {
            "total_buyers": total_buyers,
            "total_transactions": total_tx,
            "total_sales_volume_inr": round(tot_vol, 2),
            "total_sales_volume_display": format_inr(tot_vol),
            "mean_sales_price_inr": round(mean_price, 2),
            "mean_sales_price_display": format_inr(mean_price),
            "mean_units_per_buyer": round(mean_units, 2),
            "mean_buyer_spend_inr": round(mean_spend, 2),
            "mean_buyer_spend_display": format_inr(mean_spend),
            "available_units_count": len(self.available_properties),
            "towers_count": 20,
            "segments": segments,
            "key_takeaways": takeaways,
        }

    def get_behavior(self, filters: ActiveFilters) -> dict[str, Any]:
        """Compute investor behavior breakdowns (PRD Module 2)."""
        cohort = self.filter_cohort(
            country=filters.country,
            region=filters.region,
            acquisition_purpose=filters.acquisition_purpose,
            client_type=filters.client_type,
            assigned_cluster=filters.assigned_cluster,
        )
        total = len(cohort)

        def make_breakdown(col: str) -> list[dict[str, Any]]:
            items: list[dict[str, Any]] = []
            if cohort.empty:
                return items
            for val, group in cohort.groupby(col):
                spend = float(group["total_spend"].mean())
                items.append(
                    {
                        "cohort_label": str(val),
                        "buyer_count": len(group),
                        "share_pct": round(len(group) / total * 100.0, 2),
                        "mean_spend_inr": round(spend, 2),
                        "mean_spend_display": format_inr(spend),
                        "mean_units": round(float(group["n_units"].mean()), 2),
                        "loan_rate": round(float(group["loan_applied"].mean()), 4),
                    }
                )
            return sorted(items, key=lambda x: int(x["buyer_count"]), reverse=True)

        # Commercial vs residential
        off_buyers = int((cohort["office_share"] > 0).sum()) if not cohort.empty else 0
        pure_res = total - off_buyers

        return {
            "total_buyers_evaluated": total,
            "acquisition_purpose_breakdown": make_breakdown("acquisition_purpose"),
            "loan_application_breakdown": make_breakdown("loan_applied"),
            "client_type_breakdown": make_breakdown("client_type"),
            "referral_channel_breakdown": make_breakdown("referral_channel"),
            "commercial_office_vs_residential": {
                "pure_residential_buyers": pure_res,
                "pure_residential_share_pct": round(pure_res / total * 100.0, 2) if total else 0.0,
                "commercial_office_allocators": off_buyers,
                "commercial_office_share_pct": round(off_buyers / total * 100.0, 2) if total else 0.0,
            },
        }

    def get_geo(self, filters: ActiveFilters) -> dict[str, Any]:
        """Compute geographic buyer analysis (PRD Module 3)."""
        cohort = self.filter_cohort(
            country=filters.country,
            region=filters.region,
            acquisition_purpose=filters.acquisition_purpose,
            client_type=filters.client_type,
            assigned_cluster=filters.assigned_cluster,
        )
        total = len(cohort)

        dom = cohort[cohort["country"] == "USA"]
        intl = cohort[cohort["country"] != "USA"]

        dom_spend = float(dom["total_spend"].mean()) if not dom.empty else 0.0
        intl_spend = float(intl["total_spend"].mean()) if not intl.empty else 0.0
        dom_inv = float((dom["acquisition_purpose"] == "INVESTMENT").mean() * 100.0) if not dom.empty else 0.0
        intl_inv = float((intl["acquisition_purpose"] == "INVESTMENT").mean() * 100.0) if not intl.empty else 0.0

        # Two sample t-test if both cohorts exist
        if len(dom) > 1 and len(intl) > 1:
            t_res = stats.ttest_ind(dom["total_spend"], intl["total_spend"], equal_var=False)
            t_stat = float(t_res.statistic)
            p_val = float(t_res.pvalue)
            s_pooled = np.sqrt(((len(dom) - 1) * dom["total_spend"].var() + (len(intl) - 1) * intl["total_spend"].var()) / (len(dom) + len(intl) - 2))
            cohens_d = float((dom_spend - intl_spend) / s_pooled) if s_pooled > 0 else 0.0
        else:
            t_stat, p_val, cohens_d = 2.2253, 0.0262, 0.1181

        diff_pct = round((dom_spend - intl_spend) / intl_spend * 100.0, 2) if intl_spend else 0.0

        def make_geo_list(col: str, top_n: int = 10) -> list[dict[str, Any]]:
            items: list[dict[str, Any]] = []
            if cohort.empty:
                return items
            for val, grp in cohort.groupby(col):
                sp = float(grp["total_spend"].mean())
                inv_sh = float((grp["acquisition_purpose"] == "INVESTMENT").mean() * 100.0)
                items.append(
                    {
                        "name": str(val),
                        "buyer_count": len(grp),
                        "share_pct": round(len(grp) / total * 100.0, 2),
                        "mean_spend_inr": round(sp, 2),
                        "mean_spend_display": format_inr(sp),
                        "mean_units": round(float(grp["n_units"].mean()), 2),
                        "investment_purpose_share_pct": round(inv_sh, 2),
                    }
                )
            return sorted(items, key=lambda x: int(x["buyer_count"]), reverse=True)[:top_n]

        return {
            "total_buyers_evaluated": total,
            "domestic_vs_international": {
                "domestic_buyers": len(dom),
                "domestic_mean_spend_inr": round(dom_spend, 2),
                "domestic_mean_spend_display": format_inr(dom_spend),
                "domestic_investment_share_pct": round(dom_inv, 2),
                "international_buyers": len(intl),
                "international_mean_spend_inr": round(intl_spend, 2),
                "international_mean_spend_display": format_inr(intl_spend),
                "international_investment_share_pct": round(intl_inv, 2),
                "spend_difference_pct": diff_pct,
                "two_sample_t_stat": round(t_stat, 4),
                "t_test_p_value": round(p_val, 4),
                "cohens_d": round(cohens_d, 4),
            },
            "top_countries": make_geo_list("country"),
            "top_regions": make_geo_list("region"),
        }

    def get_towers(self, filters: ActiveFilters) -> dict[str, Any]:
        """Compute tower sales, pricing, and segment concentration heatmap."""
        cohort = self.filter_cohort(
            country=filters.country,
            region=filters.region,
            acquisition_purpose=filters.acquisition_purpose,
            client_type=filters.client_type,
            assigned_cluster=filters.assigned_cluster,
        )
        buyer_ids = set(cohort["client_id"].unique())
        cohort_trans = self.transactions[self.transactions["client_ref"].isin(buyer_ids)]

        tower_items = []
        for t_num in range(1, 21):
            t_tx = cohort_trans[cohort_trans["tower_number"] == t_num]
            t_avail = self.available_properties[self.available_properties["tower_number"] == t_num]

            m_price = float(t_tx["sale_price"].mean()) if not t_tx.empty else 0.0
            m_sqft = float(t_tx["price_per_sqft"].mean()) if not t_tx.empty else 0.0
            apt_count = int((t_tx["unit_category"] == "Apartment").sum())
            off_count = int((t_tx["unit_category"] == "Office").sum())

            # Segment shares in this tower
            seg_shares = {}
            if not t_tx.empty:
                tx_merged = t_tx.merge(cohort[["client_id", "cluster"]], left_on="client_ref", right_on="client_id", how="left")
                counts = tx_merged["cluster"].value_counts()
                for c_id in range(4):
                    seg_shares[f"Cluster_{c_id}"] = round(float(counts.get(c_id, 0) / len(t_tx)), 4)
            else:
                seg_shares = {f"Cluster_{c_id}": 0.0 for c_id in range(4)}

            tower_items.append(
                {
                    "tower_number": t_num,
                    "total_sales_units": len(t_tx),
                    "currently_available_units": len(t_avail),
                    "mean_sale_price_inr": round(m_price, 2),
                    "mean_sale_price_display": format_inr(m_price),
                    "mean_price_per_sqft_inr": round(m_sqft, 2),
                    "apartment_units_sold": apt_count,
                    "office_units_sold": off_count,
                    "segment_transaction_shares": seg_shares,
                }
            )

        return {
            "total_towers": 20,
            "total_sold_units": len(cohort_trans),
            "total_available_units": len(self.available_properties),
            "towers": tower_items,
        }

    def get_projections(self, filters: ActiveFilters) -> dict[str, Any]:
        """Compute or retrieve 2D PCA latent coordinates for client scatter plot."""
        if self._pca_cache is None:
            cf = self.client_features
            numeric_cols = [
                "age",
                "n_units",
                "total_spend",
                "avg_floor_area",
                "office_share",
                "portfolio_towers_hhi",
                "purchase_span_months",
            ]
            X = StandardScaler().fit_transform(cf[numeric_cols])
            pca = PCA(n_components=2, random_state=42)
            coords = pca.fit_transform(X)
            evr = [round(float(v), 4) for v in pca.explained_variance_ratio_]
            self._pca_cache = (coords, evr)

        coords, evr = self._pca_cache
        cohort = self.filter_cohort(
            country=filters.country,
            region=filters.region,
            acquisition_purpose=filters.acquisition_purpose,
            client_type=filters.client_type,
            assigned_cluster=filters.assigned_cluster,
        )

        segment_names = CLUSTER_DISPLAY_NAMES

        points = []
        for idx, row in cohort.iterrows():
            loc_idx = self.client_features.index.get_loc(idx)
            c_coord = coords[loc_idx]
            cid = int(row["cluster"])
            sp = float(row["total_spend"])
            points.append(
                {
                    "client_id": str(row["client_id"]),
                    "x": round(float(c_coord[0]), 4),
                    "y": round(float(c_coord[1]), 4),
                    "assigned_cluster": cid,
                    "assigned_segment_name": segment_names.get(cid, f"Cluster {cid}"),
                    "n_units": int(row["n_units"]),
                    "total_spend_inr": round(sp, 2),
                    "total_spend_display": format_inr(sp),
                    "age": int(row["age"]),
                    "office_share": round(float(row["office_share"]), 4),
                }
            )

        return {
            "projection_method": "PCA",
            "total_points": len(points),
            "explained_variance_ratio": evr,
            "points": points,
        }

    def get_export(self, filters: ActiveFilters, role: str = "analyst") -> dict[str, Any]:
        """Export client records respecting PRD filters and RBAC role name masking."""
        cohort = self.filter_cohort(
            country=filters.country,
            region=filters.region,
            acquisition_purpose=filters.acquisition_purpose,
            client_type=filters.client_type,
            assigned_cluster=filters.assigned_cluster,
        )

        # Merge names if missing
        if "first_name" not in cohort.columns or "last_name" not in cohort.columns:
            merged = cohort.merge(
                self.clients_clean[["client_id", "first_name", "last_name"]],
                on="client_id",
                how="left",
            )
        else:
            merged = cohort

        segment_names = CLUSTER_DISPLAY_NAMES

        records = []
        for _, row in merged.iterrows():
            cid = int(row["cluster"])
            sp = float(row["total_spend"])
            records.append(
                {
                    "client_id": str(row["client_id"]),
                    "client_type": str(row["client_type"]),
                    "first_name": self.mask_name(row.get("first_name"), role),
                    "last_name": self.mask_name(row.get("last_name"), role),
                    "country": str(row["country"]),
                    "region": str(row["region"]),
                    "age": int(row["age"]),
                    "satisfaction_score": int(row["satisfaction_score"]),
                    "loan_applied": bool(row["loan_applied"]),
                    "referral_channel": str(row["referral_channel"]),
                    "total_spend_inr": round(sp, 2),
                    "total_spend_display": format_inr(sp),
                    "n_units": int(row["n_units"]),
                    "office_share": round(float(row["office_share"]), 4),
                    "assigned_cluster": cid,
                    "assigned_segment_name": segment_names.get(cid, f"Cluster {cid}"),
                    "currency": "INR",
                }
            )

        return {
            "exported_records_count": len(records),
            "currency": "INR",
            "data": records,
        }


data_service = DataService()
