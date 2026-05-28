/** Unified agent execution timeline.
 *
 * Replaces the separate ClassificationCard / PlaybookCard / DraftSection /
 * ActionApproval / PlannerStatusBanner stack with a single vertical
 * timeline. Each step is one node on the line:
 *
 *   Classified           ✓ (always)
 *   Retrieved playbook   ✓ (when retrieval ran)
 *   Draft generated      ✓ (when draft ran)
 *   --- skills path ---
 *     Planner started    ✓
 *     [executed skill]   ✓  one per history row, chrono order
 *     [skill_name]       ⏸  one per pending row, awaiting approval
 *     Agent finished     ✓ / Agent failed ✗ / Hit iteration cap ✗
 *   --- legacy path ---
 *     Awaiting review    ⏸  draft + Approve / Edit / Reject buttons
 *     OR Decided         ✓/✗ once feedback_status is set
 *
 * Dot states: emerald (done), amber pulse (awaiting), slate (pending),
 * red (error). The connecting vertical line is drawn per-step so it
 * naturally ends at the last node.
 */
import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Bot,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Inbox,
  Loader2,
  MessageSquarePlus,
  Pencil,
  Play,
  Search,
  Tag,
  X,
  type LucideProps,
} from 'lucide-react';

import type {
  AgentSessionDetail,
  AuditEntry,
  PendingAction,
} from '../lib/types';


type DotState = 'done' | 'awaiting' | 'pending' | 'error';
type LucideIcon = React.ComponentType<LucideProps>;


export interface AgentTimelineProps {
  /** Null when this ticket has never been processed — the timeline
   *  renders a single 'Ready to process' starter step instead of the
   *  full Classified → Retrieved → Draft sequence. */
  session: AgentSessionDetail | null;
  source: 'local' | 'jira';
  pendingActions: PendingAction[];
  history: AuditEntry[];
  busyActionId: string | null;
  onApproveAction: (id: string) => void | Promise<void>;
  onRejectAction: (id: string) => void | Promise<void>;

  // --- initial-process controls (no session yet) ---
  processing: boolean;
  processError: string | null;
  onProcess: () => void;

  // --- legacy draft-decision controls (no-skills path) ---
  editing: boolean;
  editedText: string;
  hasEdits: boolean;
  submitting: boolean;
  submitError: string | null;
  isActionable: boolean;
  onStartEdit: () => void;
  onCancelEdit: () => void;
  onEditedTextChange: (v: string) => void;
  onDraftApprove: () => void;
  onDraftReject: () => void;
}


export function AgentTimeline(props: AgentTimelineProps) {
  const { session } = props;

  return (
    <section>
      <h2 className="text-[14px] font-semibold text-ink mb-4">
        Agent execution timeline
      </h2>
      <ol className="relative">
        {session ? (
          <SessionBranches {...props} session={session} />
        ) : (
          <ReadyToProcessStep {...props} />
        )}
      </ol>
    </section>
  );
}


function SessionBranches(
  props: AgentTimelineProps & { session: AgentSessionDetail },
) {
  const { session } = props;
  // Skills path engages when ANY skills-layer signal exists: an audit
  // row, a pending tool_use, or a planner_status the agent_runner
  // already persisted. Without these we render the legacy draft flow.
  const skillsActive =
    props.pendingActions.length > 0 ||
    props.history.length > 0 ||
    !!session.planner_status;
  return (
    <>
      <ClassifiedStep session={session} />
      <RetrievedStep session={session} />
      <DraftStep session={session} />
      {skillsActive ? <SkillsBranch {...props} /> : <LegacyBranch {...props} />}
    </>
  );
}


// ===========================================================================
// Starter step — no session yet
// ===========================================================================


