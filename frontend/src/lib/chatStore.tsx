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
 * Aborting is only triggered by explicit user action (Clear / New chat /
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
    const v = readNumber(LS_TOP_K, 3);
    return Math.max(1, Math.min(5, v));
  });
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<RetrievalHitOut[]>([]);
  const [citationIndex, setCitationIndex] = useState<CitationIndexEntry[]>([]);
  const [status, setStatus] = useState<ChatStatus>('idle');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);

  const abortRef = useRef<AbortController | null>(null);

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
        setAnswer(s.answer);
        setSources(s.hits);
        setCitationIndex(s.citation_index ?? []);
        setTopKState(Math.max(1, Math.min(5, s.top_k)));
        setActiveSessionId(s.id);

        if (s.status === 'streaming') {
          setStatus('streaming');
          abortRef.current = attachToChatSession(s.id, {
            onSources: (e) => setSources(e.hits),
            onDelta: (e) => setAnswer((prev) => prev + e.text),
            onDone: (e) => {
              setAnswer(e.answer);
              if (e.citation_index) setCitationIndex(e.citation_index);
              setStatus('done');
              window.dispatchEvent(new Event('chat-sessions-changed'));
            },
            onError: (e) => {
              setErrorMsg(e.message);
              setStatus('error');
            },
          });
        } else if (s.status === 'error') {
          setErrorMsg(s.error_message ?? 'unknown error');
          setStatus('error');
        } else {
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
    setAskedQuestion(q);
    setSources([]);
    setCitationIndex([]);
    setAnswer('');
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
      onDelta: (e) => setAnswer((prev) => prev + e.text),
      onDone: (e) => {
        setAnswer(e.answer);
        if (e.citation_index) setCitationIndex(e.citation_index);
        setActiveSessionId(e.session_id);
        if (e.session_id != null) writeString(LS_ACTIVE_ID, String(e.session_id));
        setStatus('done');
        window.dispatchEvent(new Event('chat-sessions-changed'));
      },
      onError: (e) => {
        setErrorMsg(e.message);
        setStatus('error');
      },
    });
  }, [question, topK, status]);

  const clear = useCallback(() => {
    abortRef.current?.abort();
    setQuestionState('');
    writeString(LS_DRAFT, null);
    setAskedQuestion('');
    setSources([]);
    setCitationIndex([]);
    setAnswer('');
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
      setAnswer(s.answer);
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
