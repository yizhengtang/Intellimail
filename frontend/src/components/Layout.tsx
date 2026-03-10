//Layout.tsx
//App shell — renders the sidebar and the active page via Outlet.

import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

//<Outlet /> is filled by React Router with the matched child route's element.
//Sidebar contains the provider switcher and navigation links.
export default function Layout() {
  return (
    <div style={{ display: 'flex' }}>
      <div style={{ width: 220, borderRight: '1px solid #e0e0e0' }}>
        <Sidebar />
      </div>
      <div style={{ flex: 1 }}>
        <Outlet />
      </div>
    </div>
  );
}
