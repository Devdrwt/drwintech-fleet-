import { create } from "zustand";

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role_code?: string;
  client?: number | null;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (u: User | null) => void;
  setTokens: (access: string, refresh: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  setTokens: (access, refresh) => {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
  },
  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({ user: null, isAuthenticated: false });
  },
}));
