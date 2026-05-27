import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react';
import { clearTokens, getTokens } from '../api/client';
import { getMe } from '../api/users';
import type { User } from '../types';

interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  login: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => !!getTokens().access,
  );
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      setUser(null);
      return;
    }
    getMe()
      .then(setUser)
      .catch(() => setUser(null));
  }, [isAuthenticated]);

  const value: AuthState = {
    isAuthenticated,
    user,
    login: async () => setIsAuthenticated(true),
    logout: () => {
      clearTokens();
      setIsAuthenticated(false);
      setUser(null);
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
