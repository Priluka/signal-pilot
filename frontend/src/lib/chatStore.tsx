/** App-level chat state — multi-turn threads (Phase 4).
 *
 * State shape:
 *
 *   threads:       ChatThreadSummary[]   — sidebar list, sorted newest-first
 *   activeThreadId: number | null        — currently-open thread (also in
 *                                          localStorage so refresh restores it)
 *   turns:         ChatTurn[]            — ordered turns of active thread,
 *                                          including any in-flight turn at
 *                                          the tail
 *   streamingTurnId: number | null       — id of the turn currently being
 *                                          streamed in; null when nothing
 *                                          is mid-flight
 *   pendingText:   string                — input box draft (persisted to LS)
 *   topK:          number                — retrieval breadth for new turns
 *
 * Smooth streaming
 * ----------------
 * Same RAF-driven typing animation as the legacy single-turn store, but
 * the buffer now points at the currently-streaming turn instead of a
 * scalar answer field. Completed turns are static text rendered
 * verbatim; only the most recent (streaming) turn ticks character by
 * character. Aborts come from explicit user action only — new chat
 * button, picking another thread, or sending a new message which
 * implicitly cancels any orphaned stream from before.
 *
 * Refresh resilience
 * ------------------
 * On mount we read ``LS_ACTIVE_THREAD_ID`` and load the thread detail.
 * If its last turn is still ``streaming`` server-side, we re-attach
 * via ``GET /chat/threads/{id}/turns/{turn_id}/stream`` — the SSE
 * tail replays whatever events the backend has persisted plus any
 * new ones until ``done``.
 */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react';

import {
  attachToThreadTurn,
  createThread,
  deleteThread as deleteThreadApi,
  getThreadDetail,
  interruptThreadTurn,
  listThreads as listThreadsApi,
  streamThreadTurn,
} from './api';
import type {
  ChatEvent,
  ChatThreadSummary,
  ChatTurn,
  CitationIndexEntry,
  RetrievalHitOut,
} from './types';


export type ChatStatus = 'idle' | 'streaming' | 'done' | 'error';


interface ChatStore {
  // Sidebar — list of all threads
  threads: ChatThreadSummary[];
  threadsLoading: boolean;

  // Currently-open conversation
  activeThreadId: number | null;
  turns: ChatTurn[];

  // In-flight tracking. Non-null only while a turn is being streamed.
  streamingTurnId: number | null;
  errorMsg: string | null;

  // Input box state
  pendingText: string;
  topK: number;

  // Actions
  setPendingText: (v: string) => void;
  setTopK: (v: number) => void;
  newThread: () => void;
  selectThread: (id: number) => Promise<void>;
  sendMessage: () => void;
  /** Cancel the in-flight turn. Hits the backend interrupt endpoint
   *  AND aborts the local SSE; the agent loop will exit at its next
   *  iteration boundary and persist status='error' with a synthetic
   *  cancellation message. UI marks the turn as cancelled
   *  immediately so the operator gets instant feedback. */
  interruptStream: () => Promise<void>;
  deleteThread: (id: number) => Promise<void>;
  refreshThreads: () => Promise<void>;
  /** Dismiss the network/send error banner. Used by the X button
   *  on the error pill above the textarea. */
  clearError: () => void;
}


const ChatContext = createContext<ChatStore | null>(null);


export function useChatStore(): ChatStore {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error('useChatStore must be used inside ChatStoreProvider');
  return ctx;
}


// localStorage keys — distinct from the legacy chat session keys so a
// rollback / parallel install doesn't cross-contaminate.
const LS_ACTIVE_THREAD_ID = 'signal-pilot.chat.activeThreadId';
const LS_TOP_K = 'signal-pilot.chat.topK';
const LS_DRAFT = 'signal-pilot.chat.draftText';


function readNumber(key: string, fallback: number): number {
  try {
    const raw = localStorage.getItem(key);
    if (raw == null) return fallback;
    const n = Number(raw);
    return Number.isFinite(n) ? n : fallback;
  } catch {
    return fallback;
  }
}


function readString(key: string): string {
  try {
    return localStorage.getItem(key) ?? '';
  } catch {
    return '';
  }
}


function writeString(key: string, value: string | null) {
  try {
    if (value == null || value === '') localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    // no-op (Safari private mode etc.)
  }
}


