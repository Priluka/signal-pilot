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
  created: string | null;
  updated: string | null;
  correction_count: number;
  frequency_per_month: number | null;
  median_resolution_minutes: number | null;
  cluster_id: string | null;
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
}
export interface ChatErrorEvent {
  message: string;
}
