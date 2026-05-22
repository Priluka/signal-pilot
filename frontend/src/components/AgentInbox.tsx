/** Left column of the Inbox — sorted list of agent-processed tickets.
 *
 * Linear-style two-pane reading list: 360px wide, subtle right border,
 * compact rows. Unread tickets (no operator decision yet) render the
 * title in semibold ink; rows the operator has already acted on drop to
 * regular weight and muted color.
 */
import { Link, useParams } from 'react-router-dom';

import type {
  AgentSessionSummary,
  AgentStatus,
  TicketSummary,
} from '../lib/types';

import { AgentModeChip } from './AgentModeChip';
import { AgentStatusPill, statusPriority } from './AgentStatusPill';


export interface InboxRow {
  ticket: TicketSummary;
  session: AgentSessionSummary | undefined;
}


interface Props {
  rows: InboxRow[];
  loading: boolean;
  error: string | null;
}


function isUnread(session: AgentSessionSummary | undefined): boolean {
  // 'Read' means the operator (or the agent in autonomous) has acted —
  // anything still awaiting a decision stays bold.
  if (!session) return true;
  if (session.feedback_status) return false;
  return true;
}


export function AgentInbox({ rows, loading, error }: Props) {
  const { ticketKey } = useParams();

  return (
    <div className="flex flex-col flex-1 min-h-0">
      <div className="px-4 py-2 text-xs text-ink-muted">
        {rows.length} ticket{rows.length === 1 ? '' : 's'}
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {loading && (
          <div className="px-4 py-6 text-sm text-ink-muted">Loading inbox…</div>
        )}
        {error && (
          <div className="px-4 py-6 text-sm text-red-600">{error}</div>
        )}
        {!loading && !error && rows.length === 0 && (
          <div className="px-4 py-6 text-sm text-ink-muted">
            No tickets in this view.
          </div>
        )}
        <ul>
          {rows.map(({ ticket: t, session: s }) => {
            const isActive = ticketKey === t.key;
            const status: AgentStatus = s?.derived_status ?? 'pending';
            const unread = isUnread(s);
            return (
              <li key={t.key}>
                <Link
                  to={`/inbox/${t.key}`}
                  className={`block mx-2 px-3 py-3 rounded-lg transition-colors duration-150 ${
                    isActive ? 'bg-hover' : 'hover:bg-hover'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="flex items-center gap-1.5 min-w-0">
                      <span
                        aria-hidden
                        className={`inline-block w-1 h-1 rounded-full shrink-0 ${
                          unread ? 'bg-accent' : 'bg-transparent'
                        }`}
                      />
                      <span
                        className={`text-2xs font-mono tabular-nums ${
                          unread
                            ? 'text-ink font-semibold'
                            : 'text-[#838383]'
                        }`}
                      >
                        {t.key}
                      </span>
                    </span>
                    <AgentStatusPill status={status} />
                  </div>
                  <div
                    className={`mt-1 text-[13px] leading-snug line-clamp-2 pl-3 ${
                      unread
                        ? 'font-semibold text-ink'
                        : 'font-normal text-[#858585]'
                    }`}
                  >
                    {t.summary}
                  </div>
                  <div
                    className={`mt-1.5 pl-3 flex items-center gap-2 text-2xs ${
                      unread ? 'text-ink-muted' : 'text-[#9a9a9a]'
                    }`}
                  >
                    {s?.processed_mode && (
                      <AgentModeChip mode={s.processed_mode} size="sm" />
                    )}
                    {s?.drafted_at && <span>{formatRelative(s.drafted_at)}</span>}
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}


export function sortInbox(rows: InboxRow[]): InboxRow[] {
  // Email-inbox model: sort strictly by when the ticket arrived
  // (``ticket.created_at``), newest first. Operator actions like approve
  // / reject MUST NOT bump a row up the list — replying to ticket #5
  // shouldn't make it leap to the top. Falls back to session timestamps
  // only when the source didn't provide a created_at.
  return [...rows].sort((a, b) => {
    const ta = a.ticket.created_at ?? a.session?.updated_at ?? '';
    const tb = b.ticket.created_at ?? b.session?.updated_at ?? '';
    return tb.localeCompare(ta);
  });
}


function formatRelative(iso: string): string {
  // Compact relative timestamps for the inbox row: "30s ago", "5m ago",
  // "2h ago", "3d ago", "2w ago", then drops to month+day for anything
  // older than a year so the row never balloons.
  try {
    const then = new Date(iso).getTime();
    const now = Date.now();
    const sec = Math.max(0, Math.floor((now - then) / 1000));
    if (sec < 5) return 'just now';
    if (sec < 60) return `${sec}s ago`;
    const min = Math.floor(sec / 60);
    if (min < 60) return `${min}m ago`;
    const hr = Math.floor(min / 60);
    if (hr < 24) return `${hr}h ago`;
    const day = Math.floor(hr / 24);
    if (day < 7) return `${day}d ago`;
    const wk = Math.floor(day / 7);
    if (wk < 5) return `${wk}w ago`;
    const mo = Math.floor(day / 30);
    if (mo < 12) return `${mo}mo ago`;
    return new Date(iso).toLocaleDateString(undefined, {
      month: 'short',
      day: '2-digit',
      year: 'numeric',
    });
  } catch {
    return iso;
  }
}
