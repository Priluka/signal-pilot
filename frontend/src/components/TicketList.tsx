/** Left column of the Agent page — filterable list of sample tickets.
 *
 * The right-hand pill shows operator workflow state (Not started /
 * Classified / Retrieved / Drafted / Approved / Edited / Rejected /
 * Auto-close) rather than the inherited Jira ticket status, which was
 * misleading — every row shipped as 'Done' simply because the sample is
 * resolved-historic tickets.
 */
import { useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import { agentWorkflowState } from '../lib/types';
import type {
  AgentSessionSummary,
  AgentWorkflowState,
  TicketSummary,
} from '../lib/types';


interface Props {
  tickets: TicketSummary[];
  loading: boolean;
  error: string | null;
  sessionByTicketId: Map<string, AgentSessionSummary>;
}


export function TicketList({ tickets, loading, error, sessionByTicketId }: Props) {
  const { ticketKey } = useParams();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | 'pending' | 'in_progress' | 'done'>(
    'all',
  );

  const annotated = useMemo(
    () =>
      tickets.map((t) => ({
        ticket: t,
        state: agentWorkflowState(sessionByTicketId.get(t.key)),
      })),
    [tickets, sessionByTicketId],
  );

  const filtered = useMemo(() => {
    let rows = annotated;
    if (filter === 'pending') {
      rows = rows.filter((r) => r.state === 'not_started');
    } else if (filter === 'in_progress') {
      rows = rows.filter((r) =>
        ['classified', 'retrieved', 'drafted'].includes(r.state),
      );
    } else if (filter === 'done') {
      rows = rows.filter((r) =>
        ['approved', 'edited', 'rejected', 'auto_close'].includes(r.state),
      );
    }
    if (search.trim()) {
      const needle = search.toLowerCase();
      rows = rows.filter(
        ({ ticket: t }) =>
          t.key.toLowerCase().includes(needle) ||
          t.summary.toLowerCase().includes(needle) ||
          t.labels.some((l) => l.toLowerCase().includes(needle)),
      );
    }
    return rows;
  }, [annotated, filter, search]);

  const counts = useMemo(() => {
    let pending = 0;
    let inProgress = 0;
    let done = 0;
    for (const a of annotated) {
      if (a.state === 'not_started') pending++;
      else if (['classified', 'retrieved', 'drafted'].includes(a.state)) inProgress++;
      else done++;
    }
    return { pending, inProgress, done, total: annotated.length };
  }, [annotated]);

  return (
    <div className="flex flex-col w-[320px] shrink-0 border-r border-panel-border bg-panel-surface">
      <div className="px-4 py-3 border-b border-panel-border space-y-2">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search tickets…"
          className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15"
        />
        <div className="flex items-center gap-1 text-[10px]">
          {(
            [
              ['all', `All ${counts.total}`],
              ['pending', `Pending ${counts.pending}`],
              ['in_progress', `In prog ${counts.inProgress}`],
              ['done', `Done ${counts.done}`],
            ] as const
          ).map(([key, label]) => (
            <button
              key={key}
              type="button"
              onClick={() => setFilter(key)}
              className={`px-1.5 py-0.5 rounded border transition-colors ${
                filter === key
                  ? 'bg-slate-100 border-slate-400 text-slate-900'
                  : 'bg-white border-slate-200 text-slate-500 hover:bg-slate-50'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="text-[11px] text-slate-500 font-mono tabular-nums">
          {filtered.length} shown
        </div>
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {loading && <div className="px-4 py-6 text-sm text-slate-400">Loading…</div>}
        {error && <div className="px-4 py-6 text-sm text-red-600">{error}</div>}
        {!loading && !error && filtered.length === 0 && (
          <div className="px-4 py-6 text-sm text-slate-400">No tickets match.</div>
        )}
        <ul>
          {filtered.map(({ ticket: t, state }) => {
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
                    <WorkflowPill state={state} />
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


function WorkflowPill({ state }: { state: AgentWorkflowState }) {
  const map: Record<AgentWorkflowState, { label: string; tone: string }> = {
    not_started: {
      label: 'pending',
      tone: 'bg-slate-50 text-slate-500 border-slate-200',
    },
    classified: {
      label: 'classified',
      tone: 'bg-blue-50 text-blue-700 border-blue-200',
    },
    retrieved: {
      label: 'retrieved',
      tone: 'bg-blue-50 text-blue-700 border-blue-200',
    },
    drafted: {
      label: 'drafted',
      tone: 'bg-amber-50 text-amber-700 border-amber-200',
    },
    approved: {
      label: 'approved',
      tone: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
    edited: {
      label: 'edited',
      tone: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    },
    rejected: {
      label: 'rejected',
      tone: 'bg-red-50 text-red-700 border-red-200',
    },
    auto_close: {
      label: 'auto-close',
      tone: 'bg-slate-50 text-slate-600 border-slate-200',
    },
  };
  const { label, tone } = map[state];
  return (
    <span
      className={`inline-flex items-center px-1.5 py-0 text-[10px] border rounded ${tone}`}
    >
      {label}
    </span>
  );
}
