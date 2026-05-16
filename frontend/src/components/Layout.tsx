/** Two-panel app layout: fixed dark sidebar on the left, scrolling content on the right. */
import { Outlet } from 'react-router-dom';

import { Sidebar } from './Sidebar';


export function Layout() {
  return (
    <div className="h-full flex">
      <Sidebar />
      <main className="flex-1 overflow-y-auto scrollbar-thin">
        <div className="max-w-6xl mx-auto px-8 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
