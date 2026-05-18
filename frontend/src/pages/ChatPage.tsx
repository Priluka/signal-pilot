/** Chat tab — left history sidebar + free-form Q&A on the right.
 *
 * All streaming + answer + sources state lives in <ChatStoreProvider> at the
 * app root, so navigating away does NOT abort the in-flight stream. The
 * answer keeps growing on the server, persists on done, and is here when
 * the operator comes back.
 */
import { useEffect, useMemo, useRef } from 'react';

import { ChatAnswer, buildCitationMap } from '../components/ChatAnswer';
import { ChatHistorySidebar } from '../components/ChatHistorySidebar';
import { SourceCard } from '../components/SourceCard';
import { useChatStore } from '../lib/chatStore';


export function ChatPage() {
  const chat = useChatStore();
  const answerScrollRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll the answer panel as new text streams in.
  useEffect(() => {
    if (chat.status === 'streaming' && answerScrollRef.current) {
      answerScrollRef.current.scrollIntoView({ block: 'end', behavior: 'smooth' });
    }
  }, [chat.answer, chat.status]);

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      chat.ask();
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    chat.ask();
  }

  const citations = useMemo(
    () => buildCitationMap(chat.answer, chat.sources),
    [chat.answer, chat.sources],
  );
  const orderedSources = useMemo(() => {
    return [...chat.sources].sort((a, b) => {
      const na = citations.get(a.playbook_id)?.number ?? 999;
      const nb = citations.get(b.playbook_id)?.number ?? 999;
      return na - nb;
    });
  }, [chat.sources, citations]);

  const isStreaming = chat.status === 'streaming';

  return (
    <div className="h-full flex">
      <ChatHistorySidebar
        activeId={chat.activeSessionId}
        onSelect={chat.loadSession}
        onNewChat={chat.clear}
      />
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        <div className="max-w-4xl mx-auto px-8 py-8 space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Chat</h1>
              <p className="text-sm text-slate-500 mt-0.5">
                Ask a free-form question — the answer is grounded in the top-k retrieved playbooks and cites them inline.
              </p>
            </div>
            <span className="text-[11px] font-mono text-slate-400">Sonnet 4.6</span>
          </div>

          <form
            onSubmit={onSubmit}
            className="bg-panel-surface border border-panel-border rounded-lg p-4"
          >
            <textarea
              value={chat.question}
              onChange={(e) => chat.setQuestion(e.target.value)}
              onKeyDown={onKeyDown}
              rows={3}
              placeholder="e.g. What do I tell a Croatian customer who got a parking fine despite paying via the app?"
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15 resize-y"
              disabled={isStreaming}
            />
            <div className="mt-3 flex items-center justify-between">
              <label className="text-xs text-slate-500 flex items-center gap-2">
                Top-k:
                <input
                  type="number"
                  min={1}
                  max={5}
                  value={chat.topK}
                  onChange={(e) => chat.setTopK(Math.max(1, Math.min(5, Number(e.target.value))))}
                  className="w-12 px-1.5 py-0.5 text-xs border border-slate-200 rounded font-mono tabular-nums"
                />
                <span className="text-[11px] text-slate-400">playbooks consulted</span>
              </label>
              <div className="flex items-center gap-2">
                {(chat.status === 'done' || chat.status === 'error' || chat.askedQuestion) && (
                  <button
                    type="button"
                    onClick={chat.clear}
                    className="px-3 py-1.5 text-sm border border-slate-200 text-slate-700 rounded hover:bg-slate-50"
                  >
                    {isStreaming ? 'Cancel' : 'Clear'}
                  </button>
                )}
                <button
                  type="submit"
                  disabled={!chat.question.trim() || isStreaming}
                  className="px-4 py-1.5 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed transition-colors"
                >
                  {isStreaming ? 'Thinking…' : 'Ask'}
                </button>
              </div>
            </div>
            <p className="mt-2 text-[11px] text-slate-400">
              Cmd/Ctrl + Enter to submit. Stream keeps running even if you navigate away.
            </p>
          </form>

          {chat.askedQuestion && (
            <section>
              <header className="mb-2 flex items-center justify-between">
                <h2 className="text-[11px] font-semibold tracking-wider uppercase text-slate-500">
                  Answer
                </h2>
                <div className="text-[11px] text-slate-400">
                  grounded in {chat.sources.length || chat.topK} playbook{chat.sources.length === 1 ? '' : 's'}
                  {' · asked: '}
                  <em className="text-slate-500">{chat.askedQuestion}</em>
                </div>
              </header>
              <div className="bg-panel-surface border border-panel-border rounded-lg p-5">
                {chat.answer ? (
                  <ChatAnswer text={chat.answer} citations={citations} />
                ) : isStreaming ? (
                  <div className="text-sm text-slate-400 flex items-center gap-2">
                    <span className="inline-block w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                    Retrieving and drafting…
                  </div>
                ) : null}
                {chat.status === 'error' && (
                  <div className="mt-3 text-sm text-red-600">{chat.errorMsg}</div>
                )}
                <div ref={answerScrollRef} />
              </div>
            </section>
          )}

          {chat.sources.length > 0 && (
            <section>
              <header className="mb-2 flex items-center justify-between">
                <h2 className="text-[11px] font-semibold tracking-wider uppercase text-slate-500">
                  Sources
                </h2>
                {chat.status === 'done' &&
                  Array.from(citations.values()).every((c) => c.number > chat.sources.length) && (
                    <span className="text-[11px] text-amber-600">
                      No inline citations detected — answer may be ungrounded.
                    </span>
                  )}
              </header>
              <ol className="space-y-2 list-none pl-0">
                {orderedSources.map((hit) => {
                  const number = citations.get(hit.playbook_id)?.number ?? 0;
                  return <SourceCard key={hit.playbook_id} hit={hit} number={number} />;
                })}
              </ol>
            </section>
          )}

          {!chat.askedQuestion && (
            <div className="text-center text-sm text-slate-400 py-8">
              Try asking about a parking-fine dispute, a payment failure, a missing invoice, …
              Past chats appear on the left.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
