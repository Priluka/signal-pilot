/** Left rail in the Chat tab — list of conversation threads.
 *
 * Replaces ``ChatHistorySidebar`` for the multi-turn flow. Each row =
 * one thread; click loads it as the active conversation; the small ×
 * on hover deletes it (cascade-removes its turns server-side).
 *
 * Title is the auto-derived preview of the thread's first message;
 * the row footer carries last-activity timestamp + turn count + a
 * streaming dot if the most recent turn is still mid-stream
 * server-side (e.g. another tab is in flight).
 */
import { Plus, X, Loader2 } from 'lucide-react';

import { useChatStore } from '../lib/chatStore';
import type { ChatThreadSummary } from '../lib/types';

import { useToast } from './Toast';


export function ChatThreadsSidebar() {
  const toast = useToast();
  const {
    threads,
    threadsLoading,
    activeThreadId,
    selectThread,
    newThread,
    deleteThread,
  } = useChatStore();

  async function handleDelete(
    e: React.MouseEvent,
    t: ChatThreadSummary,
  ) {
    e.stopPropagation();
    e.preventDefault();
    try {
      await deleteThread(t.id);
    } catch (err) {
      toast.error((err as Error).message);
    }
  }

  return (
    <aside className="flex flex-col w-[280px] shrink-0 border-r border-line-subtle bg-card">
      <div className="px-3 pt-3">
        <button
          type="button"
          onClick={newThread}
          className="w-full h-9 inline-flex items-center justify-center gap-2 border border-line rounded-lg text-[13px] text-ink-body hover:bg-hover transition-colors duration-150"
        >
          <Plus width={14} height={14} strokeWidth={2} />
          New chat
        </button>
      </div>

      <div className="text-[11px] uppercase tracking-wider font-semibold text-ink-muted px-3 pt-4 pb-2">
        Threads <span className="text-ink-muted">· {threads.length}</span>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin pb-2">
        {threadsLoading && (
          <div className="px-4 py-6 text-sm text-ink-muted">Loading…</div>
        )}
        {!threadsLoading && threads.length === 0 && (
          <div className="px-4 py-6 text-[12px] text-ink-muted">
            No conversations yet.
          </div>
        )}
        <ul>
          {threads.map((t) => {
            const isActive = activeThreadId === t.id;
            const streaming = t.last_status === 'streaming';
            return (
              <li key={t.id}>
                <div
                  className={`group/row mx-2 rounded-lg px-3 py-2.5 cursor-pointer transition-colors duration-150 ${
                    isActive ? 'bg-hover' : 'hover:bg-hover'
                  }`}
                  onClick={() => void selectThread(t.id)}
                >
                  <div className="flex items-start gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="text-[12px] font-medium text-ink line-clamp-2 leading-snug">
                        {t.title}
                      </div>
                      <div className="mt-1 text-[10px] text-ink-muted flex items-center gap-1.5">
                        {streaming && (
                          <Loader2
                            width={10}
                            height={10}
                            className="animate-spin text-accent shrink-0"
                          />
                        )}
                        <span>
                          {formatTimestamp(t.updated_at)} ·{' '}
                          {t.turn_count} turn{t.turn_count === 1 ? '' : 's'}
                        </span>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => void handleDelete(e, t)}
                      title="Delete thread"
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
      return d.toLocaleTimeString(undefined, {
        hour: '2-digit',
        minute: '2-digit',
      });
    }
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: '2-digit',
    });
  } catch {
    return iso;
  }
}
