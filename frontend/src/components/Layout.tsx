//Layout.tsx
//App shell — renders the sidebar, search header, account button, and the active page via Outlet.

import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import SearchBar from './SearchBar';
import AccountPanel from './AccountPanel';

//<Outlet /> is filled by React Router with the matched child route's element.
//Sidebar contains the provider switcher and navigation links.
//The header contains the SearchBar on the left and the Account button on the right.
//Clicking Account toggles the AccountPanel dropdown.
export default function Layout() {
  const [accountOpen, setAccountOpen] = useState(false);

  return (
    <div style={{ display: 'flex' }}>
      <div style={{ width: 220, borderRight: '1px solid #e0e0e0' }}>
        <Sidebar />
      </div>
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
