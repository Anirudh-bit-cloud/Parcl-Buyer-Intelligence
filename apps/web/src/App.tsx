import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { ExecutiveOverview } from './pages/ExecutiveOverview';
import { SegmentExplorer } from './pages/SegmentExplorer';
import { BehaviorLab } from './pages/BehaviorLab';
import { GeoIntelligence } from './pages/GeoIntelligence';
import { TowerHeatmap } from './pages/TowerHeatmap';
import { ClusterMap } from './pages/ClusterMap';
import { OpportunityFinder } from './pages/OpportunityFinder';
import { CampaignSimulator } from './pages/CampaignSimulator';
import { ClientLookup } from './pages/ClientLookup';
import { ModelLab } from './pages/ModelLab';
import { DataQuality } from './pages/DataQuality';
import { DataSource } from './pages/DataSource';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<ExecutiveOverview />} />
          <Route path="segments" element={<SegmentExplorer />} />
          <Route path="behavior" element={<BehaviorLab />} />
          <Route path="geo" element={<GeoIntelligence />} />
          <Route path="towers" element={<TowerHeatmap />} />
          <Route path="cluster-map" element={<ClusterMap />} />
          <Route path="opportunities" element={<OpportunityFinder />} />
          <Route path="campaigns" element={<CampaignSimulator />} />
          <Route path="clients" element={<ClientLookup />} />
          <Route path="model-lab" element={<ModelLab />} />
          <Route path="data-quality" element={<DataQuality />} />
          <Route path="data" element={<DataSource />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
