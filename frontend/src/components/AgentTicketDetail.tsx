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
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import {
  approveAction,
  deleteAgentSession,
  getAgentSession,
  listActionHistoryForTicket,
  listPendingActionsForTicket,
  postJiraComment,
  streamProcessJiraTicket,
  rejectAction,
  submitFeedback,
} from '../lib/api';
import type {
  AgentSessionDetail,
  AgentStatus,
  AgentStepEvent,
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
  // Brief 'Finishing up…' beat right after an approve/reject resolves
  // with planner status='done'. Without it the executed-skill row and
  // the terminal 'Agent finished' step land on the same React tick and
  // the operator misses the sequence — feels like teleportation.
  const [finishingUp, setFinishingUp] = useState(false);
  const [processError, setProcessError] = useState<string | null>(null);
  // Step-scoped error captured from the SSE stream. Cleared on a fresh
  // processNow / redo. Distinct from processError (which is the fetch
  // / network failure) — this one says "the agent itself failed mid
  // pipeline" and the timeline renders a red node for it.
  const [streamError, setStreamError] = useState<{
    step: string;
    message: string;
  } | null>(null);
  // Pending actions + audit history power the unified timeline. Polled
  // every 3s while mounted so a planner iteration that produces a new
  // pending row surfaces without manual refresh.
  const [pendingActions, setPendingActions] = useState<PendingAction[]>([]);
  const [history, setHistory] = useState<AuditEntry[]>([]);
  const [busyActionId, setBusyActionId] = useState<string | null>(null);
  const toast = useToast();

  const refreshTimeline = useCallback(async () => {
    // Returning a Promise lets the approve/reject handlers wait for the
    // executed skill's audit row to land BEFORE collapsing the pending
    // step into 'Finishing up…'. Without the await, the executed-skill
    // row would pop in mid-way through the finishing beat (or after it)
    // and the operator misses the sequence.
    await Promise.all([
      listPendingActionsForTicket(ticket.key)
        .then(setPendingActions)
        .catch(() => setPendingActions([])),
      listActionHistoryForTicket(ticket.key)
        .then(setHistory)
        .catch(() => setHistory([])),
    ]);
  }, [ticket.key]);

  // Ref mirror of ``editing`` so refresh() can read it without becoming
  // a stale closure (or re-running every keystroke if we used the
  // state value directly in the dep list). The ref is updated in an
  // effect rather than during render to avoid the react-hooks/refs
  // warning about mutating refs in the render phase.
  const editingRef = useRef(editing);
  useEffect(() => {
    editingRef.current = editing;
  }, [editing]);

  const refresh = useCallback(() => {
    getAgentSession(ticket.key)
      .then((s) => {
        setSession(s);
        if (s && !editingRef.current) {
          setEditedText(s.edited_text ?? s.draft?.draft ?? '');
        }
      })
      .catch(() => {});
  }, [ticket.key]);

  useEffect(() => {
    let cancelled = false;
    // Pattern intentionally resets local UI state on prop change so the
    // detail pane shows a clean spinner instead of stale data from the
    // previous ticket. The react-hooks lint rule flags synchronous
    // setState in effects, but per React docs this is the recommended
    // "reset on prop change" path when restructuring to a key prop on
    // the parent isn't an option.
    /* eslint-disable react-hooks/set-state-in-effect */
    setLoading(true);
    setError(null);
    setEditing(false);
    setSubmitError(null);
    /* eslint-enable react-hooks/set-state-in-effect */
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
    // Poll BOTH the canonical session row AND the timeline (pending +
    // history). Without the session poll, a reload during a long
    // planner run would never see planner_status flip to 'done' —
    // the SSE stream from that tab is gone, agent-sessions-changed
    // fires only on operator actions, and the timeline would keep
    // showing 'Composing response…' forever. Polling session here is
    // the persistence story: agent_sessions IS the source of truth,
    // refresh just pulls the latest snapshot.
    const poll = setInterval(() => {
      refreshTimeline();
      refresh();
    }, 3000);
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
  }, [ticket.key, refresh, refreshTimeline]);


  async function handleApproveAction(
    id: string,
    editedInput?: Record<string, unknown>,
  ) {
    setBusyActionId(id);
    // Show 'Finishing up…' from the click moment so the bottom of the
    // timeline is never static — the operator should always have a
    // visible spinner indicating the agent is doing something. Without
    // this the 3-4s while the approve POST is in flight feels like
    // dead air, even though the PendingStep button reads 'Executing…'.
    setFinishingUp(true);
    try {
      const result = await approveAction(id, editedInput);
      setSession((prev) =>
        prev
          ? {
              ...prev,
              planner_status: result.status,
              planner_error: result.error,
            }
          : prev,
      );
      // Wait for the audit row (executed skill) and the cleared
      // pending row to land in local state TOGETHER. Avoids a frame
      // where the executed action briefly disappears between the
      // PendingStep collapsing and the history row materialising.
      await refreshTimeline();
      // Keep Finishing visible for 1.2s after refresh resolves so the
      // operator gets a clear beat to register the 'Jira comment
      // posted' history row before 'Agent finished' takes over.
      if (result.status === 'done') {
        setTimeout(() => setFinishingUp(false), 1200);
      } else {
        // awaiting_approval or other non-terminal: planner queued
        // another pending action, drop Finishing immediately so the
        // new PendingStep is the focus.
        setFinishingUp(false);
      }
      toast.success(
        result.status === 'done'
          ? 'Skill executed · planner done'
          : `Skill executed · ${result.status}`,
      );
      refresh();
      window.dispatchEvent(new Event('agent-sessions-changed'));
    } catch (e) {
      toast.error((e as Error).message);
      // Drop the spinner on failure — otherwise it sits there forever.
      setFinishingUp(false);
    } finally {
      setBusyActionId(null);
    }
  }

  async function handleRejectAction(id: string) {
    setBusyActionId(id);
    setFinishingUp(true);
    try {
      const result = await rejectAction(id, 'Operator rejected from inbox.');
      setSession((prev) =>
        prev
          ? {
              ...prev,
              planner_status: result.status,
              planner_error: result.error,
            }
          : prev,
      );
      await refreshTimeline();
      if (result.status === 'done') {
        setTimeout(() => setFinishingUp(false), 1200);
      } else {
        setFinishingUp(false);
      }
      toast.success(`Skill rejected · ${result.status}`);
      refresh();
      window.dispatchEvent(new Event('agent-sessions-changed'));
    } catch (e) {
      toast.error((e as Error).message);
      setFinishingUp(false);
    } finally {
      setBusyActionId(null);
    }
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
    if (source !== 'jira') return;
    setProcessing(true);
    setProcessError(null);
    setStreamError(null);
    // Reset partial state for a clean stream — old events shouldn't
    // leak through if the operator clicks Process twice in a row.
    setSession(null);
    try {
      await streamProcessJiraTicket(ticket.key, (event) => {
        if (event.type === 'error') {
          // Step-scoped failure (classify / retrieve / draft / planner).
          // Surface as a red node in the timeline.
          setStreamError({ step: event.step, message: event.message });
          // Planner errors flow through SkillsBranch.PlannerOutcomeStep
          // which keys off ``planner_status === 'failed'``. Backend has
          // already mark_planner_status'd before yielding the event,
          // but the 3s polling lag would briefly show a spinner — fold
          // it in optimistically so the timeline flips immediately.
          if (event.step === 'planner') {
            setSession((prev) =>
              prev
                ? {
                    ...prev,
                    planner_status: 'failed',
                    planner_error: event.message,
                  }
                : prev,
            );
          }
          return;
        }
        // Merge each event into the session shape so AgentTimeline can
        // render it without knowing about the SSE protocol. Sub-fields
        // only get filled as the corresponding step completes.
        setSession((prev) => mergeStepEvent(prev, ticket.key, event));
        if (event.type === 'drafted') {
          setEditedText(event.draft);
        }
        if (event.type === 'planner_done' || event.type === 'done') {
          // Pending actions and audit history live in separate tables —
          // kick the timeline to re-poll once the planner has spoken.
          refreshTimeline();
        }
        if (event.type === 'planner_done' && event.status === 'done') {
          // Streaming counterpart of the approve/reject handler: when
          // the planner finishes on its own (autonomous / shadow), the
          // last audit row and 'Agent finished' land on the same tick.
          // Hold a 'Finishing up…' beat so the operator sees the
          // executed-skill row register before the terminal step
          // takes over.
          setFinishingUp(true);
          setTimeout(() => setFinishingUp(false), 1200);
        }
      });
      // After the stream closes, fetch the canonical session so any
      // server-side post-process (auto-post, mode-aware comments) is
      // reflected.
      refresh();
      window.dispatchEvent(new Event('agent-sessions-changed'));
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
    // Wipe local UI state immediately. The audit log row(s) remain in
    // the DB for compliance, but the timeline filter below hides them
    // from view until a fresh session.started_at sets a new baseline.
    setSession(null);
    setPendingActions([]);
    setHistory([]);
    setStreamError(null);
    setEditing(false);
    setEditedText('');
    setFinishingUp(false);
    window.dispatchEvent(new Event('agent-sessions-changed'));
  }

  const status: AgentStatus = session?.derived_status ?? 'pending';
  const isAutoPosted = Boolean(session?.auto_posted_at);
  const isActionable =
    !isAutoPosted && (status === 'needs_review' || status === 'escalated');
  const hasEdits = session?.draft != null && editedText !== session.draft.draft;
  // Audit history is append-only — re-processing a ticket leaves the
  // old run's rows in the DB. Without filtering, the timeline would
  // visually mix the previous attempt's executed/rejected skills with
  // the current run's. Anchor on the current session.started_at so
  // only "this run" rows render.
  const currentRunHistory = useMemo(() => {
    if (!session?.started_at) return history;
    const anchor = session.started_at;
    return history.filter((h) => h.decided_at >= anchor);
  }, [history, session?.started_at]);

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

        {!loading && session && status === 'skipped' && (
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
        )}

        {/* Single AgentTimeline component owns the entire right pane:
            empty state ('Ready to process'), full session flow, skills
            branch, awaiting-review actions. No separate cards above. */}
        {!loading && (!session || status !== 'skipped') && (
          <AgentTimeline
            session={session}
            source={source}
            pendingActions={pendingActions}
            history={currentRunHistory}
            streamError={streamError}
            busyActionId={busyActionId}
            onApproveAction={handleApproveAction}
            onRejectAction={handleRejectAction}
            processing={processing}
            processError={processError}
            onProcess={processNow}
            finishingUp={finishingUp}
            editing={editing}
            editedText={editedText}
            hasEdits={hasEdits}
            submitting={submitting}
            submitError={submitError}
            isActionable={isActionable}
            onStartEdit={() => setEditing(true)}
            onCancelEdit={() => {
              setEditing(false);
              setEditedText(session?.draft?.draft ?? '');
            }}
            onEditedTextChange={setEditedText}
            onDraftApprove={() => decide(hasEdits ? 'edited' : 'approved')}
            onDraftReject={() => decide('rejected')}
          />
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


/** Fold one SSE step event into the session shape AgentTimeline reads.
 *
 *  Returning a NEW partial each call keeps React's diff cheap. Fields
 *  that the event doesn't touch are preserved from ``prev`` so steps
 *  rendered earlier in the stream stay visible. When the stream's first
 *  event arrives ``prev`` is null and we seed a stub.
 */
function mergeStepEvent(
  prev: AgentSessionDetail | null,
  ticketKey: string,
  event: AgentStepEvent,
): AgentSessionDetail {
  const base: AgentSessionDetail =
    prev ?? {
      ticket_id: ticketKey,
      classification: null,
      retrieval: null,
      draft: null,
      draft_playbook_id: null,
      edited_text: null,
      feedback_status: null,
      derived_status: 'in_progress' as AgentStatus,
      updated_at: new Date().toISOString(),
      started_at: null,
      classified_at: null,
      retrieved_at: null,
      drafted_at: null,
      feedback_at: null,
      auto_posted_at: null,
      processed_mode: null,
      jira_browse_url: null,
      planner_status: null,
      planner_error: null,
      planner_updated_at: null,
      routing: null,
    };
  switch (event.type) {
    case 'started':
      return {
        ...base,
        started_at: event.at,
        processed_mode: event.mode as AgentSessionDetail['processed_mode'],
        derived_status: 'in_progress' as AgentStatus,
      };
    case 'classified':
      // Backend hands us a raw string; ClassifyResponse.label is a tight
      // three-value union. Cast through the union after narrowing — if
      // the classifier ever returns something exotic the timeline will
      // still render it as text.
      return {
        ...base,
        classification: {
          label: event.label as 'support_request' | 'internal_log' | 'spam_or_junk',
          confidence: event.confidence,
          reason: event.reason,
        },
        classified_at: event.at,
      };
    case 'retrieved':
      return {
        ...base,
        retrieval: {
          hits: event.hits,
          detected_language: event.detected_language,
          detected_country: event.detected_country,
        },
        retrieved_at: event.at,
        draft_playbook_id: event.hits[0]?.playbook_id ?? null,
        routing: event.routing,
      };
    case 'drafted':
      return {
        ...base,
        draft: {
          draft: event.draft,
          recommended_action:
            event.recommended_action as AgentSessionDetail['draft'] extends infer D
              ? D extends { recommended_action: infer R }
                ? R
                : string
              : string,
          rationale: event.rationale,
        } as AgentSessionDetail['draft'],
        drafted_at: event.at,
        draft_playbook_id: event.playbook_id,
        derived_status: 'needs_review' as AgentStatus,
      };
    case 'planner_done':
      return {
        ...base,
        planner_status: event.status,
        planner_error: event.error,
      };
    case 'skipped':
      return { ...base, derived_status: 'skipped' as AgentStatus };
    default:
      // started, no_hits, planner_started, error (handled separately
      // via streamError state), done — no session-shape impact.
      return base;
  }
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


