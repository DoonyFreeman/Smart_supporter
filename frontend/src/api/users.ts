import { api } from './client';
import type { User } from '../types';

export async function getMe(): Promise<User> {
  return api.get<User>('/users/me');
}
