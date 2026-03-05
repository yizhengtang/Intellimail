//App.tsx
//Root component — wraps the app in ProviderContext and RouterProvider.

import { RouterProvider } from 'react-router-dom';
import { ProviderContextProvider } from './context/ProviderContext';
import router from './router';

//ProviderContextProvider makes the active email provider (gmail/outlook/unified)
//available to every component in the tree via useProvider().
//RouterProvider takes the router defined in router/index.tsx and renders
//the matching route on every navigation event.
export default function App() {
  return (
    <ProviderContextProvider>
      <RouterProvider router={router} />
    </ProviderContextProvider>
  );
}
