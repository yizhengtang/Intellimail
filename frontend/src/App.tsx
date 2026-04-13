//App.tsx
//Root component — wraps the app in ProviderContext, AuthContext, and RouterProvider.

import { RouterProvider } from 'react-router-dom';
import { ProviderContextProvider } from './context/ProviderContext';
import { AuthContextProvider } from './context/AuthContext';
import router from './router';

//AuthContextProvider fetches auth status once on app load and shares it via useAuth().
//ProviderContextProvider makes the active email provider (gmail/outlook/unified)
//available to every component in the tree via useProvider().
//RouterProvider takes the router defined in router/index.tsx and renders
//the matching route on every navigation event.
export default function App() {
  return (
    <AuthContextProvider>
      <ProviderContextProvider>
        <RouterProvider router={router} />
      </ProviderContextProvider>
    </AuthContextProvider>
  );
}
