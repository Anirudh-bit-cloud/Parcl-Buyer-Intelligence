import React from 'react';
import { KPICard } from '../components/ui/KPICard';
import { Users, TrendingUp, DollarSign } from 'lucide-react';

export default {
  title: 'Design System/KPICard',
  component: KPICard,
  tags: ['autodocs'],
};

export const Standard = () => (
  <KPICard
    label="Total Active Buyers"
    value="2,000"
    subtitle="Audited microdata cohort"
    icon={<Users className="w-4 h-4" />}
    badge={{ text: '100% Complete', variant: 'success' }}
  />
);

export const Financial = () => (
  <KPICard
    label="Portfolio Spend"
    value="₹2,50,00,000"
    subtitle="Mean: ₹12,500 per unit"
    icon={<DollarSign className="w-4 h-4" />}
    badge={{ text: '+14.2% YoY', variant: 'accent' }}
    tooltip="Grounded in clean transaction records."
  />
);
