/** Dark fixed sidebar — flat navigation.
 *
 * Surfaces only the four real destinations (Playbooks / Chat / Agent Feed /
 * Suggestions) plus a disabled placeholder for Agents. Counters next to
 * Playbooks and Suggestions are fetched live so the sidebar always reflects
 * the corpus and the review queue.
 *
 * Other components (PlaybookViewer, SuggestionsPage) emit a custom
 * 'suggestions-changed' window event whenever they submit, accept, or
 * reject a row so the pending badge can refresh without polling.
 */
import { useCallback, useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';

import { getCategories, getSuggestionStats } from '../lib/api';


interface CountedNavRowProps {
  to: string;
  label: string;
  count?: number;
  /** Render the count as a colored pill instead of a muted number. */
  badge?: boolean;
}


function NavRow({ to, label, count, badge }: CountedNavRowProps) {
  return (
    <NavLink
      to={to}
      end={to === '/'}
      className={({ isActive }) =>
        [
          'flex items-center justify-between px-3 py-2 mx-2 rounded-md text-sm transition-colors',
          isActive
            ? 'bg-sidebar-surface text-sidebar-textActive'
            : 'text-sidebar-text hover:bg-sidebar-surface/60 hover:text-sidebar-textActive',
        ].join(' ')
      }
    >
      <span>{label}</span>
      {typeof count === 'number' && count > 0 && (
        badge ? (
          <span className="inline-flex items-center px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-blue-500 text-white">
            {count}
          </span>
        ) : (
          <span className="text-xs text-sidebar-muted font-mono tabular-nums">{count}</span>
        )
      )}
    </NavLink>
  );
}


function DisabledRow({ label, hint }: { label: string; hint: string }) {
  return (
    <div
      title={hint}
      className="flex items-center justify-between px-3 py-2 mx-2 rounded-md text-sm text-sidebar-heading cursor-not-allowed select-none"
    >
      <span>{label}</span>
      <span className="text-[10px] italic">coming soon</span>
    </div>
  );
}


export function Sidebar() {
  const [playbooksCount, setPlaybooksCount] = useState<number | undefined>(undefined);
  const [pendingCount, setPendingCount] = useState<number | undefined>(undefined);

  const refreshPlaybooks = useCallback(() => {
    getCategories()
      .then((data) => setPlaybooksCount(data.total))
      .catch(() => setPlaybooksCount(undefined));
  }, []);

  const refreshSuggestions = useCallback(() => {
    getSuggestionStats()
      .then((stats) => setPendingCount(stats.pending))
      .catch(() => setPendingCount(undefined));
  }, []);

  useEffect(() => {
    refreshPlaybooks();
    refreshSuggestions();
    const handler = () => refreshSuggestions();
    window.addEventListener('suggestions-changed', handler);
    return () => window.removeEventListener('suggestions-changed', handler);
  }, [refreshPlaybooks, refreshSuggestions]);

  return (
    <aside className="flex flex-col w-64 shrink-0 bg-sidebar-bg border-r border-sidebar-border text-sidebar-text">
      <div className="px-5 pt-6 pb-4">
        <div className="text-base font-semibold text-sidebar-textActive tracking-tight">
          Signal Pilot
        </div>
        <div className="text-[11px] text-sidebar-muted mt-0.5">
          Support triage prototype
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto scrollbar-thin py-2 space-y-0.5">
        <NavRow to="/knowledge" label="Playbooks" count={playbooksCount} />
        <NavRow to="/chat" label="Chat" />
        <NavRow to="/agent" label="Agent Feed" />
        <NavRow to="/suggestions" label="Suggestions" count={pendingCount} badge />
      </nav>

      <div className="border-t border-sidebar-border py-2">
        <DisabledRow label="Agents" hint="Coming soon — deployed agents, shadow mode, performance" />
      </div>
    </aside>
  );
}
