/** Left rail in the Chat tab — list of past Q&A sessions.
 *
 * Each row is one question (truncated) plus a relative timestamp and
 * source/citation counts. Clicking loads that session into the main
 * panel. "New chat" clears the panel back to the empty state. Hovering
 * exposes a small × that deletes the row.
 */
import { useEffect, useState } from 'react';
import { Plus, X } from 'lucide-react';

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
    <aside className="flex flex-col w-[280px] shrink-0 border-r border-line-subtle bg-card">
      <div className="px-3 pt-3">
        <button
          type="button"
          onClick={onNewChat}
          className="w-full h-9 inline-flex items-center justify-center gap-2 border border-line rounded-lg text-[13px] text-ink-body hover:bg-hover transition-colors duration-150"
        >
          <Plus width={14} height={14} strokeWidth={2} />
          New chat
        </button>
      </div>

      <div className="text-[11px] uppercase tracking-wider font-semibold text-ink-muted px-3 pt-4 pb-2">
        History <span className="text-ink-muted">· {sessions.length}</span>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin pb-2">
        {loading && (
          <div className="px-4 py-6 text-sm text-ink-muted">Loading…</div>
        )}
        {error && (
          <div className="px-4 py-6 text-sm text-red-600">{error}</div>
        )}
        {!loading && !error && sessions.length === 0 && (
          <div className="px-4 py-6 text-[12px] text-ink-muted">
            No history yet.
          </div>
        )}
        <ul>
          {sessions.map((s) => {
            const isActive = activeId === s.id;
            return (
              <li key={s.id}>
                <div
                  className={`group/row mx-2 rounded-lg px-3 py-2.5 cursor-pointer transition-colors duration-150 ${
                    isActive ? 'bg-hover' : 'hover:bg-hover'
                  }`}
                  onClick={() => onSelect(s.id)}
                >
                  <div className="flex items-start gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="text-[12px] font-medium text-ink line-clamp-2 leading-snug">
                        {s.question}
                      </div>
                      <div className="mt-1 text-[10px] text-ink-muted">
                        {(() => {
                          const n = s.citation_count > 0 ? s.citation_count : s.source_count;
                          return `${formatTimestamp(s.timestamp)} · ${n} source${n === 1 ? '' : 's'}`;
                        })()}
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => handleDelete(e, s)}
                      disabled={deletingId === s.id}
                      title="Delete"
                      className="opacity-0 group-hover/row:opacity-100 transition-opacity text-ink-muted hover:text-red-600 shrink-0 w-5 h-5 inline-flex items-center justify-center rounded"
                    >
                      <X width={12} height={12} strokeWidth={2} />
                    </button>
                  </div>
                </div>
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
