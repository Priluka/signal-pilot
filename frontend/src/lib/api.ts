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
  AgentStepEvent,
  BatchStatus,
  CategoriesResponse,
  ChatDeltaEvent,
  AuditEntry,
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

// Operator bearer token from .env.local — paired with backend OPERATOR_TOKEN.
// Empty / unset means dev-mode (backend also unauthenticated).
const OPERATOR_TOKEN: string | undefined = (
  import.meta.env.VITE_OPERATOR_TOKEN as string | undefined
)?.trim();

function _authHeader(): Record<string, string> {
  return OPERATOR_TOKEN ? { Authorization: `Bearer ${OPERATOR_TOKEN}` } : {};
}

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  // Merge order: caller's headers win over defaults, but auth always
  // attaches because spreading init AFTER our header object would
  // erase Authorization. Keep auth inside the final merged object.
  const callerHeaders = (init?.headers as Record<string, string> | undefined) ?? {};
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ..._authHeader(),
      ...callerHeaders,
    },
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


/**
 * SSE stream of agent processing milestones — one event per step
 * (classified → retrieved → drafted → planner_*). The frontend feeds
 * these into AgentTimeline so the operator watches the work happen
 * live instead of staring at a spinner for 20 seconds.
 *
 * Resolves once the server has sent a ``done`` event (or surfaces
 * ``error``). Caller passes ``onEvent`` to receive each step as it
 * arrives. AbortController support so navigating away cancels the
 * connection cleanly.
 */
