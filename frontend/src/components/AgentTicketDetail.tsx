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
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import {
  deleteAgentSession,
  getAgentSession,
  postJiraComment,
  processJiraTicket,
  submitFeedback,
} from '../lib/api';
import type {
  AgentSessionDetail,
  AgentStatus,
  TicketDetail,
} from '../lib/types';
import { useAgentMode } from '../lib/useAgentMode';

import { AgentModeChip } from './AgentModeChip';
import { AgentStatusPill } from './AgentStatusPill';
import { DiffView } from './DiffView';


type FeedbackKind = 'approved' | 'edited' | 'rejected';
export type TicketSource = 'local' | 'jira';


// ---------------------------------------------------------------------------
// Shared atoms
// ---------------------------------------------------------------------------

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-[11px] font-medium uppercase tracking-wider text-ink-muted mb-3">
      {children}
    </div>
  );
}


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
    const handler = () => refresh();
    window.addEventListener('agent-sessions-changed', handler);
    return () => {
      cancelled = true;
      window.removeEventListener('agent-sessions-changed', handler);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticket.key]);

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
        />

        {/* Original message — quiet inset card right after the header so
            the operator reads the prompt before the agent's reaction. */}
        <OriginalMessage description={ticket.description ?? ''} />

        {loading && (
          <div className="text-sm text-ink-muted">Loading session…</div>
        )}
        {error && <div className="text-sm text-red-600">{error}</div>}

        {!loading && session && (
          <>
            <Timeline session={session} />
            {session.classification && (
              <ClassificationCard session={session} />
            )}
            {session.draft_playbook_id && session.retrieval && (
              <PlaybookCard
                playbookId={session.draft_playbook_id}
                title={
                  session.retrieval.hits.find(
                    (h) => h.playbook_id === session.draft_playbook_id,
                  )?.title ?? session.draft_playbook_id
                }
                description={
                  session.retrieval.hits.find(
                    (h) => h.playbook_id === session.draft_playbook_id,
                  )?.description ?? ''
                }
                score={
                  session.retrieval.hits.find(
                    (h) => h.playbook_id === session.draft_playbook_id,
                  )?.score ?? null
                }
              />
            )}

            {session.draft && (
              <DraftSection
                session={session}
                editing={editing}
                editedText={editedText}
                onEditedTextChange={setEditedText}
                onStartEdit={() => setEditing(true)}
                onCancelEdit={() => {
                  setEditing(false);
                  setEditedText(session.draft?.draft ?? '');
                }}
                hasEdits={hasEdits}
                postsToJira={postsToJira}
                isActionable={isActionable}
                isHistorical={isHistorical}
                isAutoPosted={isAutoPosted}
                submitting={submitting}
                submitError={submitError}
                onApprove={() => decide(hasEdits ? 'edited' : 'approved')}
                onReject={() => decide('rejected')}
                onRedo={redo}
                jiraUrl={session.jira_browse_url ?? null}
                ticketKey={ticket.key}
              />
            )}

            {status === 'skipped' && (
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
          </>
        )}

        {!loading && !session && source === 'jira' && (
          <div className="border border-line bg-app rounded-lg px-4 py-6 text-sm text-ink-body text-center space-y-3">
            <p>This Jira ticket hasn't been processed by the agent yet.</p>
            <button
              type="button"
              onClick={processNow}
              disabled={processing}
              className="px-4 h-9 text-[13px] font-medium text-white bg-accent rounded-md hover:bg-accent-hover transition-colors duration-150 disabled:opacity-60"
            >
              {processing ? 'Classifying → retrieving → drafting…' : 'Process with agent'}
            </button>
            {processError && (
              <p className="text-[11px] text-red-600">{processError}</p>
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
}: {
  ticket: TicketDetail;
  status: AgentStatus;
  processedMode: 'shadow' | 'assisted' | 'autonomous' | null;
}) {
  return (
    <section className="border-b border-line-subtle pb-5">
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs font-mono text-ink-muted tabular-nums">{ticket.key}</span>
        <AgentStatusPill status={status} size="md" />
        {processedMode && <AgentModeChip mode={processedMode} size="sm" />}
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


// ---------------------------------------------------------------------------
// Timeline
// ---------------------------------------------------------------------------

type TimelineStep = {
  at: string | null;
  label: string;
  detail?: string;
  state: 'done' | 'pending' | 'rejected';
};


function Timeline({ session }: { session: AgentSessionDetail }) {
  const steps: TimelineStep[] = [];
  if (session.classified_at && session.classification) {
    steps.push({
      at: session.classified_at,
      label: 'Classified',
      detail: `${session.classification.label} (${session.classification.confidence.toFixed(2)})`,
      state: 'done',
    });
  }
  if (session.retrieved_at && session.retrieval) {
    const top = session.retrieval.hits[0];
    steps.push({
      at: session.retrieved_at,
      label: 'Retrieved',
      detail: top
        ? `${session.retrieval.hits.length} match${
            session.retrieval.hits.length === 1 ? '' : 'es'
          }, top: ${top.title.slice(0, 60)}${top.title.length > 60 ? '…' : ''}`
        : 'no matches',
      state: 'done',
    });
  }
  if (session.drafted_at && session.draft) {
    steps.push({
      at: session.drafted_at,
      label: 'Draft generated',
      detail: `recommended: ${session.draft.recommended_action.replace(/_/g, ' ')}`,
      state: 'done',
    });
  }
  if (session.feedback_at && session.feedback_status) {
    steps.push({
      at: session.feedback_at,
      label: `Reviewer ${session.feedback_status}`,
      state: session.feedback_status === 'rejected' ? 'rejected' : 'done',
    });
  } else if (session.draft && !session.feedback_status) {
    steps.push({
      at: null,
      label: 'Awaiting review',
      state: 'pending',
    });
  }

  if (steps.length === 0) return null;

  return (
    <section>
      <SectionLabel>Processing timeline</SectionLabel>
      <ol>
        {steps.map((step, i) => {
          const isLast = i === steps.length - 1;
          const dotClass =
            step.state === 'done'
              ? 'bg-emerald-500'
              : step.state === 'rejected'
              ? 'bg-red-500'
              : 'bg-line';
          return (
            <li key={i} className="flex items-start gap-3">
              <span className="text-[11px] font-mono text-ink-muted w-20 shrink-0 text-right pt-1">
                {step.at ? formatTime(step.at) : '—'}
              </span>
              <span className="flex flex-col items-center self-stretch">
                <span
                  className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${dotClass}`}
                />
                {!isLast && <span className="w-px flex-1 bg-line-subtle my-1" />}
              </span>
              <div className={isLast ? '' : 'pb-3'}>
                <div className="text-[13px] font-medium text-ink leading-snug">
                  {step.label}
                </div>
                {step.detail && (
                  <div className="text-[12px] text-ink-body mt-0.5 leading-snug">
                    {step.detail}
                  </div>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}


// ---------------------------------------------------------------------------
// Classification
// ---------------------------------------------------------------------------

function ClassificationCard({ session }: { session: AgentSessionDetail }) {
  if (!session.classification) return null;
  return (
    <section>
      <SectionLabel>Classification</SectionLabel>
      <div className="border border-line rounded-lg p-4">
        <div className="flex items-center gap-2">
          <code className="font-mono text-[11px] bg-app border border-line rounded px-1.5 py-0.5 text-ink-body">
            {session.classification.label}
          </code>
          <span className="text-[11px] text-ink-muted font-mono">
            conf {session.classification.confidence.toFixed(2)}
          </span>
        </div>
        {session.classification.reason && (
          <p className="mt-2 text-[13px] text-ink-body leading-relaxed">
            {session.classification.reason}
          </p>
        )}
      </div>
    </section>
  );
}


// ---------------------------------------------------------------------------
// Matched playbook
// ---------------------------------------------------------------------------

function PlaybookCard({
  playbookId,
  title,
  description,
  score,
}: {
  playbookId: string;
  title: string;
  description: string;
  score: number | null;
}) {
  const [expanded, setExpanded] = useState(false);
  const longDescription = description.length > 220;
  return (
    <section>
      <SectionLabel>Matched playbook</SectionLabel>
      <div className="border border-line rounded-lg p-4">
        <div className="flex items-start justify-between gap-4">
          <Link
            to={`/knowledge/${playbookId}`}
            className="text-[13px] font-semibold text-ink leading-snug hover:text-accent-fg transition-colors duration-150"
          >
            {title}
          </Link>
          {score != null && (
            <span className="text-[11px] font-mono text-ink-muted shrink-0">
              score {score.toFixed(2)}
            </span>
          )}
        </div>
        <div className="mt-0.5 text-[11px] font-mono text-ink-muted">{playbookId}</div>
        {description && (
          <>
            <p
              className={`mt-2 text-[13px] text-ink-body leading-relaxed ${
                longDescription && !expanded ? 'line-clamp-3' : ''
              }`}
            >
              {description}
            </p>
            {longDescription && (
              <button
                type="button"
                onClick={() => setExpanded((v) => !v)}
                className="mt-1 text-[12px] text-accent-fg hover:underline"
              >
                {expanded ? 'Show less' : 'Show more'}
              </button>
            )}
          </>
        )}
      </div>
    </section>
  );
}


// ---------------------------------------------------------------------------
// Draft + decision
// ---------------------------------------------------------------------------

interface DraftSectionProps {
  session: AgentSessionDetail;
  editing: boolean;
  editedText: string;
  onEditedTextChange: (v: string) => void;
  onStartEdit: () => void;
  onCancelEdit: () => void;
  hasEdits: boolean;
  postsToJira: boolean;
  isActionable: boolean;
  isHistorical: boolean;
  isAutoPosted: boolean;
  submitting: boolean;
  submitError: string | null;
  onApprove: () => void;
  onReject: () => void;
  onRedo: () => void;
  jiraUrl: string | null;
  ticketKey: string;
}


function DraftSection({
  session,
  editing,
  editedText,
  onEditedTextChange,
  onStartEdit,
  onCancelEdit,
  hasEdits,
  postsToJira,
  isActionable,
  isHistorical,
  isAutoPosted,
  submitting,
  submitError,
  onApprove,
  onReject,
  onRedo,
  jiraUrl,
  ticketKey,
}: DraftSectionProps) {
  if (!session.draft) return null;
  const action = session.draft.recommended_action.replace(/_/g, ' ');
  return (
    <section>
      <div className="flex items-center justify-between mb-3">
        <SectionLabel>Draft reply</SectionLabel>
        <div className="flex items-center gap-3 mb-3">
          <span className="text-[11px] font-mono text-ink-muted">action: {action}</span>
          {!editing && !isAutoPosted && !isHistorical && (
            <button
              type="button"
              onClick={onStartEdit}
              className="text-[12px] text-accent-fg hover:underline font-medium"
            >
              Edit
            </button>
          )}
        </div>
      </div>

      {/* Draft body card — slightly more padding than other cards. */}
      <div className="border border-line rounded-lg p-5">
        {!editing ? (
          <div className="text-[13px] text-ink whitespace-pre-line leading-relaxed">
            {editedText}
          </div>
        ) : (
          <>
            <textarea
              value={editedText}
              onChange={(e) => onEditedTextChange(e.target.value)}
              rows={Math.max(8, Math.min(20, editedText.split('\n').length + 1))}
              className="w-full px-3 py-2 text-[13px] bg-card border border-accent rounded-md font-sans focus:outline-none focus:ring-2 focus:ring-accent/20 resize-y leading-relaxed"
            />
            <div className="mt-2 flex items-center justify-between">
              {hasEdits ? (
                <details className="text-[11px] text-ink-muted">
                  <summary className="cursor-pointer hover:text-ink-body">Show diff</summary>
                  <div className="mt-2 p-2 bg-app border border-line-subtle rounded-md">
                    <DiffView original={session.draft.draft} edited={editedText} />
                  </div>
                </details>
              ) : (
                <span />
              )}
              <button
                type="button"
                onClick={onCancelEdit}
                className="text-[12px] text-ink-body rounded-md px-2.5 h-7 hover:bg-hover"
              >
                Cancel edits
              </button>
            </div>
          </>
        )}
      </div>

      {/* Playbook caveat — quiet contextual info, NOT a warning. */}
      {session.draft.rationale && (
        <p className="text-[12px] text-ink-muted italic leading-relaxed mt-3 px-1">
          {session.draft.rationale}
        </p>
      )}

      {/* Decision UX — exactly one of: action row, banner, or auto-resolved. */}
      {isAutoPosted && (
        <AutoResolvedBanner
          postedAt={session.auto_posted_at!}
          jiraUrl={jiraUrl}
          ticketKey={ticketKey}
        />
      )}

      {isActionable && (
        <DecisionRow
          hasEdits={hasEdits}
          submitting={submitting}
          submitError={submitError}
          postsToJira={postsToJira}
          onApprove={onApprove}
          onEdit={onStartEdit}
          onReject={onReject}
          editing={editing}
        />
      )}

      {isHistorical && (
        <DecisionBanner
          status={session.feedback_status as 'approved' | 'edited' | 'rejected'}
          feedbackAt={session.feedback_at}
          onRedo={onRedo}
        />
      )}
    </section>
  );
}


function DecisionRow({
  hasEdits,
  submitting,
  submitError,
  postsToJira,
  editing,
  onApprove,
  onEdit,
  onReject,
}: {
  hasEdits: boolean;
  submitting: boolean;
  submitError: string | null;
  postsToJira: boolean;
  editing: boolean;
  onApprove: () => void;
  onEdit: () => void;
  onReject: () => void;
}) {
  const approveLabel = postsToJira
    ? hasEdits
      ? 'Approve & send edited'
      : 'Approve & send'
    : hasEdits
    ? 'Approve & save edit'
    : 'Approve';
  return (
    <div className="mt-4">
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onReject}
          disabled={submitting}
          className="mr-auto inline-flex items-center px-4 h-9 text-[13px] font-medium bg-transparent border border-red-200 text-red-600 rounded-md hover:bg-red-50 transition-colors duration-150 disabled:opacity-60"
        >
          Reject
        </button>
        {!editing && !hasEdits && (
          <button
            type="button"
            onClick={onEdit}
            disabled={submitting}
            className="inline-flex items-center px-4 h-9 text-[13px] font-medium bg-app border border-line text-ink rounded-md hover:bg-hover transition-colors duration-150 disabled:opacity-60"
          >
            Edit
          </button>
        )}
        <button
          type="button"
          onClick={onApprove}
          disabled={submitting}
          className="inline-flex items-center px-4 h-9 text-[13px] font-medium text-white bg-accent rounded-md hover:bg-accent-hover transition-colors duration-150 disabled:opacity-60"
        >
          {approveLabel}
        </button>
      </div>
      {submitError && (
        <p className="mt-2 text-right text-[11px] text-red-600">{submitError}</p>
      )}
    </div>
  );
}


function DecisionBanner({
  status,
  feedbackAt,
  onRedo,
}: {
  status: 'approved' | 'edited' | 'rejected';
  feedbackAt: string | null;
  onRedo: () => void;
}) {
  const isRejected = status === 'rejected';
  const tone = isRejected
    ? 'bg-red-50 border-red-200'
    : 'bg-emerald-50 border-emerald-200';
  const textTone = isRejected ? 'text-red-700' : 'text-emerald-700';
  const subTone = isRejected ? 'text-red-400' : 'text-emerald-500';
  return (
    <div className={`flex items-center justify-between border rounded-lg px-4 py-3 mt-4 ${tone}`}>
      <span className="text-[13px]">
        <span className={`font-medium ${textTone}`}>
          Decision: {status === 'edited' ? 'approved (edited)' : status}
        </span>
        {feedbackAt && (
          <span className={`ml-2 text-[12px] font-mono ${subTone}`}>
            at {formatTime(feedbackAt)}
          </span>
        )}
      </span>
      <button
        type="button"
        onClick={onRedo}
        className="text-[12px] text-accent-fg hover:underline font-medium"
      >
        Re-process this ticket
      </button>
    </div>
  );
}


function AutoResolvedBanner({
  postedAt,
  jiraUrl,
  ticketKey,
}: {
  postedAt: string;
  jiraUrl: string | null;
  ticketKey: string;
}) {
  return (
    <div className="flex items-center justify-between border border-emerald-200 bg-emerald-50 rounded-lg px-4 py-3 mt-4">
      <div className="flex items-center gap-2 text-[13px] text-emerald-700">
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="text-emerald-600 shrink-0"
        >
          <polyline points="20 6 9 17 4 12" />
        </svg>
        <span>
          <span className="font-medium">Auto-resolved</span> — posted to Jira at{' '}
          <span className="font-mono text-[12px]">{formatTimestampFull(postedAt)}</span>
        </span>
      </div>
      {jiraUrl ? (
        <a
          href={jiraUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[12px] text-emerald-700 hover:underline font-medium inline-flex items-center gap-1"
        >
          Open {ticketKey}
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
            <polyline points="15 3 21 3 21 9" />
            <line x1="10" y1="14" x2="21" y2="3" />
          </svg>
        </a>
      ) : (
        <span className="text-[11px] font-mono text-emerald-600">{ticketKey}</span>
      )}
    </div>
  );
}


// ---------------------------------------------------------------------------
// Date helpers
// ---------------------------------------------------------------------------

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return iso;
  }
}


function formatTimestampFull(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}
