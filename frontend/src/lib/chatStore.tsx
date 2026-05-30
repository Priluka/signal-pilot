/** App-level chat state.
 *
 * Two layers of persistence so a refresh never throws work away:
 *
 *   1. The conversation itself is stored server-side in chat_sessions on
 *      every successful stream.
 *   2. The client remembers (a) which session is currently open, (b) the
 *      operator's top-k preference, and (c) any draft question they're
 *      typing — all in localStorage. On mount we rehydrate from these.
 *
 * Smooth streaming
 * ----------------
 * SSE chunks arrive in bursts (often 50–300 chars at once after a pause
 * for tool calls or buffer flushes), which makes the visible text jump
 * forward in chunks. To match the Claude.ai / ChatGPT typing feel, the
 * store decouples *received* text from *displayed* text:
 *
 *   • ``targetRef``    = everything the server has sent so far.
 *   • ``answer`` state = what we're currently rendering (grows char-by-
 *                        char from displayedRef on each animation frame).
 *
 * A single requestAnimationFrame loop drains targetRef → answer at an
 * adaptive rate. When the buffer is small we type at ~50 chars/sec
 * (readable cadence); when the buffer balloons (network burst or
 * mid-stream rehydrate catch-up) we speed up so the user isn't left
 * waiting for text the server has already produced. After the SSE
 * ``done`` event, the loop flushes whatever remains and exits.
 *
 * Aborts are only triggered by explicit user action (Clear / New chat /
 * picking another history row) — never by component unmount or remount.
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
  attachToChatSession,
  getChatSession,
  streamAgenticChat,
} from './api';
import type { ChatEvent } from './types';
import type { CitationIndexEntry, RetrievalHitOut } from './types';


export type ChatStatus = 'idle' | 'streaming' | 'done' | 'error';


interface ChatStore {
  question: string;
  askedQuestion: string;
  topK: number;
  answer: string;
  sources: RetrievalHitOut[];
  /** Server-resolved citation map. Every ``[id]`` in the answer is looked
   * up against the full playbook corpus on the backend so the UI can
   * render each citation as a real numbered, clickable link even when
   * the model cited a playbook outside the retrieved top-K. */
  citationIndex: CitationIndexEntry[];
  /** Agentic-chat skill execution timeline. Empty for legacy chat or
   *  questions where Claude didn't call any tools. */
  events: ChatEvent[];
  /** True once the SSE 'composing' event arrives — signals to the UI
   *  that the skills phase is over and prose is incoming. */
  composing: boolean;
  status: ChatStatus;
  errorMsg: string | null;
  activeSessionId: number | null;
  setQuestion: (v: string) => void;
  setTopK: (v: number) => void;
  ask: () => void;
  clear: () => void;
  loadSession: (id: number) => Promise<void>;
}


const ChatContext = createContext<ChatStore | null>(null);


export function useChatStore(): ChatStore {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error('useChatStore must be used inside ChatStoreProvider');
  return ctx;
}


// localStorage keys — kept distinct so they don't collide with anything else.
const LS_ACTIVE_ID = 'signal-pilot.chat.activeSessionId';
const LS_TOP_K = 'signal-pilot.chat.topK';
const LS_DRAFT = 'signal-pilot.chat.draftQuestion';


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


