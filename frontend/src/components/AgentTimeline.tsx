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
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  ClipboardList,
  Clock,
  Inbox,
  Loader2,
  Pencil,
  Play,
  Search,
  Tag,
  X,
  type LucideProps,
} from 'lucide-react';

import { useTheme } from '../lib/theme';
import type {
  AgentSessionDetail,
  AuditEntry,
  PendingAction,
} from '../lib/types';


type LucideIcon = React.ComponentType<LucideProps>;


/** Visual identity of a single step on the timeline. Drives the icon
 *  circle's background + the icon colour. Light/dark variants are
 *  resolved at render time via ``useTheme``. */
type StepKind =
  | 'classified'
  | 'retrieved'
  | 'drafted'
  | 'planner_started'
  | 'comment_posted'
  | 'approved'
  | 'rejected'
  | 'awaiting'
  | 'finished'
  | 'finished_failed'
  | 'failed'
  | 'shadow'
  | 'active';


interface StepPalette {
  bg: string;
  fg: string;
  bgDark: string;
  fgDark: string;
  /** Border + text accent for the special 'finished' terminal node. */
  border?: string;
  borderDark?: string;
  textAccent?: string;
  textAccentDark?: string;
}


// Enterprise palette — three states only. The "consumer app" rainbow
// (blue/violet/amber/green/red on every step) is intentionally collapsed
// down to neutral / success / error so a glance at the timeline reads
// as Process / Done / Problem and nothing else competes for attention.
const _NEUTRAL: StepPalette = {
  bg: '#F1EFE8',
  fg: '#5F5E5A',
  bgDark: '#2C2C2A',
  fgDark: '#B4B2A9',
};
const _SUCCESS: StepPalette = {
  bg: '#EAF3DE',
  fg: '#3B6D11',
  bgDark: '#173404',
  fgDark: '#97C459',
};
const _ERROR: StepPalette = {
  bg: '#FCEBEB',
  fg: '#A32D2D',
  bgDark: '#501313',
  fgDark: '#F09595',
};

const STEP_COLORS: Record<StepKind, StepPalette> = {
  classified: _NEUTRAL,
  retrieved: _NEUTRAL,
  drafted: _NEUTRAL,
  planner_started: _NEUTRAL,
  comment_posted: _SUCCESS,
  approved: _SUCCESS,
  rejected: _ERROR,
  awaiting: _NEUTRAL,
  // Terminal node — keeps the green border + accent text per spec.
  finished: {
    ..._SUCCESS,
    border: '#5DCAA5',
    borderDark: '#5DCAA5',
    textAccent: '#0F6E56',
    textAccentDark: '#5DCAA5',
  },
  // Agent finished but at least one action was rejected — same border
  // treatment as the green variant, but red palette so a quick glance
  // shows the outcome wasn't clean.
  finished_failed: {
    ..._ERROR,
    border: '#A32D2D',
    borderDark: '#F09595',
    textAccent: '#A32D2D',
    textAccentDark: '#F09595',
  },
  failed: _ERROR,
  shadow: _NEUTRAL,
  active: _NEUTRAL,
};


function usePalette(kind: StepKind): {
  bg: string;
  fg: string;
  border: string | null;
  textAccent: string | null;
} {
  const { theme } = useTheme();
  const p = STEP_COLORS[kind];
  const dark = theme === 'dark';
  return {
    bg: dark ? p.bgDark : p.bg,
    fg: dark ? p.fgDark : p.fg,
    border: dark ? p.borderDark ?? null : p.border ?? null,
    textAccent: dark ? p.textAccentDark ?? null : p.textAccent ?? null,
  };
}


export interface AgentTimelineProps {
  /** Null when this ticket has never been processed — the timeline
   *  renders a single 'Ready to process' starter step instead of the
   *  full Classified → Retrieved → Draft sequence. */
  session: AgentSessionDetail | null;
  source: 'local' | 'jira';
  pendingActions: PendingAction[];
  history: AuditEntry[];
  busyActionId: string | null;
  onApproveAction: (
    id: string,
    editedInput?: Record<string, unknown>,
  ) => void | Promise<void>;
  onRejectAction: (id: string) => void | Promise<void>;

