//Layout.tsx
//App shell — sidebar, slide-out panel, and the active page via Outlet.
//Account button lives in Sidebar. Search and compose live in InboxPage.

import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import SlidePanel from './SlidePanel';

type OpenPanel = 'gmail' | 'outlook' | 'teams' | null;

//<Outlet /> is filled by React Router with the matched child route's element.
//openPanel lives here so both Sidebar (sets it) and SlidePanel (reads it) can share it as siblings.
export default function Layout() {
  const [openPanel, setOpenPanel] = useState<OpenPanel>(null);

  function handlePanelToggle(panel: OpenPanel) {
    setOpenPanel(prev => (prev === panel ? null : panel));
  }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <div style={{ width: 64, flexShrink: 0 }}>
        <Sidebar onPanelToggle={handlePanelToggle} openPanel={openPanel} />
      </div>

      <SlidePanel open={openPanel} />

      <div style={{ flex: 1, minWidth: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <Outlet />
      </div>
    </div>
  );
}