/** Collapse paired skill_executing/skill_executed entries into a single
 *  row per call. Backend persists every event the daemon emitted, so
 *  events_json contains BOTH halves of every tool call. During live
 *  streaming the SSE handlers below fold them in real time; on history
 *  load we get the raw stream from the DB and have to do the same here
 *  — otherwise switching between chats keeps appending stale "running"
 *  rows next to their already-finished counterparts.
 *
 *  Match strategy: call_id (Anthropic-issued unique id) when present;
 *  fall back to the most recent executing row of the same skill name
 *  for legacy sessions that pre-date that field. Composing markers
 *  pass through unchanged. */
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
  // Initial state from localStorage (lazy init so we read once per mount).
  const [question, setQuestionState] = useState<string>(() => readString(LS_DRAFT));
  const [askedQuestion, setAskedQuestion] = useState('');
  const [topK, setTopKState] = useState<number>(() => {
    // 5 by default: chat is the operator's research surface, more
    // grounding wins over a marginal token saving. Power users can
    // dial it down in /settings.
    const v = readNumber(LS_TOP_K, 5);
    return Math.max(1, Math.min(5, v));
  });
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<RetrievalHitOut[]>([]);
  const [citationIndex, setCitationIndex] = useState<CitationIndexEntry[]>([]);
  const [events, setEvents] = useState<ChatEvent[]>([]);
  const [composing, setComposing] = useState(false);
  const [status, setStatus] = useState<ChatStatus>('idle');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);

  const abortRef = useRef<AbortController | null>(null);

  // --- Smooth streaming machinery ---------------------------------------
  // targetRef holds the FULL text the server has sent; displayedRef mirrors
  // the (state) ``answer`` so the RAF tick can read its own progress
  // without going through React's batching. The tick drains target into
  // displayed at adaptiveChars(...) chars/sec.
  const targetRef = useRef('');
  const displayedRef = useRef('');
  const streamDoneRef = useRef(false);
  const rafRef = useRef<number | null>(null);
  const lastTickRef = useRef<number>(0);
  // Fractional char accumulator. The desired chars-per-frame is usually
  // a small float (e.g. 0.84 at the baseline 50 cps × 16 ms), so we
  // can't just floor() it — that would clip every frame to 0 and the
  // floor-then-Math.max(1) workaround would inflate the effective rate
  // to 60 cps regardless of the tier. We accumulate the fraction and
  // emit whole chars when it crosses 1.
  const charBudgetRef = useRef(0);

  function adaptiveCharsPerSecond(gap: number, streamDone: boolean): number {
    // When the stream is done, flush whatever remains briskly but still
    // smoothly — proportional to the gap so a 50-char tail finishes in
    // ~half a second, a 2000-char tail in ~3 seconds.
    if (streamDone) return Math.max(160, gap * 6);
    // Live streaming: ~50 c/s is the readable baseline (close to fast
    // human typing). We speed up when the buffer balloons so the user
    // doesn't fall behind the server.
    if (gap > 500) return 400;
    if (gap > 200) return 200;
    if (gap > 50) return 100;
    return 50;
  }

  function tick(now: number) {
    if (lastTickRef.current === 0) lastTickRef.current = now;
    // dt always reflects ONE frame, never accumulated idle time.
    // ``lastTickRef`` is updated unconditionally below so a long pause
    // (waiting for the next SSE chunk) never lands a 500 ms-worth of
    // chars in a single frame — that's what caused the visible "batch
    // jump" after the first few seconds of streaming.
    const dt = now - lastTickRef.current;
    lastTickRef.current = now;

    const target = targetRef.current;
    const cur = displayedRef.current;
    const gap = target.length - cur.length;

    if (gap <= 0) {
      // Caught up. If the stream is done too, end the loop entirely;
      // otherwise wait for the next chunk in another frame. Drop the
      // accumulated char budget so a long idle doesn't dump a burst
      // when the next chunk lands.
      charBudgetRef.current = 0;
      if (streamDoneRef.current) {
        rafRef.current = null;
        return;
      }
      rafRef.current = requestAnimationFrame(tick);
      return;
    }

    const cps = adaptiveCharsPerSecond(gap, streamDoneRef.current);
    // Accumulate fractional chars across frames so cps tiers below
    // ~60 chars/sec are honoured cleanly. A budget cap protects against
    // huge dt spikes (browser-throttled tab, GC pause) producing a
    // visible flush.
    charBudgetRef.current = Math.min(
      charBudgetRef.current + (dt / 1000) * cps,
      Math.max(8, cps * 0.1),
    );
    const charsToAdd = Math.floor(charBudgetRef.current);
    if (charsToAdd <= 0) {
      rafRef.current = requestAnimationFrame(tick);
      return;
    }
    charBudgetRef.current -= charsToAdd;
    const nextLen = Math.min(cur.length + charsToAdd, target.length);
    const next = target.slice(0, nextLen);
    displayedRef.current = next;
    setAnswer(next);
    rafRef.current = requestAnimationFrame(tick);
  }

  function startRAF() {
    if (rafRef.current != null) return;
    lastTickRef.current = 0;
    charBudgetRef.current = 0;
    rafRef.current = requestAnimationFrame(tick);
  }

  function stopRAF() {
    if (rafRef.current != null) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    lastTickRef.current = 0;
    charBudgetRef.current = 0;
  }

  function resetStreamRefs() {
    stopRAF();
    targetRef.current = '';
    displayedRef.current = '';
    streamDoneRef.current = false;
  }

  /** Set the answer instantly (no typing animation). Used for already-
   * completed sessions loaded from history. */
  function setAnswerInstant(text: string) {
    stopRAF();
    targetRef.current = text;
    displayedRef.current = text;
    streamDoneRef.current = true;
    setAnswer(text);
  }

  // Stop the RAF on unmount so we don't leak frames if the provider ever
  // does get torn down (e.g. in tests).
  useEffect(() => {
    return () => {
      stopRAF();
    };
  }, []);

  // --- localStorage-backed setters --------------------------------------
  const setQuestion = useCallback((v: string) => {
    setQuestionState(v);
    writeString(LS_DRAFT, v);
  }, []);

  const setTopK = useCallback((v: number) => {
    const clamped = Math.max(1, Math.min(5, v));
    setTopKState(clamped);
    writeString(LS_TOP_K, String(clamped));
  }, []);

  // --- Rehydrate the active session on mount -----------------------------
  // If the saved session is still streaming on the backend, we *re-attach*
  // to it via SSE so the operator sees the rest of the answer pour in.
  // If it's done or errored, we just paint the final state.
  useEffect(() => {
    const savedId = readNumber(LS_ACTIVE_ID, NaN);
    if (!Number.isFinite(savedId) || savedId <= 0) return;
    let cancelled = false;
    (async () => {
      try {
        const s = await getChatSession(savedId);
        if (cancelled) return;
        setAskedQuestion(s.question);
        setSources(s.hits);
        setCitationIndex(s.citation_index ?? []);
        // Seed the skill timeline from any events already persisted.
        // For an in-flight session the SSE tail will append more; for
        // a finished one this is the full replay.
        // Dedupe: backend stores both halves of every tool call. We
        // collapse them here so the UI never renders a stale running
        // row next to its already-finished counterpart.
        setEvents(dedupeEvents((s.events ?? []) as ChatEvent[]));
        setTopKState(Math.max(1, Math.min(5, s.top_k)));
        setActiveSessionId(s.id);

        if (s.status === 'streaming') {
          // Don't pre-populate from REST. The SSE tail will send the
          // saved partial as its first delta, and the RAF loop will
          // smoothly catch up. This also avoids the prev+text doubling
          // we'd otherwise hit (REST gives us s.answer; SSE then sends
          // the same content again as its first delta).
          resetStreamRefs();
          setAnswer('');
          setStatus('streaming');
          // If the persisted events already include 'composing', the
          // skills phase is past — start in composing state so the UI
          // doesn't flash back to the skill timeline frontier.
          setComposing(
            (s.events ?? []).some((e: { type?: string }) => e.type === 'composing'),
          );
          abortRef.current = attachToChatSession(s.id, {
            onSources: (e) => setSources(e.hits),
            onSkillExecuting: (e) => {
              setEvents((prev) => [
                ...prev,
                { type: 'skill_executing', skill: e.skill, params: e.params },
              ]);
            },
            onSkillExecuted: (e) => {
              setEvents((prev) => {
                const idx = prev.findIndex(
                  (ev) =>
                    ev.type === 'skill_executing' &&
                    ev.skill === e.skill &&
                    JSON.stringify(ev.params) === JSON.stringify(e.params),
                );
                const finished: ChatEvent = {
                  type: 'skill_executed',
                  skill: e.skill,
                  params: e.params,
                  ok: e.ok,
                  result: e.result,
                  error: e.error,
                  elapsed_ms: e.elapsed_ms,
                };
                if (idx === -1) return [...prev, finished];
                const copy = prev.slice();
                copy[idx] = finished;
                return copy;
              });
            },
            onComposing: () => setComposing(true),
            onDelta: (e) => {
              targetRef.current += e.text;
              startRAF();
            },
            onDone: (e) => {
              targetRef.current = e.answer;
              streamDoneRef.current = true;
              startRAF();
              if (e.citation_index) setCitationIndex(e.citation_index);
              setStatus('done');
              window.dispatchEvent(new Event('chat-sessions-changed'));
            },
            onError: (e) => {
              setErrorMsg(e.message);
              setStatus('error');
              stopRAF();
            },
          });
        } else if (s.status === 'error') {
          setAnswerInstant(s.answer);
          setErrorMsg(s.error_message ?? 'unknown error');
          setStatus('error');
          setComposing(true);
        } else {
          setAnswerInstant(s.answer);
          setStatus('done');
          setComposing(true);
        }
      } catch {
        // Stale id — the row may have been deleted. Clear and continue.
        writeString(LS_ACTIVE_ID, null);
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // --- Actions ----------------------------------------------------------
  const ask = useCallback(() => {
    const q = question.trim();
    if (!q || status === 'streaming') return;

    abortRef.current?.abort();
    resetStreamRefs();
    setAnswer('');
    setAskedQuestion(q);
    setSources([]);
    setCitationIndex([]);
    setEvents([]);
    setComposing(false);
    setErrorMsg(null);
    setActiveSessionId(null);
    writeString(LS_ACTIVE_ID, null);
    setStatus('streaming');

    abortRef.current = streamAgenticChat(q, topK, {
      onSources: (e) => {
        setSources(e.hits);
        if (e.session_id != null) {
          setActiveSessionId(e.session_id);
          writeString(LS_ACTIVE_ID, String(e.session_id));
        }
        setQuestionState('');
        writeString(LS_DRAFT, null);
        window.dispatchEvent(new Event('chat-sessions-changed'));
      },
      onSkillExecuting: (e) => {
        // Append an executing row immediately — UI shows a spinner
        // until the matching skill_executed event swaps it for the
        // result. Guard against the same call_id being emitted twice
        // (can happen on SSE reconnect mid-stream) by skipping the
        // append when a row with the same id already exists.
        setEvents((prev) => {
          if (e.call_id && prev.some(
            (r) =>
              (r.type === 'skill_executing' || r.type === 'skill_executed') &&
              r.call_id === e.call_id,
          )) {
            return prev;
          }
          return [
            ...prev,
            {
              type: 'skill_executing',
              skill: e.skill,
              params: e.params,
              call_id: e.call_id,
            },
          ];
        });
      },
      onSkillExecuted: (e) => {
        // Fold the executing row into the executed row — there must
        // only ever be ONE row per tool call. Match by call_id (the
        // Anthropic tool_use id, identical in both events) when we
        // have it; fall back to the most recent skill_executing for
        // the same skill name on legacy events that lack a call_id.
        setEvents((prev) => {
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
          let idx = -1;
          if (e.call_id) {
            idx = prev.findIndex(
              (ev) => ev.type === 'skill_executing' && ev.call_id === e.call_id,
            );
          }
          if (idx === -1) {
            // Search backwards so we hit the most recent executing
            // row for this skill name first — that's the one this
            // executed event is closing.
            for (let i = prev.length - 1; i >= 0; i--) {
              const ev = prev[i];
              if (ev.type === 'skill_executing' && ev.skill === e.skill) {
                idx = i;
                break;
              }
            }
          }
          if (idx === -1) return [...prev, finished];
          const copy = prev.slice();
          copy[idx] = finished;
          return copy;
        });
      },
      onComposing: () => {
        setComposing(true);
      },
      onDelta: (e) => {
        targetRef.current += e.text;
        startRAF();
      },
      onDone: (e) => {
        targetRef.current = e.answer;
        streamDoneRef.current = true;
        startRAF();
        if (e.citation_index) setCitationIndex(e.citation_index);
        setActiveSessionId(e.session_id);
        if (e.session_id != null) writeString(LS_ACTIVE_ID, String(e.session_id));
        setStatus('done');
        window.dispatchEvent(new Event('chat-sessions-changed'));
      },
      onError: (e) => {
        setErrorMsg(e.message);
        setStatus('error');
        stopRAF();
      },
    });
  }, [question, topK, status]);

  const clear = useCallback(() => {
    abortRef.current?.abort();
    resetStreamRefs();
    setAnswer('');
    setQuestionState('');
    writeString(LS_DRAFT, null);
    setAskedQuestion('');
    setSources([]);
    setCitationIndex([]);
    setEvents([]);
    setComposing(false);
    setErrorMsg(null);
    setActiveSessionId(null);
    writeString(LS_ACTIVE_ID, null);
    setStatus('idle');
  }, []);

  const loadSession = useCallback(async (id: number) => {
    // Abort any in-flight SSE stream from a previous chat — without
    // this its handlers keep firing and append events to the NEW
    // session's state, producing duplicate "running" rows.
    abortRef.current?.abort();
    // Reset every streaming-derived field BEFORE fetching the new
    // chat. Otherwise a fast switch shows stale tool calls and prose
    // from the previous chat for a frame.
    resetStreamRefs();
    setAnswer('');
    setEvents([]);
    setComposing(false);
    setErrorMsg(null);
    try {
      const s = await getChatSession(id);
      setQuestionState('');
      writeString(LS_DRAFT, null);
      setAskedQuestion(s.question);
      setAnswerInstant(s.answer);
      setSources(s.hits);
      setCitationIndex(s.citation_index ?? []);
      // Dedupe: backend stores both halves of every tool call. We
      // collapse them here so the UI never renders a stale running
      // row next to its already-finished counterpart.
      setEvents(dedupeEvents((s.events ?? []) as ChatEvent[]));
      // Historical sessions are already past composing; treat as such
      // so the UI doesn't show the "writing response…" frontier.
      setComposing(true);
      setTopKState(Math.max(1, Math.min(5, s.top_k)));
      setActiveSessionId(s.id);
      writeString(LS_ACTIVE_ID, String(s.id));
      setStatus('done');
      setErrorMsg(null);
    } catch (err) {
      setErrorMsg((err as Error).message);
      setStatus('error');
    }
  }, []);

  const value: ChatStore = {
    question,
    askedQuestion,
    topK,
    answer,
    sources,
    citationIndex,
    events,
    composing,
    status,
    errorMsg,
    activeSessionId,
    setQuestion,
    setTopK,
    ask,
    clear,
    loadSession,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}
