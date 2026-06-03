/** Chat tab — multi-turn agentic conversations.
 *
 * Layout: left rail = ChatThreadsSidebar (list of threads), right pane =
 * scrolling conversation (turns rendered in order) + sticky input box
 * at the bottom. Each turn renders as a user bubble (right-aligned)
 * followed by the agent's response area — a collapsible skill
 * timeline (only present if the agent called tools) plus the prose
 * answer with inline citations.
 *
 * Streaming UX:
 *  - sending a message appends an optimistic turn instantly
 *  - skill events stream into that turn's events array as they fire
 *  - the agent's prose text drains via a RAF animator (smooth typing)
 *  - on ``done`` the citation index is finalised + sidebar refreshes
 *  - input is disabled while ``streamingTurnId != null``
 *
 * Refresh resilience lives in the store: on mount we restore the
 * active thread from localStorage and re-attach SSE if the last turn
 * is still mid-stream server-side.
 */
import { useEffect, useLayoutEffect, useMemo, useRef } from 'react';
import { ArrowUp, Sparkles, Square } from 'lucide-react';

import { AgenticSkillTimeline } from '../components/AgenticSkillTimeline';
import { ChatAnswer, buildCitationMap } from '../components/ChatAnswer';
import { ChatThreadsSidebar } from '../components/ChatThreadsSidebar';
import { useChatStore } from '../lib/chatStore';
import type { ChatTurn } from '../lib/types';


// Cap the auto-grown textarea around ~9 lines so the answer area is
// never crushed by an absurdly long pasted question.
const TEXTAREA_MAX_PX = 200;


const EXAMPLE_QUESTIONS = [
  'Provjeri W-55123K — kupac kaže dvostruka naplata u Millennium City Wien.',
  'Kako da postupim s B2B Croatian partnerom koji traži R1 invoice?',
  'Što napraviti kad korisniku ne radi ticketless u Beču?',
];


