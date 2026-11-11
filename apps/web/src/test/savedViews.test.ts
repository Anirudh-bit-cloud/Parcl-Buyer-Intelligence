import { describe, it, expect, beforeEach } from 'vitest';
import { useSavedViewsStore } from '../stores/savedViewsStore';

describe('Saved Views Store Suite', () => {

  it('initializes with default enterprise views', () => {
    const { savedViews } = useSavedViewsStore.getState();
    expect(savedViews.length).toBeGreaterThanOrEqual(3);
    expect(savedViews.some((v) => v.name.includes('USA'))).toBe(true);
  });

  it('saves and activates a custom filter view', () => {
    const store = useSavedViewsStore.getState();
    const customFilters = {
      country: 'UK',
      region: 'London',
      acquisition_purpose: 'INVESTMENT' as const,
      client_type: 'COMPANY' as const,
    };

    const newView = store.saveCurrentView('London Institutional Portfolios', customFilters);
    expect(newView.id).toBeDefined();
    expect(newView.name).toBe('London Institutional Portfolios');

    const updated = useSavedViewsStore.getState();
    expect(updated.savedViews.some((v) => v.id === newView.id)).toBe(true);
    expect(updated.activeViewId).toBe(newView.id);
  });

  it('loads filters by view ID and handles deletion', () => {
    const store = useSavedViewsStore.getState();
    const loaded = store.loadView('us-investors');
    expect(loaded).toBeDefined();
    expect(loaded?.country).toBe('USA');
    expect(loaded?.acquisition_purpose).toBe('INVESTMENT');

    store.deleteView('us-investors');
    const postDelete = useSavedViewsStore.getState();
    expect(postDelete.savedViews.some((v) => v.id === 'us-investors')).toBe(false);
  });
});
