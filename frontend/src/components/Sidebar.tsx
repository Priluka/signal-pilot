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

import { getAgentMetrics, getCategories, getSuggestionStats } from '../lib/api';
import { useChatStore } from '../lib/chatStore';


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


/** Special Chat row that shows a pulsing dot when a stream is in flight,
 * even from another route — so the operator knows their question is still
 * cooking even after navigating away. */
function ChatNavRow() {
  const { status } = useChatStore();
  const streaming = status === 'streaming';
  return (
    <NavLink
      to="/chat"
      className={({ isActive }) =>
        [
          'flex items-center justify-between px-3 py-2 mx-2 rounded-md text-sm transition-colors',
          isActive
            ? 'bg-sidebar-surface text-sidebar-textActive'
            : 'text-sidebar-text hover:bg-sidebar-surface/60 hover:text-sidebar-textActive',
        ].join(' ')
      }
    >
      <span className="flex items-center gap-2">
        Chat
        {streaming && (
          <span
            title="Streaming…"
            className="inline-block w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"
          />
        )}
      </span>
      {streaming && (
        <span className="text-[10px] uppercase tracking-wider text-blue-400">live</span>
      )}
    </NavLink>
  );
}


export function Sidebar() {
  const [playbooksCount, setPlaybooksCount] = useState<number | undefined>(undefined);
  const [suggestionsPending, setSuggestionsPending] = useState<number | undefined>(undefined);
  const [inboxCount, setInboxCount] = useState<number | undefined>(undefined);

  const refreshPlaybooks = useCallback(() => {
    getCategories()
      .then((data) => setPlaybooksCount(data.total))
      .catch(() => setPlaybooksCount(undefined));
  }, []);

  const refreshSuggestions = useCallback(() => {
    getSuggestionStats()
      .then((stats) => setSuggestionsPending(stats.pending))
      .catch(() => setSuggestionsPending(undefined));
  }, []);

  const refreshInbox = useCallback(() => {
    getAgentMetrics()
      .then((m) => setInboxCount(m.needs_review + m.escalated))
      .catch(() => setInboxCount(undefined));
  }, []);

  useEffect(() => {
    refreshPlaybooks();
    refreshSuggestions();
    refreshInbox();
    const suggHandler = () => refreshSuggestions();
    const agentHandler = () => refreshInbox();
    window.addEventListener('suggestions-changed', suggHandler);
    window.addEventListener('agent-sessions-changed', agentHandler);
    return () => {
      window.removeEventListener('suggestions-changed', suggHandler);
      window.removeEventListener('agent-sessions-changed', agentHandler);
    };
  }, [refreshPlaybooks, refreshSuggestions, refreshInbox]);

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
        <ChatNavRow />
        <NavRow to="/inbox" label="Inbox" count={inboxCount} badge />
        <NavRow to="/activity-log" label="Activity Log" />
        <NavRow to="/suggestions" label="Suggestions" count={suggestionsPending} badge />
        <NavRow to="/agents" label="Agents" />
      </nav>
    </aside>
  );
}
