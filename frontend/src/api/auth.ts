import { api, setTokens } from './client';
import type { AuthTokens, LoginRequest, RegisterRequest } from '../types';

export async function login(data: LoginRequest): Promise<AuthTokens> {
  const form = new URLSearchParams({ username: data.email, password: data.password });
  const res = await fetch('/api/v1/auth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  const tokens: AuthTokens = await res.json();
  setTokens(tokens.access_token, tokens.refresh_token);
  return tokens;
}

export async function register(data: RegisterRequest): Promise<AuthTokens> {
  const tokens = await api.post<AuthTokens>('/auth/register', data);
  setTokens(tokens.access_token, tokens.refresh_token);
  return tokens;
}
