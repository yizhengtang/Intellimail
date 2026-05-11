//AuthContext.tsx
//Stores the auth status for all providers globally so it is fetched once on app load.
//Components read from this context instead of calling the API on every render.

import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { AuthStatus } from '../types/auth';
import { getAuthStatus } from '../services/authService';

interface AuthContextType {
  authStatus: AuthStatus | null;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

//AuthContextProvider fetches auth status once on mount and exposes a refresh() function.
//refresh() is called by AccountPanel after a sign in or sign out to update the stored status.
export function AuthContextProvider({ children }: { children: ReactNode }) {
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);

  async function refresh() {
    try {
      const updated = await getAuthStatus();
      setAuthStatus(updated);
    } catch {
      //Leave authStatus unchanged — panel will show whatever state it already has.
    }
  }

  //Fetch once on app load.
  useEffect(() => {
    refresh();
  }, []);

  return (
    <AuthContext.Provider value={{ authStatus, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

//useAuth is a custom hook that reads the current auth context.
//Throws if used outside of AuthContextProvider — catches wiring bugs early.
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthContextProvider');
  }
  return context;
}
