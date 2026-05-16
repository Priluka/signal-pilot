---
id: croatia-bmove-app-feedback-miscellaneous
name: croatia_bmove_app_feedback_miscellaneous
title: Miscellaneous end-user feedback submitted via Bmove App in-app feedback form
description: 'End users in Croatia (and occasionally other countries) submit unstructured, short feedback messages through
  the Bmove App feedback form covering a wide range of topics: app problems, parking queries, permit/card management issues,
  improvement suggestions, and off-topic or incomplete messages. The tickets are highly heterogeneous in content and typically
  require minimal or no structured resolution, with many being bulk-closed or redirected to the local parking concession operator.
  A minority involve actionable issues such as inability to renew resident parking permits or missing map zones.'
category: end_user/knowledge_gaps
ticket_class: end_user
issue_category: knowledge_gap
resolution_pattern: no_action
languages:
- hr
- en
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|croatia|no_label:c2
project_key: BS
cluster_size: 37
cluster_size_dedup: 37
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.72
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.73
median_resolution_minutes: 1168.0
p95_resolution_minutes: 36350.999999999956
cannot_reproduce_rate: 0.027
data_window_start: '2023-04-26'
data_window_end: '2026-04-25'
annual_hours_saved: 0.4
roi:
  baseline_active_hours: 1.9
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.5
  deflection_hours_range:
  - 0.3
  - 0.6
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.4
  agent_assist_hours_range:
  - 0.3
  - 0.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.4
  product_fix_hours_range:
  - 0.3
  - 0.5
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 0.2
  autonomous_resolve_hours_range:
  - 0.1
  - 0.2
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-43105
- BS-20816
- BS-34892
- BS-7660
- BS-13421
- BS-20218
- BS-24151
- BS-34995
- BS-48762
- BS-7724
- BS-46280
- BS-52590
- BS-10113
- BS-8215
- BS-46752
- BS-36428
- BS-49029
- BS-24425
canonical_examples:
- BS-46752
- BS-20218
- BS-52590
vendor_dependency:
  vendor_name: Local parking concession operators (e.g., Gradski Parking, Karlovac parking operator)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Informational — safe for agent self-service
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-acknowledge and bulk-close tickets that are clearly no-action (detected as off-topic,
    duplicate appreciation, or incomplete messages with no extractable issue) after a 24-hour hold for agent review.
  autonomous_resolve_safety_constraints:
  - 'Human review queue required before final close: no ticket auto-closed without a 24-hour agent review window.'
  - Scope limited to off-topic / incomplete messages only; any ticket mentioning permit renewal, map zones, or account issues
    must be routed to a human agent.
  - Confidence threshold for autonomous classification must exceed 0.90 before triggering auto-close action.
  - No outbound contact or data changes permitted autonomously.
  - Vendor-related issues (local parking operators) must always be escalated to agent for redirect.
related_playbooks:
- croatia-parking-fine-dispute
- croatia-parking-fine-dispute-and-payment
- croatia-parking-fine-payment-failure
- croatia-parking-payment-failure__ffdf4e
- croatia-parking-ticket-storno-user-error
- croatia-ticketless-best-in-parking-knowledge-gap
- croatia-ticketless-open-session-at-exit__f25b63
- croatia-ticketless-rental-car-ghost-charge
- croatian-end-user-wrong-registration-storno-refund
- croatian-invoice-download-request
- croatian-parking-debt-payment-failure
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__56d2b2
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- open-session-at-exit-payment-failure
- parking-collector-purchase-lot-exhaustion-alert
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Miscellaneous end-user feedback submitted via Bmove App in-app feedback form

## What this pattern is

End users in Croatia (and occasionally other countries) submit unstructured, short feedback messages through the Bmove App feedback form covering a wide range of topics: app problems, parking queries, permit/card management issues, improvement suggestions, and off-topic or incomplete messages. The tickets are highly heterogeneous in content and typically require minimal or no structured resolution, with many being bulk-closed or redirected to the local parking concession operator. A minority involve actionable issues such as inability to renew resident parking permits or missing map zones.

## When this applies

- User submits feedback via the in-app feedback form (feedback types: 'Problemi s aplikacijom', 'Ostalo', 'Prijedlog unaprjeđenja', 'Problems with the application')
- User has a general parking or app question and uses the feedback form instead of a direct support channel
- User encounters a specific app or permit issue (e.g., cannot renew resident card, missing map polygons)
- User submits incomplete or very short message with no clear issue

## Typical resolution flow

1. User opens Bmove App and navigates to the feedback form
2. User selects a feedback type and writes a short message (often incomplete or vague)
3. Ticket is automatically created in Bmove Support project
4. Support agent reviews the ticket; majority require no action or are bulk-closed
5. For permit/concession issues, user is redirected to local parking operator
6. For map/zone issues, ticket may be escalated internally or logged as a product suggestion

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Bulk close tickets with no actionable content | support_agent | Jira bulk close | 1 min |
| Redirect user to local parking concession operator for permit-related issues | support_agent | Jira comment / email | 5 min |
| Log missing map polygon or zone as product improvement ticket | support_agent | Jira | 5 min |
| Acknowledge resolved issue reported by user | support_agent | Jira comment | 2 min |

## Vendor dependency

- **Vendor:** Local parking concession operators (e.g., Gradski Parking, Karlovac parking operator)

## Evidence

Derived from 37 tickets in cluster `BS:end_user|croatia|no_label:c2`. Direct quotes from 8 representative tickets:

