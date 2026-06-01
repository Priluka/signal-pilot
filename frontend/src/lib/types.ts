// Mirrors backend/schemas.py — keep in sync.

export interface PlaybookSummary {
  id: string;
  title: string;
  description: string;
  category: string;
  ticket_class: string;
  issue_category: string;
  languages: string[];
  country_focus: string[];
  resolution_pattern: string;
  status: string;
  extraction_confidence: number | null;
  cluster_size: number | null;
  project_keys: string[];
}

export interface TicketActionRow {
  what: string;
  who: string;
  tool: string;
  duration: string;
}

export interface EvidenceQuote {
  ticket_id: string;
  language: string | null;
  quote: string;
}

export interface ROIStrategy {
  hours_midpoint: number | null;
  hours_range_low: number | null;
  hours_range_high: number | null;
  confidence_tier: string | null;
}

export interface ROIBreakdown {
  baseline_active_hours: number | null;
  baseline_confidence_tier: string | null;
  agent_assist: ROIStrategy | null;
  product_fix: ROIStrategy | null;
  deflection: ROIStrategy | null;
  autonomous_resolve: ROIStrategy | null;
}

export interface RelatedPlaybookOut {
  id: string;
  title: string;
  description: string;
  issue_category: string;
  status: string;
}

export interface PlaybookDetail extends PlaybookSummary {
  when_applies: string;
  resolution_flow: string;
  typical_actions: string;
  typical_actions_rows: TicketActionRow[];
  risks: string;
  body: string;
  resolution_steps: string[];
  evidence_tickets: string[];
  evidence_quotes: EvidenceQuote[];
  canonical_examples: string[];
  related_playbooks: string[];
  related_playbooks_resolved: RelatedPlaybookOut[];
  created: string | null;
  updated: string | null;
  correction_count: number;
  sample_size_used: number | null;
  frequency_per_month: number | null;
  median_resolution_minutes: number | null;
  cluster_id: string | null;
  roi: ROIBreakdown | null;
  metadata: Record<string, unknown>;
}

export interface CountedName {
  name: string;
  count: number;
}

export interface CategoriesResponse {
  total: number;
  ticket_classes: CountedName[];
  issue_categories: CountedName[];
  by_ticket_class: Record<string, CountedName[]>;
}


// --- Discovery report ------------------------------------------------------
export interface DiscoveryCategoryEntry {
  name: string;
  count: number;
  playbook_titles: string[];
}

export interface DiscoveryCountryEntry {
  code: string;
  count: number;
}

export interface DiscoveryROISummary {
  baseline_hours: number;
  agent_assist_hours: number;
  autonomous_hours: number;
}

export interface DiscoveryGap {
  category: string;
  count: number;
}

export interface DiscoveryTopPlaybook {
  id: string;
  title: string;
  cluster_size: number;
}

export interface DiscoveryQuality {
  min: number | null;
  max: number | null;
  avg: number | null;
  low_confidence_count: number;
}

export interface DiscoveryReport {
  total_playbooks: number;
  total_tickets_covered: number;
  avg_confidence: number | null;
  categories: DiscoveryCategoryEntry[];
  countries: DiscoveryCountryEntry[];
  languages: CountedName[];
  roi_summary: DiscoveryROISummary;
  gaps: DiscoveryGap[];
  top_playbooks: DiscoveryTopPlaybook[];
  quality: DiscoveryQuality;
}

export interface TicketSummary {
  key: string;
  summary: string;
  status: string;
  status_category: string | null;
  priority: string | null;
  labels: string[];
  reporter_email: string | null;
  reporter_name: string | null;
  created_at: string | null;
  resolved_at: string | null;
}

export interface TicketDetail extends TicketSummary {
  description: string;
  assignee_name: string | null;
  project_key: string | null;
  issue_type: string | null;
  resolution: string | null;
  resolution_minutes: number | null;
  comment_count_total: number;
}

export interface ClassifyRequest {
  summary: string;
  description?: string;
  reporter_email?: string | null;
  labels?: string[];
}

export interface ClassifyResponse {
  label: 'support_request' | 'internal_log' | 'spam_or_junk';
  confidence: number;
  reason: string;
}

