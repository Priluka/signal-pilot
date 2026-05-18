/** App-level chat state.
 *
 * Lives ABOVE the router so that navigating away from /chat doesn't unmount
 * the streaming logic. The fetch keeps going, the answer keeps growing, the
 * backend still persists on done — and when the operator comes back to the
 * tab they see the answer right where they left it (or already finished, if
 * the stream completed while they were on another route).
 *
 * Aborting is only triggered by explicit user action (Clear / New chat /
 * picking another history row) — never by component unmount.
 */
import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
  type ReactNode,
} from 'react';

import { getChatSession, streamChatAnswer } from './api';
import type { RetrievalHitOut } from './types';


export type ChatStatus = 'idle' | 'streaming' | 'done' | 'error';


interface ChatStore {
  // State the UI consumes
  question: string;
  askedQuestion: string;
  topK: number;
  answer: string;
  sources: RetrievalHitOut[];
  status: ChatStatus;
  errorMsg: string | null;
  activeSessionId: number | null;
  // Actions
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


export function ChatStoreProvider({ children }: { children: ReactNode }) {
  const [question, setQuestion] = useState('');
  const [askedQuestion, setAskedQuestion] = useState('');
  const [topK, setTopK] = useState(3);
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<RetrievalHitOut[]>([]);
  const [status, setStatus] = useState<ChatStatus>('idle');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);

  const abortRef = useRef<AbortController | null>(null);

  const ask = useCallback(() => {
    const q = question.trim();
    if (!q || status === 'streaming') return;

    abortRef.current?.abort();
    setAskedQuestion(q);
    setSources([]);
    setAnswer('');
    setErrorMsg(null);
    setActiveSessionId(null);
    setStatus('streaming');

    abortRef.current = streamChatAnswer(q, topK, {
      onSources: (e) => setSources(e.hits),
      onDelta: (e) => setAnswer((prev) => prev + e.text),
      onDone: (e) => {
        setAnswer(e.answer);
        setActiveSessionId(e.session_id);
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
    setQuestion('');
    setAskedQuestion('');
    setSources([]);
    setAnswer('');
    setErrorMsg(null);
    setActiveSessionId(null);
    setStatus('idle');
  }, []);

  const loadSession = useCallback(async (id: number) => {
    abortRef.current?.abort();
    try {
      const s = await getChatSession(id);
      setQuestion('');
      setAskedQuestion(s.question);
      setAnswer(s.answer);
      setSources(s.hits);
      setTopK(s.top_k);
      setActiveSessionId(s.id);
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
