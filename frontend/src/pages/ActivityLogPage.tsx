/** Activity Log — Linear-style issues list.
 *
 * Full-width, flat, compact. The page is a single audit stream grouped
 * by ticket (or by playbook for suggestion events, or by 'config' for
 * global config changes). Each group is a single row that expands in
 * place to show its event timeline. No cards, no right-side detail
 * pane — the row IS the detail.
 */
import { Fragment, useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, ChevronRight, Settings } from 'lucide-react';

import { listAgentActivity, listAgentSessions } from '../lib/api';
import type {
  AgentActivityEvent,
  AgentEventType,
  AgentSessionSummary,
} from '../lib/types';


type TypeFilter = AgentEventType | 'all' | 'suggestions';


const TYPE_FILTERS: Array<{ key: TypeFilter; label: string }> = [
  { key: 'all', label: 'All' },
  { key: 'classified', label: 'Classified' },
  { key: 'retrieved', label: 'Retrieved' },
  { key: 'drafted', label: 'Drafted' },
  { key: 'approved', label: 'Approved' },
  { key: 'rejected', label: 'Rejected' },
  { key: 'skipped', label: 'Skipped' },
  { key: 'suggestions', label: 'Suggestions' },
  { key: 'config_change', label: 'Config' },
];


function matchesFilter(eventType: AgentEventType, filter: TypeFilter): boolean {
  if (filter === 'all') return true;
  if (filter === 'suggestions') return eventType.startsWith('suggestion_');
  return eventType === filter;
}


function isSuggestionEvent(eventType: AgentEventType): boolean {
  return eventType.startsWith('suggestion_');
}


// ---------------------------------------------------------------------------
// Color mapping
// ---------------------------------------------------------------------------

// Row-level status dot (collapsed row). Reads the group's session state
// rather than any specific event so the dot reflects "where does this
// ticket stand right now", not "what was the last thing logged".
function rowStatusDot(group: TicketGroup): string {
  const status = group.session?.derived_status;
  switch (status) {
    case 'escalated':
    case 'rejected':
      return 'bg-red-500';
    case 'needs_review':
      return 'bg-amber-500';
    case 'approved':
    case 'auto_resolved':
      return 'bg-emerald-500';
    case 'auto_drafted':
      return 'bg-blue-500';
    case 'skipped':
      return 'bg-gray-400';
    case 'in_progress':
      return 'bg-indigo-500';
    default:
      return 'bg-gray-300';
  }
}


// Event-level dot (expanded sub-rows). One per AgentEventType.
const EVENT_DOT: Record<AgentEventType, string> = {
  classified: 'bg-blue-500',
  retrieved: 'bg-indigo-500',
  drafted: 'bg-amber-500',
  approved: 'bg-emerald-500',
  edited: 'bg-indigo-500',
  rejected: 'bg-red-500',
  skipped: 'bg-gray-400',
  // Suggestions and config use icons, not dots — values here just keep
  // the Record exhaustive.
  suggestion_created: 'bg-purple-500',
  suggestion_accepted: 'bg-purple-600',
  suggestion_rejected: 'bg-purple-400',
  config_change: 'bg-gray-400',
};


function labelForEvent(eventType: AgentEventType): string {
  switch (eventType) {
    case 'edited':
      return 'approved (edited)';
    case 'suggestion_created':
      return 'suggestion · created';
    case 'suggestion_accepted':
      return 'suggestion · accepted';
    case 'suggestion_rejected':
      return 'suggestion · rejected';
    case 'config_change':
      return 'config · changed';
    default:
      return eventType;
  }
}


// ---------------------------------------------------------------------------
// Grouping
// ---------------------------------------------------------------------------

interface TicketGroup {
  ticket_id: string;
  events: AgentActivityEvent[];
  latest_at: string;
  session: AgentSessionSummary | undefined;
  /** True when all events in the group are suggestion lifecycle events —
   * the row points at a playbook rather than a ticket. */
  isPlaybookOnly: boolean;
  /** True when ticket_id is the global config pseudo-id. */
  isGlobalConfig: boolean;
}


// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function ActivityLogPage() {
  const [events, setEvents] = useState<AgentActivityEvent[]>([]);
  const [sessions, setSessions] = useState<AgentSessionSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const [typeFilter, setTypeFilter] = useState<TypeFilter>('all');
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const refresh = useCallback(async () => {
    try {
      const [a, s] = await Promise.all([listAgentActivity(), listAgentSessions()]);
      setEvents(a);
      setSessions(s);
    } catch {
      /* swallow — agent-sessions-changed will retrigger */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const handler = () => refresh();
    window.addEventListener('agent-sessions-changed', handler);
    return () => window.removeEventListener('agent-sessions-changed', handler);
  }, [refresh]);

  const sessionByTicketId = useMemo(() => {
    const m = new Map<string, AgentSessionSummary>();
    for (const s of sessions) m.set(s.ticket_id, s);
    return m;
  }, [sessions]);

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
      const isPlaybookOnly =
        list.length > 0 &&
        list.every(
          (e) => isSuggestionEvent(e.event_type) || e.event_type === 'config_change',
        );
      out.push({
        ticket_id,
        events: list,
        latest_at,
        session: sessionByTicketId.get(ticket_id),
        isPlaybookOnly,
        isGlobalConfig: ticket_id === 'config',
      });
    }
    out.sort((a, b) => b.latest_at.localeCompare(a.latest_at));
    return out;
  }, [events, sessionByTicketId]);

  const filteredGroups = useMemo(() => {
    if (typeFilter === 'all') return groups;
    return groups.filter((g) =>
      g.events.some((e) => matchesFilter(e.event_type, typeFilter)),
    );
  }, [groups, typeFilter]);

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
      {/* Header */}
      <header className="h-12 px-4 flex items-center border-b border-line-subtle shrink-0">
        <h1 className="text-base font-semibold text-ink tracking-tight">Activity Log</h1>
      </header>

      {/* Filter chips */}
      <div className="px-4 py-2 border-b border-line-subtle flex items-center gap-1 overflow-x-auto scrollbar-thin">
        {TYPE_FILTERS.map((f) => {
          const active = typeFilter === f.key;
          return (
            <button
              key={f.key}
              type="button"
              onClick={() => setTypeFilter(f.key)}
              className={`px-2.5 py-1 rounded-md text-[12px] font-medium whitespace-nowrap transition-colors duration-150 cursor-pointer ${
                active
                  ? 'bg-active text-ink'
                  : 'text-ink-muted hover:text-ink-body hover:bg-hover'
              }`}
            >
              {f.label}
            </button>
          );
        })}
      </div>

      {/* Event list — flat, full width */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {loading ? (
          <div className="px-4 py-6 text-sm text-ink-muted">Loading activity…</div>
        ) : filteredGroups.length === 0 ? (
          <EmptyState />
        ) : (
          <ul>
            {filteredGroups.map((g) => (
              <ActivityRow
                key={g.ticket_id}
                group={g}
                expanded={expanded.has(g.ticket_id)}
                onToggle={() => toggleExpanded(g.ticket_id)}
              />
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Row
// ---------------------------------------------------------------------------

function ActivityRow({
  group,
  expanded,
  onToggle,
}: {
  group: TicketGroup;
  expanded: boolean;
  onToggle: () => void;
}) {
  const confidence = group.session?.classification_confidence ?? null;

  return (
    <li>
      <div
        onClick={onToggle}
        className="flex items-center px-4 h-10 hover:bg-hover cursor-pointer transition-colors duration-150 border-b border-line-subtle"
        role="button"
        aria-expanded={expanded}
      >
        <ChevronRight
          width={14}
          height={14}
          strokeWidth={2}
          className={`text-ink-muted shrink-0 transition-transform duration-150 ${
            expanded ? 'rotate-90' : ''
          }`}
        />
        <TicketIdLink group={group} />
        <StatusOrIcon group={group} />
        <span className="text-[12px] font-mono text-ink-muted ml-3 w-20 shrink-0">
          {formatTimeOfDay(group.latest_at)}
        </span>
        {!group.isPlaybookOnly && confidence != null && (
          <span className="text-[12px] font-mono text-ink-muted ml-2">
            conf {confidence.toFixed(2)}
          </span>
        )}
        <span className="text-[12px] text-ink-muted ml-auto shrink-0">
          {group.events.length} event{group.events.length === 1 ? '' : 's'}
        </span>
      </div>

      {expanded && (
        <ExpandedTimeline group={group} />
      )}
    </li>
  );
}


function TicketIdLink({ group }: { group: TicketGroup }) {
  const baseClass =
    'text-[13px] font-medium font-mono ml-2 w-24 shrink-0 truncate transition-colors duration-150';
  if (group.isGlobalConfig) {
    return (
      <span className={`${baseClass} text-ink-muted`}>{group.ticket_id}</span>
    );
  }
  if (group.isPlaybookOnly) {
    return (
      <Link
        to={`/knowledge/${group.ticket_id}`}
        onClick={(e) => e.stopPropagation()}
        className={`${baseClass} text-purple-700 dark:text-purple-300 hover:underline`}
        title="Open playbook"
      >
        {group.ticket_id}
      </Link>
    );
  }
  return (
    <Link
      to={`/inbox/${group.ticket_id}`}
      onClick={(e) => e.stopPropagation()}
      className={`${baseClass} text-accent-fg hover:underline`}
    >
      {group.ticket_id}
    </Link>
  );
}


function StatusOrIcon({ group }: { group: TicketGroup }) {
  if (group.isGlobalConfig) {
    return (
      <span className="ml-2 flex items-center gap-1.5">
        <Settings width={13} height={13} strokeWidth={1.75} className="text-ink-muted" />
        <span className="text-[11px] font-mono bg-hover text-ink-muted rounded px-1.5 py-0.5">
          config
        </span>
      </span>
    );
  }
  if (group.isPlaybookOnly) {
    return (
      <span className="ml-2 text-[11px] font-mono bg-hover text-purple-700 dark:text-purple-300 rounded px-1.5 py-0.5">
        playbook
      </span>
    );
  }
  return (
    <span
      title={group.session?.derived_status ?? 'pending'}
      className={`ml-2 w-2 h-2 rounded-full shrink-0 ${rowStatusDot(group)}`}
    />
  );
}


function ExpandedTimeline({ group }: { group: TicketGroup }) {
  const showAwaiting =
    group.session?.recommended_action &&
    !group.session.feedback_status &&
    group.session.derived_status !== 'auto_resolved' &&
    group.session.derived_status !== 'skipped';

  return (
    <div className="border-b border-line-subtle bg-hover pl-12 pr-4 py-3">
      <ul className="space-y-px">
        {group.events.map((e, i) => {
          // Show a date divider when the day rolls over between events.
          // Without this, events at different dates with closer
          // times-of-day read as out-of-order ("5:59 PM" sitting
          // visually below "6:01 PM" even though it's days later).
          const dayKey = e.timestamp.slice(0, 10); // YYYY-MM-DD
          const prevDayKey =
            i > 0 ? group.events[i - 1].timestamp.slice(0, 10) : null;
          const showDay = prevDayKey !== dayKey;
          return (
          <Fragment key={`${e.timestamp}-${e.event_type}-${i}`}>
          {showDay && <DayDivider iso={e.timestamp} />}
          <li
            className="py-1.5"
          >
            <div className="flex items-center gap-3">
              <span className="text-[11px] font-mono text-ink-muted w-24 shrink-0 tabular-nums">
                {formatTime(e.timestamp)}
              </span>
              <EventIcon eventType={e.event_type} />
              <span
                className={`text-[12px] font-medium w-32 shrink-0 ${
                  e.event_type === 'config_change'
                    ? 'text-ink-body'
                    : isSuggestionEvent(e.event_type)
                    ? 'text-purple-700 dark:text-purple-300'
                    : 'text-ink'
                }`}
              >
                {labelForEvent(e.event_type)}
              </span>
              <span className="text-[12px] text-ink-body leading-relaxed truncate">
                {e.detail}
              </span>
            </div>
            {e.diff && (e.diff.old || e.diff.new) && (
              <SuggestionDiffLines diff={e.diff} />
            )}
          </li>
          </Fragment>
          );
        })}
        {showAwaiting && (
          <li className="flex items-center gap-3 py-1.5">
            <span className="text-[11px] font-mono text-ink-muted w-24 shrink-0">—</span>
            <span className="w-1.5 h-1.5 rounded-full bg-line shrink-0 animate-pulse" />
            <span className="text-[12px] font-medium text-ink-muted w-32 shrink-0">
              awaiting
            </span>
            <span className="text-[12px] text-ink-muted italic">
              Operator review pending
            </span>
          </li>
        )}
      </ul>
    </div>
  );
}


function DayDivider({ iso }: { iso: string }) {
  // Inline date header inserted between events when the day rolls over.
  // Linear-style: hairline border on either side of a small mono label
  // — visually quiet but disambiguates same-time-of-day collisions
  // across days.
  return (
    <li className="flex items-center gap-3 pt-2 pb-1 select-none" aria-hidden="true">
      <span className="w-24 shrink-0" />
      <span className="flex items-center gap-2 flex-1 min-w-0">
        <span className="h-px bg-line-subtle flex-1" />
        <span className="text-[10px] uppercase tracking-wider font-medium text-ink-muted font-mono shrink-0">
          {formatDay(iso)}
        </span>
        <span className="h-px bg-line-subtle flex-1" />
      </span>
    </li>
  );
}


function SuggestionDiffLines({ diff }: { diff: { old: string | null; new: string | null } }) {
  // Indent past the time (w-24 = 96px) + gap-3 (12px) + dot (~6-11px)
  // + gap-3 (12px) so the diff lines anchor under the event-type label
  // column. Mono font + colour-coded chevron prefix matches the diff
  // styling in Suggestions view; truncate keeps long edits one-line.
  return (
    <div className="pl-[7.75rem] mt-1 space-y-0.5">
      {diff.old && (
        <div className="text-[11px] font-mono text-red-600 dark:text-red-400 truncate max-w-[640px]">
          <span className="select-none mr-1">−</span>
          <span className="line-through opacity-70">{diff.old}</span>
        </div>
      )}
      {diff.new && (
        <div className="text-[11px] font-mono text-emerald-600 dark:text-emerald-400 truncate max-w-[640px]">
          <span className="select-none mr-1">+</span>
          <span>{diff.new}</span>
        </div>
      )}
    </div>
  );
}


function EventIcon({ eventType }: { eventType: AgentEventType }) {
  if (eventType === 'config_change') {
    return <Settings width={11} height={11} strokeWidth={1.75} className="text-ink-muted shrink-0" />;
  }
  if (isSuggestionEvent(eventType)) {
    const tone =
      eventType === 'suggestion_accepted'
        ? 'bg-purple-600'
        : eventType === 'suggestion_rejected'
        ? 'bg-purple-400'
        : 'bg-purple-500';
    return <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${tone}`} />;
  }
  return <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${EVENT_DOT[eventType]}`} />;
}


// ---------------------------------------------------------------------------
// Atoms
// ---------------------------------------------------------------------------

function EmptyState() {
  return (
    <div className="h-full flex flex-col items-center justify-center px-6 text-center">
      <Activity width={40} height={40} strokeWidth={1.5} className="text-ink-muted opacity-50 mb-3" />
      <p className="text-[13px] text-ink-muted">No events found</p>
      <p className="mt-0.5 text-[12px] text-ink-muted opacity-70">Try a different filter</p>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Date helpers
// ---------------------------------------------------------------------------

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


function formatDay(iso: string): string {
  try {
    const d = new Date(iso);
    const today = new Date();
    const sameYear = d.getFullYear() === today.getFullYear();
    const sameDay =
      sameYear &&
      d.getMonth() === today.getMonth() &&
      d.getDate() === today.getDate();
    if (sameDay) return 'Today';
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: '2-digit',
      year: sameYear ? undefined : 'numeric',
    });
  } catch {
    return iso;
  }
}