export interface RetrieveRequest {
  summary: string;
  description?: string;
  labels?: string[];
  ticket_class?: string | null;
  top_k?: number;
}

export interface RetrievalHitOut {
  playbook_id: string;
  title: string;
  description: string;
  score: number;
  rank: number;
  ticket_class: string;
  issue_category: string;
  country_focus: string[];
  languages: string[];
  status: string;
  extraction_confidence: number | null;
  project_keys: string[];
}

export interface RetrieveResponse {
  hits: RetrievalHitOut[];
  detected_language: string | null;
  detected_country: string | null;
}

export interface DraftRequest {
  ticket_summary: string;
  ticket_description?: string;
  playbook_id: string;
}

export interface DraftResponse {
  draft: string;
  recommended_action: 'send_draft' | 'send_with_review' | 'escalate_to_human' | 'auto_close';
  rationale: string;
}

/** Single source of truth for an Agent Feed ticket's state. Mirrors the
 * backend's ``derive_status`` so the frontend can render the same pill
 * regardless of how the session reached that state. */
export type AgentStatus =
  | 'pending'
  | 'in_progress'
  | 'skipped'
  | 'auto_resolved'
  | 'auto_drafted'
  | 'needs_review'
  | 'escalated'
  | 'approved'
  | 'rejected';

export interface AgentSessionSummary {
  ticket_id: string;
  derived_status: AgentStatus;
  classification_label: string | null;
  classification_confidence: number | null;
  draft_playbook_id: string | null;
  draft_playbook_title: string | null;
  recommended_action: string | null;
  feedback_status: 'approved' | 'edited' | 'rejected' | null;
  updated_at: string;
  drafted_at: string | null;
  feedback_at: string | null;
  processed_mode?: AgentMode | null;
}

export interface AgentSessionDetail {
  ticket_id: string;
  classification: ClassifyResponse | null;
  retrieval: RetrieveResponse | null;
  draft: DraftResponse | null;
  draft_playbook_id: string | null;
  edited_text: string | null;
  feedback_status: 'approved' | 'edited' | 'rejected' | null;
  derived_status: AgentStatus;
  updated_at: string;
  started_at: string | null;
  classified_at: string | null;
  retrieved_at: string | null;
  drafted_at: string | null;
  feedback_at: string | null;
  auto_posted_at?: string | null;
  processed_mode?: AgentMode | null;
  jira_browse_url?: string | null;
  planner_status?: 'done' | 'awaiting_approval' | 'failed' | 'max_iterations' | null;
  planner_error?: string | null;
  planner_updated_at?: string | null;
  /** Writer path picked at retrieve time. 'drafter' = classic single-LLM
   *  reply, 'planner' = tool_use skills loop. Mutually exclusive; the
   *  timeline branches on this rather than guessing from drafted_at. */
  routing?: 'drafter' | 'planner' | null;
  /** First crashed step persisted on the session row. Frontend renders
   *  this as a red error node identical to the live SSE error event —
   *  without it a refresh after a failure shows an infinite spinner. */
  error_step?: 'classify' | 'retrieve' | 'draft' | 'planner' | null;
  error_message?: string | null;
}

export interface BatchStatus {
  running: boolean;
  processed: number;
  total: number;
  started_at: string | null;
  finished_at: string | null;
  current_ticket: string | null;
  errors: { ticket_id: string; step: string; message: string }[];
}

export interface AgentMetrics {
  total: number;
  processed: number;
  needs_review: number;
  auto_drafted: number;
  auto_resolved: number;
  escalated: number;
  skipped: number;
  approved: number;
  rejected: number;
  in_progress: number;
  pending: number;
  approval_rate: number;
  avg_confidence: number;
}

export type AgentEventType =
  | 'classified'
  | 'retrieved'
  | 'drafted'
  | 'approved'
  | 'edited'
  | 'rejected'
  | 'skipped'
  | 'suggestion_created'
  | 'suggestion_accepted'
  | 'suggestion_rejected'
  | 'config_change';