/** Map a low-level network error from ``fetch`` ("Failed to fetch",
 *  "NetworkError", "Load failed", connection refused, etc.) into an
 *  operator-friendly message. Everything else is passed through so
 *  HTTP error bodies (rate limit, validation, cost cap) still surface
 *  with their full detail. */
function friendlyError(err: unknown): string {
  if (!err) return 'Unknown error';
  const msg = err instanceof Error ? err.message : String(err);
  const lower = msg.toLowerCase();
  const networkMarkers = [
    'failed to fetch',
    'networkerror',
    'load failed',
    'network request failed',
    'connection refused',
    'connection reset',
    'err_connection',
    'err_network',
  ];
  if (networkMarkers.some((m) => lower.includes(m))) {
    return 'Backend unavailable — please try again.';
  }
  return msg;
}


/** Collapse paired skill_executing / skill_executed events into a
 *  single executed row per call. Same logic as the legacy store —
 *  server persists both halves; the UI shows only one. */
function dedupeEvents(events: ChatEvent[]): ChatEvent[] {
  const out: ChatEvent[] = [];
  for (const ev of events) {
    if (ev.type !== 'skill_executed') {
      out.push(ev);
      continue;
    }
    let idx = -1;
    if (ev.call_id) {
      idx = out.findIndex(
        (r) => r.type === 'skill_executing' && r.call_id === ev.call_id,
      );
    }
    if (idx === -1) {
      for (let i = out.length - 1; i >= 0; i--) {
        const r = out[i];
        if (r.type === 'skill_executing' && r.skill === ev.skill) {
          idx = i;
          break;
        }
      }
    }
    if (idx >= 0) {
      out[idx] = ev;
    } else {
      out.push(ev);
    }
  }
  return out;
}