function ReadyToProcessStep(props: AgentTimelineProps) {
  // Local-source tickets are queued by the background batch runner; the
  // operator can't kick them off ad hoc the same way Jira's on-demand
  // /jira/process endpoint allows. We surface the right copy + the
  // right (or no) call-to-action accordingly.
  const isJira = props.source === 'jira';
  return (
    <Step
      state="pending"
      icon={isJira ? Play : Inbox}
      title={isJira ? 'Ready to process' : 'Queued for batch'}
      timestamp={null}
      forceExpanded
      last
      expandedContent={
        <div className="space-y-3">
          <p className="text-[13px] text-ink-body">
            {isJira
              ? "This ticket hasn't been processed yet. Click below to run classify → retrieve → draft (and the planner, if the matched playbook has skills enabled)."
              : "The background agent batch hasn't reached this ticket yet — it'll appear here once classify/retrieve/draft finishes."}
          </p>
          {isJira && (
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={props.onProcess}
                disabled={props.processing}
                className="inline-flex items-center gap-1.5 px-4 h-9 text-[13px] font-medium text-white bg-accent rounded-md hover:bg-accent-hover transition-colors duration-150 disabled:opacity-60"
              >
                {props.processing ? (
                  <>
                    <Loader2 width={13} height={13} className="animate-spin" />
                    Working…
                  </>
                ) : (
                  <>
                    <Play width={13} height={13} strokeWidth={2} />
                    Process with agent
                  </>
                )}
              </button>
              {props.processError && (
                <span className="text-[11px] text-red-600 dark:text-red-400 break-words">
                  {props.processError}
                </span>
              )}
            </div>
          )}
        </div>
      }
    />
  );
}


// ===========================================================================
// Always-on steps
// ===========================================================================


function ClassifiedStep({ session }: { session: AgentSessionDetail }) {
  const cls = session.classification;
  if (!cls && !session.classified_at) {
    return (
      <Step
        state="pending"
        icon={Tag}
        title="Classify…"
        timestamp={null}
        subtitle="waiting for the classifier"
      />
    );
  }
  return (
    <Step
      state="done"
      icon={Tag}
      title="Classified"
      timestamp={session.classified_at}
      subtitle={
        cls ? `${cls.label} · confidence ${cls.confidence.toFixed(2)}` : '—'
      }
      expandable={!!cls?.reason}
      expandedContent={
        cls?.reason ? (
          <p className="text-[12px] text-ink-body leading-relaxed">
            {cls.reason}
          </p>
        ) : null
      }
    />
  );
}


function RetrievedStep({ session }: { session: AgentSessionDetail }) {
  if (!session.retrieval || !session.draft_playbook_id) return null;
  const hit = session.retrieval.hits.find(
    (h) => h.playbook_id === session.draft_playbook_id,
  );
  return (
    <Step
      state="done"
      icon={Search}
      title="Retrieved playbook"
      timestamp={session.retrieved_at}
      subtitle={
        <span className="text-[13px] text-ink-body">
          <Link
            to={`/knowledge/${session.draft_playbook_id}`}
            className="text-accent-fg hover:underline"
          >
            {hit?.title ?? session.draft_playbook_id}
          </Link>
          {hit?.score != null && (
            <span className="text-ink-muted">
              {' '}· score {hit.score.toFixed(2)}
            </span>
          )}
        </span>
      }
    />
  );
}


function DraftStep({ session }: { session: AgentSessionDetail }) {
  if (!session.draft) return null;
  const action = session.draft.recommended_action.replace(/_/g, ' ');
  return (
    <Step
      state="done"
      icon={Pencil}
      title="Draft generated"
      timestamp={session.drafted_at}
      subtitle={`recommended: ${action}`}
      expandable
      expandedContent={
        <div className="space-y-2">
          <pre className="text-[12px] text-ink-body whitespace-pre-wrap font-sans leading-relaxed bg-app rounded-md px-3 py-2 border border-line-subtle max-h-72 overflow-y-auto scrollbar-thin">
            {session.draft.draft}
          </pre>
          {session.draft.rationale && (
            <p className="text-[11px] text-ink-muted italic">
              {session.draft.rationale}
            </p>
          )}
        </div>
      }
    />
  );
}


// ===========================================================================
// Skills branch — planner + executed skills + pending skills + outcome
// ===========================================================================


function SkillsBranch(props: AgentTimelineProps) {
  const { session, pendingActions, history } = props;
  const sortedHistory = useMemo(
    () => [...history].sort((a, b) => a.decided_at.localeCompare(b.decided_at)),
    [history],
  );
  return (
    <>
      <Step
        state="done"
        icon={Bot}
        title="Planner started"
        timestamp={session.drafted_at}
        subtitle={`${session.processed_mode ?? 'assisted'} mode`}
      />
      {sortedHistory.map((entry) => (
        <HistoryStep key={`hist-${entry.id}`} entry={entry} />
      ))}
      {pendingActions.map((pa) => (
        <PendingStep
          key={`pend-${pa.id}`}
          action={pa}
          busy={props.busyActionId === pa.id}
          onApprove={() => props.onApproveAction(pa.id)}
          onReject={() => props.onRejectAction(pa.id)}
        />
      ))}
      <PlannerOutcomeStep
        status={session.planner_status ?? null}
        error={session.planner_error ?? null}
        history={sortedHistory}
        hasPending={pendingActions.length > 0}
      />
    </>
  );
}