export async function streamProcessJiraTicket(
  issueKey: string,
  onEvent: (event: AgentStepEvent) => void,
  opts: { signal?: AbortSignal } = {},
): Promise<void> {
  const res = await fetch(
    `${API_BASE}/jira/process/${encodeURIComponent(issueKey)}/stream`,
    {
      method: 'POST',
      headers: { ..._authHeader() },
      signal: opts.signal,
    },
  );
  if (!res.ok || !res.body) {
    const txt = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} stream: ${txt}`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    // SSE frames are separated by blank lines. Split, keep the trailing
    // incomplete frame in the buffer for the next chunk.
    const frames = buffer.split('\n\n');
    buffer = frames.pop() ?? '';
    for (const frame of frames) {
      const parsed = _parseSseFrame(frame);
      if (parsed) onEvent(parsed);
    }
  }
}


function _parseSseFrame(frame: string): AgentStepEvent | null {
  let eventName = 'message';
  const dataLines: string[] = [];
  for (const line of frame.split('\n')) {
    if (line.startsWith('event:')) {
      eventName = line.slice('event:'.length).trim();
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice('data:'.length).trim());
    }
  }
  if (dataLines.length === 0) return null;
  try {
    const data = JSON.parse(dataLines.join('\n'));
    return { type: eventName, ...data } as AgentStepEvent;
  } catch {
    return null;
  }
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

export function listActionHistoryForTicket(
  ticketId: string,
): Promise<AuditEntry[]> {
  return json<AuditEntry[]>(
    `/actions/history/${encodeURIComponent(ticketId)}`,
  );
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


// --- Multi-turn chat threads (Phase 4) -------------------------------------


/** Create a brand-new empty thread. The backend auto-derives the
 *  title from the first turn's user_text once it lands. Frontend calls
 *  this when the operator clicks 'New chat' (or implicitly on the
 *  first message when no thread is active). */
export function createThread(
  title?: string,
): Promise<import('./types').ChatThread> {
  return json<import('./types').ChatThread>('/chat/threads', {
    method: 'POST',
    body: JSON.stringify({ title: title ?? null }),
  });
}


export function listThreads(): Promise<import('./types').ChatThreadSummary[]> {
  return json<import('./types').ChatThreadSummary[]>('/chat/threads');
}


export function getThreadDetail(
  id: number,
): Promise<import('./types').ChatThreadDetail> {
  return json<import('./types').ChatThreadDetail>(`/chat/threads/${id}`);
}


export async function deleteThread(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/chat/threads/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`${res.status} delete /chat/threads/${id}`);
}


/** Append a new turn to a thread and consume the SSE response.
 *  Wire format mirrors the legacy /chat/agentic stream — same
 *  ``sources / skill_executing / skill_executed / composing / delta /
 *  done / error`` events, plus a new ``compacted`` event when the
 *  multi-turn compaction layer kicks in. */
export function streamThreadTurn(
  thread_id: number,
  user_text: string,
  top_k: number,
  handlers: ChatStreamHandlers,
): AbortController {
  return _consumeSSE(
    `${API_BASE}/chat/threads/${thread_id}/turns`,
    { method: 'POST', body: JSON.stringify({ user_text, top_k }) },
    handlers,
  );
}


/** Cancel an in-flight turn. Backend sets a cooperative flag; the
 *  agent loop checks it at the next iteration boundary and exits
 *  with ``status='error'`` + a specific error_message the UI keys on
 *  to render "Stopped" instead of "Error". Latency up to one full
 *  Anthropic round-trip (5-15s). Idempotent. */
export async function interruptThreadTurn(
  thread_id: number,
  turn_id: number,
): Promise<void> {
  const res = await fetch(
    `${API_BASE}/chat/threads/${thread_id}/turns/${turn_id}/interrupt`,
    { method: 'POST' },
  );
  if (!res.ok) {
    throw new Error(`${res.status} interrupt turn ${turn_id}`);
  }
}


/** Re-attach to a turn that's already mid-stream (refresh during
 *  active generation). Replays whatever events have been persisted so
 *  far, then continues live until ``done`` / ``error``. */
export function attachToThreadTurn(
  thread_id: number,
  turn_id: number,
  handlers: ChatStreamHandlers,
): AbortController {
  return _consumeSSE(
    `${API_BASE}/chat/threads/${thread_id}/turns/${turn_id}/stream`,
    { method: 'GET' },
    handlers,
  );
}

// --- Chat (SSE) ------------------------------------------------------------
export interface ChatSkillExecutingEvent {
  skill: string;
  params: Record<string, unknown>;
  /** Anthropic tool_use id — same value lands in the matching executed
   *  event so the timeline can fold both into one row. */
  call_id?: string;
}
export interface ChatSkillExecutedEvent {
  skill: string;
  params: Record<string, unknown>;
  call_id?: string;
  ok: boolean;
  result: Record<string, unknown> | null;
  error: string | null;
  elapsed_ms: number;
}
export interface ChatComposingEvent {
  // empty payload — just a signal that token stream is about to start
}
export interface ChatThinkingEvent {
  /** 1-based iteration index. Reaches the operator BEFORE the
   *  Anthropic stream returns its first byte for the iteration, so
   *  the UI can show a heartbeat during the silent gap between a
   *  tool_result and the next text/tool_use block. */
  iteration: number;
}
export interface ChatThinkingTextEvent {
  /** A chunk of the agent's extended-thinking channel. Streams just
   *  like a text delta — append to the accumulated thinking buffer
   *  for the current turn. */
  text: string;
}
export interface ChatCompactedEvent {
  tier: number;
  before_tokens: number;
  after_tokens: number;
  dropped_turns: number;
}
export interface ChatStreamHandlers {
  onSources?: (e: ChatSourcesEvent) => void;
  onDelta?: (e: ChatDeltaEvent) => void;
  onDone?: (e: ChatDoneEvent) => void;
  onError?: (e: ChatErrorEvent) => void;
  // New agentic-only events. Legacy /chat/answer never emits these, so
  // the handlers are optional and the same component can consume either
  // wire format.
  onSkillExecuting?: (e: ChatSkillExecutingEvent) => void;
  onSkillExecuted?: (e: ChatSkillExecutedEvent) => void;
  onComposing?: (e: ChatComposingEvent) => void;
  /** Heartbeat fired at the top of every agent iteration so the UI
   *  has a continuous activity signal even when the next Anthropic
   *  call takes several seconds to first byte. */
  onThinking?: (e: ChatThinkingEvent) => void;
  /** Phase 9B — extended-thinking delta. UI accumulates and renders
   *  as a collapsible quote above the final answer. */
  onThinkingText?: (e: ChatThinkingTextEvent) => void;
  /** Fires whenever the multi-turn compaction layer trims the
   *  context. Tier 1 = snip; Tier 2 = drop old turns; Tier 3 =
   *  LLM summarisation. UI can surface a small badge so the
   *  operator knows older context has been compressed. */
  onCompacted?: (e: ChatCompactedEvent) => void;
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


/** Agentic chat: same wire as /chat/answer plus skill_executing /
 *  skill_executed / composing events. When the top retrieved playbook
 *  has read-only skills, the backend drives a tool_use loop and emits
 *  skill timeline events before streaming the final answer. Otherwise
 *  it falls back to plain text streaming and the new event types
 *  simply don't fire. Frontend uses the same handler shape for both. */
export function streamAgenticChat(
  question: string,
  top_k: number,
  handlers: ChatStreamHandlers,
): AbortController {
  return _consumeSSE(
    `${API_BASE}/chat/agentic`,
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
    case 'skill_executing':
      handlers.onSkillExecuting?.(payload as ChatSkillExecutingEvent);
      break;
    case 'skill_executed':
      handlers.onSkillExecuted?.(payload as ChatSkillExecutedEvent);
      break;
    case 'composing':
      handlers.onComposing?.(payload as ChatComposingEvent);
      break;
    case 'thinking':
      handlers.onThinking?.(payload as ChatThinkingEvent);
      break;
    case 'thinking_text':
      handlers.onThinkingText?.(payload as ChatThinkingTextEvent);
      break;
    case 'compacted':
      handlers.onCompacted?.(payload as ChatCompactedEvent);
      break;
  }
}
