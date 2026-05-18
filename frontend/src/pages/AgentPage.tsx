/** Agent Feed — inbox of agent-processed tickets.
 *
 * On mount we kick off ``POST /agent/batch-process`` (idempotent) and poll
 * the batch status every 2 s until done so the progress bar tracks the
 * background work. Metrics + sessions are refreshed in lockstep and again
 * on the 'agent-sessions-changed' window event (fired by AgentTicketDetail
 * after an Approve / Edit / Reject / Re-process).
 *
 * The "Needs attention" view shows only the tickets that actually wait on
 * a human — escalated + needs_review. Toggle to "Full trail" to scan
 * everything the agent did, including auto-resolved / approved / skipped.
 */
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { AgentActivityLog } from '../components/AgentActivityLog';
import {
  AgentInbox,
  sortInbox,
  type InboxRow,
} from '../components/AgentInbox';
import { AgentMetricsBar } from '../components/AgentMetricsBar';
import { AgentTicketDetail } from '../components/AgentTicketDetail';
import {
  getAgentBatchStatus,
  getAgentMetrics,
  getTicket,
  listAgentSessions,
  listTickets,
  startAgentBatch,
} from '../lib/api';
import type {
  AgentMetrics,
  AgentSessionSummary,
  AgentStatus,
  BatchStatus,
  TicketDetail,
  TicketSummary,
} from '../lib/types';


type ViewMode = 'needs_attention' | 'full' | 'activity';
type StatusFilter = AgentStatus | 'all';

const NEEDS_ATTENTION_SET = new Set<AgentStatus>(['needs_review', 'escalated']);

const FULL_TRAIL_FILTERS: { key: StatusFilter; label: string }[] = [
  { key: 'all', label: 'All' },
  { key: 'needs_review', label: 'Needs review' },
  { key: 'escalated', label: 'Escalated' },
  { key: 'auto_drafted', label: 'Auto-drafted' },
  { key: 'auto_resolved', label: 'Auto-resolved' },
  { key: 'approved', label: 'Approved' },
  { key: 'rejected', label: 'Rejected' },
  { key: 'skipped', label: 'Skipped' },
];


