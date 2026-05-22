/** Inbox view — operator decision queue.
 *
 * Two sources, switched by tabs:
 *   * Local — the JSONL sample. Only tickets where the agent's derived
 *     status is needs_review / escalated appear. Approve = log feedback.
 *   * Jira — live tickets from the configured Jira project. All tickets
 *     show until the operator processes them. Approve = post a comment to
 *     Jira AND log feedback.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import {
  Inbox as InboxIcon,
  ListFilter,
} from 'lucide-react';


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


const NEEDS_ATTENTION = new Set<AgentStatus>(['needs_review', 'escalated']);
type Source = 'local' | 'jira';
type SourceFilter = 'all' | 'local' | 'jira';
type StatusFilter = 'all' | AgentStatus;


const SOURCE_OPTIONS: Array<{ key: SourceFilter; label: string }> = [
  { key: 'all', label: 'All sources' },
  { key: 'local', label: 'Local tickets' },
  { key: 'jira', label: 'Jira tickets' },
];


const STATUS_OPTIONS: Array<{ key: StatusFilter; label: string }> = [
  { key: 'all', label: 'All statuses' },
  { key: 'escalated', label: 'Escalated' },
  { key: 'needs_review', label: 'Needs review' },
  { key: 'auto_drafted', label: 'Auto-drafted' },
  { key: 'auto_resolved', label: 'Auto-sent' },
  { key: 'approved', label: 'Approved' },
  { key: 'rejected', label: 'Rejected' },
  { key: 'pending', label: 'Pending' },
  { key: 'skipped', label: 'Skipped' },
];


export function InboxPage() {
  const { ticketKey } = useParams();
  const navigate = useNavigate();

  // Two filter dimensions, both persisted across reloads.
  //   * source — 'all' (interleave both) | 'local' | 'jira'
  //   * status — 'all' | any AgentStatus value
  // Live in the same ListFilter dropdown as two sections.
  const [sourceFilter, setSourceFilterState] = useState<SourceFilter>(() => {
    const stored = typeof window !== 'undefined'
      ? window.localStorage.getItem('inboxFilter')
      : null;
    if (stored === 'local' || stored === 'jira' || stored === 'all') return stored;
    return 'all';
  });
  const setSourceFilter = useCallback((f: SourceFilter) => {
    setSourceFilterState(f);
    try {
      window.localStorage.setItem('inboxFilter', f);
    } catch {
      /* private-mode safe */
    }
  }, []);

  const [statusFilter, setStatusFilterState] = useState<StatusFilter>(() => {
    const stored = typeof window !== 'undefined'
      ? window.localStorage.getItem('inboxStatusFilter')
      : null;
    if (stored && STATUS_OPTIONS.some((o) => o.key === stored)) {
      return stored as StatusFilter;
    }
    return 'all';
  });
  const setStatusFilter = useCallback((f: StatusFilter) => {
    setStatusFilterState(f);
    try {
      window.localStorage.setItem('inboxStatusFilter', f);
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
      // so derived statuses update.
      if (sourceFilter !== 'local') refreshJira();
    };
    window.addEventListener('agent-sessions-changed', handler);

    return () => {
      cancelled = true;
      window.removeEventListener('agent-sessions-changed', handler);
      if (intervalId) clearInterval(intervalId);
    };
  }, [refresh, refreshJira, sourceFilter]);

  // Jira: fetch on mount regardless of the active filter so the count is
  // accurate even while viewing 'local'. Otherwise the operator switches
  // filters and stares at (0) until the first paint.
  useEffect(() => {
    refreshJira();
  }, [refreshJira]);

  // Refetch when the operator switches to a filter that surfaces Jira so
  // the list isn't a stale snapshot from page load.
  useEffect(() => {
    if (sourceFilter !== 'local') refreshJira();
  }, [sourceFilter, refreshJira]);

  async function triggerBatch() {
    try {
      const b = await startAgentBatch();
      setBatch(b);
    } catch {
      /* ignored */
    }
  }

  const sessionByTicketId = useMemo(() => {
    const m = new Map<string, AgentSessionSummary>();
    for (const s of sessions) m.set(s.ticket_id, s);
    return m;
  }, [sessions]);

  // Per-ticket source map so the detail fetcher knows which backend to
  // hit — needed when filter='all' interleaves both sources.
  const sourceByKey = useMemo(() => {
    const m = new Map<string, Source>();
    for (const t of localTickets) m.set(t.key, 'local');
    for (const t of jiraTickets) m.set(t.key, 'jira');
    return m;
  }, [localTickets, jiraTickets]);

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

  const jiraInboxRows: InboxRow[] = useMemo(() => {
    return sortInbox(
      jiraTickets.map((t) => ({
        ticket: t,
        session: sessionByTicketId.get(t.key),
      })),
    );
  }, [jiraTickets, sessionByTicketId]);

  const inboxRows: InboxRow[] = useMemo(() => {
    let rows: InboxRow[];
    if (sourceFilter === 'local') rows = localInboxRows;
    else if (sourceFilter === 'jira') rows = jiraInboxRows;
    // 'all' — merge then sort by timestamp so newest tickets win
    // regardless of source.
    else rows = sortInbox([...localInboxRows, ...jiraInboxRows]);

    if (statusFilter !== 'all') {
      rows = rows.filter(
        (r) => (r.session?.derived_status ?? 'pending') === statusFilter,
      );
    }
    return rows;
  }, [sourceFilter, statusFilter, localInboxRows, jiraInboxRows]);

  // For 'all', wait until BOTH sources are loaded before rendering — &&
  // would let the local rows render first and then visibly grow as the
  // Jira batch arrives, which felt like a reorder flash.
  const rowsLoading =
    sourceFilter === 'jira'
      ? jiraLoading
      : sourceFilter === 'local'
      ? ticketsLoading
      : ticketsLoading || jiraLoading;
  const rowsError = sourceFilter === 'jira' ? jiraError : ticketsError;

  // Active source is best-effort from the lookup map; the fetcher below
  // falls back to the other backend if this guess is wrong (e.g. when
  // the operator deep-links to a ticket that isn't in either list yet).
  const guessedSource: Source = ticketKey
    ? sourceByKey.get(ticketKey) ?? 'local'
    : 'local';
  const [activeSource, setActiveSource] = useState<Source>('local');

  // Ticket detail fetch — try the guessed source first, fall back to the
  // other one on failure. Lets deep-links from the Activity Log (where
  // the ticket may already be decided and absent from the inbox list)
  // load reliably regardless of source.
  useEffect(() => {
    if (!ticketKey) {
      setActiveTicket(null);
      return;
    }
    let cancelled = false;
    setActiveLoading(true);
    setActiveTicket(null);
    (async () => {
      const order: Source[] =
        guessedSource === 'jira' ? ['jira', 'local'] : ['local', 'jira'];
      for (const src of order) {
        try {
          const fetcher = src === 'jira' ? getJiraTicket : getTicket;
          const data = await fetcher(ticketKey);
          if (!cancelled) {
            setActiveTicket(data);
            setActiveSource(src);
            setActiveLoading(false);
          }
          return;
        } catch {
          /* try the next source */
        }
      }
      if (!cancelled) {
        setActiveTicket(null);
        setActiveLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [ticketKey, guessedSource]);

  // Clear selection when the operator EXPLICITLY changes the filter and
  // the active row is no longer visible. We track the last-seen filter
  // values in a ref and only act on an actual change — a simple boolean
  // "initial mount" flag breaks under StrictMode dev double-invocation
  // (second run sees flag already flipped and redirects on mount).
  const lastSeenFilter = useRef<string | null>(null);
  useEffect(() => {
    const key = `${sourceFilter}:${statusFilter}`;
    const prev = lastSeenFilter.current;
    lastSeenFilter.current = key;
    if (prev === null || prev === key) return; // initial run or no real change
    if (!ticketKey) return;
    const still = inboxRows.some((r) => r.ticket.key === ticketKey);
    if (!still) navigate('/inbox', { replace: true });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sourceFilter, statusFilter]);

  // Auto-select first row when no key in URL.
  useEffect(() => {
    if (ticketKey) return;
    if (inboxRows.length === 0) return;
    navigate(`/inbox/${inboxRows[0].ticket.key}`, { replace: true });
  }, [ticketKey, inboxRows, navigate]);

  // After a LOCAL decision the just-approved/rejected row leaves the
  // visible list — auto-clear the URL so the operator isn't stuck on a
  // dead selection. We only redirect when the active ticket WAS visible
  // a moment ago and is now gone; landing on a deep link to a decided
  // ticket (e.g. from the Activity Log) must NOT trigger this.
  const prevVisibleKeys = useRef<Set<string>>(new Set());
  useEffect(() => {
    const now = new Set(inboxRows.map((r) => r.ticket.key));
    const prev = prevVisibleKeys.current;
    if (
      activeSource === 'local' &&
      ticketKey &&
      prev.has(ticketKey) &&
      !now.has(ticketKey)
    ) {
      navigate('/inbox', { replace: true });
    }
    prevVisibleKeys.current = now;
  }, [inboxRows, ticketKey, navigate, activeSource]);

  const sourceLabel = SOURCE_OPTIONS.find((o) => o.key === sourceFilter)?.label ?? 'All';
  const statusLabel = STATUS_OPTIONS.find((o) => o.key === statusFilter)?.label ?? 'All';
  const filteredCount = inboxRows.length;
  const showLocalCTAs =
    sourceFilter !== 'jira' && metrics != null && metrics.processed < metrics.total;
  const activeFilterCount =
    (sourceFilter === 'all' ? 0 : 1) + (statusFilter === 'all' ? 0 : 1);

  const showLoadingState = !initialLoaded || rowsLoading;
  const showEmptyList = !showLoadingState && !rowsError && inboxRows.length === 0;

  return (
    <div className="h-full flex flex-col">
      {/* Full-width header row — Inbox title + icons live in the left
          half (over the list), right half is intentionally empty. The
          border-b runs edge-to-edge so the line separates header from
          everything below across both panes. */}
      <div className="flex border-b border-line-subtle shrink-0">
        <header className="w-[360px] h-12 px-4 flex items-center border-r border-line-subtle shrink-0">
          <h1 className="text-base font-semibold text-ink tracking-tight flex items-center gap-2 min-w-0">
            <span>Inbox</span>
            {activeFilterCount > 0 && (
              <span className="text-ink-muted font-normal truncate">
                ·{' '}
                {sourceFilter !== 'all' && sourceLabel.replace(' tickets', '')}
                {sourceFilter !== 'all' && statusFilter !== 'all' && ', '}
                {statusFilter !== 'all' && statusLabel}{' '}
                ({filteredCount})
              </span>
            )}
          </h1>
          <div className="ml-auto flex items-center gap-1">
            <InboxFilterDropdown
              sourceFilter={sourceFilter}
              statusFilter={statusFilter}
              onSourceChange={setSourceFilter}
              onStatusChange={setStatusFilter}
              activeCount={activeFilterCount}
            />
          </div>
        </header>
        <div className="flex-1 h-12" aria-hidden />
      </div>

      {/* Body: list (left, 360px) + ticket detail (right, flex-1) */}
      <div className="flex-1 flex min-h-0">
        <div className="w-[360px] shrink-0 flex flex-col border-r border-line-subtle min-h-0">
          <BatchInlineNotice
            sourceFilter={sourceFilter}
            batch={batch}
            showCTA={!!showLocalCTAs}
            metrics={metrics}
            onTrigger={triggerBatch}
          />
          {showLoadingState ? (
            <div className="flex-1 flex items-center justify-center text-sm text-ink-muted">
              Loading inbox…
            </div>
          ) : rowsError ? (
            <div className="flex-1 flex items-center justify-center px-4 text-sm text-red-600 text-center">
              {rowsError}
            </div>
          ) : showEmptyList ? (
            sourceFilter === 'local' ? (
              <div className="flex-1 flex flex-col items-center justify-center px-4 text-center">
                <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-emerald-50 text-emerald-600 mb-3">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </div>
                <p className="text-sm text-ink">All caught up</p>
                <p className="mt-0.5 text-xs text-ink-muted">
                  No tickets need your attention.
                </p>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-sm text-ink-muted">
                No tickets in this view.
              </div>
            )
          ) : (
            <AgentInbox rows={inboxRows} loading={false} error={rowsError} />
          )}
        </div>

        <div className="flex-1 flex flex-col min-w-0">
          {activeLoading ? (
            <div className="flex-1 flex items-center justify-center text-sm text-ink-muted">
              Loading ticket…
            </div>
          ) : activeTicket ? (
            <AgentTicketDetail ticket={activeTicket} source={activeSource} />
          ) : (
            <EmptyTicketDetail />
          )}
        </div>
      </div>
    </div>
  );
}


function InboxFilterDropdown({
  sourceFilter,
  statusFilter,
  onSourceChange,
  onStatusChange,
  activeCount,
}: {
  sourceFilter: SourceFilter;
  statusFilter: StatusFilter;
  onSourceChange: (next: SourceFilter) => void;
  onStatusChange: (next: StatusFilter) => void;
  activeCount: number;
}) {
  const [open, setOpen] = useState(false);

  // Click-outside dismiss — single document-level handler, only active
  // while the popover is open.
  useEffect(() => {
    if (!open) return;
    function onClickAway(e: MouseEvent) {
      const target = e.target as Element | null;
      if (target && !target.closest('[data-inbox-filter-root]')) setOpen(false);
    }
    document.addEventListener('mousedown', onClickAway);
    return () => document.removeEventListener('mousedown', onClickAway);
  }, [open]);

  const highlighted = open || activeCount > 0;

  return (
    <div className="relative" data-inbox-filter-root>
      <button
        type="button"
        title="Filter"
        onClick={() => setOpen((v) => !v)}
        className={`w-7 h-7 inline-flex items-center justify-center rounded-md transition-colors duration-150 focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-1 outline-none ${
          highlighted
            ? 'bg-hover text-ink-body'
            : 'text-ink-muted hover:bg-hover hover:text-ink-body'
        }`}
      >
        <ListFilter width={16} height={16} strokeWidth={1.75} />
      </button>
      {open && (
        <div className="absolute right-0 mt-1 w-52 bg-card border border-line rounded-md shadow-md py-1 z-20">
          <DropdownSection
            label="Source"
            options={SOURCE_OPTIONS}
            current={sourceFilter}
            onPick={(k) => onSourceChange(k as SourceFilter)}
          />
          <div className="my-1 border-t border-line-subtle" />
          <DropdownSection
            label="Status"
            options={STATUS_OPTIONS}
            current={statusFilter}
            onPick={(k) => onStatusChange(k as StatusFilter)}
          />
          {activeCount > 0 && (
            <>
              <div className="my-1 border-t border-line-subtle" />
              <button
                type="button"
                onClick={() => {
                  onSourceChange('all');
                  onStatusChange('all');
                }}
                className="w-full text-left px-3 py-1.5 text-[12px] text-ink-muted hover:text-ink-body hover:bg-hover transition-colors duration-150"
              >
                Clear all filters
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}


function DropdownSection({
  label,
  options,
  current,
  onPick,
}: {
  label: string;
  options: Array<{ key: string; label: string }>;
  current: string;
  onPick: (key: string) => void;
}) {
  return (
    <div>
      <div className="px-3 pt-1 pb-0.5 text-[10px] font-medium uppercase tracking-wider text-ink-muted">
        {label}
      </div>
      {options.map((opt) => {
        const active = opt.key === current;
        return (
          <button
            key={opt.key}
            type="button"
            onClick={() => onPick(opt.key)}
            className={`w-full text-left px-3 py-1 text-[13px] flex items-center justify-between gap-2 transition-colors duration-150 ${
              active
                ? 'text-ink font-medium'
                : 'text-ink-body hover:bg-hover hover:text-ink'
            }`}
          >
            <span>{opt.label}</span>
            {active && <span className="text-xs text-accent">✓</span>}
          </button>
        );
      })}
    </div>
  );
}


function BatchInlineNotice({
  sourceFilter,
  batch,
  showCTA,
  metrics,
  onTrigger,
}: {
  sourceFilter: SourceFilter;
  batch: BatchStatus | null;
  showCTA: boolean;
  metrics: AgentMetrics | null;
  onTrigger: () => void;
}) {
  // Thin info row that surfaces batch state without bloating the header.
  // Renders nothing when there's nothing actionable.
  if (sourceFilter === 'jira') return null;
  if (batch?.running) {
    return (
      <div className="px-4 py-1.5 border-b border-line-subtle flex items-center gap-2 text-xs text-accent-fg">
        <span className="inline-block w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
        Processing tickets… {batch.processed} / {batch.total}
        {batch.current_ticket && (
          <span className="font-mono text-ink-muted">· {batch.current_ticket}</span>
        )}
      </div>
    );
  }
  if (showCTA && metrics) {
    const remaining = metrics.total - metrics.processed;
    return (
      <div className="px-4 py-1.5 border-b border-line-subtle flex items-center gap-3 text-xs">
        <span className="text-ink-muted">
          {remaining} ticket{remaining === 1 ? '' : 's'} not yet processed
        </span>
        <button
          type="button"
          onClick={onTrigger}
          className="inline-flex items-center h-6 px-2.5 rounded-md text-xs font-medium text-white bg-accent hover:bg-accent-hover transition-colors duration-150"
        >
          Process {remaining}
        </button>
      </div>
    );
  }
  return null;
}


function EmptyTicketDetail() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center text-ink-muted">
      <InboxIcon width={28} height={28} strokeWidth={1.5} className="text-ink-faint mb-3" />
      <p className="text-sm">Select a ticket to view details</p>
    </div>
  );
}


