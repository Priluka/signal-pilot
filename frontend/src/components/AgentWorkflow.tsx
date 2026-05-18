/** Right column of the Agent page — orchestrates classify → retrieve → draft → decide.
 *
 * State is keyed by ticket: when the user picks a different ticket the entire
 * workflow resets. Classifier auto-runs on load; retrieval auto-runs once a
 * support_request is confirmed; the drafter is manual so the operator can
 * choose which playbook to anchor against.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import {
  classifyTicket,
  deleteAgentSession,
  draftReply,
  getAgentSession,
  getPlaybook,
  retrievePlaybooks,
  submitFeedback,
} from '../lib/api';
import type {
  ClassifyResponse,
  DraftResponse,
  PlaybookDetail,
  RetrievalHitOut,
  RetrieveResponse,
  TicketDetail,
  TicketSummary,
} from '../lib/types';

import { Chip, ConfidenceBar, SectionHeading, StepCircle } from './ui';
import { DiffView } from './DiffView';


interface Props {
  ticket: TicketDetail;
  tickets: TicketSummary[];
}


type FeedbackStatus = 'approved' | 'edited' | 'rejected';


export function AgentWorkflow({ ticket, tickets }: Props) {
  const navigate = useNavigate();

  // --- Workflow state, reset on ticket change ----------------------------
  const [classification, setClassification] = useState<ClassifyResponse | null>(null);
  const [classifyError, setClassifyError] = useState<string | null>(null);
  const [classifyLoading, setClassifyLoading] = useState(false);

  const [retrieval, setRetrieval] = useState<RetrieveResponse | null>(null);
  const [retrieveError, setRetrieveError] = useState<string | null>(null);
  const [retrieveLoading, setRetrieveLoading] = useState(false);

  const [chosenIdx, setChosenIdx] = useState(0);

  const [draft, setDraft] = useState<DraftResponse | null>(null);
  const [draftLoading, setDraftLoading] = useState(false);
  const [draftError, setDraftError] = useState<string | null>(null);

  const [editedText, setEditedText] = useState('');
  const [showDiff, setShowDiff] = useState(false);

  const [feedbackStatus, setFeedbackStatus] = useState<FeedbackStatus | null>(null);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false);

  // Source-playbook content for the right-hand "Playbook source" panel.
  const [sourcePlaybook, setSourcePlaybook] = useState<PlaybookDetail | null>(null);

  // Cancel-on-unmount / on-ticket-change for the in-flight requests.
  const ticketRef = useRef(ticket.key);
  ticketRef.current = ticket.key;

  // Reset state whenever the ticket key changes, then try to rehydrate any
  // persisted workflow for this ticket (classification + retrieval + draft +
  // edit + feedback_status). Missing fields stay null so the operator sees
  // the right starting step (Classify button, retrieval list, etc.).
  useEffect(() => {
    setClassification(null);
    setClassifyError(null);
    setClassifyLoading(false);
    setRetrieval(null);
    setRetrieveError(null);
    setRetrieveLoading(false);
    setChosenIdx(0);
    setDraft(null);
    setDraftLoading(false);
    setDraftError(null);
    setEditedText('');
    setShowDiff(false);
    setFeedbackStatus(null);
    setFeedbackError(null);
    setFeedbackSubmitting(false);
    setSourcePlaybook(null);

    let cancelled = false;
    getAgentSession(ticket.key)
      .then((session) => {
        if (cancelled || !session) return;
        if (session.classification) setClassification(session.classification);
        if (session.retrieval) {
          setRetrieval(session.retrieval);
          if (session.draft_playbook_id) {
            const idx = session.retrieval.hits.findIndex(
              (h) => h.playbook_id === session.draft_playbook_id,
            );
            if (idx >= 0) setChosenIdx(idx);
          }
        }
        if (session.draft) {
          setDraft(session.draft);
          setEditedText(session.edited_text ?? session.draft.draft);
        }
        if (
          session.feedback_status === 'approved' ||
          session.feedback_status === 'edited' ||
          session.feedback_status === 'rejected'
        ) {
          setFeedbackStatus(session.feedback_status);
        }
      })
      .catch(() => {
        // No persisted session — fresh state is correct.
      });
    return () => {
      cancelled = true;
    };
  }, [ticket.key]);

  // Classification is manual — fired from the Classify button so the API isn't
  // billed on every refresh / navigation. The backend persists the result
  // under this ticket_id so a later reload restores the workflow.
  function handleClassify() {
    if (classifyLoading || classification) return;
    setClassifyLoading(true);
    setClassifyError(null);
    const myTicketKey = ticket.key;
    classifyTicket(
      {
        summary: ticket.summary,
        description: ticket.description,
        reporter_email: ticket.reporter_email,
        labels: ticket.labels,
      },
      myTicketKey,
    )
      .then((res) => {
        if (ticketRef.current !== myTicketKey) return;
        setClassification(res);
      })
      .catch((err: Error) => {
        if (ticketRef.current !== myTicketKey) return;
        setClassifyError(err.message);
      })
      .finally(() => {
        if (ticketRef.current === myTicketKey) setClassifyLoading(false);
      });
  }

  // Auto-run retrieve after a positive classification.
  useEffect(() => {
    if (!classification || classification.label !== 'support_request') return;
    if (retrieval || retrieveLoading || retrieveError) return;
    setRetrieveLoading(true);
    const myTicketKey = ticket.key;
    retrievePlaybooks(
      {
        summary: ticket.summary,
        description: ticket.description,
        labels: ticket.labels,
        top_k: 3,
      },
      myTicketKey,
    )
      .then((res) => {
        if (ticketRef.current !== myTicketKey) return;
        setRetrieval(res);
      })
      .catch((err: Error) => {
        if (ticketRef.current !== myTicketKey) return;
        setRetrieveError(err.message);
      })
      .finally(() => {
        if (ticketRef.current === myTicketKey) setRetrieveLoading(false);
      });
  }, [classification, retrieval, retrieveLoading, retrieveError, ticket]);

  // Load the chosen playbook's resolution sections for the right pane,
  // but only once the operator has clicked Generate draft.
  useEffect(() => {
    if (!draft || !retrieval) {
      setSourcePlaybook(null);
      return;
    }
    const chosen = retrieval.hits[chosenIdx];
    if (!chosen) return;
    let cancelled = false;
    getPlaybook(chosen.playbook_id)
      .then((pb) => {
        if (!cancelled) setSourcePlaybook(pb);
      })
      .catch(() => {
        if (!cancelled) setSourcePlaybook(null);
      });
    return () => {
      cancelled = true;
    };
  }, [draft, retrieval, chosenIdx]);

  const chosenHit: RetrievalHitOut | null = retrieval?.hits[chosenIdx] ?? null;

  function handleGenerateDraft() {
    if (!chosenHit) return;
    setDraftLoading(true);
    setDraftError(null);
    setDraft(null);
    setShowDiff(false);
    const myTicketKey = ticket.key;
    draftReply(
      {
        ticket_summary: ticket.summary,
        ticket_description: ticket.description,
        playbook_id: chosenHit.playbook_id,
      },
      myTicketKey,
    )
      .then((res) => {
        if (ticketRef.current !== myTicketKey) return;
        setDraft(res);
        setEditedText(res.draft);
      })
      .catch((err: Error) => {
        if (ticketRef.current !== myTicketKey) return;
        setDraftError(err.message);
      })
      .finally(() => {
        if (ticketRef.current === myTicketKey) setDraftLoading(false);
      });
  }

  async function handleSubmit(status: FeedbackStatus) {
    if (!draft || !chosenHit) return;
    setFeedbackSubmitting(true);
    setFeedbackError(null);
    try {
      await submitFeedback({
        ticket_id: ticket.key,
        playbook_id: chosenHit.playbook_id,
        draft_text: draft.draft,
        final_text:
          status === 'rejected'
            ? null
            : status === 'edited' || editedText !== draft.draft
            ? editedText
            : null,
        status,
      });
      setFeedbackStatus(status);
    } catch (err) {
      setFeedbackError((err as Error).message);
    } finally {
      setFeedbackSubmitting(false);
    }
  }

  async function handleRedo() {
    // Wipe the persisted session so a refresh doesn't immediately rehydrate
    // the old state we just discarded.
    try {
      await deleteAgentSession(ticket.key);
    } catch {
      // Non-blocking — local state still resets below.
    }
    setClassification(null);
    setRetrieval(null);
    setChosenIdx(0);
    setDraft(null);
    setEditedText('');
    setShowDiff(false);
    setFeedbackStatus(null);
    setSourcePlaybook(null);
  }

  function handleNextTicket() {
    const idx = tickets.findIndex((t) => t.key === ticket.key);
    if (idx < 0 || idx + 1 >= tickets.length) return;
    navigate(`/agent/${tickets[idx + 1].key}`);
  }

  const hasEdits = draft != null && editedText !== draft.draft;
  const isLastTicket = useMemo(() => {
    const idx = tickets.findIndex((t) => t.key === ticket.key);
    return idx < 0 || idx + 1 >= tickets.length;
  }, [tickets, ticket.key]);

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin">
      <div className="max-w-5xl mx-auto px-8 py-6 space-y-6">
        {/* Ticket card */}
        <TicketHeader ticket={ticket} />

        {/* If feedback submitted, swap the workflow for a confirmation panel. */}
        {feedbackStatus ? (
          <FeedbackDone
            ticket={ticket}
            status={feedbackStatus}
            isLastTicket={isLastTicket}
            onNext={handleNextTicket}
            onRedo={handleRedo}
          />
        ) : (
          <>
            <ClassifySection
              loading={classifyLoading}
              error={classifyError}
              classification={classification}
              onClassify={handleClassify}
            />

            {classification?.label === 'support_request' && (
              <RetrieveSection
                loading={retrieveLoading}
                error={retrieveError}
                retrieval={retrieval}
                chosenIdx={chosenIdx}
                onChoose={setChosenIdx}
                disabled={draft != null || draftLoading}
              />
            )}

            {classification?.label === 'support_request' && retrieval && retrieval.hits.length > 0 && (
              <DraftSection
                draft={draft}
                draftLoading={draftLoading}
                draftError={draftError}
                onGenerate={handleGenerateDraft}
                chosenHitTitle={chosenHit?.title ?? ''}
                editedText={editedText}
                onEditChange={setEditedText}
                showDiff={showDiff}
                onToggleDiff={() => setShowDiff((v) => !v)}
                hasEdits={hasEdits}
                feedbackSubmitting={feedbackSubmitting}
                feedbackError={feedbackError}
                onApprove={() => handleSubmit(hasEdits ? 'edited' : 'approved')}
                onReject={() => handleSubmit('rejected')}
                sourcePlaybook={sourcePlaybook}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Sub-sections
// ---------------------------------------------------------------------------

function TicketHeader({ ticket }: { ticket: TicketDetail }) {
  return (
    <section className="bg-panel-surface border border-panel-border rounded-lg p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="text-[11px] font-mono text-slate-500">{ticket.key}</div>
          <h2 className="mt-0.5 text-lg font-semibold tracking-tight text-slate-900 leading-snug">
            {ticket.summary}
          </h2>
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          <span className="text-[11px] text-slate-500">
            {ticket.status} · {ticket.priority ?? '—'}
          </span>
          <span className="text-[11px] text-slate-400">
            {ticket.reporter_email ?? 'unknown reporter'}
          </span>
        </div>
      </div>
      {ticket.labels.length > 0 && (
        <div className="mt-3 flex items-center gap-1.5 flex-wrap">
          {ticket.labels.map((l) => (
            <Chip key={l}>{l}</Chip>
          ))}
        </div>
      )}
      <div className="mt-4 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
        {ticket.description || <span className="text-slate-400 italic">No description.</span>}
      </div>
    </section>
  );
}


function ClassifySection({
  loading,
  error,
  classification,
  onClassify,
}: {
  loading: boolean;
  error: string | null;
  classification: ClassifyResponse | null;
  onClassify: () => void;
}) {
  return (
    <section>
      <div className="flex items-center gap-3 mb-3">
        <StepCircle n={1} />
        <h3 className="text-sm font-semibold text-slate-900">Classification</h3>
      </div>
      <div className="ml-10 bg-panel-surface border border-panel-border rounded-lg p-4">
        {!classification && !loading && !error && (
          <div className="flex items-center justify-between gap-3">
            <span className="text-sm text-slate-500">
              Run the classifier to decide whether this ticket needs a reply.
            </span>
            <button
              type="button"
              onClick={onClassify}
              className="px-4 py-1.5 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 transition-colors"
            >
              Classify
            </button>
          </div>
        )}
        {loading && (
          <div className="text-sm text-slate-400 flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            Classifying…
          </div>
        )}
        {error && (
          <div className="flex items-center justify-between gap-3">
            <div className="text-sm text-red-600">{error}</div>
            <button
              type="button"
              onClick={onClassify}
              className="px-3 py-1.5 text-sm border border-slate-200 text-slate-700 rounded hover:bg-slate-50"
            >
              Retry
            </button>
          </div>
        )}
        {classification && !loading && (
          <>
            <div className="flex items-center gap-3">
              <ClassificationPill label={classification.label} />
              <span className="text-[11px] text-slate-500 font-mono">
                conf {classification.confidence.toFixed(2)}
              </span>
            </div>
            {classification.reason && (
              <p className="mt-2 text-sm text-slate-600">{classification.reason}</p>
            )}
            {classification.label !== 'support_request' && (
              <div className="mt-3 px-3 py-2 bg-amber-50 border border-amber-200 rounded text-sm text-amber-800">
                Auto-close path — no reply needed.
              </div>
            )}
          </>
        )}
      </div>
    </section>
  );
}


function ClassificationPill({
  label,
}: {
  label: 'support_request' | 'internal_log' | 'spam_or_junk';
}) {
  const map = {
    support_request: { tone: 'bg-emerald-50 text-emerald-700 border-emerald-200', text: 'support request' },
    internal_log: { tone: 'bg-indigo-50 text-indigo-700 border-indigo-200', text: 'internal log' },
    spam_or_junk: { tone: 'bg-red-50 text-red-700 border-red-200', text: 'spam / junk' },
  };
  const { tone, text } = map[label];
  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium border rounded ${tone}`}>
      {text}
    </span>
  );
}


function RetrieveSection({
  loading,
  error,
  retrieval,
  chosenIdx,
  onChoose,
  disabled,
}: {
  loading: boolean;
  error: string | null;
  retrieval: RetrieveResponse | null;
  chosenIdx: number;
  onChoose: (i: number) => void;
  disabled: boolean;
}) {
  return (
    <section>
      <div className="flex items-center gap-3 mb-3">
        <StepCircle n={2} />
        <h3 className="text-sm font-semibold text-slate-900">Matched playbooks</h3>
      </div>
      <div className="ml-10 space-y-3">
        {loading && (
          <div className="text-sm text-slate-400 flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            Retrieving…
          </div>
        )}
        {error && <div className="text-sm text-red-600">{error}</div>}
        {retrieval && (
          <>
            <div className="text-[11px] text-slate-500">
              detected language: <span className="font-mono">{retrieval.detected_language ?? '—'}</span>
              {' · '}country: <span className="font-mono">{retrieval.detected_country ?? '—'}</span>
            </div>
            {retrieval.hits.map((h, i) => {
              const isChosen = i === chosenIdx;
              return (
                <button
                  key={h.playbook_id}
                  type="button"
                  onClick={() => onChoose(i)}
                  disabled={disabled}
                  className={`w-full text-left bg-panel-surface border rounded-lg p-4 transition-colors ${
                    isChosen
                      ? 'border-blue-400 ring-2 ring-blue-100'
                      : 'border-panel-border hover:border-blue-200'
                  } ${disabled ? 'cursor-not-allowed opacity-60' : ''}`}
                >
                  <div className="flex items-start gap-3">
                    <span
                      className={`inline-flex items-center justify-center w-5 h-5 mt-0.5 rounded-full text-[10px] font-semibold border ${
                        isChosen
                          ? 'bg-blue-500 text-white border-blue-500'
                          : 'bg-white text-slate-500 border-slate-300'
                      }`}
                    >
                      {isChosen ? '✓' : i + 1}
                    </span>
                    <div className="flex-1">
                      <div className="text-sm font-medium text-slate-900 leading-snug">
                        {h.title}
                      </div>
                      <div className="mt-0.5 text-[11px] text-slate-500 font-mono">
                        {h.playbook_id}
                      </div>
                      <div className="mt-2">
                        <ConfidenceBar score={h.score} />
                      </div>
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        <Chip tone="blue">{h.ticket_class}</Chip>
                        <Chip>{h.issue_category}</Chip>
                        {h.country_focus
                          .filter((c) => c !== 'other')
                          .map((c) => (
                            <Chip key={c}>{c}</Chip>
                          ))}
                        {h.project_keys.map((k) => (
                          <Chip key={k}>{k}</Chip>
                        ))}
                      </div>
                    </div>
                  </div>
                </button>
              );
            })}
          </>
        )}
      </div>
    </section>
  );
}


interface DraftSectionProps {
  draft: DraftResponse | null;
  draftLoading: boolean;
  draftError: string | null;
  onGenerate: () => void;
  chosenHitTitle: string;
  editedText: string;
  onEditChange: (v: string) => void;
  showDiff: boolean;
  onToggleDiff: () => void;
  hasEdits: boolean;
  feedbackSubmitting: boolean;
  feedbackError: string | null;
  onApprove: () => void;
  onReject: () => void;
  sourcePlaybook: PlaybookDetail | null;
}

function DraftSection(props: DraftSectionProps) {
  const {
    draft,
    draftLoading,
    draftError,
    onGenerate,
    chosenHitTitle,
    editedText,
    onEditChange,
    showDiff,
    onToggleDiff,
    hasEdits,
    feedbackSubmitting,
    feedbackError,
    onApprove,
    onReject,
    sourcePlaybook,
  } = props;

  return (
    <section>
      <div className="flex items-center gap-3 mb-3">
        <StepCircle n={3} />
        <h3 className="text-sm font-semibold text-slate-900">Draft & decide</h3>
      </div>
      <div className="ml-10 space-y-4">
        {!draft && (
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={onGenerate}
              disabled={draftLoading}
              className="px-4 py-1.5 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed transition-colors"
            >
              {draftLoading ? 'Drafting…' : 'Generate draft'}
            </button>
            <span className="text-[11px] text-slate-500">
              against <strong className="text-slate-700">{chosenHitTitle}</strong>
            </span>
          </div>
        )}
        {draftError && <div className="text-sm text-red-600">{draftError}</div>}

        {draft && (
          <>
            <div className="flex items-center gap-2 flex-wrap">
              <ActionPill action={draft.recommended_action} />
              <span className="text-[11px] text-slate-500">{draft.rationale}</span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-[1.2fr_1fr] gap-4">
              {/* Draft editor (left) */}
              <div className="bg-panel-surface border border-panel-border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <SectionHeading>Draft reply</SectionHeading>
                  {hasEdits && (
                    <button
                      type="button"
                      onClick={onToggleDiff}
                      className="text-[11px] text-blue-600 hover:text-blue-700"
                    >
                      {showDiff ? 'Hide diff' : 'Show diff'}
                    </button>
                  )}
                </div>
                <textarea
                  value={editedText}
                  onChange={(e) => onEditChange(e.target.value)}
                  rows={14}
                  className="w-full px-3 py-2 text-sm border border-slate-200 rounded font-sans focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15 resize-y leading-relaxed"
                />
                {hasEdits && showDiff && (
                  <div className="mt-3 p-3 bg-slate-50 border border-panel-border rounded">
                    <div className="text-[11px] font-semibold tracking-wider uppercase text-slate-500 mb-2">
                      Diff vs. original draft
                    </div>
                    <DiffView original={draft.draft} edited={editedText} />
                  </div>
                )}
              </div>

              {/* Playbook source (right) */}
              <div className="bg-panel-surface border border-panel-border rounded-lg p-4">
                <SectionHeading>Playbook source</SectionHeading>
                {sourcePlaybook ? (
                  <div className="space-y-3 text-sm">
                    <div>
                      <div className="font-medium text-slate-900">{sourcePlaybook.title}</div>
                      <div className="text-[11px] font-mono text-slate-500 mt-0.5">
                        {sourcePlaybook.id}
                      </div>
                    </div>
                    {sourcePlaybook.when_applies && (
                      <div>
                        <div className="text-[11px] font-semibold tracking-wider uppercase text-slate-500 mb-1">
                          When this applies
                        </div>
                        <div className="prose prose-sm prose-slate max-w-none">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {sourcePlaybook.when_applies}
                          </ReactMarkdown>
                        </div>
                      </div>
                    )}
                    {sourcePlaybook.resolution_steps.length > 0 && (
                      <div>
                        <div className="text-[11px] font-semibold tracking-wider uppercase text-slate-500 mb-2">
                          Resolution flow
                        </div>
                        <ol className="space-y-2">
                          {sourcePlaybook.resolution_steps.map((s, i) => (
                            <li key={i} className="flex gap-2 items-start">
                              <span className="inline-flex items-center justify-center w-5 h-5 mt-0.5 rounded-full bg-blue-50 text-blue-700 text-[10px] font-semibold border border-blue-200 shrink-0">
                                {i + 1}
                              </span>
                              <span className="text-slate-700 text-sm leading-relaxed">{s}</span>
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-sm text-slate-400">Loading playbook…</div>
                )}
              </div>
            </div>

            {/* Decide row */}
            <div className="flex items-center justify-between gap-3 pt-2">
              <div className="text-[11px] text-slate-400">
                {hasEdits
                  ? 'Edits detected — Approve will log this as edited.'
                  : 'No edits — Approve will log this as approved.'}
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={onReject}
                  disabled={feedbackSubmitting}
                  className="px-3 py-1.5 text-sm border border-red-200 text-red-700 bg-white rounded hover:bg-red-50 disabled:opacity-60"
                >
                  Reject
                </button>
                <button
                  type="button"
                  onClick={onApprove}
                  disabled={feedbackSubmitting}
                  className="px-4 py-1.5 text-sm font-medium text-white bg-emerald-600 rounded hover:bg-emerald-700 disabled:opacity-60"
                >
                  {hasEdits ? 'Approve & save edit' : 'Approve & send'}
                </button>
              </div>
            </div>
            {feedbackError && <div className="text-sm text-red-600">{feedbackError}</div>}
          </>
        )}
      </div>
    </section>
  );
}


function ActionPill({
  action,
}: {
  action: 'send_draft' | 'send_with_review' | 'escalate_to_human' | 'auto_close';
}) {
  const map = {
    send_draft: { tone: 'bg-emerald-50 text-emerald-700 border-emerald-200', text: 'send draft' },
    send_with_review: { tone: 'bg-blue-50 text-blue-700 border-blue-200', text: 'send with review' },
    escalate_to_human: { tone: 'bg-amber-50 text-amber-700 border-amber-200', text: 'escalate to human' },
    auto_close: { tone: 'bg-slate-50 text-slate-700 border-slate-200', text: 'auto close' },
  };
  const { tone, text } = map[action];
  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium border rounded ${tone}`}>
      {text}
    </span>
  );
}


function FeedbackDone({
  ticket,
  status,
  isLastTicket,
  onNext,
  onRedo,
}: {
  ticket: TicketDetail;
  status: FeedbackStatus;
  isLastTicket: boolean;
  onNext: () => void;
  onRedo: () => void;
}) {
  const map = {
    approved: { tone: 'bg-emerald-50 border-emerald-200', text: `Reply approved for ${ticket.key}.` },
    edited: { tone: 'bg-blue-50 border-blue-200', text: `Edited reply logged for ${ticket.key}.` },
    rejected: { tone: 'bg-red-50 border-red-200', text: `Rejection logged for ${ticket.key} — no reply sent.` },
  };
  return (
    <div className={`border rounded-lg p-5 ${map[status].tone}`}>
      <div className="text-sm font-medium text-slate-900">{map[status].text}</div>
      <p className="text-[11px] text-slate-500 mt-1">
        Stored in feedback.sqlite3 — visible at /feedback/stats.
      </p>
      <div className="mt-4 flex items-center gap-2">
        <button
          type="button"
          onClick={onNext}
          disabled={isLastTicket}
          className="px-4 py-1.5 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400"
        >
          Next ticket
        </button>
        <button
          type="button"
          onClick={onRedo}
          className="px-3 py-1.5 text-sm border border-slate-200 text-slate-700 rounded hover:bg-slate-50"
        >
          Redo this ticket
        </button>
        {isLastTicket && (
          <span className="text-[11px] text-slate-400">No more tickets in the sample.</span>
        )}
      </div>
    </div>
  );
}
