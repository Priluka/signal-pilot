/** Collapsible skill-execution timeline.
 *
 * Default rendering: a single summary strip ("Queried N sources · X
 * found, Y not found") that expands on click to reveal the per-call
 * rows the chat_agent emitted.
 *
 * Auto-expand / auto-collapse:
 *   • Live streaming (any executing row present)        → expanded
 *   • Transitioned from streaming to all-complete       → collapse 1s later
 *   • Loaded from history (no executing ever seen here) → collapsed
 *
 * The collapsed default keeps the eye on question → answer; the
 * expanded transient lets the operator watch the agent work, then
 * tucks itself away once everything is settled.
 */
import { useEffect, useRef, useState } from 'react';
import { Check, ChevronRight, Loader2, Search, X } from 'lucide-react';

import type { ChatEvent } from '../lib/types';


const SKILL_LABEL: Record<string, string> = {
  bmove_user_lookup: 'Bmove account',
  graylog_search: 'Graylog logs',
  skidata_session_lookup: 'SKIDATA session',
  parkis_lookup: 'ParkIS payment',
  datatrans_transaction: 'Datatrans transaction',
  jira_get_history: 'Jira ticket history',
};


function labelFor(skill: string): string {
  return SKILL_LABEL[skill] ?? skill;
}


function paramsHint(params: Record<string, unknown>): string {
  // Single-line hint of what was queried — operator's eye should pick
  // it up while scanning. We grab the first non-empty value: plate,
  // query, reference, etc. work for every skill in the registry.
  const entries = Object.entries(params).filter(
    ([, v]) => v !== '' && v !== null && v !== undefined,
  );
  if (entries.length === 0) return '';
  const [, v] = entries[0];
  return String(v);
}


function resultSummary(skill: string, result: Record<string, unknown> | null): string {
  if (!result) return '—';
  // Heuristic summaries that match what each skill returns in its data
  // dict. Falls back to a generic "OK" so the row always has SOMETHING
  // to display.
  if (skill === 'graylog_search') {
    const n = result['total_results'];
    return typeof n === 'number' ? `${n} hits` : 'OK';
  }
  if (result['found'] === false) return 'not found';
  if (result['found'] === true) return 'found';
  if ('transaction' in result || 'session' in result || 'user' in result) {
    return 'OK';
  }
  return 'OK';
}


/** Roll up the events list into the strip text. Returns the count of
 *  tool calls (one per call_id, executing+executed collapsed) and a
 *  short comma list of result categories ('2 found', '1 not found',
 *  '3 hits'). */
function summarize(events: ChatEvent[]): {
  totalCalls: number;
  hasInflight: boolean;
  parts: string[];
} {
  let totalCalls = 0;
  let hasInflight = false;
  let found = 0;
  let notFound = 0;
  let totalHits = 0;
  let otherOk = 0;
  let failed = 0;
  for (const ev of events) {
    if (
      ev.type === 'composing' ||
      ev.type === 'compacted' ||
      ev.type === 'thinking' ||
      ev.type === 'thinking_text'
    ) continue;
    if (ev.type === 'skill_executing') {
      totalCalls += 1;
      hasInflight = true;
      continue;
    }
    // skill_executed
    totalCalls += 1;
    if (!ev.ok || !ev.result) {
      failed += 1;
      continue;
    }
    const result = ev.result;
    const n = result['total_results'];
    if (typeof n === 'number') {
      totalHits += n;
      continue;
    }
    if (result['found'] === false) notFound += 1;
    else if (result['found'] === true) found += 1;
    else otherOk += 1;
  }
  const parts: string[] = [];
  if (found > 0) parts.push(`${found} found`);
  if (notFound > 0) parts.push(`${notFound} not found`);
  if (totalHits > 0) parts.push(`${totalHits} hits`);
  if (otherOk > 0 && parts.length === 0) parts.push(`${otherOk} checked`);
  if (failed > 0) parts.push(`${failed} failed`);
  return { totalCalls, hasInflight, parts };
}


