/** Inbox view — only tickets that need a human decision (escalated +
 * needs_review). Approved / rejected / auto-resolved / skipped do not show
 * here; they live in the Activity Log. When the inbox empties, the right
 * panel renders the "All caught up" state.
 */
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import {
  AgentInbox,
  sortInbox,
  type InboxRow,
} from '../components/AgentInbox';
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


const NEEDS_ATTENTION = new Set<AgentStatus>(['needs_review', 'escalated']);


export function InboxPage() {
  const { ticketKey } = useParams();
  const navigate = useNavigate();

  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [ticketsLoading, setTicketsLoading] = useState(true);
  const [ticketsError, setTicketsError] = useState<string | null>(null);

  const [sessions, setSessions] = useState<AgentSessionSummary[]>([]);
  const [metrics, setMetrics] = useState<AgentMetrics | null>(null);
  const [batch, setBatch] = useState<BatchStatus | null>(null);
  const [initialLoaded, setInitialLoaded] = useState(false);

  const [activeTicket, setActiveTicket] = useState<TicketDetail | null>(null);
  const [activeLoading, setActiveLoading] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [s, m] = await Promise.all([listAgentSessions(), getAgentMetrics()]);
      setSessions(s);
      setMetrics(m);
    } catch {
      // Swallow — the periodic poll will try again on the next tick.
    } finally {
      // We let the page out of its loading state on first attempt regardless
      // of outcome, so a failed metrics fetch doesn't trap the operator in
      // an infinite spinner.
      setInitialLoaded(true);
    }
  }, []);

  // Load tickets once + kick off batch + poll status.
  useEffect(() => {
    let cancelled = false;
    let intervalId: ReturnType<typeof setInterval> | null = null;

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
              refresh();
              if (!s.running && intervalId) {
                clearInterval(intervalId);
                intervalId = null;
              }
            } catch {
              // transient
            }
          }, 2000);
        }
      })
      .catch(() => {});

    refresh();
    const handler = () => refresh();
    window.addEventListener('agent-sessions-changed', handler);

    return () => {
      cancelled = true;
      window.removeEventListener('agent-sessions-changed', handler);
      if (intervalId) clearInterval(intervalId);
    };
  }, [refresh]);

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
    return sortInbox(
      annotated.filter((r) =>
        r.session ? NEEDS_ATTENTION.has(r.session.derived_status) : false,
      ),
    );
  }, [tickets, sessionByTicketId]);

  // Auto-select first inbox ticket when no key in URL.
  useEffect(() => {
    if (ticketKey) return;
    if (inboxRows.length === 0) return;
    navigate(`/inbox/${inboxRows[0].ticket.key}`, { replace: true });
  }, [ticketKey, inboxRows, navigate]);

  // After a decision, the active ticket leaves the inbox — clear it.
  useEffect(() => {
    if (!ticketKey) return;
    const still = inboxRows.some((r) => r.ticket.key === ticketKey);
    if (!still) {
      navigate('/inbox', { replace: true });
    }
  }, [inboxRows, ticketKey, navigate]);

  const escalated = metrics?.escalated ?? 0;
  const needsReview = metrics?.needs_review ?? 0;
  const totalPending = escalated + needsReview;
  const totalProcessed = metrics?.processed ?? 0;
  const approvalRate = metrics
    ? Math.round(metrics.approval_rate * 100)
    : 0;

  return (
    <div className="h-full flex flex-col">
      <header className="px-6 py-3 border-b border-panel-border bg-panel-surface space-y-2">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-slate-900">
              Inbox
            </h1>
            <p className="text-sm text-slate-600 mt-0.5">
              {totalPending === 0
                ? 'All caught up — no tickets need your attention.'
                : `${totalPending} ticket${totalPending === 1 ? '' : 's'} need your attention (${escalated} escalated, ${needsReview} needs review)`}
            </p>
          </div>
          <div className="flex items-center gap-x-5 text-[11px]">
            <Metric label="Processed" value={`${totalProcessed}`} />
            <Metric label="Pending" value={`${totalPending}`} tone="text-amber-700" />
            <Metric
              label="Approval rate"
              value={metrics && metrics.approved + metrics.rejected > 0 ? `${approvalRate}%` : '—'}
            />
          </div>
        </div>
        {batch?.running && (
          <div className="flex items-center gap-2 text-[11px] text-blue-700">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
            Processing tickets… {batch.processed} / {batch.total}
            {batch.current_ticket && (
              <span className="font-mono text-slate-500">{batch.current_ticket}</span>
            )}
          </div>
        )}
      </header>
      <div className="flex-1 flex overflow-hidden">
        {!initialLoaded || ticketsLoading ? (
          <div className="flex-1 flex items-center justify-center text-sm text-slate-400">
            Loading inbox…
          </div>
        ) : inboxRows.length === 0 ? (
          <AllCaughtUp running={batch?.running ?? false} processed={batch?.processed ?? 0} total={batch?.total ?? 0} />
        ) : (
          <>
            <AgentInbox
              rows={inboxRows}
              loading={false}
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
                Pick a ticket from the inbox.
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}


function Metric({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone?: string;
}) {
  return (
    <div className="flex items-baseline gap-1.5">
      <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">
        {label}
      </span>
      <span className={`text-sm font-mono tabular-nums font-medium ${tone ?? 'text-slate-900'}`}>
        {value}
      </span>
    </div>
  );
}


function AllCaughtUp({
  running,
  processed,
  total,
}: {
  running: boolean;
  processed: number;
  total: number;
}) {
  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 mb-4">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold tracking-tight text-slate-900">All caught up</h2>
        <p className="mt-1 text-sm text-slate-500">
          {running
            ? `Agent is still processing tickets (${processed} / ${total}). New ones will appear here as they need review.`
            : 'No tickets need your attention right now. Check the Activity Log for the full audit trail.'}
        </p>
      </div>
    </div>
  );
}
