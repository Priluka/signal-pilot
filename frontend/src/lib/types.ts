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

export interface SuggestionRequest {
  playbook_id: string;
  section: string;
  step_number: number | null;
  old_text: string;
  new_text: string;
  author?: string;
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
}
export interface ChatDeltaEvent {
  text: string;
}
export interface ChatDoneEvent {
  answer: string;
  cited_ids: string[];
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
}

export interface ChatSessionDetail extends ChatSessionSummary {
  answer: string;
  hits: RetrievalHitOut[];
  cited_ids: string[];
}