  // --- initial-process controls (no session yet) ---
  processing: boolean;
  processError: string | null;
  onProcess: () => void;

  /** Step-scoped failure surfaced by the SSE stream. When set, the
   *  active-stage loader is replaced by a red Error node and the
   *  frontier is suppressed so the spinner doesn't keep ticking. */
  streamError: { step: string; message: string } | null;

  /** True for ~1.2s after operator approves/rejects the final pending
   *  action. Holds a 'Finishing up…' spinner on the timeline so the
   *  executed-skill row and the terminal 'Agent finished' step don't
   *  flash in simultaneously. */
  finishingUp: boolean;

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
  const { session, processing, streamError } = props;
  // Effective error = live SSE error (current tab) OR the one persisted
  // on the session row from a previous run that crashed. Without the
  // persisted half, a page refresh after a credit-limit / network
  // failure would strip the red error node and revert to a spinner
  // forever — agent_sessions.error_step/error_message are the source
  // of truth across reloads.
  const persistedError =
    session?.error_step && session?.error_message
      ? { step: session.error_step, message: session.error_message }
      : null;
  const anyError = streamError ?? persistedError;
  // Planner-step failures are rendered INLINE by SkillsBranch's
  // PlannerOutcomeStep (it already shows 'Agent loop failed' when
  // session.planner_status === 'failed'), keeping the executed-skill
  // history visible above the failure node. Only classify / retrieve /
  // draft failures need the top-level error overlay — those steps
  // happen before SkillsBranch is even applicable.
  const topLevelError = anyError?.step === 'planner' ? null : anyError;
  // Compute the currently-running stage from the session shape. While
  // SSE streams events in, each completed milestone fills another
  // field; the first one still empty is what's "in progress". Any
  // error stops the frontier immediately so the spinner doesn't keep
  // ticking next to a failed pipeline.
  const frontier = anyError ? null : activeStage(session, processing);

  return (
    // pb-[200px] keeps the last node scrollable past the fold — without
    // it the terminal step (Agent finished / Jira comment posted) sits
    // glued to the bottom edge and the operator can't centre it for a
    // clean read.
    <section className="pb-[200px]">
      <h2 className="text-[11px] uppercase tracking-wider font-semibold text-ink-muted mb-4">
        Agent execution timeline
      </h2>
      <ol className="relative">
        {session ? (
          <SessionBranches
            {...props}
            session={session}
            frontier={frontier}
            streamError={topLevelError}
          />
        ) : processing && !anyError ? (
          <ActiveStageStep stage={frontier ?? 'classifying'} last />
        ) : anyError ? (
          // Pre-session failure (e.g. classify crashed before the row
          // even existed). Show the error node alone so the operator
          // knows the agent stopped before anything happened.
          <StreamErrorStep error={anyError} last />
        ) : (
          <ReadyToProcessStep {...props} />
        )}
      </ol>
    </section>
  );
}


type ActiveStage =
  | 'classifying'
  | 'retrieving'
  | 'drafting'
  | 'planning'
  // Mid-planner-loop: a skill just returned, Claude is making the next
  // tool_use decision. Shown inline at the bottom of SkillsBranch so the
  // operator sees that the agent is still working instead of staring at
  // dead air between the last audit row and the next pending action.
  | 'composing'
  // Post-decision wrap-up: operator just approved/rejected the final
  // pending action and we're momentarily holding the timeline on a
  // 'Finishing up…' frame before the 'Agent finished' terminal step
  // resolves. Without this beat the executed-skill row and the terminal
  // step flash into existence simultaneously and the eye loses the
  // sequence.
  | 'finishing';


