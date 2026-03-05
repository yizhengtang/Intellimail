//Layout.tsx
//App shell — renders a sidebar placeholder and the active page via Outlet.

import { Outlet } from 'react-router-dom';

//<Outlet /> is filled by React Router with the matched child route's element.
//The sidebar will be built out properly in commit 11.
export default function Layout() {
  return (
    <div style={{ display: 'flex' }}>
      <div style={{ width: 220 }}>
        <p>Sidebar</p>
      </div>
      <div style={{ flex: 1 }}>
        <Outlet />
      </div>
    </div>
  );
}
