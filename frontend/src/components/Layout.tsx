//Layout.tsx
//App shell — renders the sidebar, slide-out panel, search header, account button, and the active page via Outlet.

import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import SlidePanel from './SlidePanel';
import SearchBar from './SearchBar';
import AccountPanel from './AccountPanel';

type OpenPanel = 'gmail' | 'outlook' | 'teams' | null;

//<Outlet /> is filled by React Router with the matched child route's element.
//openPanel lives here so both Sidebar (sets it) and SlidePanel (reads it) can share it as siblings.
//Clicking the same provider icon a second time toggles the panel closed.
export default function Layout() {
  const [accountOpen, setAccountOpen] = useState(false);
  const [openPanel, setOpenPanel] = useState<OpenPanel>(null);

  function handlePanelToggle(panel: OpenPanel) {
    setOpenPanel(prev => (prev === panel ? null : panel));
  }

  return (
    <div style={{ display: 'flex' }}>
      <div style={{ width: 64, flexShrink: 0 }}>
        <Sidebar onPanelToggle={handlePanelToggle} openPanel={openPanel} />
      </div>

      <SlidePanel open={openPanel} />

      <div style={{ flex: 1 }}>
        <div style={{
          padding: '12px 24px',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'relative',
        }}>
          <SearchBar />
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setAccountOpen(o => !o)}
              style={{
                padding: '6px 14px',
                cursor: 'pointer',
                border: '1px solid #ccc',
                borderRadius: 4,
                backgroundColor: 'transparent',
                fontSize: 13,
              }}
            >
              Account
            </button>
            {accountOpen && <AccountPanel onClose={() => setAccountOpen(false)} />}
          </div>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
