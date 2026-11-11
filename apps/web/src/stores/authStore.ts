import { create } from 'zustand';

interface AuthState {
  role: 'analyst' | 'admin';
  token: string | null;
  setRole: (role: 'analyst' | 'admin') => void;
  setToken: (token: string | null) => void;
  fetchDemoToken: (role: 'analyst' | 'admin') => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  role: 'analyst',
  token: null,
  setRole: (role) => set({ role }),
  setToken: (token) => set({ token }),
  fetchDemoToken: async (role: 'analyst' | 'admin') => {
    try {
      const payload: Record<string, string> = { role };
      if (role === 'admin') {
        payload.admin_key = 'dev-demo-admin-key-parcl-2026';
      }
      const res = await fetch('/api/v1/auth/demo-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Demo-Admin-Key': 'dev-demo-admin-key-parcl-2026',
        },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const data = await res.json();
        set({ role, token: data.access_token });
      } else {
        set({ role, token: `mock-demo-${role}-jwt-token` });
      }
    } catch {
      set({ role, token: `mock-demo-${role}-jwt-token` });
    }
  },
}));