export function ChatStoreProvider({ children }: { children: ReactNode }) {
  // ----- State ------------------------------------------------------------
  const [threads, setThreads] = useState<ChatThreadSummary[]>([]);
  const [threadsLoading, setThreadsLoading] = useState(true);
  const [activeThreadId, setActiveThreadId] = useState<number | null>(null);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [streamingTurnId, setStreamingTurnId] = useState<number | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [pendingText, setPendingTextState] = useState<string>(() =>
    readString(LS_DRAFT),
  );
  const [topK, setTopKState] = useState<number>(() => {
    const v = readNumber(LS_TOP_K, 5);
    return Math.max(1, Math.min(5, v));
  });

  const abortRef = useRef<AbortController | null>(null);

  // ----- Smooth streaming machinery --------------------------------------
  // targetRef = the latest text the server has sent for the streaming
  // turn (cumulative). displayedRef = the count of chars already
  // committed to React state. RAF interpolates between them.
  const targetRef = useRef<string>('');
  const displayedRef = useRef<number>(0);
  const streamingDoneRef = useRef<boolean>(false);
  const rafIdRef = useRef<number | null>(null);

  const stopRAF = useCallback(() => {
    if (rafIdRef.current != null) {
      cancelAnimationFrame(rafIdRef.current);
      rafIdRef.current = null;
    }
  }, []);

  const startRAF = useCallback(() => {
    if (rafIdRef.current != null) return;
    const tick = () => {
      const total = targetRef.current.length;
      const shown = displayedRef.current;
      const gap = total - shown;
      if (gap <= 0) {
        if (streamingDoneRef.current) {
          rafIdRef.current = null;
          return;
        }
        rafIdRef.current = requestAnimationFrame(tick);
        return;
      }
      // Adaptive rate: catch up fast when buffer is huge, type at
      // human pace when small. 50 char/sec baseline → ~3 chars/frame
      // @60fps; scale up linearly past 200-char gap so refresh
      // catch-up doesn't make the operator wait minutes for old text.
      const step = Math.max(3, Math.min(gap, Math.ceil(gap / 12)));
      displayedRef.current = shown + step;
      const newText = targetRef.current.slice(0, displayedRef.current);
      setTurns((prev) => {
        if (streamingTurnIdRef.current == null) return prev;
        const idx = prev.findIndex((t) => t.id === streamingTurnIdRef.current);
        if (idx === -1) return prev;
        const updated = { ...prev[idx], final_assistant_text: newText };
        const copy = prev.slice();
        copy[idx] = updated;
        return copy;
      });
      rafIdRef.current = requestAnimationFrame(tick);
    };
    rafIdRef.current = requestAnimationFrame(tick);
  }, []);

  const streamingTurnIdRef = useRef<number | null>(null);
  useEffect(() => {
    streamingTurnIdRef.current = streamingTurnId;
  }, [streamingTurnId]);

  const resetStreamRefs = useCallback(() => {
    targetRef.current = '';
    displayedRef.current = 0;
    streamingDoneRef.current = false;
    stopRAF();
  }, [stopRAF]);

  // ----- Pure setters (with LS persistence) ------------------------------

  const setPendingText = useCallback((v: string) => {
    setPendingTextState(v);
    writeString(LS_DRAFT, v);
  }, []);

  const setTopK = useCallback((v: number) => {
    const clamped = Math.max(1, Math.min(5, Math.floor(v)));
    setTopKState(clamped);
    writeString(LS_TOP_K, String(clamped));
  }, []);

  // ----- Thread list --------------------------------------------------------

  const refreshThreads = useCallback(async () => {
    setThreadsLoading(true);
    try {
      const list = await listThreadsApi();
      setThreads(list);
    } catch {
      setThreads([]);
    } finally {
      setThreadsLoading(false);
    }
  }, []);

  // ----- Event handler that builds up the streaming turn -----------------

  const buildStreamHandlers = useCallback(
    (turnId: number) => ({
      onSources: (e: { hits: RetrievalHitOut[] }) => {
        setTurns((prev) => {
          const idx = prev.findIndex((t) => t.id === turnId);
          if (idx === -1) return prev;
          const copy = prev.slice();
          copy[idx] = { ...copy[idx], sources: e.hits };
          return copy;
        });
      },
      onSkillExecuting: (e: {
        skill: string;
        params: Record<string, unknown>;
        call_id?: string;
      }) => {
        setTurns((prev) => {
          const idx = prev.findIndex((t) => t.id === turnId);
          if (idx === -1) return prev;
          // Guard against duplicate executing events for the same
          // call_id (can happen on SSE reconnect mid-stream).
          if (
            e.call_id &&
            copy_has_call_id(prev[idx].events, e.call_id)
          ) {
            return prev;
          }
          const events = [
            ...prev[idx].events,
            {
              type: 'skill_executing' as const,
              skill: e.skill,
              params: e.params,
              call_id: e.call_id,
            },
          ];
          const copy = prev.slice();
          copy[idx] = { ...copy[idx], events };
          return copy;
        });
      },
      onSkillExecuted: (e: {
        skill: string;
        params: Record<string, unknown>;
        call_id?: string;
        ok: boolean;
        result: Record<string, unknown> | null;
        error: string | null;
        elapsed_ms: number;
      }) => {
        setTurns((prev) => {
          const idx = prev.findIndex((t) => t.id === turnId);
          if (idx === -1) return prev;
          const finished: ChatEvent = {
            type: 'skill_executed',
            skill: e.skill,
            params: e.params,
            call_id: e.call_id,
            ok: e.ok,
            result: e.result,
            error: e.error,
            elapsed_ms: e.elapsed_ms,
          };
          // Replace matching skill_executing (by call_id, else most-
          // recent same-name executing); fall back to append.
          let evIdx = -1;
          const evs = prev[idx].events;
          if (e.call_id) {
            evIdx = evs.findIndex(
              (r) => r.type === 'skill_executing' && r.call_id === e.call_id,
            );
          }
          if (evIdx === -1) {
            for (let i = evs.length - 1; i >= 0; i--) {
              const r = evs[i];
              if (r.type === 'skill_executing' && r.skill === e.skill) {
                evIdx = i;
                break;
              }
            }
          }
          const events =
            evIdx === -1
              ? [...evs, finished]
              : evs.map((r, i) => (i === evIdx ? finished : r));
          const copy = prev.slice();
          copy[idx] = { ...copy[idx], events };
          return copy;
        });
      },
      onComposing: () => {
        setTurns((prev) => {
          const idx = prev.findIndex((t) => t.id === turnId);
          if (idx === -1) return prev;
          const events = [...prev[idx].events, { type: 'composing' as const }];
          const copy = prev.slice();
          copy[idx] = { ...copy[idx], events };
          return copy;
        });
      },
      onThinking: (e: { iteration: number }) => {
        // Heartbeat between skills and text. We keep only the LATEST
        // thinking event per turn — older ones are stale once a new
        // iteration starts. The UI reads this to show a subtle 'agent
        // is alive' indicator during the silent gap between a
        // tool_result and the next Anthropic stream.
        setTurns((prev) => {
          const idx = prev.findIndex((t) => t.id === turnId);
          if (idx === -1) return prev;
          const events = [
            ...prev[idx].events.filter((ev) => ev.type !== 'thinking'),
            { type: 'thinking' as const, iteration: e.iteration },
          ];
          const copy = prev.slice();
          copy[idx] = { ...copy[idx], events };
          return copy;
        });
      },
      onThinkingText: (e: { text: string }) => {
        // Phase 9B — accumulate the extended-thinking channel into a
        // single ``thinking_text`` event per turn. Subsequent deltas
        // append to that event's text. The UI renders the
        // accumulated buffer as a collapsible quote above the answer.
        setTurns((prev) => {
          const idx = prev.findIndex((t) => t.id === turnId);
          if (idx === -1) return prev;
          const existing = prev[idx].events.find(
            (ev): ev is Extract<typeof ev, { type: 'thinking_text' }> =>
              ev.type === 'thinking_text',
          );
          const newText = (existing?.text ?? '') + e.text;
          const events = [
            ...prev[idx].events.filter((ev) => ev.type !== 'thinking_text'),
            { type: 'thinking_text' as const, text: newText },
          ];
          const copy = prev.slice();
          copy[idx] = { ...copy[idx], events };
          return copy;
        });
      },
      onCompacted: (e: {
        tier: number;
        before_tokens: number;
        after_tokens: number;
        dropped_turns: number;
      }) => {
        // Persisted server-side as a row in events_json; we append
        // locally for instant feedback. TurnView renders a small
        // badge whenever a compacted event is in the turn's events.
        setTurns((prev) => {
          const idx = prev.findIndex((t) => t.id === turnId);
          if (idx === -1) return prev;
          const events = [
            ...prev[idx].events,
            {
              type: 'compacted' as const,
              tier: e.tier,
              before_tokens: e.before_tokens,
              after_tokens: e.after_tokens,
              dropped_turns: e.dropped_turns,
            },
          ];
          const copy = prev.slice();
          copy[idx] = { ...copy[idx], events };
          return copy;
        });
      },
      onDelta: (e: { text: string }) => {
        targetRef.current += e.text;
        startRAF();
      },
      onDone: (e: {
        answer: string;
        citation_index?: CitationIndexEntry[];
      }) => {
        targetRef.current = e.answer;
        streamingDoneRef.current = true;
        startRAF();
        setTurns((prev) => {
          const idx = prev.findIndex((t) => t.id === turnId);
          if (idx === -1) return prev;
          const copy = prev.slice();
          copy[idx] = {
            ...copy[idx],
            status: 'done',
            final_assistant_text: e.answer,
            citation_index: e.citation_index ?? copy[idx].citation_index,
          };
          return copy;
        });
        setStreamingTurnId(null);
        // Sidebar count + last_status need refreshing after a turn
        // lands. Best-effort — no UI block if it fails.
        void refreshThreads();
      },
      onError: (e: { message: string }) => {
        const pretty = friendlyError(new Error(e.message));
        setErrorMsg(pretty);
        streamingDoneRef.current = true;
        stopRAF();
        setTurns((prev) => {
          const idx = prev.findIndex((t) => t.id === turnId);
          if (idx === -1) return prev;
          const copy = prev.slice();
          copy[idx] = {
            ...copy[idx],
            status: 'error',
            error_message: pretty,
          };
          return copy;
        });
        setStreamingTurnId(null);
      },
    }),
    [refreshThreads, startRAF, stopRAF],
  );

  // ----- Actions ----------------------------------------------------------

  const newThread = useCallback(() => {
    // User clicked 'New chat'. Abort any active stream, clear UI.
    // The thread row itself isn't created until the first send.
    abortRef.current?.abort();
    resetStreamRefs();
    setActiveThreadId(null);
    writeString(LS_ACTIVE_THREAD_ID, null);
    setTurns([]);
    setStreamingTurnId(null);
    setErrorMsg(null);
    setPendingTextState('');
    writeString(LS_DRAFT, null);
  }, [resetStreamRefs]);

  const selectThread = useCallback(
    async (id: number) => {
      abortRef.current?.abort();
      resetStreamRefs();
      setActiveThreadId(id);
      writeString(LS_ACTIVE_THREAD_ID, String(id));
      setErrorMsg(null);
      setStreamingTurnId(null);
      setTurns([]);  // clear before load to avoid stale-then-new flicker
      try {
        const detail = await getThreadDetail(id);
        const loaded: ChatTurn[] = detail.turns.map((t) => ({
          ...t,
          events: dedupeEvents(t.events),
        }));
        setTurns(loaded);
        // If the last turn is mid-stream on the server, re-attach so
        // we resume the live stream. Replay events first (already in
        // ``loaded``), then continue.
        const last = loaded[loaded.length - 1];
        if (last && last.status === 'streaming') {
          setStreamingTurnId(last.id);
          targetRef.current = last.final_assistant_text || '';
          displayedRef.current = targetRef.current.length;
          streamingDoneRef.current = false;
          abortRef.current = attachToThreadTurn(
            id,
            last.id,
            buildStreamHandlers(last.id),
          );
        }
      } catch (err) {
        setErrorMsg((err as Error).message);
      }
    },
    [resetStreamRefs, buildStreamHandlers],
  );

  const sendMessage = useCallback(async () => {
    const text = pendingText.trim();
    if (!text) return;
    if (streamingTurnId != null) return;  // already streaming

    abortRef.current?.abort();
    resetStreamRefs();
    setErrorMsg(null);

    // Create thread on the fly if none active.
    let threadId = activeThreadId;
    if (threadId == null) {
      try {
        const t = await createThread();
        threadId = t.id;
        setActiveThreadId(t.id);
        writeString(LS_ACTIVE_THREAD_ID, String(t.id));
      } catch (err) {
        setErrorMsg(friendlyError(err));
        return;
      }
    }

    // Optimistic local turn so the user bubble appears INSTANTLY —
    // no waiting for the server to acknowledge the POST. Backend
    // will create the real row and start streaming events into it;
    // when ``sources`` arrives we have the real id and map it onto
    // this placeholder.
    const optimisticId = -Date.now();  // negative so it can't collide
    const optimisticTurn: ChatTurn = {
      id: optimisticId,
      thread_id: threadId,
      turn_index: turns.length,
      user_text: text,
      final_assistant_text: '',
      events: [],
      sources: [],
      citation_index: [],
      status: 'streaming',
      error_message: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    setTurns((prev) => [...prev, optimisticTurn]);
    setStreamingTurnId(optimisticId);
    streamingTurnIdRef.current = optimisticId;

    setPendingTextState('');
    writeString(LS_DRAFT, null);

    // SSE handlers — but the first ``sources`` event tells us the
    // real turn_id. We swap our optimistic id for the real one in
    // that callback before invoking the per-turn-id helpers.
    const baseHandlers = buildStreamHandlers(optimisticId);
    let realId: number | null = null;

    abortRef.current = streamThreadTurn(threadId, text, topK, {
      onSources: (e) => {
        // First event of the stream carries the real turn_id.
        const tid = (e as unknown as { turn_id?: number }).turn_id;
        if (tid && realId == null) {
          realId = tid;
          // Swap optimistic id → real id in the turns array AND in
          // the streaming-turn ref so subsequent setters target the
          // right row.
          setTurns((prev) => {
            const idx = prev.findIndex((t) => t.id === optimisticId);
            if (idx === -1) return prev;
            const copy = prev.slice();
            copy[idx] = { ...copy[idx], id: tid };
            return copy;
          });
          setStreamingTurnId(tid);
          streamingTurnIdRef.current = tid;
        }
        // Now run the rest of onSources with the right id-aware
        // handler. Rebuild with the real id so subsequent setters
        // find the row.
        const h = realId != null ? buildStreamHandlers(realId) : baseHandlers;
        h.onSources(e);
      },
      onSkillExecuting: (e) => {
        const h = realId != null ? buildStreamHandlers(realId) : baseHandlers;
        h.onSkillExecuting(e);
      },
      onSkillExecuted: (e) => {
        const h = realId != null ? buildStreamHandlers(realId) : baseHandlers;
        h.onSkillExecuted(e);
      },
      onComposing: () => {
        const h = realId != null ? buildStreamHandlers(realId) : baseHandlers;
        h.onComposing();
      },
      onThinking: (e) => {
        const h = realId != null ? buildStreamHandlers(realId) : baseHandlers;
        h.onThinking?.(e);
      },
      onThinkingText: (e) => {
        const h = realId != null ? buildStreamHandlers(realId) : baseHandlers;
        h.onThinkingText?.(e);
      },
      onDelta: (e) => {
        const h = realId != null ? buildStreamHandlers(realId) : baseHandlers;
        h.onDelta(e);
      },
      onDone: (e) => {
        const h = realId != null ? buildStreamHandlers(realId) : baseHandlers;
        h.onDone(e);
      },
      onError: (e) => {
        const h = realId != null ? buildStreamHandlers(realId) : baseHandlers;
        h.onError(e);
      },
    });
  }, [
    activeThreadId,
    buildStreamHandlers,
    pendingText,
    resetStreamRefs,
    streamingTurnId,
    topK,
    turns.length,
  ]);

  const interruptStream = useCallback(async () => {
    const turnId = streamingTurnIdRef.current;
    if (turnId == null || activeThreadId == null) return;
    // Mark UI immediately — operator sees instant feedback even
    // though the server takes up to one Anthropic round-trip to
    // actually wind down.
    setTurns((prev) => {
      const idx = prev.findIndex((t) => t.id === turnId);
      if (idx === -1) return prev;
      const copy = prev.slice();
      copy[idx] = {
        ...copy[idx],
        status: 'error',
        error_message: 'Cancelled by operator',
      };
      return copy;
    });
    setStreamingTurnId(null);
    abortRef.current?.abort();
    stopRAF();
    streamingDoneRef.current = true;
    // Fire-and-forget the server-side interrupt. If it fails (network
    // hiccup, server already finished), we don't surface the error —
    // the local cancellation is already visible.
    try {
      await interruptThreadTurn(activeThreadId, turnId);
    } catch {
      /* best effort */
    }
    void refreshThreads();
  }, [activeThreadId, refreshThreads, stopRAF]);

  const deleteThread = useCallback(
    async (id: number) => {
      try {
        await deleteThreadApi(id);
      } catch (err) {
        setErrorMsg((err as Error).message);
        return;
      }
      if (id === activeThreadId) {
        abortRef.current?.abort();
        resetStreamRefs();
        setActiveThreadId(null);
        writeString(LS_ACTIVE_THREAD_ID, null);
        setTurns([]);
        setStreamingTurnId(null);
        setErrorMsg(null);
      }
      void refreshThreads();
    },
    [activeThreadId, refreshThreads, resetStreamRefs],
  );

  // ----- Mount lifecycle: rehydrate ---------------------------------------

  useEffect(() => {
    // Run once on mount: load sidebar + restore active thread.
    /* eslint-disable react-hooks/set-state-in-effect */
    void refreshThreads();
    const savedId = readNumber(LS_ACTIVE_THREAD_ID, 0);
    if (savedId > 0) {
      void selectThread(savedId);
    }
    return () => {
      abortRef.current?.abort();
      stopRAF();
    };
    /* eslint-enable react-hooks/set-state-in-effect */
    // Only on mount — selectThread / refreshThreads are stable via
    // useCallback so re-running on every render would be wasted work
    // and could re-trigger the SSE attach.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const value: ChatStore = {
    threads,
    threadsLoading,
    activeThreadId,
    turns,
    streamingTurnId,
    errorMsg,
    pendingText,
    topK,
    setPendingText,
    setTopK,
    newThread,
    selectThread,
    sendMessage,
    interruptStream,
    deleteThread,
    refreshThreads,
    clearError: () => setErrorMsg(null),
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}


// Helper used by buildStreamHandlers — avoid duplicate executing rows
// when SSE reconnect emits the same event twice.
function copy_has_call_id(events: ChatEvent[], call_id: string): boolean {
  return events.some(
    (r) =>
      (r.type === 'skill_executing' || r.type === 'skill_executed') &&
      r.call_id === call_id,
  );
}
