import { api, setTokens } from './client';
import type { AuthTokens, LoginRequest, RegisterRequest } from '../types';

export async function login(data: LoginRequest): Promise<AuthTokens> {
  const tokens = await api.post<AuthTokens>('/auth/token', data);
  setTokens(tokens.access_token, tokens.refresh_token);
  return tokens;
}

export async function register(data: RegisterRequest): Promise<AuthTokens> {
  const tokens = await api.post<AuthTokens>('/auth/register', data);
  setTokens(tokens.access_token, tokens.refresh_token);
  return tokens;
}
