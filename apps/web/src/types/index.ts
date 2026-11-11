export interface GlobalFilters {
  country?: string;
  region?: string;
  acquisition_purpose?: 'HOME' | 'INVESTMENT' | '';
  client_type?: 'INDIVIDUAL' | 'COMPANY' | '';
}

export interface ClientSummary {
  client_id: string;
  first_name: string;
  last_name: string;
  client_type: string;
  country: string;
  region: string;
  assigned_cluster: number;
  cluster_name: string;
  n_units: number;
  total_spend_inr: number;
  satisfaction_score: number;
  loan_applied: boolean;
  referral_channel: string;
  [key: string]: any;
}

export interface SegmentCatalogItem {
  cluster_id: number;
  segment_id: number;
  name: string;
  defining_archetype: string;
  buyer_count: number;
  buyer_share_pct: number;
  total_units: number;
  mean_units_per_buyer: number;
  total_spend_inr: number;
  total_spend_formatted_inr: string;
  mean_spend_per_buyer_inr: number;
  mean_spend_formatted_inr: string;
  office_unit_share_pct: number;
  mean_buyer_age: number;
  portfolio_towers_hhi: number;
  loan_dependence_rate_pct: number;
  top_referral_channel: string;
  primary_purpose: string;
}

export interface OverviewMetrics {
  total_buyers: number;
  total_transactions: number;
  total_portfolio_volume_inr: number;
  total_portfolio_volume_formatted_inr: string;
  mean_spend_per_buyer_inr: number;
  mean_spend_formatted_inr: string;
  mean_units_per_buyer: number;
  loan_dependence_rate_pct: number;
  top_country: string;
  top_country_share_pct: number;
  segments: SegmentCatalogItem[];
  key_takeaways?: string[];
  notices?: string[];
}

export interface BehaviorAnalytics {
  total_buyers: number;
  acquisition_purpose_split: {
    HOME: { count: number; pct: number };
    INVESTMENT: { count: number; pct: number };
  };
  loan_dependence_by_segment: Record<string, number>;
  referral_channel_mix: {
    Website: { count: number; pct: number };
    Agency: { count: number; pct: number };
    Client: { count: number; pct: number };
  };
  satisfaction_score_distribution: Record<number, number>;
  satisfaction_chi_square_evidence: {
    statistic: number;
    p_value: number;
    degrees_of_freedom: number;
    interpretation: string;
  };
  age_band_distribution: Record<string, number>;
}

export interface CountryStat {
  country: string;
  buyer_count: number;
  buyer_share_pct: number;
  total_spend_inr: number;
  total_spend_formatted_inr: string;
  mean_spend_per_buyer_inr: number;
  mean_spend_formatted_inr: string;
  loan_dependence_rate_pct: number;
}

export interface RegionStat {
  region: string;
  country: string;
  buyer_count: number;
  total_spend_inr: number;
  total_spend_formatted_inr: string;
}

export interface GeographyAnalytics {
  total_buyers: number;
  domestic_usa: {
    buyer_count: number;
    buyer_share_pct: number;
    total_spend_inr: number;
    total_spend_formatted_inr: string;
    mean_spend_inr: number;
    mean_spend_formatted_inr: string;
    loan_rate_pct: number;
  };
  international: {
    buyer_count: number;
    buyer_share_pct: number;
    total_spend_inr: number;
    total_spend_formatted_inr: string;
    mean_spend_inr: number;
    mean_spend_formatted_inr: string;
    loan_rate_pct: number;
  };
  usa_spend_premium_inr: number;
  usa_spend_premium_formatted_inr: string;
  welch_t_stat: number;
  welch_p_value: number;
  countries: CountryStat[];
  top_regions: RegionStat[];
}

export interface TowerMatrixCell {
  tower_number: number;
  month: string;
  unit_sales_count: number;
  sales_volume_inr: number;
}

export interface TowerSummary {
  tower_number: number;
  total_units_sold: number;
  apartment_count: number;
  office_count: number;
  office_share_pct: number;
  average_price_per_sqft_inr: number;
  group_type: '3-Unit Dominant (0% Group)' | '4+ Unit Concentrated (66.6% Group)';
}

export interface TowerAnalytics {
  total_towers: number;
  matrix: TowerMatrixCell[];
  tower_summaries: TowerSummary[];
  tower_clustering_observation: string;
}

export interface ProjectionPoint {
  client_id: string;
  assigned_cluster: number;
  segment_name: string;
  pca_x: number;
  pca_y: number;
  umap_x: number;
  umap_y: number;
  total_spend_inr: number;
  n_units: number;
}

export interface OpportunityUnit {
  property_id: string;
  unit_category: 'Apartment' | 'Office';
  tower_number: number;
  floor_area_sqft: number;
  sale_price_inr: number;
  sale_price_formatted_inr: string;
  price_per_sqft_inr: number;
  price_per_sqft_formatted_inr: string;
  segment_compatibility_score: number;
  rank: number;
}

export interface ClientProfile {
  client_id: string;
  client_name: string;
  country: string;
  region: string;
  client_type: 'INDIVIDUAL' | 'COMPANY';
  acquisition_purpose: 'HOME' | 'INVESTMENT';
  date_of_birth: string;
  age: number;
  referral_channel: 'Website' | 'Agency' | 'Client';
  loan_applied: boolean;
  satisfaction_score: number;
  n_units: number;
  total_spend_inr: number;
  total_spend_formatted_inr: string;
  spend_percentile: number;
  assigned_cluster: number;
  segment_name: string;
  probabilities: {
    cluster_0: number;
    cluster_1: number;
    cluster_2: number;
    cluster_3: number;
    p_max: number;
    is_ambiguous_boundary: boolean;
    is_ambiguous_margin: boolean;
  };
  transactions: Array<{
    property_id: string;
    tower_number: number;
    unit_category: string;
    floor_area_sqft: number;
    sale_price_inr: number;
    sale_price_formatted_inr: string;
    transaction_date: string;
  }>;
}

export interface CampaignSimulationResult {
  budget_breakdown_inr: {
    Website: number;
    Agency: number;
    Client: number;
    Total: number;
  };
  modeled_acquisitions: {
    Website: number;
    Agency: number;
    Client: number;
    Total: number;
  };
  modeled_gross_sales_volume_inr: {
    Website: number;
    Agency: number;
    Client: number;
    Total: number;
  };
  modeled_gross_sales_volume_formatted_inr: string;
  illustrative_cpa_inr: {
    Website: number;
    Agency: number;
    Client: number;
    Blended: number;
  };
  formula_disclaimer: string;
}

export interface DataQualityReport {
  timestamp: string;
  raw_properties_total: number;
  sold_properties: number;
  available_properties: number;
  clients_total: number;
  missing_values: Record<string, number>;
  dob_slash_dash_impact: {
    discrepancy_count: number;
    max_age_difference_years: number;
    verdict: string;
  };
  satisfaction_uniformity_test: {
    chi2: number;
    p_value: number;
    is_uniform: boolean;
  };
}

export interface ModelCardData {
  production_model: string;
  feature_count: number;
  k_clusters: number;
  macro_silhouette_score: number;
  beta_agreement_grid: Array<{
    beta: number;
    oof_agreement_pct: number;
    mean_oof_log_likelihood: number;
    ambiguity_rate_pct: number;
  }>;
  selected_beta: number;
  gmm_collapse_disclosure: string;
  prd_hypotheses_evaluation: Array<{
    hypothesis_code: string;
    name: string;
    prd_expectation: string;
    empirical_evidence: string;
    verdict: 'Supported' | 'Contradicted' | 'Reframed';
  }>;
}
