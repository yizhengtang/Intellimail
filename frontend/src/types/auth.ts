//auth.ts
//TypeScript interfaces for /auth/* API responses.

export interface ProviderAuthInfo {
  connected: boolean;
  email: string | null;
}

export interface AuthStatus {
  gmail:   ProviderAuthInfo;
  outlook: ProviderAuthInfo;
  teams:   ProviderAuthInfo;
}