function HistoryStep({ entry }: { entry: AuditEntry }) {
  const isReject = entry.outcome === 'rejected';
  const isFail = !entry.ok && !isReject;
  const state: DotState = isReject || isFail ? 'error' : 'done';
  const icon: LucideIcon = isReject ? X : isFail ? X : Check;
  const title = isReject
    ? `${entry.skill_name} rejected`
    : isFail
    ? `${entry.skill_name} failed`
    : `${entry.skill_name} executed`;
  const subtitle = isReject
    ? entry.error || 'rejected by operator'
    : isFail
    ? entry.error || 'skill error'
    : briefResult(entry.result_data);
  return (
    <Step
      state={state}
      icon={icon}
      title={title}
      timestamp={entry.decided_at}
      subtitle={subtitle}
      expandable
      expandedContent={
        <div className="space-y-2 text-[12px]">
          <ParamsBlock label="parameters" input={entry.skill_input} />
          {entry.result_data && (
            <ParamsBlock label="result" input={entry.result_data} />
          )}
          {entry.error && (
            <div className="text-red-600 dark:text-red-400 font-mono text-[11px]">
              {entry.error}
            </div>
          )}
          {entry.decided_by && (
            <div className="text-[11px] text-ink-muted">
              decided by {entry.decided_by} · iter {entry.iteration} · {entry.mode}
            </div>
          )}
        </div>
      }
    />
  );
}


function PendingStep({
  action,
  busy,
  onApprove,
  onReject,
}: {
  action: PendingAction;
  busy: boolean;
  onApprove: () => void;
  onReject: () => void;
}) {
  const bodyPreview = pickBodyPreview(action.skill_input);
  return (
    <Step
      state="awaiting"
      icon={MessageSquarePlus}
      title={action.skill_name}
      timestamp={action.created_at}
      subtitle={`iter ${action.iteration} · ${action.mode}`}
      forceExpanded
      expandedContent={
        <div className="space-y-3">
          {bodyPreview && (
            <pre className="text-[12px] text-ink-body whitespace-pre-wrap font-sans leading-relaxed bg-app rounded-md px-3 py-2 border-l-[3px] border-amber-400 max-h-44 overflow-y-auto scrollbar-thin">
              {bodyPreview}
            </pre>
          )}
          <ParamsBlock label="parameters" input={action.skill_input} dense />
          <div className="flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onReject}
              disabled={busy}
              className="inline-flex items-center gap-1 px-3 h-8 text-[12px] font-medium rounded-md border border-red-200 text-red-600 hover:bg-red-50 dark:border-red-800/60 dark:text-red-400 dark:hover:bg-red-950/40 transition-colors duration-150 disabled:opacity-60"
            >
              <X width={12} height={12} strokeWidth={2} />
              Reject
            </button>
            <button
              type="button"
              onClick={onApprove}
              disabled={busy}
              className="inline-flex items-center gap-1 px-3 h-8 text-[12px] font-medium rounded-md bg-accent text-white hover:bg-accent-hover transition-colors duration-150 disabled:opacity-60"
            >
              {busy ? (
                <Loader2 width={12} height={12} className="animate-spin" />
              ) : (
                <Check width={12} height={12} strokeWidth={2} />
              )}
              {busy ? 'Working…' : 'Approve & run'}
            </button>
          </div>
        </div>
      }
    />
  );
}


function PlannerOutcomeStep({
  status,
  error,
  history,
  hasPending,
}: {
  status: AgentSessionDetail['planner_status'] | null;
  error: string | null;
  history: AuditEntry[];
  hasPending: boolean;
}) {
  if (hasPending) return null; // still in flight; show outcome when settled
  if (status === 'failed') {
    return (
      <Step
        state="error"
        icon={X}
        title="Agent loop failed"
        subtitle={error || 'unknown error'}
        timestamp={null}
        last
      />
    );
  }
  if (status === 'max_iterations') {
    return (
      <Step
        state="error"
        icon={X}
        title="Agent hit iteration cap"
        subtitle={error || 'no progress within allowed iterations'}
        timestamp={null}
        last
      />
    );
  }
  if (status === 'done') {
    const executed = history.filter((h) => h.ok && h.outcome !== 'rejected').length;
    const rejected = history.filter((h) => h.outcome === 'rejected').length;
    return (
      <Step
        state="done"
        icon={CheckCircle2}
        title="Agent finished"
        subtitle={`${executed} action${executed === 1 ? '' : 's'} executed · ${rejected} rejected`}
        timestamp={null}
        last
      />
    );
  }
  return null;
}


