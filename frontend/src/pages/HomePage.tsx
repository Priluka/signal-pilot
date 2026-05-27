/** Home — default landing page.
 *
 * Linear-grade glance view. Greeting, a row of bare stat numbers, then
 * two slim list sections — tickets that need a decision and the latest
 * activity. No cards, no borders around sections; the operator scans
 * the page in three seconds and knows where to click.
 */
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, ArrowRight, Inbox } from 'lucide-react';

import {
  getAgentMetrics,
  listAgentActivity,
  listAgentSessions,
  listJiraTickets,
  listTickets,
} from '../lib/api';
import type {
  AgentActivityEvent,
  AgentMetrics,
  AgentSessionSummary,
  TicketSummary,
} from '../lib/types';


export function HomePage() {
  const [metrics, setMetrics] = useState<AgentMetrics | null>(null);
  const [sessions, setSessions] = useState<AgentSessionSummary[]>([]);
  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [events, setEvents] = useState<AgentActivityEvent[]>([]);

  useEffect(() => {
    Promise.all([
      getAgentMetrics(),
      listAgentSessions(),
      listTickets(),
      // Jira may be unconfigured (offline) — swallow errors so the rest
      // of the page still renders. KAN-* keys without a Jira hit fall
      // back to the dash placeholder.
      listJiraTickets().catch(() => [] as TicketSummary[]),
      listAgentActivity(5),
    ]).then(([m, s, t, j, e]) => {
      setMetrics(m);
      setSessions(s);
      setTickets([...t, ...j]);
      setEvents(e);
    });
  }, []);

  const ticketMap = useMemo(() => {
    // Last write wins. Jira summaries come second so live data trumps
    // any stale local-sample row sharing the same key.
    const map = new Map<string, TicketSummary>();
    for (const t of tickets) map.set(t.key, t);
    return map;
  }, [tickets]);

  const needsAttention = useMemo(
    () =>
      sessions
        .filter(
          (s) =>
            s.derived_status === 'needs_review' ||
            s.derived_status === 'escalated',
        )
        .sort((a, b) => (a.updated_at < b.updated_at ? 1 : -1))
        .slice(0, 5),
    [sessions],
  );

  return (
    <div className="h-full overflow-y-auto scrollbar-thin">
      <div className="max-w-4xl mx-auto px-8 py-8 space-y-8">
        <Greeting />
        <StatsRow metrics={metrics} needs={needsAttention.length} />
        <NeedsAttention rows={needsAttention} ticketMap={ticketMap} />
        <RecentActivity events={events} />
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// 1. Greeting
// ---------------------------------------------------------------------------

function Greeting() {
  const now = new Date();
  const hour = now.getHours();
  const slot =
    hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
  const dateStr = now.toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });
  return (
    <header>
      <h1 className="text-xl font-semibold text-ink">{slot}, Operator</h1>
      <p className="text-[13px] text-ink-muted mt-1">{dateStr}</p>
    </header>
  );
}


// ---------------------------------------------------------------------------
// 2. Stats row — bare numbers, no cards
// ---------------------------------------------------------------------------

function StatsRow({
  metrics,
  needs,
}: {
  metrics: AgentMetrics | null;
  needs: number;
}) {
  return (
    <div className="grid grid-cols-4 gap-8 py-6 border-b border-line-subtle">
      <Stat
        label="Processed"
        value={metrics ? metrics.processed.toString() : '—'}
        sub={metrics ? `of ${metrics.total} total` : ''}
      />
      <Stat
        label="Needs you"
        value={metrics ? needs.toString() : '—'}
        sub="awaiting review"
        emphasis={needs > 0}
      />
      <Stat
        label="Approval rate"
        value={metrics ? `${Math.round(metrics.approval_rate * 100)}%` : '—'}
        sub="across decided tickets"
      />
      <Stat
        label="Avg confidence"
        value={metrics ? `${Math.round(metrics.avg_confidence * 100)}%` : '—'}
        sub="classifier"
      />
    </div>
  );
}


function Stat({
  label,
  value,
  sub,
  emphasis,
}: {
  label: string;
  value: string;
  sub: string;
  emphasis?: boolean;
}) {
  return (
    <div>
      <div className="text-[11px] uppercase tracking-wider text-ink-muted font-medium">
        {label}
      </div>
      <div
        className={`text-[28px] leading-none font-semibold font-mono mt-1 tabular-nums ${
          emphasis ? 'text-amber-600 dark:text-amber-400' : 'text-ink'
        }`}
      >
        {value}
      </div>
      {sub && (
        <div className="text-[11px] text-ink-muted mt-1.5">{sub}</div>
      )}
    </div>
  );
}


// ---------------------------------------------------------------------------
// 3. Needs your attention
// ---------------------------------------------------------------------------

