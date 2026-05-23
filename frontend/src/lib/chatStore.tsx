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

import { attachToChatSession, getChatSession, streamChatAnswer } from './api';
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
          abortRef.current = attachToChatSession(s.id, {
            onSources: (e) => setSources(e.hits),
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
        } else {
          setAnswerInstant(s.answer);
          setStatus('done');
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
    setErrorMsg(null);
    setActiveSessionId(null);
    writeString(LS_ACTIVE_ID, null);
    setStatus('streaming');

    abortRef.current = streamChatAnswer(q, topK, {
      onSources: (e) => {
        setSources(e.hits);
        // Pin the session_id to localStorage immediately so a refresh
        // mid-stream restores the row (with whatever partial answer the
        // backend has checkpointed at that moment).
        if (e.session_id != null) {
          setActiveSessionId(e.session_id);
          writeString(LS_ACTIVE_ID, String(e.session_id));
        }
        // Also drop the draft now — the question is in flight, no point
        // restoring it as a half-written textarea after refresh.
        setQuestionState('');
        writeString(LS_DRAFT, null);
        window.dispatchEvent(new Event('chat-sessions-changed'));
      },
      onDelta: (e) => {
        targetRef.current += e.text;
        startRAF();
      },
      onDone: (e) => {
        // Canonical final text — overrides any rounding error from
        // accumulated deltas. RAF will keep draining until displayed
        // catches up; status flips to 'done' now so the operator can
        // start typing the next question without waiting for the type-
        // out animation to finish.
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
    setErrorMsg(null);
    setActiveSessionId(null);
    writeString(LS_ACTIVE_ID, null);
    setStatus('idle');
  }, []);

  const loadSession = useCallback(async (id: number) => {
    abortRef.current?.abort();
    try {
      const s = await getChatSession(id);
      setQuestionState('');
      writeString(LS_DRAFT, null);
      setAskedQuestion(s.question);
      setAnswerInstant(s.answer);
      setSources(s.hits);
      setCitationIndex(s.citation_index ?? []);
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