/** Where the agent currently is in the pipeline, derived purely from
 *  which fields on the session have been populated. Returns null only
 *  for terminal states (skipped/no-hits/done/draft-ready). The previous
 *  version also required ``processing === true`` — that broke page
 *  refresh during a long planner run, since ``processing`` is local
 *  React state and gets reset to false on reload. The session row in
 *  agent_sessions is the authoritative source: if classified_at is set
 *  but planner_status is not, the agent is still working regardless of
 *  whether the SSE stream this tab opened is still alive. Trade-off:
 *  a session genuinely abandoned mid-loop (backend crash) will spin
 *  here forever — operator must hit Re-process. Acceptable. */
function activeStage(
  session: AgentSessionDetail | null,
  _processing: boolean,
): ActiveStage | null {
  if (!session) return null;
  if (!session.classified_at) return 'classifying';
  // Non-support tickets short-circuit at classify — no further work.
  if (
    session.classification &&
    session.classification.label !== 'support_request'
  ) {
    return null;
  }
  if (!session.retrieved_at) return 'retrieving';
  if (!session.retrieval?.hits?.length) return null;
  // After retrieval, exactly one writer runs based on session.routing.
  // The runner sets routing in the same step it emits `retrieved`, so
  // the placeholder switches immediately to the correct label.
  if (session.routing === 'planner') {
    if (session.planner_status === null || session.planner_status === undefined) {
      return 'planning';
    }
    return null;
  }
  if (session.routing === 'drafter') {
    if (!session.drafted_at) return 'drafting';
    return null;
  }
  // Legacy rows pre-routing column: fall back to the old drafted_at →
  // planner_status sequence so historical sessions still animate sanely.
  if (!session.drafted_at) return 'drafting';
  if (session.planner_status === null || session.planner_status === undefined) {
    return 'planning';
  }
  return null;
}


function SessionBranches(
  props: AgentTimelineProps & {
    session: AgentSessionDetail;
    frontier: ActiveStage | null;
    streamError: { step: string; message: string } | null;
  },
) {
  const { session, frontier, streamError } = props;
  // Routing decides which writer ran (and which timeline step is
  // meaningful). Sessions written before this column existed have
  // routing===null — for those we keep the old skills-signal heuristic
  // so historical rows still render coherently.
  const routing = session.routing ?? null;
  const skillsActive =
    routing === 'planner' ||
    (routing === null &&
      (props.pendingActions.length > 0 ||
        props.history.length > 0 ||
        !!session.planner_status));
  // The drafter step is meaningless on the planner path — that writer
  // didn't run, so its row would just lie about what happened. Render
  // it only on the drafter path (or on legacy rows with drafted_at).
  const showDraftStep =
    !!session.drafted_at &&
    (routing === 'drafter' || routing === null);
  return (
    <>
      {/* The completed steps render only when their data is in. The
          live placeholder appears at the bottom — one node always
          visibly active while the stream is in flight. */}
      {session.classified_at && <ClassifiedStep session={session} />}
      {session.retrieved_at && <RetrievedStep session={session} />}
      {showDraftStep && <DraftStep session={session} />}
      {streamError ? (
        <StreamErrorStep error={streamError} last />
      ) : skillsActive ? (
        // SkillsBranch owns the bottom of the timeline whenever the
        // planner is responsible — it renders executed skills, pending
        // actions, AND its own inline 'composing' loader for the gap
        // between iterations. Letting the generic frontier placeholder
        // replace it would hide the skill history that already streamed.
        <SkillsBranch {...props} session={session} />
      ) : frontier ? (
        <ActiveStageStep stage={frontier} last />
      ) : (
        <LegacyBranch {...props} session={session} />
      )}
    </>
  );
}


// ===========================================================================
// Stream error — red terminal node when the SSE stream emitted 'error'
// ===========================================================================


function StreamErrorStep({
  error,
  last = false,
}: {
  error: { step: string; message: string };
  last?: boolean;
}) {
  return (
    <Step
      kind="failed"
      icon={X}
      title={`Agent failed at ${error.step}`}
      subtitle={
        <span className="font-mono text-[12px] text-red-700 dark:text-red-300 break-words">
          {error.message}
        </span>
      }
      timestamp={null}
      last={last}
    />
  );
}


// ===========================================================================
// Active-stage placeholder — one pulsing node at the streaming frontier
// ===========================================================================


