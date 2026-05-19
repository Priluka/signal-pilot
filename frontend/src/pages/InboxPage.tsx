/** Inbox view — operator decision queue.
 *
 * Two sources, switched by tabs:
 *   * Local — the JSONL sample. Only tickets where the agent's derived
 *     status is needs_review / escalated appear. Approve = log feedback.
 *   * Jira — live tickets from the configured Jira project. All tickets
 *     show until the operator processes them. Approve = post a comment to
 *     Jira AND log feedback.
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
  getJiraTicket,
  getTicket,
  listAgentSessions,
  listJiraTickets,
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
import { useAgentMode } from '../lib/useAgentMode';

import { AgentModeChip } from '../components/AgentModeChip';


const NEEDS_ATTENTION = new Set<AgentStatus>(['needs_review', 'escalated']);
type Source = 'local' | 'jira';


export function InboxPage() {
  const { ticketKey } = useParams();
  const navigate = useNavigate();
  const agentMode = useAgentMode();

  // Hold the active source in localStorage so the tab choice survives
  // page reloads + cross-tab navigation.
  const [source, setSourceState] = useState<Source>(() => {
    const stored = typeof window !== 'undefined'
      ? window.localStorage.getItem('inboxSource')
      : null;
    return stored === 'jira' ? 'jira' : 'local';
  });
  const setSource = useCallback((s: Source) => {
    setSourceState(s);
    try {
      window.localStorage.setItem('inboxSource', s);
    } catch {
      /* private-mode safe */
    }
  }, []);

  // --- Local tickets -----------------------------------------------------
  const [localTickets, setLocalTickets] = useState<TicketSummary[]>([]);
  const [ticketsLoading, setTicketsLoading] = useState(true);
  const [ticketsError, setTicketsError] = useState<string | null>(null);

  const [sessions, setSessions] = useState<AgentSessionSummary[]>([]);
  const [metrics, setMetrics] = useState<AgentMetrics | null>(null);
  const [batch, setBatch] = useState<BatchStatus | null>(null);
  const [initialLoaded, setInitialLoaded] = useState(false);

  // --- Jira tickets ------------------------------------------------------
  const [jiraTickets, setJiraTickets] = useState<TicketSummary[]>([]);
  const [jiraLoading, setJiraLoading] = useState(false);
  const [jiraError, setJiraError] = useState<string | null>(null);

  const [activeTicket, setActiveTicket] = useState<TicketDetail | null>(null);
  const [activeLoading, setActiveLoading] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [s, m] = await Promise.all([listAgentSessions(), getAgentMetrics()]);
      setSessions(s);
      setMetrics(m);
    } catch {
      // Periodic poll retries on the next tick.
    } finally {
      setInitialLoaded(true);
    }
  }, []);

  const refreshJira = useCallback(async () => {
    setJiraLoading(true);
    setJiraError(null);
    try {
      const data = await listJiraTickets();
      setJiraTickets(data);
    } catch (err) {
      setJiraError((err as Error).message);
    } finally {
      setJiraLoading(false);
    }
  }, []);

  // Local: tickets + batch polling + session refresh on agent-sessions-changed.
  useEffect(() => {
    let cancelled = false;
    let intervalId: ReturnType<typeof setInterval> | null = null;

    setTicketsLoading(true);
    listTickets()
      .then((data) => {
        if (!cancelled) setLocalTickets(data);
      })
      .catch((err: Error) => {
        if (!cancelled) setTicketsError(err.message);
      })
      .finally(() => {
        if (!cancelled) setTicketsLoading(false);
      });

    getAgentBatchStatus()
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
              /* transient */
            }
          }, 2000);
        }
      })
      .catch(() => {});

    refresh();
    const handler = () => {
      refresh();
      // Sessions changed (typically post-approve) — also refresh Jira list
      // so its derived statuses update.
      if (source === 'jira') refreshJira();
    };
    window.addEventListener('agent-sessions-changed', handler);

    return () => {
      cancelled = true;
      window.removeEventListener('agent-sessions-changed', handler);
      if (intervalId) clearInterval(intervalId);
    };
  }, [refresh, refreshJira, source]);

  // Jira: fetch on mount regardless of active source so the 'Jira tickets (N)'
  // tab badge shows the real count before the operator clicks. Otherwise
  // the badge sits at (0) and the operator dismisses the tab thinking
  // there's nothing there.
  useEffect(() => {
    refreshJira();
  }, [refreshJira]);

  // Refetch when the operator switches to the Jira tab so the list isn't
  // a stale snapshot from page load.
  useEffect(() => {
    if (source === 'jira') refreshJira();
  }, [source, refreshJira]);

  async function triggerBatch() {
    try {
      const b = await startAgentBatch();
      setBatch(b);
    } catch {
      /* ignored */
    }
  }

  // Ticket detail fetch — routes through the right backend depending on source.
  useEffect(() => {
    if (!ticketKey) {
      setActiveTicket(null);
      return;
    }
    let cancelled = false;
    setActiveLoading(true);
    const fetcher = source === 'jira' ? getJiraTicket : getTicket;
    fetcher(ticketKey)
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
  }, [ticketKey, source]);

  const sessionByTicketId = useMemo(() => {
    const m = new Map<string, AgentSessionSummary>();
    for (const s of sessions) m.set(s.ticket_id, s);
    return m;
  }, [sessions]);

  const localInboxRows: InboxRow[] = useMemo(() => {
    const annotated: InboxRow[] = localTickets.map((t) => ({
      ticket: t,
      session: sessionByTicketId.get(t.key),
    }));
    return sortInbox(
      annotated.filter((r) =>
        r.session ? NEEDS_ATTENTION.has(r.session.derived_status) : false,
      ),
    );
  }, [localTickets, sessionByTicketId]);

  // Jira shows ALL tickets — agent state appears once the operator processes
  // each one, and any decided ticket still stays visible (its session pill
  // shows "approved" / "rejected").
  const jiraInboxRows: InboxRow[] = useMemo(() => {
    return jiraTickets.map((t) => ({
      ticket: t,
      session: sessionByTicketId.get(t.key),
    }));
  }, [jiraTickets, sessionByTicketId]);

  const inboxRows = source === 'jira' ? jiraInboxRows : localInboxRows;
  const rowsLoading = source === 'jira' ? jiraLoading : ticketsLoading;
  const rowsError = source === 'jira' ? jiraError : ticketsError;

  // Clear selection when switching tabs so we don't show a /tickets ticket
  // under the Jira tab or vice versa.
  useEffect(() => {
    if (ticketKey) navigate('/inbox', { replace: true });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [source]);

  // Auto-select first row when no key in URL.
  useEffect(() => {
    if (ticketKey) return;
    if (inboxRows.length === 0) return;
    navigate(`/inbox/${inboxRows[0].ticket.key}`, { replace: true });
  }, [ticketKey, inboxRows, navigate]);

  // After a local decision the ticket leaves the inbox; for Jira we keep it.
  useEffect(() => {
    if (source !== 'local') return;
    if (!ticketKey) return;
    const still = inboxRows.some((r) => r.ticket.key === ticketKey);
    if (!still) {
      navigate('/inbox', { replace: true });
    }
  }, [inboxRows, ticketKey, navigate, source]);

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
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold tracking-tight text-slate-900">
              Inbox
            </h1>
            {agentMode && (
              <AgentModeChip mode={agentMode} size="sm" prefix="Default:" />
            )}
            <div className="flex items-center gap-1">
              <SourceTab
                active={source === 'local'}
                onClick={() => setSource('local')}
                label="Local tickets"
                count={localTickets.length}
              />
              <SourceTab
                active={source === 'jira'}
                onClick={() => setSource('jira')}
                label="Jira tickets"
                count={jiraTickets.length}
              />
            </div>
          </div>
          <div className="flex items-center gap-x-5 text-[11px]">
            {source === 'local' ? (
              <>
                <Metric label="Processed" value={`${totalProcessed}`} />
                <Metric label="Pending" value={`${totalPending}`} tone="text-amber-700" />
                <Metric
                  label="Approval rate"
                  value={metrics && metrics.approved + metrics.rejected > 0 ? `${approvalRate}%` : '—'}
                />
              </>
            ) : (
              <Metric label="Total in KAN" value={`${jiraTickets.length}`} />
            )}
          </div>
        </div>
        {source === 'local' && batch?.running ? (
          <div className="flex items-center gap-2 text-[11px] text-blue-700">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
            Processing tickets… {batch.processed} / {batch.total}
            {batch.current_ticket && (
              <span className="font-mono text-slate-500">{batch.current_ticket}</span>
            )}
          </div>
        ) : source === 'local' && metrics && metrics.processed < metrics.total ? (
          <div className="flex items-center gap-3 text-[11px]">
            <span className="text-slate-500">
              {metrics.total - metrics.processed} ticket{metrics.total - metrics.processed === 1 ? '' : 's'} not yet processed by the agent.
            </span>
            <button
              type="button"
              onClick={triggerBatch}
              className="px-2.5 py-1 text-xs font-medium text-white bg-blue-600 rounded hover:bg-blue-700"
            >
              Process pending tickets
            </button>
          </div>
        ) : null}
        {source === 'jira' && (
          <p className="text-[11px] text-slate-500">
            Live from your Jira project. Pick a ticket and click{' '}
            <span className="font-medium text-slate-700">Process with agent</span>{' '}
            to classify → retrieve → draft. Approve writes the draft as a Jira
            comment.
          </p>
        )}
      </header>
      <div className="flex-1 flex overflow-hidden">
        {source === 'local' && (!initialLoaded || rowsLoading) ? (
          <div className="flex-1 flex items-center justify-center text-sm text-slate-400">
            Loading inbox…
          </div>
        ) : source === 'jira' && rowsLoading && jiraTickets.length === 0 ? (
          <div className="flex-1 flex items-center justify-center text-sm text-slate-400">
            Loading Jira tickets…
          </div>
        ) : source === 'jira' && rowsError ? (
          <div className="flex-1 flex items-center justify-center text-sm text-red-600 px-8 text-center">
            {rowsError}
          </div>
        ) : inboxRows.length === 0 ? (
          source === 'local' ? (
            <AllCaughtUp running={batch?.running ?? false} processed={batch?.processed ?? 0} total={batch?.total ?? 0} />
          ) : (
            <div className="flex-1 flex items-center justify-center text-sm text-slate-400">
              No tickets in this Jira project.
            </div>
          )
        ) : (
          <>
            <AgentInbox
              rows={inboxRows}
              loading={false}
              error={rowsError}
            />
            {activeLoading ? (
              <div className="flex-1 flex items-center justify-center text-sm text-slate-400">
                Loading ticket…
              </div>
            ) : activeTicket ? (
              <AgentTicketDetail ticket={activeTicket} source={source} />
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


function SourceTab({
  active,
  onClick,
  label,
  count,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
  count: number;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex items-center gap-1.5 px-3 py-1 text-sm rounded-md transition-colors ${
        active
          ? 'bg-white text-slate-900 font-medium border border-slate-200 shadow-sm'
          : 'text-slate-600 hover:bg-white/60 hover:text-slate-900 border border-transparent'
      }`}
    >
      <span>{label}</span>
      <span className="text-[11px] font-mono text-slate-400 tabular-nums">({count})</span>
    </button>
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
