import overviewFallback from '../data/samples/overview.json';
import segmentsFallback from '../data/samples/segments_catalog.json';
import segmentDetail2Fallback from '../data/samples/segment_detail_cluster_2.json';
import behaviorFallback from '../data/samples/behavior.json';
import geoFallback from '../data/samples/geo.json';
import towersFallback from '../data/samples/towers.json';
import projectionFallback from '../data/samples/projection.json';
import opportunitiesFallback from '../data/samples/opportunities_segment_2_office.json';
import campaignFallback from '../data/samples/campaign_scenario.json';
import clientsFallback from '../data/samples/clients.json';
import clientC0001Fallback from '../data/samples/client_detail_c0001.json';
import nboFallback from '../data/samples/nbo_c0001.json';
import dataQualityFallback from '../data/samples/data_quality.json';
import modelCardFallback from '../data/samples/model_card.json';
import modelSelectionFallback from '../data/samples/model_selection.json';
import metaFiltersFallback from '../data/samples/meta_filters.json';
import { useAuthStore } from '../stores/authStore';
import { useFilterStore } from '../stores/filterStore';
import { useDatasetStore } from '../stores/datasetStore';

function buildQueryString(params: Record<string, string | number | boolean | undefined | null>): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') {
      q.append(k, String(v));
    }
  }
  const s = q.toString();
  return s ? `?${s}` : '';
}

async function apiFetch<T>(endpoint: string, options: RequestInit = {}, fallbackData: T): Promise<T> {
  const token = useAuthStore.getState().token;
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  try {
    const res = await fetch(endpoint, {
      ...options,
      headers,
    });
    if (res.ok) {
      useDatasetStore.getState().setIsOffline(false);
      return (await res.json()) as T;
    }
    console.warn(`API responded with ${res.status} for ${endpoint}, using verified fallback data.`);
    return fallbackData;
  } catch {
    // Backend offline / network unreachable -> trigger subtle offline indicator
    useDatasetStore.getState().setIsOffline(true);
    return fallbackData;
  }
}

export const api = {
  async getMetaFilters() {
    return apiFetch('/api/v1/meta/filters', {}, metaFiltersFallback);
  },

  async getOverview() {
    const { country, region, acquisition_purpose, client_type } = useFilterStore.getState();
    const qs = buildQueryString({ country, region, acquisition_purpose, client_type });
    return apiFetch(`/api/v1/analytics/overview${qs}`, {}, overviewFallback);
  },

  async getSegments() {
    const { country, region, acquisition_purpose, client_type } = useFilterStore.getState();
    const qs = buildQueryString({ country, region, acquisition_purpose, client_type });
    return apiFetch(`/api/v1/segments${qs}`, {}, segmentsFallback);
  },

  async getSegmentDetail(segmentId: number) {
    return apiFetch(`/api/v1/segments/${segmentId}`, {}, segmentDetail2Fallback);
  },

  async getBehavior() {
    const { country, region, acquisition_purpose, client_type } = useFilterStore.getState();
    const qs = buildQueryString({ country, region, acquisition_purpose, client_type });
    return apiFetch(`/api/v1/analytics/behavior${qs}`, {}, behaviorFallback);
  },

  async getGeography() {
    const { country, region, acquisition_purpose, client_type } = useFilterStore.getState();
    const qs = buildQueryString({ country, region, acquisition_purpose, client_type });
    return apiFetch(`/api/v1/analytics/geography${qs}`, {}, geoFallback);
  },

  async getTowers() {
    const { country, region, acquisition_purpose, client_type } = useFilterStore.getState();
    const qs = buildQueryString({ country, region, acquisition_purpose, client_type });
    return apiFetch(`/api/v1/analytics/towers${qs}`, {}, towersFallback);
  },

  async getProjection() {
    return apiFetch('/api/v1/analytics/projection', {}, projectionFallback);
  },

  async getOpportunities(segmentId = 2, unitCategory?: string) {
    const qs = buildQueryString({ segment_id: segmentId, unit_category: unitCategory });
    return apiFetch(`/api/v1/recommendations/opportunities${qs}`, {}, opportunitiesFallback);
  },

  async getClients(page = 1, pageSize = 20, search?: string) {
    const { country, region, acquisition_purpose, client_type } = useFilterStore.getState();
    const qs = buildQueryString({ page, page_size: pageSize, search, country, region, acquisition_purpose, client_type });
    return apiFetch(`/api/v1/clients${qs}`, {}, clientsFallback);
  },

  async getClientDetail(clientId: string) {
    return apiFetch(`/api/v1/clients/${clientId}`, {}, clientC0001Fallback);
  },

  async getClientRecommendations(clientId: string) {
    return apiFetch(`/api/v1/clients/${clientId}/recommendations`, {}, nboFallback);
  },

  async simulateCampaign(payload: {
    total_budget_inr: number;
    allocation_website_pct: number;
    allocation_agency_pct: number;
    allocation_client_pct: number;
  }) {
    return apiFetch('/api/v1/campaigns/scenario', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }, campaignFallback);
  },

  async predictSegment(payload: {
    age: number;
    country: string;
    region: string;
    acquisition_purpose: string;
    referral_channel: string;
    n_units: number;
  }) {
    return apiFetch('/api/v1/predict/segment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }, {
      assigned_cluster: 2,
      assigned_cluster_name: 'Commercial Office Diversifiers',
      confidence_probability: 0.6726,
      p_max: 0.6726,
      probabilities: {
        cluster_0: 0.0026,
        cluster_1: 0.3222,
        cluster_2: 0.6726,
        cluster_3: 0.0026
      },
      is_ambiguous_boundary: false,
      is_ambiguous_margin: false
    });
  },

  async getDataQuality() {
    return apiFetch('/api/v1/governance/data-quality', {}, dataQualityFallback);
  },

  async getModelCard() {
    return apiFetch('/api/v1/governance/model-card', {}, modelCardFallback);
  },

  async getModelSelection() {
    return apiFetch('/api/v1/governance/model-selection', {}, modelSelectionFallback);
  },
};