export function AgentPage() {
  const { ticketKey } = useParams();
  const navigate = useNavigate();

  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [ticketsLoading, setTicketsLoading] = useState(true);
  const [ticketsError, setTicketsError] = useState<string | null>(null);

  const [sessions, setSessions] = useState<AgentSessionSummary[]>([]);
  const [metrics, setMetrics] = useState<AgentMetrics | null>(null);
  const [batch, setBatch] = useState<BatchStatus | null>(null);

  const [view, setView] = useState<ViewMode>('needs_attention');
  const [filter, setFilter] = useState<StatusFilter>('all');

  const [activeTicket, setActiveTicket] = useState<TicketDetail | null>(null);
  const [activeLoading, setActiveLoading] = useState(false);

  const refreshSessions = useCallback(async () => {
    try {
      const [s, m] = await Promise.all([listAgentSessions(), getAgentMetrics()]);
      setSessions(s);
      setMetrics(m);
    } catch {
      // ignored — bar shows loading state when metrics is null
    }
  }, []);

  // Load ticket list once.
  useEffect(() => {
    let cancelled = false;
    setTicketsLoading(true);
    listTickets()
      .then((data) => {
        if (!cancelled) setTickets(data);
      })
      .catch((err: Error) => {
        if (!cancelled) setTicketsError(err.message);
      })
      .finally(() => {
        if (!cancelled) setTicketsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Kick off the batch + poll while running.
  useEffect(() => {
    let cancelled = false;
    let intervalId: ReturnType<typeof setInterval> | null = null;

    startAgentBatch()
      .then((b) => {
        if (cancelled) return;
        setBatch(b);
        if (b.running) {
          intervalId = setInterval(async () => {
            try {
              const s = await getAgentBatchStatus();
              if (cancelled) return;
              setBatch(s);
              refreshSessions();
              if (!s.running && intervalId) {
                clearInterval(intervalId);
                intervalId = null;
              }
            } catch {
              // transient — try again on next tick
            }
          }, 2000);
        }
      })
      .catch(() => {});

    refreshSessions();
    const handler = () => refreshSessions();
    window.addEventListener('agent-sessions-changed', handler);

    return () => {
      cancelled = true;
      window.removeEventListener('agent-sessions-changed', handler);
      if (intervalId) clearInterval(intervalId);
    };
  }, [refreshSessions]);

  // Active ticket detail load.
  useEffect(() => {
    if (!ticketKey) {
      setActiveTicket(null);
      return;
    }
    let cancelled = false;
    setActiveLoading(true);
    getTicket(ticketKey)
      .then((data) => {
        if (!cancelled) setActiveTicket(data);
      })
      .catch(() => {
        if (!cancelled) setActiveTicket(null);
      })
      .finally(() => {
        if (!cancelled) setActiveLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [ticketKey]);

  const sessionByTicketId = useMemo(() => {
    const m = new Map<string, AgentSessionSummary>();
    for (const s of sessions) m.set(s.ticket_id, s);
    return m;
  }, [sessions]);

  const inboxRows: InboxRow[] = useMemo(() => {
    const annotated: InboxRow[] = tickets.map((t) => ({
      ticket: t,
      session: sessionByTicketId.get(t.key),
    }));
    let rows = annotated;
    if (view === 'needs_attention') {
      rows = rows.filter((r) =>
        r.session ? NEEDS_ATTENTION_SET.has(r.session.derived_status) : false,
      );
    } else if (filter !== 'all') {
      rows = rows.filter((r) => r.session?.derived_status === filter);
    }
    return sortInbox(rows);
  }, [tickets, sessionByTicketId, view, filter]);

  // Auto-select the first row when no ticketKey in the URL.
  useEffect(() => {
    if (ticketKey) return;
    if (inboxRows.length === 0) return;
    navigate(`/agent/${inboxRows[0].ticket.key}`, { replace: true });
  }, [ticketKey, inboxRows, navigate]);

  return (
    <div className="h-full flex flex-col">
      <header className="px-6 py-3 border-b border-panel-border bg-panel-surface space-y-3">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold tracking-tight text-slate-900">
            Agent Feed
          </h1>
          <ViewToggle view={view} onChange={setView} />
        </div>
        <AgentMetricsBar metrics={metrics} batch={batch} />
        {view === 'full' && (
          <FilterChipStrip value={filter} onChange={setFilter} counts={metrics} />
        )}
      </header>
      <div className="flex-1 flex overflow-hidden">
        {view === 'activity' ? (
          <AgentActivityLog />
        ) : (
          <>
            <AgentInbox
              rows={inboxRows}
              loading={ticketsLoading}
              error={ticketsError}
            />
            {activeLoading ? (
              <div className="flex-1 flex items-center justify-center text-sm text-slate-400">
                Loading ticket…
              </div>
            ) : activeTicket ? (
              <AgentTicketDetail ticket={activeTicket} />
            ) : (
              <div className="flex-1 flex items-center justify-center text-sm text-slate-400">
                {inboxRows.length === 0
                  ? batch?.running
                    ? `Processing tickets… ${batch.processed} / ${batch.total}`
                    : 'Nothing in this view.'
                  : 'Pick a ticket from the inbox.'}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}


function ViewToggle({
  view,
  onChange,
}: {
  view: ViewMode;
  onChange: (v: ViewMode) => void;
}) {
  return (
    <div className="inline-flex items-center rounded-md border border-slate-200 overflow-hidden text-sm">
      {(
        [
          ['needs_attention', 'Needs attention'],
          ['full', 'All tickets'],
          ['activity', 'Activity log'],
        ] as const
      ).map(([key, label]) => (
        <button
          key={key}
          type="button"
          onClick={() => onChange(key)}
          className={`px-3 py-1 transition-colors ${
            view === key
              ? 'bg-blue-600 text-white'
              : 'bg-white text-slate-700 hover:bg-slate-50'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}


function FilterChipStrip({
  value,
  onChange,
  counts,
}: {
  value: StatusFilter;
  onChange: (v: StatusFilter) => void;
  counts: AgentMetrics | null;
}) {
  const countFor = (k: StatusFilter): number => {
    if (!counts) return 0;
    if (k === 'all') return counts.processed;
    return counts[k as keyof AgentMetrics] as number;
  };
  return (
    <div className="flex items-center gap-1 flex-wrap">
      {FULL_TRAIL_FILTERS.map((f) => (
        <button
          key={f.key}
          type="button"
          onClick={() => onChange(f.key)}
          className={`px-2 py-0.5 text-[11px] border rounded transition-colors ${
            value === f.key
              ? 'bg-slate-100 border-slate-400 text-slate-900'
              : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
          }`}
        >
          {f.label} <span className="text-slate-400 font-mono">{countFor(f.key)}</span>
        </button>
      ))}
    </div>
  );
}
