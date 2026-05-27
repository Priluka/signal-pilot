/**
 * Typed client for the Signal Pilot backend.
 *
 * Base URL falls back to ``http://localhost:8000`` so ``npm run dev`` works
 * against a local FastAPI on the default port without extra config. Override
 * with ``VITE_API_URL=https://api.example.com`` in ``.env.local``.
 */
import type {
  AgentActivityEvent,
  AgentMetrics,
  AgentSessionDetail,
  AgentSessionSummary,
  BatchStatus,
  CategoriesResponse,
  ChatDeltaEvent,
  DiscoveryReport,
  PendingAction,
  PlannerResultOut,
  ChatDoneEvent,
  ChatErrorEvent,
  ChatSessionDetail,
  ChatSessionSummary,
  ChatSourcesEvent,
  ClassifyRequest,
  ClassifyResponse,
  DraftRequest,
  DraftResponse,
  FeedbackRecord,
  FeedbackRequest,
  FeedbackStats,
  AgentConfig,
  AgentConfigUpdate,
  AgentOverview,
  GraphResponse,
  JiraCommentRequest,
  JiraCommentResponse,
  JiraConnectionStatus,
  JiraTicketDetail,
  JiraTicketSummary,
  PlaybookDetail,
  PlaybookModeRow,
  PlaybookSummary,
  RetrieveRequest,
  RetrieveResponse,
  SuggestionRecord,
  SuggestionRequest,
  SuggestionStats,
  TicketDetail,
  TicketSummary,
} from './types';

import { cachedFetch } from './cache';


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
  // /playbooks (no filters) is the heaviest stable resource — every page
  // mount used to refetch it. Cache the unfiltered case; filtered calls
  // are rare and stay live.
  if (!tail) {
    return cachedFetch('playbooks', () => json<PlaybookSummary[]>('/playbooks'));
  }
  return json<PlaybookSummary[]>(`/playbooks${tail}`);
}

export function getPlaybook(id: string): Promise<PlaybookDetail> {
  return cachedFetch(`playbook:${id}`, () =>
    json<PlaybookDetail>(`/playbooks/${encodeURIComponent(id)}`),
  );
}

export function getCategories(): Promise<CategoriesResponse> {
  return cachedFetch('categories', () => json<CategoriesResponse>('/categories'));
}

export function getDiscoveryReport(): Promise<DiscoveryReport> {
  return json<DiscoveryReport>('/discovery/report');
}

export function getGraph(): Promise<GraphResponse> {
  return cachedFetch('graph', () => json<GraphResponse>('/playbooks/graph'));
}

// --- Tickets ---------------------------------------------------------------
export function listTickets(): Promise<TicketSummary[]> {
  return cachedFetch('tickets', () => json<TicketSummary[]>('/tickets'));
}

export function getTicket(key: string): Promise<TicketDetail> {
  return cachedFetch(`ticket:${key}`, () =>
    json<TicketDetail>(`/tickets/${encodeURIComponent(key)}`),
  );
}

// --- Jira ------------------------------------------------------------------
// Live data; no caching — the operator wants to see the current state of
// their Jira board, not whatever we fetched five minutes ago.
export function listJiraTickets(limit = 100): Promise<JiraTicketSummary[]> {
  return json<JiraTicketSummary[]>(`/jira/tickets?limit=${limit}`);
}

export function getJiraTicket(issueKey: string): Promise<JiraTicketDetail> {
  return json<JiraTicketDetail>(`/jira/tickets/${encodeURIComponent(issueKey)}`);
}

export function processJiraTicket(issueKey: string): Promise<AgentSessionDetail> {
  return json<AgentSessionDetail>(
    `/jira/process/${encodeURIComponent(issueKey)}`,
    { method: 'POST' },
  );
}

