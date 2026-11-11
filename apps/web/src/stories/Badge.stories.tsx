import React from 'react';
import { Badge } from '../components/ui/Badge';

export default {
  title: 'Design System/Badge',
  component: Badge,
  tags: ['autodocs'],
};

export const Default = () => <Badge variant="default">Default Token</Badge>;
export const Success = () => <Badge variant="success">Validated 100%</Badge>;
export const Warning = () => <Badge variant="warning">Review Required</Badge>;
export const Danger = () => <Badge variant="danger">Disparity Detected</Badge>;
export const Accent = () => <Badge variant="accent">Enterprise v2.0</Badge>;
export const Cluster0 = () => <Badge variant="cluster-0">C0: Cautious Buyers</Badge>;
export const Cluster1 = () => <Badge variant="cluster-1">C1: Global Investors</Badge>;
export const Cluster2 = () => <Badge variant="cluster-2">C2: High-Density Investors</Badge>;
export const Cluster3 = () => <Badge variant="cluster-3">C3: Commercial Specialists</Badge>;