function NeedsAttention({
  rows,
  ticketMap,
}: {
  rows: AgentSessionSummary[];
  ticketMap: Map<string, TicketSummary>;
}) {
  return (
    <section>
      <SectionHeader icon={Inbox} title="Needs your attention" />
      {rows.length === 0 ? (
        <p className="text-[12px] text-ink-muted py-2">
          No tickets are waiting on you right now.
        </p>
      ) : (
        <ul>
          {rows.map((s) => {
            const t = ticketMap.get(s.ticket_id);
            return (
              <li key={s.ticket_id}>
                <Link
                  to={`/inbox/${s.ticket_id}`}
                  className="flex items-center h-10 px-2 -mx-2 hover:bg-hover rounded-md transition-colors duration-150"
                >
                  <span className="text-[12px] font-mono text-accent-fg w-20 flex-shrink-0">
                    {s.ticket_id}
                  </span>
                  <span className="text-[13px] text-ink truncate flex-1">
                    {t?.summary ?? '—'}
                  </span>
                  {s.classification_label && (
                    <span className="text-[11px] font-mono text-ink-muted flex-shrink-0 ml-4">
                      {s.classification_label}
                    </span>
                  )}
                  <StatusDot status={s.derived_status} />
                  <span className="text-[11px] text-ink-muted flex-shrink-0 ml-3 w-12 text-right tabular-nums">
                    {formatRelative(s.updated_at)}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
      <SectionFooter to="/inbox" label="View all in Inbox" />
    </section>
  );
}


function StatusDot({ status }: { status: string }) {
  const cls =
    status === 'escalated'
      ? 'bg-red-500'
      : status === 'needs_review'
      ? 'bg-amber-500'
      : status === 'approved' || status === 'auto_resolved'
      ? 'bg-emerald-500'
      : 'bg-ink-muted';
  const title = status.replace(/_/g, ' ');
  return (
    <span
      title={title}
      aria-label={title}
      className={`w-2 h-2 rounded-full flex-shrink-0 ml-4 ${cls}`}
    />
  );
}


// ---------------------------------------------------------------------------
// 4. Recent activity
// ---------------------------------------------------------------------------

function RecentActivity({ events }: { events: AgentActivityEvent[] }) {
  return (
    <section>
      <SectionHeader icon={Activity} title="Recent activity" />
      {events.length === 0 ? (
        <p className="text-[12px] text-ink-muted py-2">
          No agent activity yet.
        </p>
      ) : (
        <ul>
          {events.map((e, i) => (
            <li key={i} className="border-b border-line-subtle last:border-0">
              <Link
                to={`/activity-log/${e.ticket_id}`}
                className="flex items-center h-9 gap-4 text-[12px] hover:bg-hover rounded-md px-2 -mx-2 transition-colors duration-150"
              >
                <span className="font-mono text-ink-muted w-16 flex-shrink-0 tabular-nums">
                  {formatRelative(e.timestamp)}
                </span>
                <span className="font-mono text-accent-fg w-24 flex-shrink-0 truncate">
                  {e.ticket_id}
                </span>
                <span className="font-semibold text-ink w-32 flex-shrink-0 uppercase text-[11px] tracking-wider">
                  {humanizeEventType(e.event_type)}
                </span>
                <span className="text-ink-body truncate flex-1 min-w-0">
                  {e.detail}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
      <SectionFooter to="/activity-log" label="View all in History" />
    </section>
  );
}


// ---------------------------------------------------------------------------
// Section chrome
// ---------------------------------------------------------------------------

function SectionHeader({
  icon: Icon,
  title,
}: {
  icon: React.ComponentType<{ width?: number; height?: number; strokeWidth?: number; className?: string }>;
  title: string;
}) {
  return (
    <div className="flex items-center gap-2 mb-3">
      <Icon
        width={14}
        height={14}
        strokeWidth={1.75}
        className="text-ink-muted"
      />
      <h2 className="text-[14px] font-semibold text-ink">{title}</h2>
    </div>
  );
}


function SectionFooter({ to, label }: { to: string; label: string }) {
  return (
    <div className="mt-2 flex justify-end">
      <Link
        to={to}
        className="inline-flex items-center gap-1 text-[12px] text-accent-fg hover:underline transition-colors duration-150"
      >
        {label}
        <ArrowRight width={12} height={12} strokeWidth={1.75} />
      </Link>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function humanizeEventType(t: string): string {
  return t.replace(/_/g, ' ');
}


function formatRelative(iso: string): string {
  try {
    const then = new Date(iso).getTime();
    const sec = Math.max(0, Math.floor((Date.now() - then) / 1000));
    if (sec < 60) return 'just now';
    const min = Math.floor(sec / 60);
    if (min < 60) return `${min}m ago`;
    const hr = Math.floor(min / 60);
    if (hr < 24) return `${hr}h ago`;
    const day = Math.floor(hr / 24);
    if (day < 7) return `${day}d ago`;
    const wk = Math.floor(day / 7);
    return `${wk}w ago`;
  } catch {
    return iso;
  }
}
