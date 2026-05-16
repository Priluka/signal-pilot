/** Two-panel app shell: fixed dark sidebar on the left, full-height content on the right.
 * Each page handles its own internal padding/layout so the knowledge master/detail can
 * occupy the full width while chat/agent can constrain themselves. */
import { Outlet } from 'react-router-dom';

import { Sidebar } from './Sidebar';


export function Layout() {
  return (
    <div className="h-full flex">
      <Sidebar />
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
