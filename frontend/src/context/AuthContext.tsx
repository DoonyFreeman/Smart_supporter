import { createContext, useContext, useState, type ReactNode } from 'react';
import { clearTokens, getTokens } from '../api/client';

interface AuthState {
  isAuthenticated: boolean;
  login: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(() => !!getTokens().access);

  const value: AuthState = {
    isAuthenticated,
    login: () => setIsAuthenticated(true),
    logout: () => {
      clearTokens();
      setIsAuthenticated(false);
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
