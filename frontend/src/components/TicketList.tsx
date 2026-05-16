/** Left column of the Agent page — filterable list of sample tickets. */
import { useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import type { TicketSummary } from '../lib/types';


interface Props {
  tickets: TicketSummary[];
  loading: boolean;
  error: string | null;
}

export function TicketList({ tickets, loading, error }: Props) {
  const { ticketKey } = useParams();
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    if (!search.trim()) return tickets;
    const needle = search.toLowerCase();
    return tickets.filter(
      (t) =>
        t.key.toLowerCase().includes(needle) ||
        t.summary.toLowerCase().includes(needle) ||
        t.labels.some((l) => l.toLowerCase().includes(needle)),
    );
  }, [tickets, search]);

  return (
    <div className="flex flex-col w-[320px] shrink-0 border-r border-panel-border bg-panel-surface">
      <div className="px-4 py-3 border-b border-panel-border">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search tickets…"
          className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15"
        />
        <div className="mt-2 text-[11px] text-slate-500 font-mono tabular-nums">
          {filtered.length} of {tickets.length}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {loading && <div className="px-4 py-6 text-sm text-slate-400">Loading…</div>}
        {error && <div className="px-4 py-6 text-sm text-red-600">{error}</div>}
        {!loading && !error && filtered.length === 0 && (
          <div className="px-4 py-6 text-sm text-slate-400">No tickets match.</div>
        )}
        <ul>
          {filtered.map((t) => {
            const isActive = ticketKey === t.key;
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
                    <StatusPill status={t.status} category={t.status_category} />
                  </div>
                  <div className="mt-1 text-sm font-medium text-slate-900 leading-snug line-clamp-2">
                    {t.summary}
                  </div>
                  {t.labels.length > 0 && (
                    <div className="mt-1.5 flex items-center gap-1 flex-wrap">
                      {t.labels.slice(0, 3).map((l) => (
                        <span
                          key={l}
                          className="text-[10px] px-1.5 py-0 rounded bg-slate-100 text-slate-600"
                        >
                          {l}
                        </span>
                      ))}
                    </div>
                  )}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}


function StatusPill({
  status,
  category,
}: {
  status: string;
  category: string | null;
}) {
  const tone =
    category === 'done'
      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
      : category === 'in_progress' || category === 'indeterminate'
      ? 'bg-amber-50 text-amber-700 border-amber-200'
      : 'bg-slate-50 text-slate-600 border-slate-200';
  return (
    <span className={`inline-flex items-center px-1.5 py-0 text-[10px] border rounded ${tone}`}>
      {status}
    </span>
  );
}