// ===========================================================================
// Legacy branch — no skills: classic draft → approve / edit / reject
// ===========================================================================


function LegacyBranch(props: AgentTimelineProps) {
  const { session } = props;
  if (!session.draft) return null;

  // Once the operator has decided, render the outcome instead of the
  // awaiting step.
  if (session.feedback_status && session.feedback_status !== '') {
    const approved =
      session.feedback_status === 'approved' || session.feedback_status === 'edited';
    return (
      <Step
        state={approved ? 'done' : 'error'}
        icon={approved ? CheckCircle2 : X}
        title={
          session.feedback_status === 'edited'
            ? 'Draft edited and sent'
            : session.feedback_status === 'approved'
            ? 'Draft approved'
            : 'Draft rejected'
        }
        timestamp={session.feedback_at ?? null}
        last
      />
    );
  }

  if (!props.isActionable) return null;

  return (
    <Step
      state="awaiting"
      icon={MessageSquarePlus}
      title="Awaiting review"
      subtitle="approve as-is, edit, or reject the draft"
      forceExpanded
      last
      expandedContent={
        <div className="space-y-3">
          {props.editing ? (
            <textarea
              value={props.editedText}
              onChange={(e) => props.onEditedTextChange(e.target.value)}
              rows={Math.min(20, Math.max(6, props.editedText.split('\n').length))}
              className="w-full text-[13px] text-ink leading-relaxed bg-app rounded-md px-3 py-2 border border-line focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 font-mono"
            />
          ) : (
            <pre className="text-[12px] text-ink-body whitespace-pre-wrap font-sans leading-relaxed bg-app rounded-md px-3 py-2 border-l-[3px] border-amber-400 max-h-72 overflow-y-auto scrollbar-thin">
              {props.editedText}
            </pre>
          )}
          {props.submitError && (
            <div className="text-[12px] text-red-600 dark:text-red-400">
              {props.submitError}
            </div>
          )}
          <div className="flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={props.onDraftReject}
              disabled={props.submitting}
              className="inline-flex items-center gap-1 px-3 h-8 text-[12px] font-medium rounded-md border border-red-200 text-red-600 hover:bg-red-50 dark:border-red-800/60 dark:text-red-400 dark:hover:bg-red-950/40 transition-colors duration-150 disabled:opacity-60"
            >
              <X width={12} height={12} strokeWidth={2} />
              Reject
            </button>
            {props.editing ? (
              <button
                type="button"
                onClick={props.onCancelEdit}
                disabled={props.submitting}
                className="px-3 h-8 text-[12px] font-medium rounded-md border border-line text-ink-body hover:bg-hover transition-colors duration-150 disabled:opacity-60"
              >
                Cancel
              </button>
            ) : (
              <button
                type="button"
                onClick={props.onStartEdit}
                disabled={props.submitting}
                className="px-3 h-8 text-[12px] font-medium rounded-md border border-line text-ink-body hover:bg-hover transition-colors duration-150 disabled:opacity-60"
              >
                Edit
              </button>
            )}
            <button
              type="button"
              onClick={props.onDraftApprove}
              disabled={props.submitting}
              className="inline-flex items-center gap-1 px-3 h-8 text-[12px] font-medium rounded-md bg-accent text-white hover:bg-accent-hover transition-colors duration-150 disabled:opacity-60"
            >
              {props.submitting ? (
                <Loader2 width={12} height={12} className="animate-spin" />
              ) : (
                <Check width={12} height={12} strokeWidth={2} />
              )}
              {props.submitting
                ? 'Working…'
                : props.hasEdits
                ? 'Approve edits & send'
                : 'Approve & send'}
            </button>
          </div>
        </div>
      }
    />
  );
}


// ===========================================================================
// Step renderer (dot + connector + content)
// ===========================================================================


interface StepProps {
  state: DotState;
  icon: LucideIcon;
  title: string;
  subtitle?: React.ReactNode;
  timestamp?: string | null;
  expandable?: boolean;
  forceExpanded?: boolean;
  expandedContent?: React.ReactNode;
  last?: boolean;
}


