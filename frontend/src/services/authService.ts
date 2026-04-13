//authService.ts
//All auth API call functions — maps to /auth/* endpoints in backend/app/routers/auth.py.

import api from './api';
import type { AuthStatus } from '../types/auth';

//GET /auth/status
//Returns connection status and logged-in email for all three providers.
export const getAuthStatus = () =>
  api.get<never, AuthStatus>('/auth/status');

//POST /auth/signout/:provider
//Deletes the stored token for the given provider.
export const signOut = (provider: string) =>
  api.post(`/auth/signout/${provider}`);

//POST /auth/connect/:provider
//Triggers the OAuth browser flow for the given provider.
export const connect = (provider: string) =>
  api.post(`/auth/connect/${provider}`);
