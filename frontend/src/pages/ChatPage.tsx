/** Chat tab — free-form question → streamed Claude answer over top-k playbooks. */
import { useEffect, useRef, useState } from 'react';

import { ChatAnswer } from '../components/ChatAnswer';
import { SourceCard } from '../components/SourceCard';
import { streamChatAnswer } from '../lib/api';
import type { RetrievalHitOut } from '../lib/types';


type Status = 'idle' | 'streaming' | 'done' | 'error';


export function ChatPage() {
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(3);

  const [status, setStatus] = useState<Status>('idle');
  const [askedQuestion, setAskedQuestion] = useState('');
  const [sources, setSources] = useState<RetrievalHitOut[]>([]);
  const [answer, setAnswer] = useState('');
  const [citedIds, setCitedIds] = useState<string[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);
  const answerScrollRef = useRef<HTMLDivElement | null>(null);

  // Cancel any in-flight stream when the user leaves the page.
  useEffect(() => () => abortRef.current?.abort(), []);

  // Auto-scroll the answer panel as text streams in.
  useEffect(() => {
    if (status === 'streaming' && answerScrollRef.current) {
      answerScrollRef.current.scrollIntoView({ block: 'end', behavior: 'smooth' });
    }
  }, [answer, status]);

  function handleSubmit(e?: React.FormEvent) {
    e?.preventDefault();
    const q = question.trim();
    if (!q || status === 'streaming') return;

    abortRef.current?.abort();
    setAskedQuestion(q);
    setSources([]);
    setAnswer('');
    setCitedIds([]);
    setErrorMsg(null);
    setStatus('streaming');

    abortRef.current = streamChatAnswer(q, topK, {
      onSources: (e) => setSources(e.hits),
      onDelta: (e) => setAnswer((prev) => prev + e.text),
      onDone: (e) => {
        setAnswer(e.answer);
        setCitedIds(e.cited_ids);
        setStatus('done');
      },
      onError: (e) => {
        setErrorMsg(e.message);
        setStatus('error');
      },
    });
  }

  function handleClear() {
    abortRef.current?.abort();
    setQuestion('');
    setAskedQuestion('');
    setSources([]);
    setAnswer('');
    setCitedIds([]);
    setErrorMsg(null);
    setStatus('idle');
  }

  const citedSet = new Set(citedIds);

  return (
    <div className="h-full overflow-y-auto scrollbar-thin">
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

        {/* Question form */}
        <form
          onSubmit={handleSubmit}
          className="bg-panel-surface border border-panel-border rounded-lg p-4"
        >
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSubmit();
            }}
            rows={3}
            placeholder="e.g. What do I tell a Croatian customer who got a parking fine despite paying via the app?"
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15 resize-y"
            disabled={status === 'streaming'}
          />
          <div className="mt-3 flex items-center justify-between">
            <label className="text-xs text-slate-500 flex items-center gap-2">
              Top-k:
              <input
                type="number"
                min={1}
                max={5}
                value={topK}
                onChange={(e) => setTopK(Math.max(1, Math.min(5, Number(e.target.value))))}
                className="w-12 px-1.5 py-0.5 text-xs border border-slate-200 rounded font-mono tabular-nums"
              />
              <span className="text-[11px] text-slate-400">playbooks consulted</span>
            </label>
            <div className="flex items-center gap-2">
              {(status === 'done' || status === 'error' || askedQuestion) && (
                <button
                  type="button"
                  onClick={handleClear}
                  className="px-3 py-1.5 text-sm border border-slate-200 text-slate-700 rounded hover:bg-slate-50"
                  disabled={status === 'streaming'}
                >
                  Clear
                </button>
              )}
              <button
                type="submit"
                disabled={!question.trim() || status === 'streaming'}
                className="px-4 py-1.5 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed transition-colors"
              >
                {status === 'streaming' ? 'Thinking…' : 'Ask'}
              </button>
            </div>
          </div>
          <p className="mt-2 text-[11px] text-slate-400">Cmd/Ctrl + Enter to submit</p>
        </form>

        {/* Answer */}
        {askedQuestion && (
          <section>
            <header className="mb-2 flex items-center justify-between">
              <h2 className="text-[11px] font-semibold tracking-wider uppercase text-slate-500">
                Answer
              </h2>
              <div className="text-[11px] text-slate-400">
                grounded in {sources.length || topK} playbook{sources.length === 1 ? '' : 's'}
                {' · asked: '}
                <em className="text-slate-500">{askedQuestion}</em>
              </div>
            </header>
            <div className="bg-panel-surface border border-panel-border rounded-lg p-5">
              {answer ? (
                <ChatAnswer text={answer} citedIds={citedSet} />
              ) : status === 'streaming' ? (
                <div className="text-sm text-slate-400 flex items-center gap-2">
                  <span className="inline-block w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                  Retrieving and drafting…
                </div>
              ) : null}
              {status === 'error' && (
                <div className="mt-3 text-sm text-red-600">{errorMsg}</div>
              )}
              <div ref={answerScrollRef} />
            </div>
          </section>
        )}

        {/* Sources */}
        {sources.length > 0 && (
          <section>
            <header className="mb-2 flex items-center justify-between">
              <h2 className="text-[11px] font-semibold tracking-wider uppercase text-slate-500">
                Sources
              </h2>
              {status === 'done' && citedIds.length === 0 && (
                <span className="text-[11px] text-amber-600">
                  No inline citations detected — answer may be ungrounded.
                </span>
              )}
            </header>
            <div className="space-y-3">
              {sources.map((hit) => (
                <SourceCard
                  key={hit.playbook_id}
                  hit={hit}
                  cited={citedSet.has(hit.playbook_id)}
                />
              ))}
            </div>
          </section>
        )}

        {/* Empty state */}
        {!askedQuestion && (
          <div className="text-center text-sm text-slate-400 py-8">
            Try asking about a parking-fine dispute, a payment failure, a missing invoice, …
          </div>
        )}
      </div>
    </div>
  );
}