- `BS-46752` _[hr]_: "Poštovani,  Ne mogu produžiti povlaštenu stanarsku kartu, hoće li se brzo otkloniti problem lp"
- `BS-20218` _[hr]_: "Kako mogu preki aplikacije kupiti povlaštenu stanarsku kartu?"
- `BS-52590` _[hr]_: "Nema upisanih poligona kod lisinskog parking"
- `BS-24425` _[hr]_: "Na području zavrtnice nisu ucrtane zone svugdje."
- `BS-48762` _[hr]_: "vezano za prethodnu poruku, rijeseno je"
- `BS-36428` _[hr]_: "Ovakvo smece od aplikacije davno nisam vidio"
- `BS-49029` _[hr]_: "mogućnost plaćanja sms porukom"
- `BS-34892` _[en]_: "bulk_close_15.04.2025_part2"

## Cluster statistics

- **Volume:** 37 tickets total (37 unique semantic events after dedup)
- **Frequency:** 0.73 tickets/month (over data window 2023-04-26 → 2026-04-25)
- **Median resolution:** 19.5 hours
- **Cannot Reproduce rate:** 2.7%
- **Languages:** hr, en
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~1.9 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.4 (range [0.27, 0.494])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.70
- **Rationale:** Several resolution actions (redirect-to-operator message, acknowledge-resolved reply, bulk-close label) are repetitive and templatable; an AI assist that auto-classifies ticket intent and pre-fills the appropriate macro or close reason could meaningfully reduce per-ticket active time, primarily for the bulk-close and redirect subsets. The heterogeneity of the cluster limits draft quality for edge cases.
- **Validation:** Run agent-assist in shadow mode for 3 weeks, presenting suggested macros and close reasons to agents without auto-applying them; measure acceptance rate and time-to-close against current baseline to calibrate the 20% reduction estimate.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~1 (range [0.7, 1.3])
- **Hours eliminated per year:** ~0.4 (range [0.27, 0.49])
- **Root cause:** The cluster is a knowledge-gap / feedback-collection issue rather than a discrete product bug. A minority of tickets do reference missing map polygons and inability to renew resident permits, but these are improvement gaps or third-party data issues rather than a single fixable defect. The core volume driver is an overly open feedback form that invites unstructured, un-routable submissions.
- **Rationale:** Adding a structured topic-picker and routing hint to the feedback form could reduce no-action and mis-directed tickets by roughly 20% of annual volume; missing map zones require third-party polygon data updates and cannot be fully eliminated by engineering alone. Estimated hours eliminated are capped well below the 1.9-hour baseline.
- **Validation:** Engineering team should audit the proportion of tickets citing missing zones vs. open-ended feedback, then prototype a structured form with 4-5 topic categories and a smart routing message; measure ticket volume and bulk-close rate 60 days post-launch.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.5 (range [0.34, 0.611])
- **Form:** `in_app_help`
- **Deflection rate:** ~25% (range [18%, 32%])
- **Feasibility:** 0.45
- **Rationale:** The cluster is highly heterogeneous — covering app issues, parking queries, permit problems, and off-topic messages — limiting how much a single FAQ or in-app help surface can pre-empt. A contextual in-app help overlay pointing users to the correct channel (Gradski Parking, Karlovac operator) before they submit could deflect the redirect-to-operator and no-action subsets, estimated at roughly 25% of volume.
- **Validation:** Deploy an in-app help banner on the feedback form for 8 weeks, surfacing links to local parking operator contacts and a common-questions list; measure whether ticket submissions drop and track deflection rate against the 25% midpoint hypothesis.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.2 (range [0.133, 0.247])
- **Narrow use case:** Auto-acknowledge and bulk-close tickets that are clearly no-action (detected as off-topic, duplicate appreciation, or incomplete messages with no extractable issue) after a 24-hour hold for agent review.
- **Safety constraints:**
  - Human review queue required before final close: no ticket auto-closed without a 24-hour agent review window.
  - Scope limited to off-topic / incomplete messages only; any ticket mentioning permit renewal, map zones, or account issues must be routed to a human agent.
  - Confidence threshold for autonomous classification must exceed 0.90 before triggering auto-close action.
  - No outbound contact or data changes permitted autonomously.
  - Vendor-related issues (local parking operators) must always be escalated to agent for redirect.
- **Rationale:** At most ~20% of annual tickets are sufficiently no-action and unambiguous to consider for autonomous handling, and even these require a hold-and-review safeguard given the mixed-topic nature of the cluster; the absolute hours at stake are small (under 0.25 hr/year) relative to implementation cost. The low ticket volume makes this automation lowest priority.
- **Validation:** Pilot with 10 manually pre-screened no-action tickets: apply auto-close logic in a sandbox, have two agents independently review the classifications, and accept only if false-negative rate (missed actionable tickets) is below 5%.

### Risks

- **Compliance concerns:**
  - Some tickets may contain personal data (name, address, vehicle registration) submitted via the open feedback form; any automated handling must comply with GDPR Article 5 data minimisation principles applicable in Croatia.
  - Automated responses must not constitute legal acknowledgement of service obligations the vendor (local parking operator) has not agreed to fulfil.
- **Must not automate:**
  - Tickets reporting inability to renew resident parking permits — these may have legal or access-rights implications for the end user and require human judgment.
  - Tickets referencing missing map zones or incorrect polygon data — these require validation against official operator data before any commitment is communicated.
  - Any ticket where the user expresses urgency, distress, or references a payment or fine dispute.
- **Vendor dependencies blocking automation:**
  - Redirect-to-operator resolutions depend on accurate, up-to-date contact information and service scope from Gradski Parking and Karlovac parking operator; automation of routing messages cannot be validated without a confirmed vendor contact directory.
  - Missing map polygon corrections require data provision from the local concession operators, which is outside the engineering team's direct control and has no measured SLA (typical_wait_days: null).

## Agent compatibility

- **Status:** `active` (extraction confidence 0.72)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** Informational — safe for agent self-service

