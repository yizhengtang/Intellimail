//router/index.tsx
//Defines application routes using React Router v7's createBrowserRouter.

import { createBrowserRouter } from 'react-router-dom';
import Layout from '../components/Layout';
import InboxPage from '../pages/InboxPage';

//there are three routes: 1. /inbox 2. /email/:provider/:id 3. /compose
//the layout component wraps all routes to provide a consistent ui structure.
const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <InboxPage /> },
      { path: '/email/:provider/:id', element: <div>Email detail</div> },
      { path: '/compose', element: <div>Compose</div> },
    ],
  },
]);

export default router;
