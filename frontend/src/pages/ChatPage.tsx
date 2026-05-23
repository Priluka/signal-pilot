/** Chat tab — left history sidebar + free-form Q&A on the right.
 *
 * All streaming + answer + sources state lives in <ChatStoreProvider> at the
 * app root, so navigating away does NOT abort the in-flight stream. The
 * answer keeps growing on the server, persists on done, and is here when
 * the operator comes back.
 *
 * The main area is split into a sticky input zone on top (textarea inside
 * a focus-ring container with top-k + actions baked into its bottom bar)
 * and a scrollable answer area below. The answer uses a left accent
 * border instead of a full card so the prose reads like a document, not
 * a form field.
 */
import { useEffect, useLayoutEffect, useMemo, useRef } from 'react';
import { ArrowUp, Sparkles } from 'lucide-react';

import { ChatAnswer, buildCitationMap } from '../components/ChatAnswer';
import { ChatHistorySidebar } from '../components/ChatHistorySidebar';
import { useChatStore } from '../lib/chatStore';


// Cap the auto-grown textarea around ~9 lines so the answer area is
// never crushed by an absurdly long pasted question. Beyond this we
// flip overflow to scrolling.
const TEXTAREA_MAX_PX = 200;


const EXAMPLE_QUESTIONS = [
  'What do I tell a customer who got a parking fine despite paying via the app?',
  'How do I handle a duplicate-charge refund request?',
  'Što napraviti kad korisnik ne može aktivirati parkiranje?',
];


export function ChatPage() {
  const chat = useChatStore();
  const answerScrollRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // Auto-grow the textarea to fit content up to a cap. Reset to 'auto'
  // first so shrink-back (e.g. after Backspace or programmatic clear)
  // measures correctly. Beyond the cap we flip overflow-y to auto so
  // the scrollbar appears only when the box can't grow any further.
  useLayoutEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    const next = Math.min(el.scrollHeight, TEXTAREA_MAX_PX);
    el.style.height = `${next}px`;
    el.style.overflowY = el.scrollHeight > TEXTAREA_MAX_PX ? 'auto' : 'hidden';
  }, [chat.question]);

  // Auto-scroll the answer panel as new text streams in.
  useEffect(() => {
    if (chat.status === 'streaming' && answerScrollRef.current) {
      answerScrollRef.current.scrollIntoView({ block: 'end', behavior: 'smooth' });
    }
  }, [chat.answer, chat.status]);

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    // Enter submits; Shift+Enter inserts a newline (standard chat UX).
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      chat.ask();
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    chat.ask();
  }

  const citations = useMemo(
    () => buildCitationMap(chat.answer, chat.sources, chat.citationIndex),
    [chat.answer, chat.sources, chat.citationIndex],
  );

  const isStreaming = chat.status === 'streaming';
  // True when the model produced an answer but emitted zero inline
  // citations — operator should treat the claims as ungrounded.
  const noCitationsDetected =
    chat.status === 'done' &&
    chat.answer.length > 0 &&
    chat.sources.length > 0 &&
    !/\[[a-z0-9][a-z0-9_-]+\]/.test(chat.answer);

  return (
    <div className="h-full flex">
      <ChatHistorySidebar
        activeId={chat.activeSessionId}
        onSelect={chat.loadSession}
        onNewChat={chat.clear}
      />
      <div className="flex-1 flex flex-col h-full overflow-hidden min-w-0">
        {/* Answer — takes all space, scrolls; scrollbar flush with panel edge */}
        <div className="flex-1 overflow-y-auto scrollbar-thin min-w-0">
          <div className="max-w-3xl mx-auto w-full px-6 pt-12 pb-6 min-w-0">
            {chat.askedQuestion ? (
              <section className="min-w-0">
                <div className="min-w-0 break-words">
                  {chat.answer ? (
                    <ChatAnswer text={chat.answer} citations={citations} />
                  ) : isStreaming ? (
                    <div className="text-[13px] text-ink-muted flex items-center gap-2">
                      <span className="inline-block w-2 h-2 rounded-full bg-accent animate-pulse" />
                      Retrieving and drafting…
                    </div>
                  ) : null}
                  {chat.status === 'error' && (
                    <div className="mt-3 text-[13px] text-red-600">
                      {chat.errorMsg}
                    </div>
                  )}
                  <div ref={answerScrollRef} />
                </div>

                {noCitationsDetected && (
                  <p className="mt-3 text-[11px] text-amber-600">
                    No inline citations detected — answer may be ungrounded.
                  </p>
                )}
              </section>
            ) : (
              <EmptyState
                onPick={(q) => chat.setQuestion(q)}
                disabled={isStreaming}
              />
            )}
          </div>
        </div>

        {/* Input — bottom, pinned */}
        <div className="shrink-0 px-6 py-4">
          <form onSubmit={onSubmit} className="max-w-3xl mx-auto w-full">
            <div className="bg-app border border-line-strong rounded-xl overflow-hidden shadow-sm focus-within:border-[#c8c8c8] dark:focus-within:border-[#5a5a5a] focus-within:shadow-md transition-[box-shadow,border-color] duration-150 flex flex-col">
              <textarea
                ref={textareaRef}
                value={chat.question}
                onChange={(e) => chat.setQuestion(e.target.value)}
                onKeyDown={onKeyDown}
                placeholder="e.g. What do I tell a Croatian customer who got a parking fine despite paying via the app?"
                disabled={isStreaming}
                rows={1}
                style={{ maxHeight: `${TEXTAREA_MAX_PX}px` }}
                className="w-full bg-transparent px-4 pt-3 pb-1 text-[13px] text-ink placeholder:text-ink-muted resize-none focus:outline-none overflow-y-hidden block leading-[1.5]"
              />
              <div className="flex items-center justify-end px-2 pb-2 pt-1">
                <button
                  type="submit"
                  disabled={!chat.question.trim() || isStreaming}
                  aria-label={isStreaming ? 'Streaming' : 'Send'}
                  className="w-8 h-8 rounded-lg bg-accent hover:bg-accent-hover text-white flex items-center justify-center transition-colors duration-150 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  {isStreaming ? (
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-white/80 animate-pulse" />
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
        Ask a question about your playbooks
      </div>
      <div className="flex flex-col gap-2 w-full max-w-md">
        {EXAMPLE_QUESTIONS.map((q) => (
          <button
            key={q}
            type="button"
            disabled={disabled}
            onClick={() => onPick(q)}
            className="text-left text-[12px] text-ink-body bg-app border border-line rounded-lg px-3 py-2 hover:bg-hover hover:border-line-strong transition-colors duration-150 disabled:opacity-40"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