export interface SuggestionDiff {
  /** Removed text — null for add/new-step suggestions. */
  old: string | null;
  /** Added text — null for removal suggestions. */
  new: string | null;
}

export interface AgentActivityEvent {
  timestamp: string;
  ticket_id: string;
  event_type: AgentEventType;
  detail: string;
  /** Populated only on suggestion_* events so the Activity Log can
   * render the actual content change below the metadata line. */
  diff?: SuggestionDiff | null;
}

export interface FeedbackRequest {
  ticket_id: string;
  playbook_id: string;
  draft_text: string;
  final_text?: string | null;
  status: 'approved' | 'edited' | 'rejected';
}

export interface FeedbackRecord {
  id: number;
  ticket_id: string;
  playbook_id: string;
  draft_text: string;
  final_text: string | null;
  status: string;
  timestamp: string;
}

export interface FeedbackStats {
  approved: number;
  edited: number;
  rejected: number;
  total: number;
}

export type SuggestionKind = 'edit' | 'add' | 'remove';

export interface SuggestionRequest {
  playbook_id: string;
  section: string;
  step_number?: number | null;
  old_text?: string;
  new_text?: string;
  author?: string;
  /** 'edit' (default), 'add' to insert a new step/bullet, or 'remove' to delete one. */
  type?: SuggestionKind;
  /** Only meaningful for type='add'. Format: 'end' (append) or 'after:N' (1-indexed). */
  position?: string | null;
}

export interface SuggestionRecord {
  id: number;
  playbook_id: string;
  section: string;
  step_number: number | null;
  old_text: string;
  new_text: string;
  author: string;
  status: 'pending' | 'accepted' | 'rejected';
  timestamp: string;
  decided_at?: string | null;
  type?: SuggestionKind;
  position?: string | null;
}

export interface SuggestionStats {
  pending: number;
  accepted: number;
  rejected: number;
  total: number;
}


// --- Agent Skills (planner / HITL) ----------------------------------------
export interface PendingAction {
  id: string;
  ticket_id: string;
  playbook_id: string;
  skill_name: string;
  skill_input: Record<string, unknown>;
  mode: string;
  iteration: number;
  created_at: string;
}

export interface PlannerResultOut {
  status: 'done' | 'awaiting_approval' | 'failed' | 'max_iterations';
  pending_action_id: string | null;
  error: string | null;
  iterations: number;
  summary: string | null;
}

// --- /jira/process/{key}/stream — SSE step events --------------------------
export type AgentStepEvent =
  | { type: 'started'; ticket_id: string; mode: string; at: string }
  | {
      type: 'classified';
      label: string;
      confidence: number;
      reason: string;
      at: string;
    }
  | { type: 'skipped'; reason: string }
  | {
      type: 'retrieved';
      hits: RetrievalHitOut[];
      detected_language: string | null;
      detected_country: string | null;
      // Writer chosen for the next stage. Null if no hits / playbook not
      // loaded (no downstream writer will run).
      routing: 'drafter' | 'planner' | null;
      at: string;
    }
  | { type: 'no_hits' }
  | {
      type: 'drafted';
      playbook_id: string;
      playbook_title: string;
      recommended_action: string;
      draft: string;
      rationale: string;
      at: string;
    }
  | {
      type: 'planner_started';
      mode: string;
      allowed_skills: string[];
      playbook_id?: string;
      playbook_title?: string;
    }
  | {
      type: 'planner_done';
      status: 'done' | 'awaiting_approval' | 'failed' | 'max_iterations';
      summary: string | null;
      error: string | null;
      iterations: number;
      pending_action_id: string | null;
    }
  | { type: 'error'; step: string; message: string }
  | { type: 'done'; ticket_id: string };


export interface AuditEntry {
  id: number;
  ticket_id: string;
  playbook_id: string;
  skill_name: string;
  skill_input: Record<string, unknown>;
  outcome: 'approved' | 'rejected' | 'auto' | 'shadow' | 'planner_error';
  ok: boolean;
  result_data: Record<string, unknown> | null;
  error: string | null;
  decided_by: string | null;
  mode: string;
  iteration: number;
  decided_at: string;
}

