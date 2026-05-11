//router/index.tsx
//Defines application routes using React Router v7's createBrowserRouter.

import { createBrowserRouter } from 'react-router-dom';
import Layout from '../components/Layout';
import InboxPage from '../pages/InboxPage';
import EmailPage from '../pages/EmailPage';
import ComposePage from '../pages/ComposePage';
import DraftsPage from '../pages/DraftsPage';
import ChatPage from '../pages/ChatPage';
import SyncPage from '../pages/SyncPage';
import TeamsPage from '../pages/TeamsPage';
import TeamsChatPage from '../pages/TeamsChatPage';
import CalendarPage from '../pages/CalendarPage';

//there are eight routes: 1. / (inbox) 2. /email/:provider/:id 3. /compose 4. /drafts
//5. /chat 6. /sync 7. /teams (chat list) 8. /teams/:chatId (single chat)
//the layout component wraps all routes to provide a consistent ui structure.
const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <InboxPage /> },
      { path: '/email/:provider/:id', element: <EmailPage /> },
      { path: '/compose', element: <ComposePage /> },
      { path: '/drafts', element: <DraftsPage /> },
      { path: '/chat', element: <ChatPage /> },
      { path: '/sync', element: <SyncPage /> },
      { path: '/teams', element: <TeamsPage /> },
      { path: '/teams/:chatId', element: <TeamsChatPage /> },
      { path: '/calendar', element: <CalendarPage /> },
    ],
  },
]);

export default router;
