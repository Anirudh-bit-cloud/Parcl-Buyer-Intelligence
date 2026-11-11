import { describe, it, expect, beforeEach } from 'vitest';
import { useFilterStore } from '../stores/filterStore';
import { useAuthStore } from '../stores/authStore';
import { useThemeStore } from '../stores/themeStore';
import { useDatasetStore } from '../stores/datasetStore';

describe('Global Zustand Stores', () => {
  beforeEach(() => {
    useFilterStore.getState().resetFilters();
  });

  it('updates country and resets region cascade in FilterStore', () => {
    const store = useFilterStore.getState();
    store.setCountry('USA');
    expect(useFilterStore.getState().country).toBe('USA');
    expect(useFilterStore.getState().region).toBe('');

    store.setRegion('California');
    expect(useFilterStore.getState().region).toBe('California');

    // Changing country must reset region
    store.setCountry('UK');
    expect(useFilterStore.getState().country).toBe('UK');
    expect(useFilterStore.getState().region).toBe('');
  });

  it('handles acquisition purpose and client type filters', () => {
    const store = useFilterStore.getState();
    store.setAcquisitionPurpose('HOME');
    expect(useFilterStore.getState().acquisition_purpose).toBe('HOME');

    store.setClientType('COMPANY');
    expect(useFilterStore.getState().client_type).toBe('COMPANY');

    store.resetFilters();
    expect(useFilterStore.getState().country).toBe('');
    expect(useFilterStore.getState().acquisition_purpose).toBe('');
    expect(useFilterStore.getState().client_type).toBe('');
  });

  it('manages role and token in AuthStore', () => {
    const auth = useAuthStore.getState();
    expect(auth.role).toBe('analyst');

    auth.setRole('admin');
    expect(useAuthStore.getState().role).toBe('admin');

    auth.setRole('analyst');
    expect(useAuthStore.getState().role).toBe('analyst');
  });

  it('manages light and dark theme toggling in ThemeStore', () => {
    const themeStore = useThemeStore.getState();
    themeStore.setTheme('light');
    expect(useThemeStore.getState().theme).toBe('light');

    themeStore.toggleTheme();
    expect(useThemeStore.getState().theme).toBe('dark');

    themeStore.toggleTheme();
    expect(useThemeStore.getState().theme).toBe('light');
  });

  it('manages active dataset switching and offline state in DatasetStore', () => {
    const datasetStore = useDatasetStore.getState();
    datasetStore.setActiveDataset('full');
    expect(useDatasetStore.getState().activeDataset).toBe('full');

    datasetStore.setActiveDataset('sample');
    expect(useDatasetStore.getState().activeDataset).toBe('sample');

    datasetStore.setIsOffline(true);
    expect(useDatasetStore.getState().isOffline).toBe(true);

    datasetStore.setIsOffline(false);
    expect(useDatasetStore.getState().isOffline).toBe(false);
  });
});