// Knowledge graph
export interface GraphNode {
  id: string;
  title: string;
  ticket_class: string;
  issue_category: string;
  cluster_size: number | null;
  extraction_confidence: number | null;
  status: string;
  degree: number;
}

export interface GraphEdge {
  source: string;
  target: string;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}


// SSE event payloads
export interface ChatSourcesEvent {
  hits: RetrievalHitOut[];
  /** Backend-assigned row id, present once the session row has been
   * created (before the first delta arrives). null if the persistence
   * write failed. */
  session_id: number | null;
}
export interface ChatDeltaEvent {
  text: string;
}
export interface CitationIndexEntry {
  playbook_id: string;
  title: string;
  description?: string;
  /** True when the playbook was in the top-K we showed the model. False
   * when the model cited a playbook from outside the retrieved set
   * (still resolvable to a real playbook via the full corpus lookup). */
  in_topk: boolean;
  /** False when the model hallucinated an id that doesn't exist anywhere
   * in the corpus. The UI suppresses these so the operator never sees a
   * broken citation marker. */
  exists: boolean;
}

export interface ChatDoneEvent {
  answer: string;
  cited_ids: string[];
  citation_index?: CitationIndexEntry[];
  session_id: number | null;
}
export interface ChatErrorEvent {
  message: string;
}

// Chat history
export interface ChatSessionSummary {
  id: number;
  question: string;
  top_k: number;
  timestamp: string;
  source_count: number;
  citation_count: number;
  status: 'streaming' | 'done' | 'error';
}

export interface ChatSessionDetail extends ChatSessionSummary {
  answer: string;
  hits: RetrievalHitOut[];
  cited_ids: string[];
  citation_index: CitationIndexEntry[];
  error_message: string | null;
  /** Replay timeline for agentic chat sessions — empty for legacy
   *  text-only chat. Each entry mirrors the SSE event payload. */
  events?: ChatEvent[];
}

export type ChatEvent =
  | {
      type: 'skill_executing';
      skill: string;
      params: Record<string, unknown>;
      /** Anthropic-issued tool_use id. Used as the join key between
       *  executing/executed events so the timeline collapses to one
       *  row per call regardless of params equality quirks. Optional
       *  for backwards compat with sessions persisted before the id
       *  was tracked. */
      call_id?: string;
    }
  | {
      type: 'skill_executed';
      skill: string;
      params: Record<string, unknown>;
      call_id?: string;
      ok: boolean;
      result: Record<string, unknown> | null;
      error: string | null;
      elapsed_ms: number;
    }
  | { type: 'composing' };

// Agent runtime config + per-playbook overrides
export type AgentMode = 'shadow' | 'assisted' | 'autonomous';

export interface AgentConfig {
  mode: AgentMode;
  confidence_threshold: number;
}

export interface AgentConfigUpdate {
  mode?: AgentMode;
  confidence_threshold?: number;
}

export interface PlaybookModeRow {
  playbook_id: string;
  title: string;
  ticket_class: string;
  mode: AgentMode;
  is_override: boolean;
  sample_count: number;
  approved_count: number;
  edited_count: number;
  rejected_count: number;
  approve_rate: number | null;
  avg_confidence: number | null;
}

export interface AgentOverview {
  name: string;
  status: string;
  mode: AgentMode;
  confidence_threshold: number;
  source_label: string;
  playbooks_loaded: number;
  processed: number;
  approval_rate: number | null;
  approved_count: number;
  rejected_count: number;
  avg_confidence: number | null;
  uptime_since: string | null;
}

export interface JiraConnectionStatus {
  configured: boolean;
  url: string | null;
  email: string | null;
  project: string | null;
  token_masked: string | null;
  reachable: boolean | null;
  detail: string | null;
}

// Jira — same shape as TicketSummary / TicketDetail, just aliased for clarity.
export type JiraTicketSummary = TicketSummary;
export type JiraTicketDetail = TicketDetail;

export interface JiraCommentRequest {
  issue_key: string;
  body: string;
}

export interface JiraCommentResponse {
  id: string;
  issue_key: string;
  created: string | null;
  author: string | null;
}
