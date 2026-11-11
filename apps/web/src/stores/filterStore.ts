import { create } from 'zustand';
import { GlobalFilters } from '../types';

interface FilterState extends GlobalFilters {
  availableRegions: string[];
  setCountry: (country?: string) => void;
  setRegion: (region?: string) => void;
  setAcquisitionPurpose: (purpose?: 'HOME' | 'INVESTMENT' | '') => void;
  setClientType: (type?: 'INDIVIDUAL' | 'COMPANY' | '') => void;
  setAvailableRegions: (regions: string[]) => void;
  resetFilters: () => void;
  setAllFilters: (filters: Partial<GlobalFilters>) => void;
  toSearchParams: () => URLSearchParams;
  loadFromSearchParams: (params: URLSearchParams) => void;
}

export const useFilterStore = create<FilterState>((set, get) => ({
  country: '',
  region: '',
  acquisition_purpose: '',
  client_type: '',
  availableRegions: [],

  setCountry: (country) => set({ country: country || '', region: '' }),
  setRegion: (region) => set({ region: region || '' }),
  setAcquisitionPurpose: (acquisition_purpose) => set({ acquisition_purpose: acquisition_purpose || '' }),
  setClientType: (client_type) => set({ client_type: client_type || '' }),
  setAvailableRegions: (availableRegions) => set({ availableRegions }),
  resetFilters: () => set({ country: '', region: '', acquisition_purpose: '', client_type: '' }),
  setAllFilters: (filters) => set((state) => ({ ...state, ...filters })),

  toSearchParams: () => {
    const s = get();
    const params = new URLSearchParams();
    if (s.country) params.set('country', s.country);
    if (s.region) params.set('region', s.region);
    if (s.acquisition_purpose) params.set('purpose', s.acquisition_purpose);
    if (s.client_type) params.set('type', s.client_type);
    return params;
  },

  loadFromSearchParams: (params: URLSearchParams) => {
    const country = params.get('country') || '';
    const region = params.get('region') || '';
    const purpose = (params.get('purpose') as 'HOME' | 'INVESTMENT' | '') || '';
    const type = (params.get('type') as 'INDIVIDUAL' | 'COMPANY' | '') || '';
    set({
      country,
      region,
      acquisition_purpose: purpose,
      client_type: type,
    });
  },
}));
