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

export interface AgentActivityEvent {
  timestamp: string;
  ticket_id: string;
  event_type: AgentEventType;
  detail: string;
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
}

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
