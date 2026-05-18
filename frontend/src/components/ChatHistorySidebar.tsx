/** Left rail in the Chat tab — list of past Q&A sessions.
 *
 * Each row is one question (truncated) plus a relative timestamp.
 * Clicking loads that session into the main panel.
 * "New chat" clears the panel back to the empty state.
 * Hovering exposes a small × that deletes the row.
 */
import { useEffect, useState } from 'react';

import { deleteChatSession, listChatSessions } from '../lib/api';
import type { ChatSessionSummary } from '../lib/types';

import { useToast } from './Toast';


interface Props {
  activeId: number | null;
  onSelect: (id: number) => void;
  onNewChat: () => void;
}


export function ChatHistorySidebar({ activeId, onSelect, onNewChat }: Props) {
  const toast = useToast();
  const [sessions, setSessions] = useState<ChatSessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  function refresh() {
    setLoading(true);
    listChatSessions()
      .then(setSessions)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    refresh();
    const handler = () => refresh();
    window.addEventListener('chat-sessions-changed', handler);
    return () => window.removeEventListener('chat-sessions-changed', handler);
  }, []);

  async function handleDelete(e: React.MouseEvent, s: ChatSessionSummary) {
    e.stopPropagation();
    e.preventDefault();
    setDeletingId(s.id);
    try {
      await deleteChatSession(s.id);
      setSessions((prev) => prev.filter((x) => x.id !== s.id));
      if (activeId === s.id) onNewChat();
      window.dispatchEvent(new Event('chat-sessions-changed'));
    } catch (err) {
      toast.error((err as Error).message);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <aside className="flex flex-col w-[280px] shrink-0 border-r border-panel-border bg-panel-surface">
      <div className="px-4 py-3 border-b border-panel-border">
        <button
          type="button"
          onClick={onNewChat}
          className="w-full inline-flex items-center justify-center gap-1.5 px-3 py-1.5 text-sm font-medium border border-slate-200 bg-white text-slate-700 rounded hover:border-blue-400 hover:text-blue-600 transition-colors"
        >
          <span className="text-base leading-none">+</span> New chat
        </button>
        <div className="mt-2 text-[11px] font-semibold tracking-wider uppercase text-slate-500">
          History · {sessions.length}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {loading && (
          <div className="px-4 py-6 text-sm text-slate-400">Loading…</div>
        )}
        {error && (
          <div className="px-4 py-6 text-sm text-red-600">{error}</div>
        )}
        {!loading && !error && sessions.length === 0 && (
          <div className="px-4 py-6 text-sm text-slate-400">
            No history yet. Ask a question on the right.
          </div>
        )}
        <ul>
          {sessions.map((s) => {
            const isActive = activeId === s.id;
            return (
              <li key={s.id}>
                <button
                  type="button"
                  onClick={() => onSelect(s.id)}
                  className={`group/row w-full text-left px-4 py-3 border-b border-panel-divider transition-colors ${
                    isActive
                      ? 'bg-blue-50/60 border-l-2 border-l-blue-500'
                      : 'hover:bg-slate-50 border-l-2 border-l-transparent'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-slate-900 leading-snug line-clamp-2">
                        {s.question}
                      </div>
                      <div className="mt-1 flex items-center gap-2 text-[10px] text-slate-500 font-mono">
                        <span>{formatTimestamp(s.timestamp)}</span>
                        <span className="text-slate-300">·</span>
                        <span>{s.source_count} src</span>
                        {s.citation_count > 0 && (
                          <>
                            <span className="text-slate-300">·</span>
                            <span>{s.citation_count} cited</span>
                          </>
                        )}
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => handleDelete(e, s)}
                      disabled={deletingId === s.id}
                      title="Delete"
                      className="opacity-0 group-hover/row:opacity-100 transition-opacity text-slate-400 hover:text-red-600 text-xs px-1 shrink-0"
                    >
                      ×
                    </button>
                  </div>
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </aside>
  );
}


function formatTimestamp(iso: string): string {
  try {
    const d = new Date(iso);
    const now = new Date();
    const sameDay =
      d.getFullYear() === now.getFullYear() &&
      d.getMonth() === now.getMonth() &&
      d.getDate() === now.getDate();
    if (sameDay) {
      return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
    }
    return d.toLocaleDateString(undefined, { month: 'short', day: '2-digit' });
  } catch {
    return iso;
  }
}
