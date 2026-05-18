/** Activity Log — complete audit trail of every agent step + operator
 * decision. Tickets are listed as collapsible cards (newest activity first);
 * the embedded timeline reveals every classify / retrieve / draft / decide
 * event in chronological order. Clicking a card opens the full detail panel
 * on the right (read-mostly; AgentTicketDetail hides the decision buttons
 * once a ticket is decided).
 */
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { AgentMetricsBar } from '../components/AgentMetricsBar';
import { AgentStatusPill } from '../components/AgentStatusPill';
import { AgentTicketDetail } from '../components/AgentTicketDetail';
import {
  getAgentBatchStatus,
  getAgentMetrics,
  getTicket,
  listAgentActivity,
  listAgentSessions,
  startAgentBatch,
} from '../lib/api';
import type {
  AgentActivityEvent,
  AgentEventType,
  AgentMetrics,
  AgentSessionSummary,
  AgentStatus,
  BatchStatus,
  TicketDetail,
} from '../lib/types';


const TYPE_FILTERS: Array<{ key: AgentEventType | 'all'; label: string }> = [
  { key: 'all', label: 'All' },
  { key: 'classified', label: 'Classified' },
  { key: 'retrieved', label: 'Retrieved' },
  { key: 'drafted', label: 'Drafted' },
  { key: 'approved', label: 'Approved' },
  { key: 'rejected', label: 'Rejected' },
  { key: 'skipped', label: 'Skipped' },
];


interface TicketGroup {
  ticket_id: string;
  events: AgentActivityEvent[];
  latest_at: string;
  session: AgentSessionSummary | undefined;
}


