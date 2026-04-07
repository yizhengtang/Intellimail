import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import type { EmailViewMode } from '../types/email';

//ProviderContext controls the active view in the email section (gmail, outlook, or unified).
//EmailViewMode is email-specific — 'unified' shows Gmail + Outlook together.
//This is separate from the global Provider type (types/provider.ts) which covers all platforms.

interface ProviderContextType {
  provider: EmailViewMode;
  setProvider: (provider: EmailViewMode) => void;
}

const ProviderContext = createContext<ProviderContextType | undefined>(undefined);

//ProviderContextProvider wraps the email section and holds the active view mode state.
//Defaults to 'gmail'.
export function ProviderContextProvider({ children }: { children: ReactNode }) {
  const [provider, setProvider] = useState<EmailViewMode>('gmail');

  return (
    <ProviderContext.Provider value={{ provider, setProvider }}>
      {children}
    </ProviderContext.Provider>
  );
}

//useProvider is a custom hook that reads the current provider context.
//Components call useProvider() instead of useContext(ProviderContext) directly.
//Throws an error if used outside of ProviderContextProvider — this catches bugs early.
export function useProvider() {
  const context = useContext(ProviderContext);
  if (!context) {
    throw new Error('useProvider must be used within a ProviderContextProvider');
  }
  return context;
}
