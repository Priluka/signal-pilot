/** Right column of the Agent Feed — what the agent did for one ticket.
 *
 * Linear-style: tight rhythm (space-y-5), narrow max-width for readability,
 * one consistent card pattern, a single accent for primary actions. The
 * draft reply is the hero section — slightly more padding, the right-most
 * primary button is the operator's main action.
 *
 * Sections, top to bottom:
 *   1. Ticket header (ID + status + title + meta + tags)        — separator after
 *   2. Original message                                          — quiet inset card
 *   3. Processing timeline                                       — vertical dots w/ connecting line
 *   4. Classification                                            — compact card
 *   5. Matched playbook                                          — emphasised card with link
 *   6. Draft reply                                               — hero card + decision row OR decision banner
 */
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Loader2 } from 'lucide-react';

import {
  approveAction,
  deleteAgentSession,
  getAgentSession,
  listActionHistoryForTicket,
  listPendingActionsForTicket,
  postJiraComment,
  processJiraTicket,
  rejectAction,
  submitFeedback,
} from '../lib/api';
import type {
  AgentSessionDetail,
  AgentStatus,
  AuditEntry,
  PendingAction,
  TicketDetail,
} from '../lib/types';
import { useAgentMode } from '../lib/useAgentMode';

import { AgentModeChip } from './AgentModeChip';
import { AgentStatusPill } from './AgentStatusPill';
import { AgentTimeline } from './AgentTimeline';
import { useToast } from './Toast';


type FeedbackKind = 'approved' | 'edited' | 'rejected';
export type TicketSource = 'local' | 'jira';


// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function AgentTicketDetail({
  ticket,
  source = 'local',
}: {
  ticket: TicketDetail;
  source?: TicketSource;
}) {
  const agentMode = useAgentMode();
  // Approve posts to Jira only when the source IS Jira AND the operator
  // has explicitly enabled outbound writes (assisted or autonomous). In
  // shadow, the comment never leaves our DB.
  const postsToJira = source === 'jira' && agentMode != null && agentMode !== 'shadow';
  const [session, setSession] = useState<AgentSessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [editing, setEditing] = useState(false);
  const [editedText, setEditedText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);
  const [processError, setProcessError] = useState<string | null>(null);
  // Pending actions + audit history power the unified timeline. Polled
  // every 3s while mounted so a planner iteration that produces a new
  // pending row surfaces without manual refresh.
  const [pendingActions, setPendingActions] = useState<PendingAction[]>([]);
  const [history, setHistory] = useState<AuditEntry[]>([]);
  const [busyActionId, setBusyActionId] = useState<string | null>(null);
  const toast = useToast();

  const refreshTimeline = useCallback(() => {
    listPendingActionsForTicket(ticket.key)
      .then(setPendingActions)
      .catch(() => setPendingActions([]));
    listActionHistoryForTicket(ticket.key)
      .then(setHistory)
      .catch(() => setHistory([]));
  }, [ticket.key]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setEditing(false);
    setSubmitError(null);
    getAgentSession(ticket.key)
      .then((s) => {
        if (cancelled) return;
        setSession(s);
        setEditedText(s?.edited_text ?? s?.draft?.draft ?? '');
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    refreshTimeline();
    const poll = setInterval(refreshTimeline, 3000);
    const handler = () => {
      refresh();
      refreshTimeline();
    };
    window.addEventListener('agent-sessions-changed', handler);
    return () => {
      cancelled = true;
      clearInterval(poll);
      window.removeEventListener('agent-sessions-changed', handler);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticket.key]);


  async function handleApproveAction(id: string) {
    setBusyActionId(id);
    try {
      const result = await approveAction(id);
      toast.success(
        result.status === 'done'
          ? 'Skill executed · planner done'
          : `Skill executed · ${result.status}`,
      );
      refreshTimeline();
      refresh();
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setBusyActionId(null);
    }
  }

  async function handleRejectAction(id: string) {
    setBusyActionId(id);
    try {
      const result = await rejectAction(id, 'Operator rejected from inbox.');
      toast.success(`Skill rejected · ${result.status}`);
      refreshTimeline();
      refresh();
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setBusyActionId(null);
    }
  }

  function refresh() {
    getAgentSession(ticket.key)
      .then((s) => {
        setSession(s);
        if (s && !editing) {
          setEditedText(s.edited_text ?? s.draft?.draft ?? '');
        }
      })
      .catch(() => {});
  }

  async function decide(kind: FeedbackKind) {
    if (!session?.draft || !session.draft_playbook_id) return;
    setSubmitting(true);
    setSubmitError(null);
    const finalText =
      kind === 'rejected'
        ? null
        : kind === 'edited' || editedText !== session.draft.draft
        ? editedText
        : null;
    try {
      if (postsToJira && kind !== 'rejected') {
        await postJiraComment({
          issue_key: ticket.key,
          body: finalText ?? session.draft.draft,
        });
      }
      await submitFeedback({
        ticket_id: ticket.key,
        playbook_id: session.draft_playbook_id,
        draft_text: session.draft.draft,
        final_text: finalText,
        status: kind,
      });
      setEditing(false);
      window.dispatchEvent(new Event('agent-sessions-changed'));
    } catch (err) {
      setSubmitError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  async function processNow() {
    setProcessing(true);
    setProcessError(null);
    try {
      const s = source === 'jira' ? await processJiraTicket(ticket.key) : null;
      if (s) {
        setSession(s);
        setEditedText(s.edited_text ?? s.draft?.draft ?? '');
        window.dispatchEvent(new Event('agent-sessions-changed'));
      }
    } catch (err) {
      setProcessError((err as Error).message);
    } finally {
      setProcessing(false);
    }
  }

  async function redo() {
    try {
      await deleteAgentSession(ticket.key);
    } catch {
      /* non-blocking */
    }
    setSession(null);
    setEditing(false);
    setEditedText('');
    window.dispatchEvent(new Event('agent-sessions-changed'));
  }

  const status: AgentStatus = session?.derived_status ?? 'pending';
  const isAutoPosted = Boolean(session?.auto_posted_at);
  const isActionable =
    !isAutoPosted && (status === 'needs_review' || status === 'escalated');
  const isHistorical =
    !isAutoPosted && (status === 'approved' || status === 'rejected');
  const hasEdits = session?.draft != null && editedText !== session.draft.draft;

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin">
      <div className="max-w-3xl mx-auto p-6 space-y-5">
        <TicketHeader
          ticket={ticket}
          status={status}
          processedMode={session?.processed_mode ?? null}
          // Only show the Re-process link once a session exists. There's
          // nothing to discard on a fresh Jira ticket — the empty-state
          // panel below already has the primary "Process with agent"
          // call to action.
          onReprocess={session ? redo : null}
        />

        {/* Original message — quiet inset card right after the header so
            the operator reads the prompt before the agent's reaction. */}
        <OriginalMessage description={ticket.description ?? ''} />

        {loading && (
          <div className="text-sm text-ink-muted">Loading session…</div>
        )}
        {error && <div className="text-sm text-red-600 dark:text-red-400">{error}</div>}

        {!loading && session && (
          <>
            {status === 'skipped' ? (
              <div className="border border-line bg-hover/60 rounded-lg px-4 py-3 text-sm text-ink-body">
                Auto-close path — classifier marked this as{' '}
                <code className="text-xs">{session.classification?.label}</code>.
                No reply was generated.{' '}
                <button
                  type="button"
                  onClick={redo}
                  className="text-[12px] text-accent-fg hover:underline font-medium"
                >
                  Re-process this ticket
                </button>
              </div>
            ) : (
              <AgentTimeline
                session={session}
                pendingActions={pendingActions}
                history={history}
                busyActionId={busyActionId}
                onApproveAction={handleApproveAction}
                onRejectAction={handleRejectAction}
                editing={editing}
                editedText={editedText}
                hasEdits={hasEdits}
                submitting={submitting}
                submitError={submitError}
                isActionable={isActionable}
                onStartEdit={() => setEditing(true)}
                onCancelEdit={() => {
                  setEditing(false);
                  setEditedText(session.draft?.draft ?? '');
                }}
                onEditedTextChange={setEditedText}
                onDraftApprove={() => decide(hasEdits ? 'edited' : 'approved')}
                onDraftReject={() => decide('rejected')}
              />
            )}
          </>
        )}

        {!loading && !session && source === 'jira' && (
          <div className="border border-line bg-app rounded-lg px-6 py-6 text-sm text-ink-body text-center space-y-4">
            {processing ? (
              <ProcessingStepper />
            ) : (
              <p>This Jira ticket hasn't been processed by the agent yet.</p>
            )}
            <button
              type="button"
              onClick={processNow}
              disabled={processing}
              className="inline-flex items-center gap-1.5 px-4 h-9 text-[13px] font-medium text-white bg-accent rounded-md hover:bg-accent-hover transition-colors duration-150 disabled:opacity-60"
            >
              {processing ? (
                <>
                  <Loader2 width={13} height={13} className="animate-spin" />
                  Working…
                </>
              ) : (
                'Process with agent'
              )}
            </button>
            {processError && (
              <p className="text-[11px] text-red-600 dark:text-red-400">{processError}</p>
            )}
          </div>
        )}

        {!loading && !session && source === 'local' && (
          <div className="border border-line bg-app rounded-lg px-4 py-6 text-sm text-ink-muted text-center">
            Agent hasn't reached this ticket yet — wait for the batch to finish.
          </div>
        )}
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------

function TicketHeader({
  ticket,
  status,
  processedMode,
  onReprocess,
}: {
  ticket: TicketDetail;
  status: AgentStatus;
  processedMode: 'shadow' | 'assisted' | 'autonomous' | null;
  /** When present, header shows a small "Re-process" link. Confirmed
   *  before firing because the action discards the current session
   *  (classification, draft, pending actions) — audit history stays. */
  onReprocess: (() => void) | null;
}) {
  function handleReprocess() {
    const ok = window.confirm(
      'Re-process this ticket?\n\n' +
        'The current classification, draft, and any pending agent actions ' +
        'will be discarded. The audit history is preserved. ' +
        'A new Anthropic call will be made.',
    );
    if (ok && onReprocess) onReprocess();
  }

  return (
    <section className="border-b border-line-subtle pb-5">
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs font-mono text-ink-muted tabular-nums">{ticket.key}</span>
        <AgentStatusPill status={status} size="md" />
        {processedMode && <AgentModeChip mode={processedMode} size="sm" />}
        {onReprocess && (
          <button
            type="button"
            onClick={handleReprocess}
            className="ml-auto text-[12px] text-ink-muted hover:text-accent-fg transition-colors duration-150"
            title="Discard current session and run classify/retrieve/draft again"
          >
            Re-process
          </button>
        )}
      </div>
      <h2 className="mt-1 text-lg font-semibold text-ink tracking-tight leading-snug">
        {ticket.summary}
      </h2>
      <div className="mt-0.5 text-[13px] text-ink-body">
        {ticket.reporter_email ?? 'unknown'} · {ticket.priority ?? '—'}
      </div>
      {ticket.labels.length > 0 && (
        <div className="mt-2 flex items-center gap-1.5 flex-wrap">
          {ticket.labels.map((l) => (
            <span
              key={l}
              className="inline-flex items-center text-xs font-mono text-ink-muted bg-app border border-line rounded px-1.5 py-0.5"
            >
              {l}
            </span>
          ))}
        </div>
      )}
    </section>
  );
}


function OriginalMessage({ description }: { description: string }) {
  return (
    <section>
      <div className="bg-app border border-line rounded-lg p-5 text-[13px] text-ink whitespace-pre-line leading-relaxed">
        {description.trim() || (
          <span className="text-ink-muted italic">No description.</span>
        )}
      </div>
    </section>
  );
}


// (Legacy Timeline / ClassificationCard / PlaybookCard / DraftSection /
//  DecisionRow / DecisionBanner / AutoResolvedBanner / formatTime helpers
//  were here — replaced by the single AgentTimeline component imported
//  above. Kept the file shorter; behaviour preserved.)


// (Legacy ClassificationCard / PlaybookCard / DraftSection / DecisionRow /
//  DecisionBanner / AutoResolvedBanner removed — AgentTimeline handles all
//  detail-pane rendering now.)


// ---------------------------------------------------------------------------
// ProcessingStepper — animated stepper while /agent/process is in flight
// ---------------------------------------------------------------------------
// The backend endpoint is a single blocking call (classify + retrieve +
// draft happen inside it without progress events), so we don't actually
// know which sub-step is running at any given moment. We instead drive a
// timer-based progression that mirrors typical timings — classify is
// fast, retrieve is faster, draft dominates — and stay on "draft" until
// the parent rerenders with the loaded session (which unmounts us).
//
// Visual: three pills in a row with a numbered/checkmark/spinner badge
// + label, chevron connectors between them. Active = accent spinner;
// done = emerald check; pending = muted bg-hover + number.

type StepState = 'pending' | 'active' | 'done';


function ProcessingStepper() {
  // 0 = classify active, 1 = retrieve active, 2 = draft active.
  const [stage, setStage] = useState<0 | 1 | 2>(0);

  useEffect(() => {
    const t1 = window.setTimeout(() => setStage(1), 1500);
    const t2 = window.setTimeout(() => setStage(2), 1500 + 800);
    return () => {
      window.clearTimeout(t1);
      window.clearTimeout(t2);
    };
  }, []);

  const classify: StepState = stage > 0 ? 'done' : 'active';
  const retrieve: StepState = stage > 1 ? 'done' : stage === 1 ? 'active' : 'pending';
  const draft: StepState = stage === 2 ? 'active' : 'pending';

  return (
    <div className="flex items-center justify-center gap-2 select-none">
      <Step index={1} label="Classify" state={classify} />
      <StepConnector />
      <Step index={2} label="Retrieve" state={retrieve} />
      <StepConnector />
      <Step index={3} label="Draft" state={draft} />
    </div>
  );
}


function Step({
  index,
  label,
  state,
}: {
  index: number;
  label: string;
  state: StepState;
}) {
  const badge =
    state === 'done' ? (
      <Check width={11} height={11} strokeWidth={3} />
    ) : state === 'active' ? (
      <Loader2 width={11} height={11} className="animate-spin" strokeWidth={2.5} />
    ) : (
      <span className="text-[10px] font-semibold tabular-nums">{index}</span>
    );
  const badgeClass =
    state === 'done'
      ? 'bg-emerald-500 text-white'
      : state === 'active'
      ? 'bg-accent text-white'
      : 'bg-hover text-ink-muted';
  const labelClass =
    state === 'active'
      ? 'text-ink font-medium'
      : state === 'done'
      ? 'text-ink-body'
      : 'text-ink-muted';
  return (
    <div className="flex items-center gap-2">
      <span
        className={`w-5 h-5 rounded-full inline-flex items-center justify-center transition-colors duration-200 ${badgeClass}`}
      >
        {badge}
      </span>
      <span className={`text-[12px] transition-colors duration-200 ${labelClass}`}>
        {label}
      </span>
    </div>
  );
}


function StepConnector() {
  return (
    <ChevronRight
      width={12}
      height={12}
      strokeWidth={1.75}
      className="text-ink-muted shrink-0"
    />
  );
}
