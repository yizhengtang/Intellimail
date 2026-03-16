//router/index.tsx
//Defines application routes using React Router v7's createBrowserRouter.

import { createBrowserRouter } from 'react-router-dom';
import Layout from '../components/Layout';
import InboxPage from '../pages/InboxPage';
import EmailPage from '../pages/EmailPage';
import ComposePage from '../pages/ComposePage';
import DraftsPage from '../pages/DraftsPage';

//there are four routes: 1. / (inbox) 2. /email/:provider/:id 3. /compose 4. /drafts
//the layout component wraps all routes to provide a consistent ui structure.
const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <InboxPage /> },
      { path: '/email/:provider/:id', element: <EmailPage /> },
      { path: '/compose', element: <ComposePage /> },
      { path: '/drafts', element: <DraftsPage /> },
    ],
  },
]);

export default router;