export function postJiraComment(req: JiraCommentRequest): Promise<JiraCommentResponse> {
  return json<JiraCommentResponse>('/jira/comment', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export function getJiraConnection(probe = false): Promise<JiraConnectionStatus> {
  return json<JiraConnectionStatus>(`/jira/connection${probe ? '?probe=true' : ''}`);
}

// --- Agent config / overview / per-playbook modes -------------------------
export function getAgentConfig(): Promise<AgentConfig> {
  return json<AgentConfig>('/agent/config');
}

export function updateAgentConfig(req: AgentConfigUpdate): Promise<AgentConfig> {
  return json<AgentConfig>('/agent/config', {
    method: 'PUT',
    body: JSON.stringify(req),
  });
}

export function getAgentOverview(): Promise<AgentOverview> {
  return json<AgentOverview>('/agent/overview');
}

export function listPlaybookModes(): Promise<PlaybookModeRow[]> {
  return json<PlaybookModeRow[]>('/agent/playbook-modes');
}

export function updatePlaybookMode(
  playbookId: string,
  mode: 'shadow' | 'assisted' | 'autonomous' | null,
): Promise<PlaybookModeRow> {
  return json<PlaybookModeRow>(
    `/agent/playbook-modes/${encodeURIComponent(playbookId)}`,
    { method: 'PUT', body: JSON.stringify({ mode }) },
  );
}

// --- Agent -----------------------------------------------------------------
function _withTicketQuery(path: string, ticketId?: string | null): string {
  if (!ticketId) return path;
  const sep = path.includes('?') ? '&' : '?';
  return `${path}${sep}ticket_id=${encodeURIComponent(ticketId)}`;
}

export function classifyTicket(
  req: ClassifyRequest,
  ticketId?: string | null,
): Promise<ClassifyResponse> {
  return json<ClassifyResponse>(_withTicketQuery('/agent/classify', ticketId), {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export function retrievePlaybooks(
  req: RetrieveRequest,
  ticketId?: string | null,
): Promise<RetrieveResponse> {
  return json<RetrieveResponse>(_withTicketQuery('/agent/retrieve', ticketId), {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export function draftReply(
  req: DraftRequest,
  ticketId?: string | null,
): Promise<DraftResponse> {
  return json<DraftResponse>(_withTicketQuery('/agent/draft', ticketId), {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export async function getAgentSession(
  ticketId: string,
): Promise<AgentSessionDetail | null> {
  const res = await fetch(
    `${API_BASE}/agent/sessions/${encodeURIComponent(ticketId)}`,
    { headers: { 'Content-Type': 'application/json' } },
  );
  if (!res.ok) throw new Error(`${res.status} /agent/sessions/${ticketId}`);
  const body = await res.json();
  return body as AgentSessionDetail | null;
}

export function listAgentSessions(): Promise<AgentSessionSummary[]> {
  return json<AgentSessionSummary[]>('/agent/sessions');
}

export function startAgentBatch(): Promise<BatchStatus> {
  return json<BatchStatus>('/agent/batch-process', { method: 'POST' });
}

export function getAgentBatchStatus(): Promise<BatchStatus> {
  return json<BatchStatus>('/agent/batch-status');
}

export function getAgentMetrics(): Promise<AgentMetrics> {
  return json<AgentMetrics>('/agent/metrics');
}

export function listAgentActivity(limit = 500): Promise<AgentActivityEvent[]> {
  return json<AgentActivityEvent[]>(`/agent/activity?limit=${limit}`);
}

export async function deleteAgentSession(ticketId: string): Promise<void> {
  const res = await fetch(
    `${API_BASE}/agent/sessions/${encodeURIComponent(ticketId)}`,
    { method: 'DELETE' },
  );
  if (!res.ok) throw new Error(`${res.status} delete /agent/sessions/${ticketId}`);
}

// --- Agent skills (HITL approvals) -----------------------------------------
export function listPendingActions(): Promise<PendingAction[]> {
  return json<PendingAction[]>('/actions/pending');
}

export function listPendingActionsForTicket(
  ticketId: string,
): Promise<PendingAction[]> {
  return json<PendingAction[]>(
    `/actions/pending/${encodeURIComponent(ticketId)}`,
  );
}

export function approveAction(
  id: string,
  editedInput?: Record<string, unknown>,
): Promise<PlannerResultOut> {
  return json<PlannerResultOut>(`/actions/${encodeURIComponent(id)}/approve`, {
    method: 'POST',
    body: JSON.stringify({ edited_input: editedInput ?? null }),
  });
}

export function rejectAction(
  id: string,
  note?: string,
): Promise<PlannerResultOut> {
  return json<PlannerResultOut>(`/actions/${encodeURIComponent(id)}/reject`, {
    method: 'POST',
    body: JSON.stringify({ note: note ?? null }),
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

// --- Suggestions -----------------------------------------------------------
export function submitSuggestion(req: SuggestionRequest): Promise<SuggestionRecord> {
  return json<SuggestionRecord>('/suggestions', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export function listSuggestions(playbookId?: string): Promise<SuggestionRecord[]> {
  const qs = playbookId ? `?playbook_id=${encodeURIComponent(playbookId)}` : '';
  return json<SuggestionRecord[]>(`/suggestions${qs}`);
}

export function acceptSuggestion(id: number): Promise<SuggestionRecord> {
  return json<SuggestionRecord>(`/suggestions/${id}/accept`, { method: 'PUT' });
}

export function rejectSuggestion(id: number): Promise<SuggestionRecord> {
  return json<SuggestionRecord>(`/suggestions/${id}/reject`, { method: 'PUT' });
}

export function getSuggestionStats(): Promise<SuggestionStats> {
  return json<SuggestionStats>('/suggestions/stats');
}

// --- Chat history ---------------------------------------------------------
export function listChatSessions(): Promise<ChatSessionSummary[]> {
  return json<ChatSessionSummary[]>('/chat/sessions');
}

export function getChatSession(id: number): Promise<ChatSessionDetail> {
  return json<ChatSessionDetail>(`/chat/sessions/${id}`);
}

export async function deleteChatSession(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/chat/sessions/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`${res.status} delete /chat/sessions/${id}`);
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
  return _consumeSSE(
    `${API_BASE}/chat/answer`,
    { method: 'POST', body: JSON.stringify({ question, top_k }) },
    handlers,
  );
}


/**
 * Re-attach to an in-flight (or already finished) chat session.
 *
 * Used on mount when localStorage has an activeSessionId that's still
 * ``streaming`` on the backend — the generator runs in a daemon thread so
 * it survived the page refresh, and this endpoint replays whatever's in
 * the DB plus any new chunks until done.
 */
export function attachToChatSession(
  session_id: number,
  handlers: ChatStreamHandlers,
): AbortController {
  return _consumeSSE(
    `${API_BASE}/chat/sessions/${session_id}/stream`,
    { method: 'GET' },
    handlers,
  );
}


function _consumeSSE(
  url: string,
  init: RequestInit,
  handlers: ChatStreamHandlers,
): AbortController {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(url, {
        ...init,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
          ...(init.headers ?? {}),
        },
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