export function ChatPage() {
  const chat = useChatStore();
  const scrollEndRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // Auto-grow the textarea to fit content up to a cap.
  useLayoutEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    const next = Math.min(el.scrollHeight, TEXTAREA_MAX_PX);
    el.style.height = `${next}px`;
    el.style.overflowY = el.scrollHeight > TEXTAREA_MAX_PX ? 'auto' : 'hidden';
  }, [chat.pendingText]);

  // Scroll to the newest turn whenever turns grow OR the streaming
  // turn's answer extends. Smooth so the operator sees the flow.
  const streamingText =
    chat.streamingTurnId != null
      ? chat.turns.find((t) => t.id === chat.streamingTurnId)
          ?.final_assistant_text
      : null;
  useEffect(() => {
    if (scrollEndRef.current) {
      scrollEndRef.current.scrollIntoView({
        block: 'end',
        behavior: 'smooth',
      });
    }
  }, [chat.turns.length, streamingText]);

  const isStreaming = chat.streamingTurnId != null;

  // ESC anywhere on the chat page interrupts an in-flight turn —
  // the textarea is ``disabled`` while streaming so its keydown
  // wouldn't fire; a document-level listener catches the key
  // regardless of focus. Cleanup releases the listener so background
  // tabs don't accumulate handlers.
  useEffect(() => {
    if (!isStreaming) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        void chat.interruptStream();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isStreaming, chat]);

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      chat.sendMessage();
      return;
    }
    // ESC interrupts the in-flight turn — Claude Code pattern.
    // Only fires when something is actually streaming; otherwise the
    // operator's ESC keypress is a no-op (avoids accidentally
    // cancelling the wrong thing).
    if (e.key === 'Escape' && isStreaming) {
      e.preventDefault();
      void chat.interruptStream();
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (isStreaming) {
      // Submit button doubles as Stop when streaming.
      void chat.interruptStream();
      return;
    }
    chat.sendMessage();
  }

  const hasConversation = chat.turns.length > 0;

  return (
    <div className="h-full flex">
      <ChatThreadsSidebar />
      <div className="flex-1 flex flex-col h-full overflow-hidden min-w-0">
        {/* Scrolling conversation */}
        <div className="flex-1 overflow-y-auto scrollbar-thin min-w-0">
          <div className="max-w-3xl mx-auto w-full px-6 pt-12 pb-6 min-w-0">
            {hasConversation ? (
              <div className="space-y-10 min-w-0">
                {chat.turns.map((turn, idx) => (
                  <TurnView
                    key={turn.id}
                    turn={turn}
                    // Tell each TurnView whether ANY prior turn in
                    // this thread already brought back skill-grounded
                    // data. Carries the "we have real evidence in
                    // scope" signal across turn boundaries so the
                    // "no inline citations" warning doesn't yell
                    // about a follow-up that legitimately answers
                    // from earlier tool_results.
                    priorTurnsGrounded={chat.turns
                      .slice(0, idx)
                      .some((t) =>
                        t.events.some(
                          (e) =>
                            e.type === 'skill_executed'
                            && e.ok
                            && e.result !== null,
                        ),
                      )}
                  />
                ))}
                <div ref={scrollEndRef} />
              </div>
            ) : (
              <EmptyState
                onPick={(q) => chat.setPendingText(q)}
                disabled={isStreaming}
              />
            )}
          </div>
        </div>

        {/* Input — bottom, pinned */}
        <div className="shrink-0 px-6 py-4">
          {/* Network / send error — surface ABOVE the textarea so the
              operator notices the failure regardless of conversation
              state (empty thread vs mid-conversation). Auto-dismisses
              when they submit a successful turn. */}
          {chat.errorMsg && (
            <div className="max-w-3xl mx-auto w-full mb-2 text-[12px] text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 rounded-md px-3 py-2 flex items-center justify-between">
              <span>{chat.errorMsg}</span>
              <button
                type="button"
                onClick={() => chat.clearError()}
                className="text-red-500 hover:text-red-700 text-[14px] leading-none px-1"
                aria-label="Dismiss error"
              >
                ×
              </button>
            </div>
          )}
          <form onSubmit={onSubmit} className="max-w-3xl mx-auto w-full">
            <div className="bg-app border border-line-strong rounded-xl overflow-hidden shadow-sm focus-within:border-[#c8c8c8] dark:focus-within:border-[#5a5a5a] focus-within:shadow-md transition-[box-shadow,border-color] duration-150 flex flex-col">
              <textarea
                ref={textareaRef}
                value={chat.pendingText}
                onChange={(e) => chat.setPendingText(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder={
                  isStreaming
                    ? 'Agent is working — wait for it to finish before sending the next message…'
                    : hasConversation
                      ? 'Reply to the agent…'
                      : 'Ask anything. Mention a plate, ticket, or topic to start.'
                }
                disabled={isStreaming}
                rows={1}
                style={{ maxHeight: `${TEXTAREA_MAX_PX}px` }}
                className="w-full bg-transparent px-4 pt-3 pb-1 text-[13px] text-ink placeholder:text-ink-muted resize-none focus:outline-none overflow-y-hidden block leading-[1.5]"
              />
              <div className="flex items-center justify-between px-2 pb-2 pt-1">
                {/* Hint about ESC when streaming so the operator
                    discovers the keyboard shortcut without needing
                    a help popup. Empty when idle to keep the box
                    quiet. */}
                <div className="text-[10px] text-ink-muted pl-2 select-none">
                  {isStreaming ? 'Press ESC or click ▢ to stop' : ''}
                </div>
                <button
                  type="submit"
                  // Submit button stays enabled WHILE streaming so it
                  // can double as Stop. Disabled only when the
                  // textarea is empty AND we're not streaming.
                  disabled={!isStreaming && !chat.pendingText.trim()}
                  aria-label={isStreaming ? 'Stop' : 'Send'}
                  className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors duration-150 disabled:opacity-40 disabled:cursor-not-allowed ${
                    isStreaming
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-btn-primary hover:bg-btn-primary-hover text-btn-primary-fg'
                  }`}
                >
                  {isStreaming ? (
                    <Square width={12} height={12} strokeWidth={2.5} fill="currentColor" />
                  ) : (
                    <ArrowUp width={16} height={16} strokeWidth={2.25} />
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// One turn — user bubble + agent reply + per-turn skill timeline.
// ---------------------------------------------------------------------------


function TurnView({
  turn,
  priorTurnsGrounded = false,
}: {
  turn: ChatTurn;
  /** Set by the caller when ANY earlier turn in the same thread
   *  brought back skill-grounded data. Used to suppress the
   *  "no inline citations" warning on follow-up turns that
   *  reference that earlier data without firing a fresh skill. */
  priorTurnsGrounded?: boolean;
}) {
  const citations = useMemo(
    () =>
      buildCitationMap(
        turn.final_assistant_text,
        turn.sources,
        turn.citation_index,
      ),
    [turn.final_assistant_text, turn.sources, turn.citation_index],
  );

  const isStreaming = turn.status === 'streaming';
  const isError = turn.status === 'error';

  // Real (non-hallucinated) citation count for the per-turn header
  // and the "grounded in N" hint when no skills fired.
  const realCitedCount = turn.citation_index.filter((c) => c.exists).length;
  const hasToolCalls = turn.events.some((e) => e.type === 'skill_executed');
  // Same heuristic as before — "no citations detected" warning is
  // only meaningful when the answer wasn't grounded by skill data.
  const skillsGroundedAnswer = turn.events.some(
    (e) => e.type === 'skill_executed' && e.ok && e.result !== null,
  );
  const noCitationsDetected =
    turn.status === 'done' &&
    turn.final_assistant_text.length > 0 &&
    turn.sources.length > 0 &&
    !skillsGroundedAnswer &&
    !priorTurnsGrounded &&
    !/\[[a-z0-9][a-z0-9_-]+\]/.test(turn.final_assistant_text);

  return (
    <section className="min-w-0">
      {/* User question bubble — right-aligned */}
      <div className="flex justify-end mb-6">
        <div className="bg-app rounded-2xl rounded-br-sm px-4 py-3 max-w-[70%] ml-auto text-[13px] text-ink whitespace-pre-wrap break-words">
          {turn.user_text}
        </div>
      </div>

      {/* Compaction hint — appears when the multi-turn compaction
          layer trimmed context for THIS turn. Quiet muted line, no
          panic; just an honest signal that older history is now
          summarised in the model's view. */}
      {turn.events
        .filter((e): e is Extract<typeof e, { type: 'compacted' }> =>
          e.type === 'compacted',
        )
        .map((e, i) => (
          <div
            key={`cmp-${i}`}
            className="text-[11px] text-ink-muted italic mb-3"
          >
            Older messages summarised to fit context (tier {e.tier}
            {e.dropped_turns > 0 ? `, dropped ${e.dropped_turns} turn${e.dropped_turns === 1 ? '' : 's'}` : ''}
            ).
          </div>
        ))}

      {/* Skill timeline — only if any events fired */}
      <AgenticSkillTimeline
        events={turn.events}
        isStreaming={isStreaming}
        sessionId={turn.id}
        citationCount={realCitedCount}
      />

      {/* Grounded-in line when no tools were called but citations
          do exist — quiet context above the prose. */}
      {!hasToolCalls && realCitedCount > 0 && (
        <div className="text-[11px] text-ink-muted mb-3">
          grounded in {realCitedCount} playbook
          {realCitedCount === 1 ? '' : 's'}
        </div>
      )}

      {/* Agent reply */}
      <div className="min-w-0 break-words">
        {turn.final_assistant_text ? (
          <ChatAnswer text={turn.final_assistant_text} citations={citations} />
        ) : isStreaming ? (
          <div className="text-[13px] text-ink-muted flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-accent animate-pulse" />
            {(() => {
              // Latest thinking event tells us which iteration the
              // agent is on — gives the operator a depth hint during
              // long multi-skill turns instead of a generic spinner.
              const latestThinking = [...turn.events]
                .reverse()
                .find(
                  (e): e is Extract<typeof e, { type: 'thinking' }> =>
                    e.type === 'thinking',
                );
              if (turn.events.length === 0) return 'Retrieving and drafting…';
              if (latestThinking && latestThinking.iteration > 1) {
                return `Thinking (step ${latestThinking.iteration})…`;
              }
              return 'Composing response…';
            })()}
          </div>
        ) : null}
        {isError && (() => {
          const msg = turn.error_message || 'Unknown error';
          // Distinguish operator-triggered cancel vs cost-cap vs real
          // error so the operator gets the right cue. Production: a
          // generic red bar conflates 'I pressed stop' with 'something
          // broke', which costs trust.
          const isInterrupt = msg.startsWith('Cancelled by operator');
          const isCostCap = msg.startsWith('Per-turn cost cap exceeded');
          if (isInterrupt) {
            return (
              <div className="mt-3 text-[12px] text-ink-muted italic">
                Stopped by operator.
              </div>
            );
          }
          if (isCostCap) {
            return (
              <div className="mt-3 text-[12px] text-amber-700 bg-amber-50 dark:bg-amber-900/20 dark:text-amber-300 border border-amber-200 dark:border-amber-800 rounded px-3 py-2">
                <div className="font-medium">Cost cap reached</div>
                <div className="opacity-80">{msg}</div>
                <div className="opacity-70 mt-1">
                  The turn was aborted before exhausting budget. Adjust
                  CHAT_TURN_COST_CAP_USD if this is a planned expensive
                  query.
                </div>
              </div>
            );
          }
          return (
            <div className="mt-3 text-[13px] text-red-600">
              {msg}
            </div>
          );
        })()}
      </div>

      {noCitationsDetected && (
        <p className="mt-3 text-[11px] text-amber-600">
          No inline citations detected — answer may be ungrounded.
        </p>
      )}
    </section>
  );
}


// ---------------------------------------------------------------------------
// Empty state — icon + prompt + clickable example chips
// ---------------------------------------------------------------------------


function EmptyState({
  onPick,
  disabled,
}: {
  onPick: (q: string) => void;
  disabled: boolean;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <Sparkles
        width={40}
        height={40}
        strokeWidth={1.5}
        className="text-ink-muted opacity-40 mb-4"
      />
      <div className="text-[13px] text-ink-muted mb-6">
        Multi-turn agentic chat — ask about a plate, a ticket, or a
        general policy. The agent will look up real data and remember
        context across turns.
      </div>
      <div className="flex flex-col gap-2 items-center w-full max-w-2xl">
        {EXAMPLE_QUESTIONS.map((q) => (
          <button
            key={q}
            type="button"
            onClick={() => onPick(q)}
            disabled={disabled}
            className="text-[12px] text-left text-ink-body bg-app border border-line rounded-lg px-3 py-2 hover:bg-hover hover:border-line-strong transition-colors duration-150 disabled:opacity-40 disabled:cursor-not-allowed w-full"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
