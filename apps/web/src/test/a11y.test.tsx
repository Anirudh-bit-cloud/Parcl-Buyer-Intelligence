import { describe, it, expect } from 'vitest';
import { render, act } from '@testing-library/react';
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import axe from 'axe-core';
import { TopBar } from '../components/layout/TopBar';
import { Sidebar } from '../components/layout/Sidebar';
import { ExecutiveOverview } from '../pages/ExecutiveOverview';
import { SegmentExplorer } from '../pages/SegmentExplorer';
import { DataSource } from '../pages/DataSource';
import { ChartCard } from '../components/ui/ChartCard';

describe('Automated Accessibility (axe-core) Suite', () => {
  it('checks TopBar accessibility in light mode', async () => {
    let container: HTMLElement = document.createElement('div');
    await act(async () => {
      const res = render(
        <BrowserRouter>
          <TopBar onOpenCommandPalette={() => {}} />
        </BrowserRouter>
      );
      container = res.container;
    });
    const results = await axe.run(container, {
      rules: {
        // Color contrast in jsdom cannot compute true computed pixel CSS colors
        'color-contrast': { enabled: false },
      },
    });
    const criticalViolations = results.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious'
    );
    expect(criticalViolations).toHaveLength(0);
  });

  it('checks TopBar accessibility in dark mode', async () => {
    let container: HTMLElement = document.createElement('div');
    await act(async () => {
      const res = render(
        <BrowserRouter>
          <div className="dark bg-slate-900 text-slate-100">
            <TopBar onOpenCommandPalette={() => {}} />
          </div>
        </BrowserRouter>
      );
      container = res.container;
    });
    const results = await axe.run(container, {
      rules: {
        'color-contrast': { enabled: false },
      },
    });
    const criticalViolations = results.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious'
    );
    expect(criticalViolations).toHaveLength(0);
  });

  it('checks Sidebar accessibility with proper nav semantics', async () => {
    const { container } = render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );
    const results = await axe.run(container, {
      rules: {
        'color-contrast': { enabled: false },
      },
    });
    const criticalViolations = results.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious'
    );
    expect(criticalViolations).toHaveLength(0);
  });

  it('checks ChartCard component accessibility with title and footer', async () => {
    const { container } = render(
      <ChartCard
        title="Test Chart Section"
        subtitle="Subtitle info"
        footer={<span>Summary statistics</span>}
      >
        <div role="img" aria-label="Sample Chart View">
          Chart Content
        </div>
      </ChartCard>
    );
    const results = await axe.run(container, {
      rules: {
        'color-contrast': { enabled: false },
      },
    });
    const criticalViolations = results.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious'
    );
    expect(criticalViolations).toHaveLength(0);
  });

  it('checks ExecutiveOverview accessibility', async () => {
    let container: HTMLElement = document.createElement('div');
    await act(async () => {
      const res = render(
        <BrowserRouter>
          <ExecutiveOverview />
        </BrowserRouter>
      );
      container = res.container;
    });
    const results = await axe.run(container, {
      rules: {
        'color-contrast': { enabled: false },
      },
    });
    const criticalViolations = results.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious'
    );
    expect(criticalViolations).toHaveLength(0);
  });

  it('checks DataSource accessibility', async () => {
    const { container } = render(
      <BrowserRouter>
        <DataSource />
      </BrowserRouter>
    );
    const results = await axe.run(container, {
      rules: {
        'color-contrast': { enabled: false },
      },
    });
    const criticalViolations = results.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious'
    );
    expect(criticalViolations).toHaveLength(0);
  });
});