export function AgenticSkillTimeline({
  events,
  isStreaming,
  sessionId,
  citationCount = 0,
}: {
  events: ChatEvent[];
  /** True while the SSE stream for the current chat is still open.
   *  Drives the auto-expand-while-running behaviour. */
  isStreaming: boolean;
  /** The chat session this timeline belongs to. Used to reset
   *  expansion state when the operator switches between chats — a
   *  freshly loaded historical chat should always start collapsed,
   *  even if the previous chat had just finished streaming. */
  sessionId: number | null;
  /** Distinct playbooks the answer actually anchored on (citation
   *  index minus hallucinated ids). 0 during streaming until the
   *  ``done`` event populates the final index. Rendered as a trailing
   *  '· N playbooks cited' segment on the summary strip so the
   *  operator gets one place to scan both data sources AND prose
   *  sources. */
  citationCount?: number;
}) {
  // Skill rows = skill_executing + skill_executed only. Compaction
  // markers and the composing signal are surfaced elsewhere; they
  // don't belong in the per-call list.
  const rows = events.filter(
    (e): e is Extract<typeof e, { type: 'skill_executing' } | { type: 'skill_executed' }> =>
      e.type === 'skill_executing' || e.type === 'skill_executed',
  );
  // Hook order matters in React — declare hooks BEFORE any early
  // return so the order stays stable across renders. The empty-rows
  // case still returns null below, just after all hooks have run.
  const [expanded, setExpanded] = useState(false);
  // Tracks whether we've EVER seen an executing row for the current
  // session. If yes, the 'transition to all-done' branch fires the
  // 1s delayed collapse. If no (historical load), we collapse
  // immediately without the delay.
  const sawExecutingRef = useRef(false);

  // Reset when the operator switches chat. Without this, switching
  // from a just-finished live chat to a historical one would inherit
  // the wasStreaming flag and apply the 1s delay incorrectly.
  const prevSessionRef = useRef<number | null>(sessionId);
  useEffect(() => {
    if (prevSessionRef.current !== sessionId) {
      sawExecutingRef.current = false;
      setExpanded(false);
      prevSessionRef.current = sessionId;
    }
  }, [sessionId]);

  const hasInflight = events.some((e) => e.type === 'skill_executing');

  // Drive expand/collapse from streaming state plus presence of
  // inflight calls. Snapshotted in a ref so the 1s collapse only
  // fires when we truly transitioned from busy → settled in THIS
  // session, not when we mounted on a finished historical chat.
  useEffect(() => {
    if (isStreaming || hasInflight) {
      sawExecutingRef.current = true;
      setExpanded(true);
      return;
    }
    if (sawExecutingRef.current && rows.length > 0) {
      // Just finished — keep the rows visible for a beat so the
      // operator registers the final results, then tuck away.
      const timer = setTimeout(() => setExpanded(false), 1000);
      return () => clearTimeout(timer);
    }
    // Historical / cold load — start collapsed, no delay.
    setExpanded(false);
  }, [isStreaming, hasInflight, rows.length]);

  if (rows.length === 0) return null;

  const { totalCalls, parts } = summarize(events);
  const summaryText =
    `Queried ${totalCalls} ${totalCalls === 1 ? 'source' : 'sources'}` +
    (parts.length > 0 ? ` · ${parts.join(', ')}` : '') +
    (citationCount > 0
      ? ` · ${citationCount} playbook${citationCount === 1 ? '' : 's'} cited`
      : '');

  return (
    <div className={expanded ? 'bg-app rounded-lg p-3 mb-4' : 'mb-4'}>
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="w-full text-left flex items-center gap-2 py-2 px-3 rounded-lg hover:bg-hover cursor-pointer transition-colors text-[12px] text-ink-muted"
      >
        <Search width={14} height={14} className="shrink-0" />
        <span>{summaryText}</span>
        {hasInflight && (
          <Loader2
            width={12}
            height={12}
            className="animate-spin text-ink-muted shrink-0"
          />
        )}
        <ChevronRight
          width={14}
          height={14}
          className={`ml-auto shrink-0 transition-transform ${
            expanded ? 'rotate-90' : ''
          }`}
        />
      </button>
      {expanded && (
        <ol className="pl-2 mt-2 space-y-1">
          {rows.map((ev, i) => (
            // ``rows`` is filtered to skill_executing | skill_executed
            // already — composing markers are dropped above. Use
            // call_id when present (stable across the executing →
            // executed swap), else fall back to skill+index.
            <SkillRow
              key={ev.call_id ?? `${ev.skill}-${i}`}
              ev={ev}
            />
          ))}
        </ol>
      )}
    </div>
  );
}


