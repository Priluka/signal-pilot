/** Linear-style floating panel shell.
 *
 * The outer shell shares one neutral grey with the sidebar; the content
 * lives in a white rounded-xl panel inset by 8px so it appears to "float"
 * over the shell. No shadows — Linear gets the depth purely from the
 * strong border around the panel.
 *
 * Each page owns its own header row (title + actions) inside the floating
 * panel — there's no shared breadcrumb / topbar above it.
 */
import { Outlet } from 'react-router-dom';

import { Sidebar } from './Sidebar';


export function Layout() {
  return (
    <div className="h-screen flex bg-app font-sans text-sm text-ink-body antialiased">
      <Sidebar />
      <div className="flex-1 pt-[13px] pr-2 pb-[13px] pl-0 min-w-0">
        <div className="h-full bg-card border border-line-strong rounded-xl overflow-hidden">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