export function ActivityLogPage() {
  const { ticketKey } = useParams();
  const navigate = useNavigate();

  const [events, setEvents] = useState<AgentActivityEvent[]>([]);
  const [sessions, setSessions] = useState<AgentSessionSummary[]>([]);
  const [metrics, setMetrics] = useState<AgentMetrics | null>(null);
  const [batch, setBatch] = useState<BatchStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<AgentEventType | 'all'>('all');
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const [activeTicket, setActiveTicket] = useState<TicketDetail | null>(null);
  const [activeLoading, setActiveLoading] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [a, s, m] = await Promise.all([
        listAgentActivity(),
        listAgentSessions(),
        getAgentMetrics(),
      ]);
      setEvents(a);
      setSessions(s);
      setMetrics(m);
    } catch {
      // ignored
    } finally {
      setLoading(false);
    }
  }, []);

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
      .then((d) => {
        if (!cancelled) setActiveTicket(d);
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

  // Group events by ticket; sort events within each group ascending so the
  // timeline reads top→bottom (oldest→newest), then sort groups by latest
  // event timestamp descending.
  const groups: TicketGroup[] = useMemo(() => {
    const map = new Map<string, AgentActivityEvent[]>();
    for (const e of events) {
      const arr = map.get(e.ticket_id) ?? [];
      arr.push(e);
      map.set(e.ticket_id, arr);
    }
    const out: TicketGroup[] = [];
    for (const [ticket_id, list] of map) {
      list.sort((a, b) => a.timestamp.localeCompare(b.timestamp));
      const latest_at = list.length ? list[list.length - 1].timestamp : '';
      out.push({
        ticket_id,
        events: list,
        latest_at,
        session: sessionByTicketId.get(ticket_id),
      });
    }
    out.sort((a, b) => b.latest_at.localeCompare(a.latest_at));
    return out;
  }, [events, sessionByTicketId]);

  const filteredGroups = useMemo(() => {
    let rows = groups;
    if (typeFilter !== 'all') {
      rows = rows.filter((g) => g.events.some((e) => e.event_type === typeFilter));
    }
    if (search.trim()) {
      const needle = search.toLowerCase();
      rows = rows.filter(
        (g) =>
          g.ticket_id.toLowerCase().includes(needle) ||
          g.events.some((e) => e.detail.toLowerCase().includes(needle)),
      );
    }
    return rows;
  }, [groups, search, typeFilter]);

  function toggleExpanded(ticketId: string) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(ticketId)) next.delete(ticketId);
      else next.add(ticketId);
      return next;
    });
  }

  return (
    <div className="h-full flex flex-col">
      <header className="px-6 py-3 border-b border-panel-border bg-panel-surface space-y-3">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold tracking-tight text-slate-900">
            Activity Log
          </h1>
          <span className="text-[11px] text-slate-500 font-mono">
            {filteredGroups.length} ticket{filteredGroups.length === 1 ? '' : 's'} ·{' '}
            {events.length} events
          </span>
        </div>
        <AgentMetricsBar metrics={metrics} batch={batch} />
        <div className="flex items-center gap-3 flex-wrap">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search ticket id or event text…"
            className="w-72 px-3 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15"
          />
          <div className="flex items-center gap-1 flex-wrap">
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
                {f.label}
              </button>
            ))}
          </div>
        </div>
      </header>
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 overflow-y-auto scrollbar-thin">
          <div className="max-w-4xl mx-auto px-6 py-4 space-y-2">
            {loading && (
              <div className="text-sm text-slate-400">Loading activity…</div>
            )}
            {!loading && filteredGroups.length === 0 && (
              <div className="text-sm text-slate-400">No matching activity yet.</div>
            )}
            {filteredGroups.map((g) => (
              <TicketActivityCard
                key={g.ticket_id}
                group={g}
                expanded={expanded.has(g.ticket_id)}
                onToggle={() => toggleExpanded(g.ticket_id)}
                onOpen={() => navigate(`/activity-log/${g.ticket_id}`)}
                isActive={ticketKey === g.ticket_id}
              />
            ))}
          </div>
        </div>
        {ticketKey && (
          <div className="w-[440px] shrink-0 border-l border-panel-border overflow-y-auto scrollbar-thin">
            {activeLoading || !activeTicket ? (
              <div className="flex items-center justify-center h-full text-sm text-slate-400">
                Loading ticket…
              </div>
            ) : (
              <AgentTicketDetail ticket={activeTicket} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Collapsible per-ticket card with embedded timeline
// ---------------------------------------------------------------------------

const EVENT_DOT: Record<AgentEventType, string> = {
  classified: 'bg-blue-500',
  retrieved: 'bg-indigo-500',
  drafted: 'bg-amber-500',
  approved: 'bg-emerald-500',
  edited: 'bg-indigo-500',
  rejected: 'bg-red-500',
  skipped: 'bg-slate-400',
};


function TicketActivityCard({
  group,
  expanded,
  onToggle,
  onOpen,
  isActive,
}: {
  group: TicketGroup;
  expanded: boolean;
  onToggle: () => void;
  onOpen: () => void;
  isActive: boolean;
}) {
  const status: AgentStatus = group.session?.derived_status ?? 'pending';
  const confidence = group.session?.classification_confidence ?? null;

  // The "Awaiting review" pending marker is added inline when the session
  // has a draft but no feedback yet.
  const showAwaiting =
    group.session?.recommended_action &&
    !group.session.feedback_status &&
    group.session.derived_status !== 'auto_resolved' &&
    group.session.derived_status !== 'skipped';

  return (
    <div
      className={`bg-panel-surface border rounded-lg transition-colors ${
        isActive ? 'border-blue-400' : 'border-panel-border'
      }`}
    >
      <div className="flex items-center gap-3 px-3 py-2">
        <button
          type="button"
          onClick={onToggle}
          aria-label={expanded ? 'Collapse' : 'Expand'}
          className="w-5 h-5 inline-flex items-center justify-center text-slate-400 hover:text-slate-700"
        >
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={`transition-transform ${expanded ? 'rotate-90' : ''}`}
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
        <button
          type="button"
          onClick={onOpen}
          className="text-[12px] font-mono text-blue-600 hover:text-blue-800 hover:underline"
        >
          {group.ticket_id}
        </button>
        <AgentStatusPill status={status} />
        <span className="text-[11px] text-slate-500 font-mono">
          {formatTimeOfDay(group.latest_at)}
        </span>
        {confidence != null && (
          <span className="text-[11px] text-slate-500 font-mono">
            conf {confidence.toFixed(2)}
          </span>
        )}
        <span className="ml-auto text-[11px] text-slate-400">
          {group.events.length} event{group.events.length === 1 ? '' : 's'}
        </span>
      </div>
      {expanded && (
        <ol className="border-t border-panel-divider divide-y divide-panel-divider">
          {group.events.map((e, i) => (
            <li
              key={`${e.timestamp}-${e.event_type}-${i}`}
              className="grid grid-cols-[88px_16px_120px_1fr] gap-3 items-baseline px-4 py-1.5 text-sm"
            >
              <span className="text-[11px] font-mono text-slate-500 tabular-nums">
                {formatTime(e.timestamp)}
              </span>
              <span className="flex items-center justify-center">
                <span
                  className={`inline-block w-2 h-2 rounded-full ${EVENT_DOT[e.event_type]}`}
                />
              </span>
              <span className="text-[12px] text-slate-700 capitalize">
                {e.event_type === 'edited'
                  ? 'Approved (edited)'
                  : e.event_type}
              </span>
              <span className="text-[13px] text-slate-700 leading-relaxed truncate">
                {e.detail}
              </span>
            </li>
          ))}
          {showAwaiting && (
            <li className="grid grid-cols-[88px_16px_120px_1fr] gap-3 items-baseline px-4 py-1.5 text-sm">
              <span className="text-[11px] font-mono text-slate-400 tabular-nums">—</span>
              <span className="flex items-center justify-center">
                <span className="inline-block w-2 h-2 rounded-full bg-slate-300 animate-pulse" />
              </span>
              <span className="text-[12px] text-slate-500">Awaiting</span>
              <span className="text-[13px] text-slate-500 italic">
                Operator review pending
              </span>
            </li>
          )}
        </ol>
      )}
    </div>
  );
}


function formatTimeOfDay(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
  } catch {
    return iso;
  }
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