function ActiveStageStep({
  stage,
  last = false,
}: {
  stage: ActiveStage;
  last?: boolean;
}) {
  const meta = ACTIVE_STAGE_META[stage];
  return (
    <Step
      kind="active"
      icon={Loader2}
      title={meta.title}
      subtitle={meta.subtitle}
      timestamp={null}
      last={last}
    />
  );
}


const ACTIVE_STAGE_META: Record<
  ActiveStage,
  { title: string; subtitle: string }
> = {
  classifying: {
    title: 'Classifying ticket…',
    subtitle: 'Reading summary and description',
  },
  retrieving: {
    title: 'Retrieving playbook…',
    subtitle: 'Searching the knowledge corpus',
  },
  drafting: {
    title: 'Generating draft…',
    subtitle: 'Writing the customer reply',
  },
  planning: {
    title: 'Planning actions…',
    subtitle: 'Deciding which skills to call',
  },
  composing: {
    title: 'Composing response…',
    subtitle: 'Reading skill results, deciding next step',
  },
  finishing: {
    title: 'Finishing up…',
    subtitle: 'Wrapping up the agent run',
  },
};


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
      kind="awaiting"
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
                className="inline-flex items-center gap-1.5 px-4 h-9 text-[13px] font-medium bg-btn-primary text-btn-primary-fg rounded-md hover:bg-btn-primary-hover transition-colors duration-150 disabled:opacity-60"
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
  // Caller (SessionBranches) only renders this once classified_at is set,
  // so we can assume completion here. The pending placeholder is owned
  // by ActiveStageStep at the timeline frontier.
  return (
    <Step
      kind="classified"
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
  if (!session.retrieval || session.retrieval.hits.length === 0) return null;
  // Prefer the explicitly-stored draft_playbook_id (set by the runner at
  // retrieve time), fall back to hits[0] for legacy rows or any session
  // where the field wasn't persisted. Without the fallback the step
  // silently disappears on the planner path after a refresh.
  const matchId = session.draft_playbook_id ?? session.retrieval.hits[0].playbook_id;
  const hit =
    session.retrieval.hits.find((h) => h.playbook_id === matchId) ??
    session.retrieval.hits[0];
  return (
    <Step
      kind="retrieved"
      icon={Search}
      title="Retrieved playbook"
      timestamp={session.retrieved_at}
      subtitle={
        <span className="text-[13px] text-ink-body">
          <Link
            to={`/knowledge/${matchId}`}
            className="text-accent-fg hover:underline"
          >
            {hit?.title ?? matchId}
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
      kind="drafted"
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


function SkillsBranch(
  props: AgentTimelineProps & { session: AgentSessionDetail },
) {
  const { session, pendingActions, history, finishingUp } = props;
  const sortedHistory = useMemo(
    () => [...history].sort((a, b) => a.decided_at.localeCompare(b.decided_at)),
    [history],
  );
  // Composing placeholder kicks in when the planner is still mid-loop
  // (no terminal status persisted yet) and there's no pending action
  // sitting on the operator. No `processing` check — the session row
  // is the authoritative signal across page refreshes; otherwise a
  // reload during a long planner run would drop the spinner and the
  // timeline would look frozen even though the agent is still working.
  const composing =
    !session.planner_status &&
    pendingActions.length === 0;
  return (
    <>
      <Step
        kind="planner_started"
        icon={ClipboardList}
        title="Planner started"
        // On the planner path drafted_at is null (drafter never ran), so
        // fall back to retrieved_at — the planner kicks off immediately
        // after retrieve, so that timestamp is honest within a few ms.
        timestamp={session.drafted_at ?? session.retrieved_at}
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
          onApprove={(editedInput) => props.onApproveAction(pa.id, editedInput)}
          onReject={() => props.onRejectAction(pa.id)}
        />
      ))}
      {/* finishingUp wins even when a PendingStep is still rendered
          above — operators consistently report the empty tail during
          the approve POST as the worst dead-air moment. With the gate
          off, a single Finishing spinner sits at the bottom from the
          click moment through to ~1.2s after the planner resolves. */}
      {finishingUp ? (
        <ActiveStageStep stage="finishing" last />
      ) : pendingActions.length === 0 ? (
        composing ? (
          <ActiveStageStep stage="composing" last />
        ) : (
          <PlannerOutcomeStep
            status={session.planner_status ?? null}
            error={session.planner_error ?? null}
            history={sortedHistory}
            hasPending={false}
          />
        )
      ) : null}
    </>
  );
}