type SkillEvent = Extract<
  ChatEvent,
  { type: 'skill_executing' } | { type: 'skill_executed' }
>;


function SkillRow({ ev }: { ev: SkillEvent }) {
  const [expanded, setExpanded] = useState(false);

  const isExecuting = ev.type === 'skill_executing';
  const ok = ev.type === 'skill_executed' && ev.ok;
  const failed = ev.type === 'skill_executed' && !ev.ok;
  const Icon = isExecuting ? Loader2 : failed ? X : Check;
  const iconClass = isExecuting
    ? 'animate-spin text-ink-muted'
    : failed
    ? 'text-red-500'
    : 'text-emerald-500';

  const hint = paramsHint(ev.params);
  const summary =
    ev.type === 'skill_executed' ? resultSummary(ev.skill, ev.result) : 'running';

  return (
    <li>
      <div
        className={`flex items-center gap-2 text-[12px] ${
          isExecuting ? 'text-ink-muted' : 'text-ink-body'
        }`}
      >
        <Search width={12} height={12} className="text-ink-muted shrink-0" />
        <span className="font-medium">{labelFor(ev.skill)}</span>
        {hint && (
          <code className="text-[11px] font-mono text-ink-muted bg-hover/60 rounded px-1">
            {hint}
          </code>
        )}
        <span className="text-ink-muted">·</span>
        <Icon width={12} height={12} className={`${iconClass} shrink-0`} />
        <span
          className={
            ok ? 'text-emerald-700 dark:text-emerald-400'
              : failed ? 'text-red-600 dark:text-red-400'
              : 'text-ink-muted'
          }
        >
          {summary}
        </span>
        {ev.type === 'skill_executed' && (
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="ml-auto inline-flex items-center text-[11px] text-ink-muted hover:text-ink-body transition-colors"
          >
            <ChevronRight
              width={12}
              height={12}
              className={`transition-transform ${expanded ? 'rotate-90' : ''}`}
            />
            {expanded ? 'hide' : 'details'}
          </button>
        )}
      </div>
      {expanded && ev.type === 'skill_executed' && (
        <div className="ml-5 mt-1 mb-2 grid grid-cols-[60px_1fr] gap-x-2 gap-y-0.5 text-[11px] font-mono text-ink-muted">
          <dt className="text-right">params</dt>
          <dd className="text-ink-body break-all whitespace-pre-wrap">
            {JSON.stringify(ev.params, null, 2)}
          </dd>
          {ev.result !== null && (
            <>
              <dt className="text-right">result</dt>
              <dd className="text-ink-body break-all whitespace-pre-wrap">
                {JSON.stringify(ev.result, null, 2)}
              </dd>
            </>
          )}
          {ev.error && (
            <>
              <dt className="text-right">error</dt>
              <dd className="text-red-600 dark:text-red-400 break-all whitespace-pre-wrap">
                {ev.error}
              </dd>
            </>
          )}
          {ev.elapsed_ms > 0 && (
            <>
              <dt className="text-right">took</dt>
              <dd>{ev.elapsed_ms} ms</dd>
            </>
          )}
        </div>
      )}
    </li>
  );
}
