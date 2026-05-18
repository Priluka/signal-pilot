/** Right column of the Agent Feed — what the agent did for this one ticket.
 *
 * Read-mostly: the agent has already classified / retrieved / drafted in the
 * background. The operator's job is to review the timeline + the matched
 * playbook + the draft and decide Approve / Edit / Reject — but only when
 * the derived status calls for human input. Auto-resolved, skipped, and
 * already-decided tickets just display their final state.
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

import { AgentStatusPill } from './AgentStatusPill';
import { DiffView } from './DiffView';
import { Chip, SectionHeading } from './ui';


type FeedbackKind = 'approved' | 'edited' | 'rejected';
export type TicketSource = 'local' | 'jira';


export function AgentTicketDetail({
  ticket,
  source = 'local',
}: {
  ticket: TicketDetail;
  source?: TicketSource;
}) {
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
      // For Jira tickets, post the comment first — if Jira rejects it, we
      // surface that error and DON'T log the local feedback, so the operator
      // can retry. Local-only flows skip this step.
      if (source === 'jira' && kind !== 'rejected') {
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
      const s =
        source === 'jira' ? await processJiraTicket(ticket.key) : null;
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
      // non-blocking
    }
    setSession(null);
    setEditing(false);
    setEditedText('');
    window.dispatchEvent(new Event('agent-sessions-changed'));
  }

  const status: AgentStatus = session?.derived_status ?? 'pending';
  const isActionable = status === 'needs_review' || status === 'escalated';
  const isHistorical = status === 'approved' || status === 'rejected';
  const hasEdits = session?.draft != null && editedText !== session.draft.draft;

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin">
      <div className="max-w-4xl mx-auto px-8 py-6 space-y-6">
        <TicketHeader ticket={ticket} status={status} />

        {loading && (
          <div className="text-sm text-slate-400">Loading session…</div>
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
              <DraftPanel
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
              />
            )}

            {isActionable && (
              <DecisionRow
                hasEdits={hasEdits}
                submitting={submitting}
                submitError={submitError}
                editing={editing}
                onApprove={() => decide(hasEdits ? 'edited' : 'approved')}
                onEdit={() => setEditing(true)}
                onReject={() => decide('rejected')}
              />
            )}

            {isHistorical && (
              <HistoricalFooter session={session} onRedo={redo} />
            )}

            {status === 'skipped' && (
              <div className="border border-panel-border bg-slate-50/60 rounded-lg px-4 py-3 text-sm text-slate-700">
                Auto-close path — classifier marked this as{' '}
                <code className="text-xs">{session.classification?.label}</code>.
                No reply was generated.
                <button
                  type="button"
                  onClick={redo}
                  className="ml-3 text-xs text-blue-600 hover:text-blue-700"
                >
                  Re-process this ticket
                </button>
              </div>
            )}

            {status === 'auto_drafted' && (
              <div className="border border-indigo-200 bg-indigo-50/60 rounded-lg px-4 py-3 text-sm text-indigo-800">
                Agent recommends sending this draft as-is. You can still review
                and approve / edit / reject below.
                <DecisionRow
                  hasEdits={hasEdits}
                  submitting={submitting}
                  submitError={submitError}
                  editing={editing}
                  onApprove={() => decide(hasEdits ? 'edited' : 'approved')}
                  onEdit={() => setEditing(true)}
                  onReject={() => decide('rejected')}
                />
              </div>
            )}

            {status === 'auto_resolved' && (
              <div className="border border-emerald-200 bg-emerald-50/60 rounded-lg px-4 py-3 text-sm text-emerald-800">
                Agent auto-resolved this ticket — no reply needed. Click below
                to re-process if you disagree.
                <button
                  type="button"
                  onClick={redo}
                  className="ml-3 text-xs text-blue-600 hover:text-blue-700"
                >
                  Re-process
                </button>
              </div>
            )}
          </>
        )}

        {!loading && !session && source === 'jira' && (
          <div className="border border-panel-border bg-slate-50/60 rounded-lg px-4 py-6 text-sm text-slate-700 text-center space-y-3">
            <p>This Jira ticket hasn't been processed by the agent yet.</p>
            <button
              type="button"
              onClick={processNow}
              disabled={processing}
              className="px-4 py-1.5 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-60"
            >
              {processing ? 'Classifying → retrieving → drafting…' : 'Process with agent'}
            </button>
            {processError && (
              <p className="text-[11px] text-red-600">{processError}</p>
            )}
          </div>
        )}

        {!loading && !session && source === 'local' && (
          <div className="border border-panel-border bg-slate-50/60 rounded-lg px-4 py-6 text-sm text-slate-500 text-center">
            Agent hasn't reached this ticket yet — wait for the batch to
            finish.
          </div>
        )}
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Pieces
// ---------------------------------------------------------------------------

function TicketHeader({
  ticket,
  status,
}: {
  ticket: TicketDetail;
  status: AgentStatus;
}) {
  return (
    <section className="bg-panel-surface border border-panel-border rounded-lg p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="text-[11px] font-mono text-slate-500">{ticket.key}</div>
          <h2 className="mt-0.5 text-lg font-semibold tracking-tight text-slate-900 leading-snug">
            {ticket.summary}
          </h2>
        </div>
        <AgentStatusPill status={status} size="md" />
      </div>
      {ticket.labels.length > 0 && (
        <div className="mt-3 flex items-center gap-1.5 flex-wrap">
          {ticket.labels.map((l) => (
            <Chip key={l}>{l}</Chip>
          ))}
        </div>
      )}
      <div className="mt-3 text-[11px] text-slate-500">
        {ticket.reporter_email ?? 'unknown'} · {ticket.priority ?? '—'}
      </div>
      <div className="mt-4 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
        {ticket.description || (
          <span className="text-slate-400 italic">No description.</span>
        )}
      </div>
    </section>
  );
}


function Timeline({ session }: { session: AgentSessionDetail }) {
  const steps: Array<{
    at: string | null;
    label: string;
    detail?: string;
    icon: 'done' | 'pending';
  }> = [];
  if (session.classified_at && session.classification) {
    steps.push({
      at: session.classified_at,
      label: 'Classified',
      detail: `${session.classification.label} (${session.classification.confidence.toFixed(
        2,
      )})`,
      icon: 'done',
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
          }, top: ${top.title.slice(0, 50)}${top.title.length > 50 ? '…' : ''}`
        : 'no matches',
      icon: 'done',
    });
  }
  if (session.drafted_at && session.draft) {
    steps.push({
      at: session.drafted_at,
      label: 'Draft generated',
      detail: `recommended: ${session.draft.recommended_action.replace(/_/g, ' ')}`,
      icon: 'done',
    });
  }
  if (session.feedback_at && session.feedback_status) {
    steps.push({
      at: session.feedback_at,
      label: `Reviewer ${session.feedback_status}`,
      icon: 'done',
    });
  } else if (session.draft && !session.feedback_status) {
    steps.push({
      at: null,
      label: 'Awaiting review',
      icon: 'pending',
    });
  }

  if (steps.length === 0) return null;

  return (
    <section>
      <SectionHeading>Processing timeline</SectionHeading>
      <ol className="space-y-2">
        {steps.map((step, i) => (
          <li key={i} className="flex items-start gap-3 text-sm">
            <span className="text-[11px] font-mono text-slate-400 w-20 shrink-0 pt-0.5">
              {step.at ? formatTime(step.at) : '—'}
            </span>
            <span
              className={`inline-block w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                step.icon === 'done' ? 'bg-emerald-500' : 'bg-slate-300 animate-pulse'
              }`}
            />
            <div>
              <div className="font-medium text-slate-900">{step.label}</div>
              {step.detail && (
                <div className="text-[12px] text-slate-500">{step.detail}</div>
              )}
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}


function ClassificationCard({ session }: { session: AgentSessionDetail }) {
  if (!session.classification) return null;
  return (
    <section>
      <SectionHeading>Classification</SectionHeading>
      <div className="bg-panel-surface border border-panel-border rounded-lg p-4">
        <div className="flex items-center gap-3 text-sm">
          <code className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 text-xs font-mono">
            {session.classification.label}
          </code>
          <span className="text-[11px] text-slate-500 font-mono">
            conf {session.classification.confidence.toFixed(2)}
          </span>
        </div>
        {session.classification.reason && (
          <p className="mt-2 text-sm text-slate-600 leading-relaxed">
            {session.classification.reason}
          </p>
        )}
      </div>
    </section>
  );
}


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
  return (
    <section>
      <SectionHeading>Matched playbook</SectionHeading>
      <Link
        to={`/knowledge/${playbookId}`}
        className="block bg-panel-surface border border-panel-border rounded-lg p-4 hover:border-blue-300 transition-colors"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <div className="text-sm font-medium text-slate-900 leading-snug">
              {title}
            </div>
            <div className="mt-0.5 text-[11px] font-mono text-slate-500">
              {playbookId}
            </div>
          </div>
          {score != null && (
            <span className="text-[11px] font-mono text-slate-500">
              score {score.toFixed(2)}
            </span>
          )}
        </div>
        <p className="mt-2 text-[13px] text-slate-600 leading-relaxed line-clamp-3">
          {description}
        </p>
      </Link>
    </section>
  );
}


function DraftPanel({
  session,
  editing,
  editedText,
  onEditedTextChange,
  onStartEdit,
  onCancelEdit,
  hasEdits,
}: {
  session: AgentSessionDetail;
  editing: boolean;
  editedText: string;
  onEditedTextChange: (v: string) => void;
  onStartEdit: () => void;
  onCancelEdit: () => void;
  hasEdits: boolean;
}) {
  if (!session.draft) return null;
  const action = session.draft.recommended_action;
  return (
    <section>
      <div className="flex items-center justify-between mb-2">
        <SectionHeading>Draft reply</SectionHeading>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono text-slate-500">
            action: {action.replace(/_/g, ' ')}
          </span>
          {!editing && (
            <button
              type="button"
              onClick={onStartEdit}
              className="text-[11px] text-blue-600 hover:text-blue-700"
            >
              Edit
            </button>
          )}
        </div>
      </div>
      <div className="bg-panel-surface border border-panel-border rounded-lg p-4">
        {!editing ? (
          <div className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed font-sans">
            {editedText}
          </div>
        ) : (
          <>
            <textarea
              value={editedText}
              onChange={(e) => onEditedTextChange(e.target.value)}
              rows={Math.max(8, Math.min(20, editedText.split('\n').length + 1))}
              className="w-full px-3 py-2 text-sm border-2 border-blue-400 rounded font-sans focus:outline-none focus:ring-2 focus:ring-blue-500/15 resize-y leading-relaxed"
            />
            <div className="mt-2 flex items-center justify-between">
              {hasEdits && (
                <details className="text-[11px] text-slate-500">
                  <summary className="cursor-pointer hover:text-slate-700">
                    Show diff
                  </summary>
                  <div className="mt-2 p-2 bg-slate-50 border border-panel-divider rounded">
                    <DiffView original={session.draft.draft} edited={editedText} />
                  </div>
                </details>
              )}
              <button
                type="button"
                onClick={onCancelEdit}
                className="ml-auto px-2.5 py-1 text-xs text-slate-600 rounded hover:bg-slate-100"
              >
                Cancel edits
              </button>
            </div>
          </>
        )}
      </div>
      {session.draft.rationale && (
        <p className="mt-2 text-[11px] text-slate-500 italic">
          {session.draft.rationale}
        </p>
      )}
    </section>
  );
}


function DecisionRow({
  hasEdits,
  submitting,
  submitError,
  editing,
  onApprove,
  onEdit,
  onReject,
}: {
  hasEdits: boolean;
  submitting: boolean;
  submitError: string | null;
  editing: boolean;
  onApprove: () => void;
  onEdit: () => void;
  onReject: () => void;
}) {
  return (
    <div className="pt-2">
      <div className="flex items-center justify-end gap-2">
        <button
          type="button"
          onClick={onReject}
          disabled={submitting}
          className="px-3 py-1.5 text-sm border border-red-200 text-red-700 bg-white rounded hover:bg-red-50 disabled:opacity-60"
        >
          Reject
        </button>
        {!editing && !hasEdits && (
          <button
            type="button"
            onClick={onEdit}
            disabled={submitting}
            className="px-3 py-1.5 text-sm border border-blue-200 text-blue-700 bg-white rounded hover:bg-blue-50 disabled:opacity-60"
          >
            Edit
          </button>
        )}
        <button
          type="button"
          onClick={onApprove}
          disabled={submitting}
          className="px-4 py-1.5 text-sm font-medium text-white bg-emerald-600 rounded hover:bg-emerald-700 disabled:opacity-60"
        >
          {hasEdits ? 'Approve & save edit' : 'Approve & send'}
        </button>
      </div>
      {submitError && (
        <p className="mt-2 text-right text-[11px] text-red-600">{submitError}</p>
      )}
    </div>
  );
}


function HistoricalFooter({
  session,
  onRedo,
}: {
  session: AgentSessionDetail;
  onRedo: () => void;
}) {
  const status = session.feedback_status;
  const tone =
    status === 'rejected'
      ? 'bg-red-50 border-red-200 text-red-800'
      : status === 'edited'
      ? 'bg-indigo-50 border-indigo-200 text-indigo-800'
      : 'bg-emerald-50 border-emerald-200 text-emerald-800';
  return (
    <div className={`border rounded-lg px-4 py-3 text-sm ${tone}`}>
      <div className="flex items-center justify-between gap-3">
        <span>
          Decision: <strong>{status}</strong>
          {session.feedback_at && (
            <span className="ml-2 text-[11px] font-mono opacity-70">
              at {formatTime(session.feedback_at)}
            </span>
          )}
        </span>
        <button
          type="button"
          onClick={onRedo}
          className="text-xs text-blue-600 hover:text-blue-700"
        >
          Re-process this ticket
        </button>
      </div>
    </div>
  );
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
