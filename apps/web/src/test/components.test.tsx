import { describe, it, expect } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { TopBar } from '../components/layout/TopBar';
import { Sidebar } from '../components/layout/Sidebar';
import { ExecutiveOverview } from '../pages/ExecutiveOverview';
import { SegmentExplorer } from '../pages/SegmentExplorer';
import { CampaignSimulator } from '../pages/CampaignSimulator';
import { DataSource } from '../pages/DataSource';

describe('Web UI Component Integration Suite', () => {
  it('renders TopBar with brand, dataset indicator, and role badge', async () => {
    await act(async () => {
      render(
        <BrowserRouter>
          <TopBar onOpenCommandPalette={() => {}} />
        </BrowserRouter>
      );
    });
    expect(screen.getByText('PARCL BUYER INTELLIGENCE')).toBeInTheDocument();
    expect(screen.getByText('Model B3')).toBeInTheDocument();
    expect(screen.getByText(/Analyst/i)).toBeInTheDocument();
  });

  it('renders Sidebar with all navigation routes including Data Source', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );
    expect(screen.getByText('Executive Overview')).toBeInTheDocument();
    expect(screen.getByText('Segment Explorer')).toBeInTheDocument();
    expect(screen.getByText('Behavior Lab')).toBeInTheDocument();
    expect(screen.getByText('Geo Intelligence')).toBeInTheDocument();
    expect(screen.getByText('Tower Heatmap')).toBeInTheDocument();
    expect(screen.getByText('Cluster Map (PCA)')).toBeInTheDocument();
    expect(screen.getByText('Opportunities & NBO')).toBeInTheDocument();
    expect(screen.getByText('Campaign Simulator')).toBeInTheDocument();
    expect(screen.getByText('Client Lookup & Predict')).toBeInTheDocument();
    expect(screen.getByText('Model Lab & Validation')).toBeInTheDocument();
    expect(screen.getByText('Data Quality & Lineage')).toBeInTheDocument();
    expect(screen.getByText('Data Source')).toBeInTheDocument();
  });

  it('renders ExecutiveOverview with primary portfolio metrics', async () => {
    render(
      <BrowserRouter>
        <ExecutiveOverview />
      </BrowserRouter>
    );
    expect(await screen.findByText('Executive Portfolio Overview')).toBeInTheDocument();
    expect(await screen.findAllByText(/₹252.08 Cr/i)).toBeTruthy();
    expect(await screen.findByText('Emerging Multi-Tower Accumulators')).toBeInTheDocument();
    expect(await screen.findByText('Concentrated Residential Buyers')).toBeInTheDocument();
  });

  it('renders SegmentExplorer with 4 grounded segments', async () => {
    render(<SegmentExplorer />);
    expect(await screen.findByText('Segment Persona Explorer')).toBeInTheDocument();
    expect(await screen.findByText(/Surrogate Decision Tree Rule/i)).toBeInTheDocument();
  });

  it('renders CampaignSimulator with channel allocation sliders', async () => {
    render(<CampaignSimulator />);
    expect(await screen.findByText('Marketing Campaign Simulator')).toBeInTheDocument();
    expect(await screen.findByText('Website Channel')).toBeInTheDocument();
    expect(await screen.findByText('Agency Channel')).toBeInTheDocument();
    expect(await screen.findAllByText('Client Referral')).toHaveLength(2);
  });

  it('renders GeoIntelligence with 10-country exact table and USA spend premium', async () => {
    const { GeoIntelligence } = await import('../pages/GeoIntelligence');
    render(<GeoIntelligence />);
    expect(await screen.findByText('Geographic Buyer Analysis')).toBeInTheDocument();
    expect(await screen.findByText(/USA Spend Premium: \+₹41,024.10/i)).toBeInTheDocument();
    expect(await screen.findByText(/Exact 10-Country Portfolio Accounting/i)).toBeInTheDocument();
  });

  it('renders TowerHeatmap with 20 towers and partition note', async () => {
    const { TowerHeatmap } = await import('../pages/TowerHeatmap');
    render(<TowerHeatmap />);
    expect(await screen.findByText('Tower & Inventory Heatmap')).toBeInTheDocument();
    expect(await screen.findByText(/Structural Tower Partition Observation/i)).toBeInTheDocument();
    expect(await screen.findByText(/313 Units \(Dec 2025\)/i)).toBeInTheDocument();
  });

  it('renders ClusterMap with 2D PCA projection scatter', async () => {
    const { ClusterMap } = await import('../pages/ClusterMap');
    render(<ClusterMap />);
    expect(await screen.findByText('2D Cluster Manifold Projection')).toBeInTheDocument();
    expect((await screen.findAllByText(/Principal Component 1/i)).length).toBeGreaterThan(0);
  });

  it('renders OpportunityFinder with available units ranking and NBO tab', async () => {
    const { OpportunityFinder } = await import('../pages/OpportunityFinder');
    render(<OpportunityFinder />);
    expect(await screen.findByText(/Opportunity Finder & NBO Engine/i)).toBeInTheDocument();
    expect(await screen.findByText('Segment Opportunity Finder')).toBeInTheDocument();
    expect(await screen.findByText('Personalized NBO (Client)')).toBeInTheDocument();
  });

  it('renders ClientLookup with client directory table and scoring modal trigger', async () => {
    const { ClientLookup } = await import('../pages/ClientLookup');
    render(<ClientLookup />);
    expect(await screen.findByText(/Client Intelligence & Live Scoring/i)).toBeInTheDocument();
    expect(await screen.findByText('Live Segment Scoring Modal')).toBeInTheDocument();
  });

  it('renders ModelLab with ablation variants and beta calibration curve', async () => {
    const { ModelLab } = await import('../pages/ModelLab');
    render(<ModelLab />);
    expect(await screen.findByText('Model Selection & Scientific Validation')).toBeInTheDocument();
    expect(await screen.findByText(/Feature Space Ablation Suite/i)).toBeInTheDocument();
    expect(await screen.findByText(/GMM Structural Collapse & Production Deprecation/i)).toBeInTheDocument();
  });

  it('renders DataQuality with DOB sensitivity and Chi-square audit proofs', async () => {
    const { DataQuality } = await import('../pages/DataQuality');
    render(<DataQuality />);
    expect(await screen.findByText('Data Quality & Pipeline Lineage')).toBeInTheDocument();
    expect((await screen.findAllByText(/0 Discrepancies/i)).length).toBeGreaterThan(0);
    expect(await screen.findByText(/7,305 \/ 2,695/i)).toBeInTheDocument();
  });

  it('renders DataSource with dataset toggles and Pandera download buttons', async () => {
    render(<DataSource />);
    expect(await screen.findByText('Dataset Management & Data Source')).toBeInTheDocument();
    expect(await screen.findByText('Active Dataset Selector')).toBeInTheDocument();
    expect(await screen.findByText('clients_sample.csv')).toBeInTheDocument();
    expect(await screen.findByText('properties_sample.csv')).toBeInTheDocument();
  });
});
