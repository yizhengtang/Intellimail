import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import type { Provider } from '../types/email';

//ProviderContext
//This context holds the active email provider (gmail, outlook, or unified).
//Any component can read or change the provider using the useProvider() hook.

interface ProviderContextType {
  provider: Provider;
  setProvider: (provider: Provider) => void;
}

const ProviderContext = createContext<ProviderContextType | undefined>(undefined);

//ProviderContextProvider wraps the app and holds the provider state.
//useState keeps track of the current provider, defaulting to 'gmail'.
//Every child component inside this wrapper can access the provider value.
export function ProviderContextProvider({ children }: { children: ReactNode }) {
  const [provider, setProvider] = useState<Provider>('gmail');

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
