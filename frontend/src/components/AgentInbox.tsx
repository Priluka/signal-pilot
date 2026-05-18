/** Left column of the Agent Feed — sorted inbox of agent-processed tickets. */
import { useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import type {
  AgentSessionSummary,
  AgentStatus,
  TicketSummary,
} from '../lib/types';

import { AgentStatusPill, statusPriority } from './AgentStatusPill';


export interface InboxRow {
  ticket: TicketSummary;
  session: AgentSessionSummary | undefined;
}


interface Props {
  rows: InboxRow[];
  loading: boolean;
  error: string | null;
}


export function AgentInbox({ rows, loading, error }: Props) {
  const { ticketKey } = useParams();
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    if (!search.trim()) return rows;
    const needle = search.toLowerCase();
    return rows.filter(
      ({ ticket: t }) =>
        t.key.toLowerCase().includes(needle) ||
        t.summary.toLowerCase().includes(needle) ||
        t.labels.some((l) => l.toLowerCase().includes(needle)),
    );
  }, [rows, search]);

  return (
    <div className="flex flex-col w-[340px] shrink-0 border-r border-panel-border bg-panel-surface">
      <div className="px-4 py-3 border-b border-panel-border">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search inbox…"
          className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15"
        />
        <div className="mt-2 text-[11px] text-slate-500 font-mono tabular-nums">
          {filtered.length} ticket{filtered.length === 1 ? '' : 's'}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {loading && (
          <div className="px-4 py-6 text-sm text-slate-400">Loading inbox…</div>
        )}
        {error && (
          <div className="px-4 py-6 text-sm text-red-600">{error}</div>
        )}
        {!loading && !error && filtered.length === 0 && (
          <div className="px-4 py-6 text-sm text-slate-400">
            No tickets in this view.
          </div>
        )}
        <ul>
          {filtered.map(({ ticket: t, session: s }) => {
            const isActive = ticketKey === t.key;
            const status: AgentStatus = s?.derived_status ?? 'pending';
            const confidence = s?.classification_confidence ?? null;
            return (
              <li key={t.key}>
                <Link
                  to={`/agent/${t.key}`}
                  className={`block px-4 py-3 border-b border-panel-divider transition-colors ${
                    isActive
                      ? 'bg-blue-50/60 border-l-2 border-l-blue-500'
                      : 'hover:bg-slate-50 border-l-2 border-l-transparent'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[11px] font-mono text-slate-500">{t.key}</span>
                    <AgentStatusPill status={status} />
                  </div>
                  <div className="mt-1 text-sm font-medium text-slate-900 leading-snug line-clamp-2">
                    {t.summary}
                  </div>
                  <div className="mt-1.5 flex items-center gap-2 text-[10px] text-slate-500 font-mono">
                    {confidence != null && (
                      <span>conf {confidence.toFixed(2)}</span>
                    )}
                    {s?.drafted_at && (
                      <span>· {formatShortTime(s.drafted_at)}</span>
                    )}
                    {s?.feedback_at && (
                      <span>· decided {formatShortTime(s.feedback_at)}</span>
                    )}
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}


export function sortInbox(rows: InboxRow[]): InboxRow[] {
  return [...rows].sort((a, b) => {
    const pa = statusPriority(a.session?.derived_status);
    const pb = statusPriority(b.session?.derived_status);
    if (pa !== pb) return pa - pb;
    const ta = a.session?.updated_at ?? '';
    const tb = b.session?.updated_at ?? '';
    return tb.localeCompare(ta);
  });
}


function formatShortTime(iso: string): string {
  try {
    const d = new Date(iso);
    const now = new Date();
    const sameDay =
      d.getFullYear() === now.getFullYear() &&
      d.getMonth() === now.getMonth() &&
      d.getDate() === now.getDate();
    if (sameDay) {
      return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
    }
    return d.toLocaleDateString(undefined, { month: 'short', day: '2-digit' });
  } catch {
    return iso;
  }
}