function HistoryStep({ entry }: { entry: AuditEntry }) {
  // Outcome semantics drive both the wording AND the dot colour:
  //   shadow   → nothing actually happened; gray dot, "no effect"
  //   rejected → operator refused; red dot
  //   ok=false → real attempt, real failure; red dot
  //   auto     → read in any mode, or autonomous-opt-in write; green
  //   approved → operator OK'd, skill ran; green
  // The previous render lumped shadow together with approved which
  // misled the operator into believing the skill had executed.
  const isShadow = entry.outcome === 'shadow';
  const isReject = entry.outcome === 'rejected';
  const isFail = !entry.ok && !isReject;
  const kind: StepKind = isShadow
    ? 'shadow'
    : isReject
    ? 'rejected'
    : isFail
    ? 'failed'
    : entry.skill_name.endsWith('comment')
    ? 'comment_posted'
    : 'approved';
  const icon: LucideIcon = isShadow ? Pencil : isReject || isFail ? X : Check;
  const title = isShadow
    ? `${entry.skill_name} · shadow — no effect`
    : isReject
    ? `${entry.skill_name} rejected`
    : isFail
    ? `${entry.skill_name} failed`
    : entry.skill_name === 'jira_add_public_comment'
    ? 'Jira comment posted'
    : entry.outcome === 'auto'
    ? `${entry.skill_name} executed (auto)`
    : `${entry.skill_name} executed`;
  const subtitle = isShadow
    ? 'Skill was not called — shadow mode logs the request only.'
    : isReject
    ? entry.error || 'rejected by operator'
    : isFail
    ? entry.error || 'skill error'
    : briefResult(entry.result_data);
  return (
    <Step
      kind={kind}
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
  onApprove: (editedInput?: Record<string, unknown>) => void;
  onReject: () => void;
}) {
  const originalBody = pickBodyPreview(action.skill_input);
  // Edit affordance only makes sense when there's a free-form body field
  // (jira comments). Other skills are pure data calls — no text to tweak.
  const editable = typeof originalBody === 'string' && originalBody.length > 0;
  const [editing, setEditing] = useState(false);
  const [editedBody, setEditedBody] = useState(originalBody ?? '');
  const hasEdits =
    editable && editedBody !== originalBody && editedBody.trim().length > 0;

  function handleApprove() {
    if (hasEdits) {
      onApprove({ ...action.skill_input, body: editedBody });
    } else {
      onApprove();
    }
  }
  return (
    <Step
      kind="awaiting"
      icon={Clock}
      title={action.skill_name}
      timestamp={action.created_at}
      subtitle={`iter ${action.iteration} · ${action.mode}`}
      forceExpanded
      expandedContent={
        <div className="space-y-3">
          {editable && editing ? (
            <textarea
              value={editedBody}
              onChange={(e) => setEditedBody(e.target.value)}
              rows={Math.min(20, Math.max(6, editedBody.split('\n').length))}
              className="w-full text-[13px] text-ink leading-relaxed bg-app rounded-md px-3 py-2 border border-line focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 font-mono"
            />
          ) : (
            originalBody && (
              <pre className="text-[12px] text-ink-body whitespace-pre-wrap font-sans leading-relaxed bg-app rounded-md px-3 py-2 border-l-[3px] border-amber-400 max-h-44 overflow-y-auto scrollbar-thin">
                {hasEdits ? editedBody : originalBody}
              </pre>
            )
          )}
          <ParamsBlock label="parameters" input={action.skill_input} dense />
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onReject}
              disabled={busy}
              className="mr-auto inline-flex items-center gap-1.5 px-4 h-9 text-[13px] font-medium rounded-lg bg-transparent border border-line text-ink-body hover:border-red-300 hover:text-red-600 hover:bg-red-50 dark:hover:border-red-800 dark:hover:text-red-400 dark:hover:bg-red-950/40 transition-colors duration-150 disabled:opacity-60"
            >
              <X width={16} height={16} strokeWidth={2} />
              Reject
            </button>
            {editable && (
              editing ? (
                <button
                  type="button"
                  onClick={() => {
                    setEditing(false);
                    setEditedBody(originalBody ?? '');
                  }}
                  disabled={busy}
                  className="px-4 h-9 text-[13px] font-medium rounded-lg bg-transparent border border-line text-ink-body hover:bg-hover transition-colors duration-150 disabled:opacity-60"
                >
                  Cancel
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => setEditing(true)}
                  disabled={busy}
                  className="px-4 h-9 text-[13px] font-medium rounded-lg bg-transparent border border-line text-ink-body hover:bg-hover transition-colors duration-150 disabled:opacity-60"
                >
                  Edit
                </button>
              )
            )}
            <button
              type="button"
              onClick={handleApprove}
              disabled={busy}
              className="inline-flex items-center gap-1.5 px-4 h-9 text-[13px] font-medium rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 dark:bg-emerald-600 dark:hover:bg-emerald-500 transition-colors duration-150 disabled:opacity-60"
            >
              {busy ? (
                <Loader2 width={16} height={16} className="animate-spin" />
              ) : (
                <Check width={16} height={16} strokeWidth={2} />
              )}
              {busy
                ? 'Executing…'
                : hasEdits
                ? 'Approve edits & run'
                : 'Approve & run'}
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
        kind="failed"
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
        kind="failed"
        icon={X}
        title="Agent hit iteration cap"
        subtitle={error || 'no progress within allowed iterations'}
        timestamp={null}
        last
      />
    );
  }
  if (status === 'done') {
    // Shadow rows logged a "would call" but did not execute anything,
    // so they don't belong in the executed count. We surface them as
    // a third bucket so the summary matches what the operator saw
    // step-by-step on the timeline.
    const executed = history.filter(
      (h) => h.ok && h.outcome !== 'rejected' && h.outcome !== 'shadow',
    ).length;
    const rejected = history.filter((h) => h.outcome === 'rejected').length;
    const shadow = history.filter((h) => h.outcome === 'shadow').length;
    const parts = [`${executed} action${executed === 1 ? '' : 's'} executed`];
    if (rejected > 0) parts.push(`${rejected} rejected`);
    if (shadow > 0) parts.push(`${shadow} shadow`);
    return (
      <Step
        // Red-bordered variant when any action was rejected — operator
        // sees at a glance the run wasn't clean even though the planner
        // ended its turn normally.
        kind={rejected > 0 ? 'finished_failed' : 'finished'}
        icon={CheckCircle2}
        title="Agent finished"
        subtitle={parts.join(' · ')}
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


function LegacyBranch(
  props: AgentTimelineProps & { session: AgentSessionDetail },
) {
  const { session } = props;
  if (!session.draft) return null;

  // Once the operator has decided, render the outcome instead of the
  // awaiting step. ('' was a defensive runtime check from earlier; the
  // type is narrowed to the four-value union so it's redundant.)
  if (session.feedback_status) {
    const approved =
      session.feedback_status === 'approved' || session.feedback_status === 'edited';
    return (
      <Step
        kind={approved ? 'approved' : 'rejected'}
        icon={approved ? Check : X}
        title={
          session.feedback_status === 'edited'
            ? 'Draft edited and sent'
            : session.feedback_status === 'approved'
            ? 'Reviewer approved'
            : 'Reviewer rejected'
        }
        timestamp={session.feedback_at ?? null}
        last
      />
    );
  }

  if (!props.isActionable) return null;

  return (
    <Step
      kind="awaiting"
      icon={Clock}
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
          {/* Three outline buttons — Reject pushed far left, Edit +
              Approve grouped on the right. Equal visual weight; no
              filled-indigo button screaming at the operator. Reject
              stays neutral until hover so the eye doesn't lock onto
              red as the obvious action. */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={props.onDraftReject}
              disabled={props.submitting}
              className="mr-auto inline-flex items-center gap-1.5 px-4 h-9 text-[13px] font-medium rounded-lg bg-transparent border border-line text-ink-body hover:border-red-300 hover:text-red-600 hover:bg-red-50 dark:hover:border-red-800 dark:hover:text-red-400 dark:hover:bg-red-950/40 transition-colors duration-150 disabled:opacity-60"
            >
              <X width={16} height={16} strokeWidth={2} />
              Reject
            </button>
            {props.editing ? (
              <button
                type="button"
                onClick={props.onCancelEdit}
                disabled={props.submitting}
                className="px-4 h-9 text-[13px] font-medium rounded-lg bg-transparent border border-line text-ink-body hover:bg-hover transition-colors duration-150 disabled:opacity-60"
              >
                Cancel
              </button>
            ) : (
              <button
                type="button"
                onClick={props.onStartEdit}
                disabled={props.submitting}
                className="px-4 h-9 text-[13px] font-medium rounded-lg bg-transparent border border-line text-ink-body hover:bg-hover transition-colors duration-150 disabled:opacity-60"
              >
                Edit
              </button>
            )}
            <button
              type="button"
              onClick={props.onDraftApprove}
              disabled={props.submitting}
              className="inline-flex items-center gap-1.5 px-4 h-9 text-[13px] font-medium rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 dark:bg-emerald-600 dark:hover:bg-emerald-500 transition-colors duration-150 disabled:opacity-60"
            >
              {props.submitting ? (
                <Loader2 width={16} height={16} className="animate-spin" />
              ) : (
                <Check width={16} height={16} strokeWidth={2} />
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
  kind: StepKind;
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
  kind,
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
  const pal = usePalette(kind);
  const isFinished = kind === 'finished';
  const isActive = kind === 'active';
  return (
    <li className="relative pb-5 last:pb-0 flex items-start gap-3">
      {/* Connector line — runs behind the icon circles, ends at the
          centre of the next circle so the last node is clean. The
          circle's z-index sits above the line. */}
      {!last && (
        <span
          aria-hidden
          className="absolute left-[14.25px] top-[30px] bottom-0 w-[1.5px] bg-line"
        />
      )}
      {/* Icon circle — 30px, coloured background per step kind. The
          'finished' node gets a 1.5px border accent; the 'active'
          placeholder gets a pulse animation. */}
      <div
        className={`relative z-10 w-[30px] h-[30px] rounded-full flex items-center justify-center flex-shrink-0 ${
          isActive ? 'animate-pulse' : ''
        }`}
        style={{
          background: pal.bg,
          border: isFinished && pal.border ? `1.5px solid ${pal.border}` : undefined,
        }}
      >
        <Icon
          width={14}
          height={14}
          strokeWidth={2}
          style={{ color: pal.fg }}
          className={isActive ? 'animate-spin' : ''}
        />
      </div>
      {/* Content */}
      <div className="flex-1 min-w-0 pt-1">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className="text-[13px] font-medium"
            style={{
              color: pal.textAccent ?? undefined,
            }}
          >
            <span className={pal.textAccent ? '' : 'text-ink'}>{title}</span>
          </span>
          {timestamp && (
            <span className="text-[11px] font-mono text-ink-muted tabular-nums">
              {formatTimestamp(timestamp)}
            </span>
          )}
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
          <div className="text-[12px] text-ink-body mt-0.5 break-words">
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
  // No truncation: the only place this renders is inside an expanded
  // step body. Expanding IS the operator's consent to see everything,
  // so cropping at 200 chars would lie about what the agent actually
  // sent (e.g. the full Jira comment body). The surrounding container
  // is already scrollable.
  if (typeof v === 'string') return v;
  if (typeof v === 'number' || typeof v === 'boolean') return String(v);
  try {
    return JSON.stringify(v, null, 2);
  } catch {
    return String(v);
  }
}
