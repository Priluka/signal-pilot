/** Chronological list of agent events for the Agent Feed third view.
 *
 * Each row is one step (classified / retrieved / drafted) or one operator
 * decision (approved / edited / rejected / skipped). Newest first. Search
 * narrows by ticket id; type chips filter by event_type. Auto-refreshes on
 * the same 'agent-sessions-changed' window event the rest of the page uses.
 */
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import { listAgentActivity } from '../lib/api';
import type { AgentActivityEvent, AgentEventType } from '../lib/types';


const TYPE_META: Record<AgentEventType, { label: string; tone: string }> = {
  classified: { label: 'classified', tone: 'bg-blue-50 text-blue-700 border-blue-200' },
  retrieved: { label: 'retrieved', tone: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  drafted: { label: 'drafted', tone: 'bg-amber-50 text-amber-700 border-amber-200' },
  approved: { label: 'approved', tone: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  edited: { label: 'edited', tone: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  rejected: { label: 'rejected', tone: 'bg-red-50 text-red-700 border-red-200' },
  skipped: { label: 'skipped', tone: 'bg-slate-50 text-slate-600 border-slate-200' },
};

const TYPE_FILTERS: Array<{ key: AgentEventType | 'all'; label: string }> = [
  { key: 'all', label: 'All' },
  { key: 'classified', label: 'Classified' },
  { key: 'retrieved', label: 'Retrieved' },
  { key: 'drafted', label: 'Drafted' },
  { key: 'approved', label: 'Approved' },
  { key: 'rejected', label: 'Rejected' },
  { key: 'skipped', label: 'Skipped' },
];


export function AgentActivityLog() {
  const [events, setEvents] = useState<AgentActivityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<AgentEventType | 'all'>('all');

  useEffect(() => {
    let cancelled = false;
    function refresh() {
      listAgentActivity()
        .then((data) => {
          if (!cancelled) setEvents(data);
        })
        .catch((err: Error) => {
          if (!cancelled) setError(err.message);
        })
        .finally(() => {
          if (!cancelled) setLoading(false);
        });
    }
    refresh();
    const handler = () => refresh();
    window.addEventListener('agent-sessions-changed', handler);
    return () => {
      cancelled = true;
      window.removeEventListener('agent-sessions-changed', handler);
    };
  }, []);

  const filtered = useMemo(() => {
    let rows = events;
    if (typeFilter !== 'all') {
      rows = rows.filter((e) => e.event_type === typeFilter);
    }
    if (search.trim()) {
      const needle = search.toLowerCase();
      rows = rows.filter(
        (e) =>
          e.ticket_id.toLowerCase().includes(needle) ||
          e.detail.toLowerCase().includes(needle),
      );
    }
    return rows;
  }, [events, search, typeFilter]);

  const countsByType = useMemo(() => {
    const m: Record<string, number> = { all: events.length };
    for (const e of events) m[e.event_type] = (m[e.event_type] ?? 0) + 1;
    return m;
  }, [events]);

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin">
      <div className="max-w-4xl mx-auto px-8 py-6">
        <div className="flex items-center justify-between gap-3 mb-3">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by ticket id or text…"
            className="w-72 px-3 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15"
          />
          <div className="text-[11px] text-slate-500 font-mono">
            {filtered.length} of {events.length} events
          </div>
        </div>

        <div className="flex items-center gap-1 flex-wrap mb-3">
          {TYPE_FILTERS.map((f) => (
            <button
              key={f.key}
              type="button"
              onClick={() => setTypeFilter(f.key)}
              className={`px-2 py-0.5 text-[11px] border rounded transition-colors ${
                typeFilter === f.key
                  ? 'bg-slate-100 border-slate-400 text-slate-900'
                  : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {f.label}{' '}
              <span className="text-slate-400 font-mono">{countsByType[f.key] ?? 0}</span>
            </button>
          ))}
        </div>

        {loading && <div className="text-sm text-slate-400">Loading activity…</div>}
        {error && <div className="text-sm text-red-600">{error}</div>}
        {!loading && !error && filtered.length === 0 && (
          <div className="text-sm text-slate-400">No events match.</div>
        )}

        <ul className="divide-y divide-panel-divider border border-panel-border rounded-lg bg-panel-surface">
          {filtered.map((e, i) => (
            <li
              key={`${e.timestamp}-${e.ticket_id}-${e.event_type}-${i}`}
              className="grid grid-cols-[88px_96px_110px_1fr] gap-3 items-baseline px-4 py-2 text-sm"
            >
              <span className="text-[11px] font-mono text-slate-500 tabular-nums">
                {formatTime(e.timestamp)}
              </span>
              <Link
                to={`/agent/${e.ticket_id}`}
                className="text-[12px] font-mono text-blue-600 hover:text-blue-800 hover:underline truncate"
                title={`Open ${e.ticket_id} in inbox`}
              >
                {e.ticket_id}
              </Link>
              <span
                className={`inline-flex items-center justify-center px-1.5 py-0 text-[10px] border rounded ${
                  TYPE_META[e.event_type].tone
                }`}
              >
                {TYPE_META[e.event_type].label}
              </span>
              <span className="text-[13px] text-slate-700 leading-relaxed truncate">
                {e.detail}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}


function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return iso;
  }
}