function Step({
  state,
  icon: Icon,
  title,
  subtitle,
  timestamp,
  expandable = false,
  forceExpanded = false,
  expandedContent,
  last = false,
}: StepProps) {
  const [open, setOpen] = useState(false);
  const expanded = forceExpanded || open;
  const dotClass = {
    done: 'bg-emerald-500',
    awaiting: 'bg-amber-500 animate-pulse',
    pending: 'bg-slate-300 dark:bg-slate-600',
    error: 'bg-red-500',
  }[state];
  const iconClass = {
    done: 'text-emerald-600 dark:text-emerald-400',
    awaiting: 'text-amber-600 dark:text-amber-400',
    pending: 'text-ink-muted',
    error: 'text-red-600 dark:text-red-400',
  }[state];
  return (
    <li className="relative pl-7 pb-5 last:pb-0">
      {/* Connector line — only between steps, not after the last one. */}
      {!last && (
        <span
          aria-hidden
          className="absolute left-[10px] top-3.5 bottom-0 w-px bg-line-subtle"
        />
      )}
      {/* Dot */}
      <span
        aria-hidden
        className={`absolute left-[6px] top-1 w-2.5 h-2.5 rounded-full ${dotClass}`}
      />
      {/* Content */}
      <div className="min-w-0">
        {timestamp && (
          <div className="text-[11px] font-mono text-ink-muted tabular-nums">
            {formatTimestamp(timestamp)}
          </div>
        )}
        <div className="flex items-center gap-2 mt-0.5">
          <Icon
            width={14}
            height={14}
            strokeWidth={1.75}
            className={`shrink-0 ${iconClass}`}
          />
          <span className="text-[14px] font-medium text-ink">{title}</span>
          {expandable && !forceExpanded && (
            <button
              type="button"
              onClick={() => setOpen((v) => !v)}
              className="ml-auto inline-flex items-center text-[11px] text-ink-muted hover:text-ink-body"
            >
              {open ? (
                <ChevronDown width={14} height={14} strokeWidth={1.75} />
              ) : (
                <ChevronRight width={14} height={14} strokeWidth={1.75} />
              )}
            </button>
          )}
        </div>
        {subtitle && (
          <div className="text-[13px] text-ink-body mt-0.5 break-words">
            {subtitle}
          </div>
        )}
        {expanded && expandedContent && (
          <div className="mt-3">{expandedContent}</div>
        )}
      </div>
    </li>
  );
}


// ===========================================================================
// Helpers
// ===========================================================================


// All timeline timestamps render in Europe/Zagreb so the timeline reads
// consistently regardless of the operator's browser timezone. Backend
// writes UTC ISO; the conversion happens here at the edge.
const TIMELINE_TIMEZONE = 'Europe/Zagreb';

function formatTimestamp(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString('en-GB', {
      timeZone: TIMELINE_TIMEZONE,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return iso;
  }
}


function briefResult(data: Record<string, unknown> | null): string {
  if (!data) return 'ok';
  // Highlight the most useful identifiers in compact form.
  const cid = data['comment_id'];
  if (typeof cid === 'string' || typeof cid === 'number') {
    return `comment ${cid}`;
  }
  const newStatus = data['new_status'];
  if (typeof newStatus === 'string') {
    return `status → ${newStatus}`;
  }
  const cc = data['comment_count'];
  if (typeof cc === 'number') {
    return `${cc} comment${cc === 1 ? '' : 's'} retrieved`;
  }
  const keys = Object.keys(data);
  return keys.length ? keys.slice(0, 3).join(', ') : 'ok';
}


function pickBodyPreview(input: Record<string, unknown>): string | null {
  const body = input['body'];
  if (typeof body === 'string' && body.length > 0) return body;
  return null;
}


function ParamsBlock({
  label,
  input,
  dense = false,
}: {
  label: string;
  input: Record<string, unknown>;
  dense?: boolean;
}) {
  const entries = Object.entries(input).filter(([k]) => k !== 'body' || !dense);
  if (entries.length === 0) return null;
  return (
    <div>
      <div className="text-[10px] uppercase tracking-wider text-ink-muted font-medium mb-1">
        {label}
      </div>
      <dl className="space-y-0.5">
        {entries.map(([k, v]) => (
          <div key={k} className="flex items-baseline gap-2 text-[12px]">
            <dt className="font-mono text-ink-muted shrink-0 min-w-[5rem]">
              {k}
            </dt>
            <dd className="text-ink-body break-words whitespace-pre-wrap font-mono">
              {formatValue(v)}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}


function formatValue(v: unknown): string {
  if (v == null) return '—';
  if (typeof v === 'string') {
    return v.length > 200 ? `${v.slice(0, 200)}…` : v;
  }
  if (typeof v === 'number' || typeof v === 'boolean') return String(v);
  try {
    return JSON.stringify(v);
  } catch {
    return String(v);
  }
}
