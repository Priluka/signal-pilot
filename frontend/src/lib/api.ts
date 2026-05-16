/**
 * Typed client for the Signal Pilot backend.
 *
 * Base URL falls back to ``http://localhost:8000`` so ``npm run dev`` works
 * against a local FastAPI on the default port without extra config. Override
 * with ``VITE_API_URL=https://api.example.com`` in ``.env.local``.
 */
import type {
  CategoriesResponse,
  ChatDeltaEvent,
  ChatDoneEvent,
  ChatErrorEvent,
  ChatSourcesEvent,
  ClassifyRequest,
  ClassifyResponse,
  DraftRequest,
  DraftResponse,
  FeedbackRecord,
  FeedbackRequest,
  FeedbackStats,
  PlaybookDetail,
  PlaybookSummary,
  RetrieveRequest,
  RetrieveResponse,
  TicketDetail,
  TicketSummary,
} from './types';

const API_BASE: string =
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000';

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    let detail = '';
    try {
      const body = await res.json();
      detail = body?.detail ?? JSON.stringify(body);
    } catch {
      detail = res.statusText;
    }
    throw new Error(`${res.status} ${path}: ${detail}`);
  }
  return (await res.json()) as T;
}

// --- Playbooks -------------------------------------------------------------
export interface PlaybookFilters {
  ticket_class?: string;
  issue_category?: string;
  country?: string;
  language?: string;
  q?: string;
}

export function listPlaybooks(filters: PlaybookFilters = {}): Promise<PlaybookSummary[]> {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (v) qs.set(k, v);
  }
  const tail = qs.toString() ? `?${qs}` : '';
  return json<PlaybookSummary[]>(`/playbooks${tail}`);
}

export function getPlaybook(id: string): Promise<PlaybookDetail> {
  return json<PlaybookDetail>(`/playbooks/${encodeURIComponent(id)}`);
}

export function getCategories(): Promise<CategoriesResponse> {
  return json<CategoriesResponse>('/categories');
}

// --- Tickets ---------------------------------------------------------------
export function listTickets(): Promise<TicketSummary[]> {
  return json<TicketSummary[]>('/tickets');
}

export function getTicket(key: string): Promise<TicketDetail> {
  return json<TicketDetail>(`/tickets/${encodeURIComponent(key)}`);
}

// --- Agent -----------------------------------------------------------------
export function classifyTicket(req: ClassifyRequest): Promise<ClassifyResponse> {
  return json<ClassifyResponse>('/agent/classify', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export function retrievePlaybooks(req: RetrieveRequest): Promise<RetrieveResponse> {
  return json<RetrieveResponse>('/agent/retrieve', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export function draftReply(req: DraftRequest): Promise<DraftResponse> {
  return json<DraftResponse>('/agent/draft', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

// --- Feedback --------------------------------------------------------------
export function submitFeedback(req: FeedbackRequest): Promise<FeedbackRecord> {
  return json<FeedbackRecord>('/feedback', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export function getFeedbackStats(): Promise<FeedbackStats> {
  return json<FeedbackStats>('/feedback/stats');
}

// --- Chat (SSE) ------------------------------------------------------------
export interface ChatStreamHandlers {
  onSources?: (e: ChatSourcesEvent) => void;
  onDelta?: (e: ChatDeltaEvent) => void;
  onDone?: (e: ChatDoneEvent) => void;
  onError?: (e: ChatErrorEvent) => void;
}

/**
 * POST /chat/answer is an SSE endpoint, but EventSource is GET-only — so we
 * read the response body as a stream and parse the SSE wire format manually.
 *
 * Wire format (one event per blank-line-delimited block):
 *
 *     event: sources
 *     data: {"hits": [...]}
 *
 * Returns an AbortController so callers can cancel mid-stream.
 */
export function streamChatAnswer(
  question: string,
  top_k: number,
  handlers: ChatStreamHandlers,
): AbortController {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${API_BASE}/chat/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, top_k }),
        signal: controller.signal,
      });
      if (!res.ok || !res.body) {
        handlers.onError?.({ message: `${res.status} ${res.statusText}` });
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // SSE separates events with a blank line (\n\n).
        let blankIdx: number;
        while ((blankIdx = buffer.indexOf('\n\n')) !== -1) {
          const raw = buffer.slice(0, blankIdx);
          buffer = buffer.slice(blankIdx + 2);
          dispatchEvent(raw, handlers);
        }
      }
    } catch (err) {
      if ((err as Error).name === 'AbortError') return;
      handlers.onError?.({ message: (err as Error).message });
    }
  })();

  return controller;
}

function dispatchEvent(raw: string, handlers: ChatStreamHandlers): void {
  let eventName = 'message';
  const dataLines: string[] = [];
  for (const line of raw.split('\n')) {
    if (line.startsWith('event:')) {
      eventName = line.slice(6).trim();
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trim());
    }
  }
  if (dataLines.length === 0) return;
  let payload: unknown;
  try {
    payload = JSON.parse(dataLines.join('\n'));
  } catch {
    return;
  }
  switch (eventName) {
    case 'sources':
      handlers.onSources?.(payload as ChatSourcesEvent);
      break;
    case 'delta':
      handlers.onDelta?.(payload as ChatDeltaEvent);
      break;
    case 'done':
      handlers.onDone?.(payload as ChatDoneEvent);
      break;
    case 'error':
      handlers.onError?.(payload as ChatErrorEvent);
      break;
  }
}
