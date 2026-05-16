---
id: pkc-vehicle-registration-automated-tickets
name: pkc_vehicle_registration_automated_tickets
title: Automated PKC Vehicle Registration Tickets with Date and Plate Identifiers
description: 'A large cluster of tickets submitted by end users (or automated systems) following a consistent pattern: ''PKC
  - <date> - <vehicle/registration code>''. The descriptions are almost universally empty, suggesting these are system-generated
  or template-driven submissions linked to vehicle registration or parking/toll events. A minority of tickets are noise (test
  entries or gibberish), but the dominant pattern is structured PKC submissions.'
category: end_user/user_issues
ticket_class: end_user
issue_category: misuse
resolution_pattern: manual_close
languages:
- other
country_focus:
- other
status: active
cluster_id: BS:end_user|austria|no_label:c2
project_key: BS
cluster_size: 34
cluster_size_dedup: 34
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.72
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.67
median_resolution_minutes: 3.5
p95_resolution_minutes: 78515.99999999971
cannot_reproduce_rate: 0.0294
data_window_start: '2024-08-02'
data_window_end: '2026-04-27'
annual_hours_saved: 0.1
roi:
  baseline_active_hours: 0.4
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.0
  deflection_hours_range:
  - 0.0
  - 0.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.1
  agent_assist_hours_range:
  - 0.1
  - 0.2
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.4
  product_fix_hours_range:
  - 0.3
  - 0.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.1
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-47595
- BS-49664
- BS-25003
- BS-42694
- BS-47107
- BS-48653
- BS-49561
- BS-47041
- BS-48551
- BS-52485
- BS-47472
- BS-48217
- BS-49256
- BS-49622
- BS-47795
- BS-49563
- BS-49194
- BS-47264
canonical_examples:
- BS-47595
- BS-49664
- BS-47107
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-close tickets whose title matches the PKC-date-plate regex and whose description
    is empty or whitespace-only, with no customer-visible reply
  autonomous_resolve_safety_constraints:
  - Regex match must be exact; any ticket with non-empty description must route to agent review
  - A human audit sample of ≥10% of auto-closed tickets must be reviewed monthly to catch false positives
  - Tickets flagged as noise/gibberish must still be logged for abuse pattern monitoring
  - Auto-close must not send any customer-facing communication that could cause confusion
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-incorrect-charge-refund
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- bmove-not-recognized-daily-worklog
- croatian-b2b-parking-ticket-storno-request
- email-address-change-not-possible
- email-address-change-not-supported
- expired-card-deletion-ticketless-link
- microsoft365-quarantine-notification-auto-tickets
- missing-parking-invoice-receipt
- missing-parking-receipt-email
- missing-parking-receipt-request
- open-session-at-exit-austria
- outstanding-payment-credit-card-failure
- test-and-junk-tickets
- ticketless-open-session-at-exit__960f17
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Automated PKC Vehicle Registration Tickets with Date and Plate Identifiers

## What this pattern is

A large cluster of tickets submitted by end users (or automated systems) following a consistent pattern: 'PKC - <date> - <vehicle/registration code>'. The descriptions are almost universally empty, suggesting these are system-generated or template-driven submissions linked to vehicle registration or parking/toll events. A minority of tickets are noise (test entries or gibberish), but the dominant pattern is structured PKC submissions.

## When this applies

- Automated or template-based submission triggered by a PKC (parking/toll/registration) event
- User submits a ticket with only a date and vehicle identifier code in the subject
- No description or supporting information is provided
- Occasional test or accidental ticket submissions

## Typical resolution flow

1. Ticket is created with summary following pattern 'PKC - <date> - <identifier>'
2. Description field is left empty
3. Ticket enters support queue without actionable content
4. Support agent reviews and likely closes or ignores the ticket due to lack of information

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Review ticket for actionable content | support_agent | Jira/ticketing system | 2 min |
| Close or discard ticket as no-action required | support_agent | Jira/ticketing system | 1 min |

## Evidence

Derived from 34 tickets in cluster `BS:end_user|austria|no_label:c2`. Direct quotes from 6 representative tickets:

- `BS-47595` _[other]_: "PKC - 08.01.2026. - W****"
- `BS-49664` _[other]_: "PKC - 18.02.2026. - W****"
- `BS-47107` _[other]_: "PKC - 29.12.25. - SW****"
- `BS-48551` _[other]_: "W****"
- `BS-25003` _[en]_: "test"
- `BS-42694` _[other]_: "K9ko9 997o999op9⁸"

## Cluster statistics

- **Volume:** 34 tickets total (34 unique semantic events after dedup)
- **Frequency:** 0.67 tickets/month (over data window 2024-08-02 → 2026-04-27)
- **Median resolution:** 4 min
- **Cannot Reproduce rate:** 2.9%
- **Languages:** other
- **Country focus:** other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~0.4 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.1 (range [0.084, 0.156])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.70
- **Rationale:** Pattern-matching on the structured ticket title can auto-populate a macro or suggested action ('close as no-action required'), reducing the agent's review and close steps from ~3 minutes to ~2 minutes. The highly consistent format makes macro suggestion straightforward, but the low annual volume limits absolute savings.
- **Validation:** Deploy a shadow-mode macro suggestion for 3 weeks that flags any ticket matching the 'PKC - \d+ - [A-****-9]+' pattern and pre-fills the close action; measure agent acceptance rate and actual time-to-close vs. baseline.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~2 (range [1.5, 2.5])
- **Hours eliminated per year:** ~0.4 (range [0.28, 0.4])
- **Root cause:** The cluster reflects misuse or misconfiguration: an external system or template is routing PKC vehicle registration events into the support ticket queue rather than a dedicated data pipeline or intake channel. This is a process/integration gap, not a software defect.
- **Rationale:** Implementing an automated intake filter or routing rule that detects the 'PKC - <date> - <plate>' pattern and silently discards or redirects these tickets before agent review could eliminate nearly all active handling time. Effort estimate assumes integration work to identify the originating system and suppress or reroute the feed.
- **Validation:** Engineering team should trace the ticket submission source to identify the originating system or API key, then estimate routing/filter effort in a spike; compare spike output against the 2-sprint midpoint before committing.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0.014, 0.026])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These tickets appear to be system-generated or template-driven submissions with empty descriptions, not user-initiated help-seeking behavior; a self-service form or FAQ cannot intercept automated or misrouted submissions upstream. Deflection is structurally unsuitable because there is no human end-user making an active decision to open a ticket.
- **Validation:** Audit ticket submission source logs over 4 weeks to confirm whether any submissions originate from human user portals vs. automated pipelines; only if human-originated should a self-service redirect be piloted.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~0.1 (range [0.06, 0.104])
- **Narrow use case:** Auto-close tickets whose title matches the PKC-date-plate regex and whose description is empty or whitespace-only, with no customer-visible reply
- **Safety constraints:**
  - Regex match must be exact; any ticket with non-empty description must route to agent review
  - A human audit sample of ≥10% of auto-closed tickets must be reviewed monthly to catch false positives
  - Tickets flagged as noise/gibberish must still be logged for abuse pattern monitoring
  - Auto-close must not send any customer-facing communication that could cause confusion
- **Rationale:** The rigid, predictable structure of these tickets and their consistent no-action resolution make them a reasonable candidate for autonomous closure within a capped volume; however, the very low annual frequency (8 tickets/year) means absolute savings are minimal and the ROI of automation investment is modest. The 25% cap is applied conservatively given the misuse classification and the minority noise component.
- **Validation:** Run a 6-week shadow pilot: apply the auto-close rule in logging-only mode, then have an agent review 100% of flagged tickets to confirm false-positive rate is below 2% before enabling live auto-close.

### Risks

- **Compliance concerns:**
  - Vehicle registration plate data may be subject to data protection regulations (e.g., GDPR, local vehicle data laws); even no-action tickets containing plate identifiers should be handled and purged in accordance with applicable retention policies.
  - Automated closure without audit trail could create compliance gaps if any PKC events later prove actionable or legally significant.
- **Must not automate:**
  - Any ticket variant that contains a non-empty description, an attachment, or content deviating from the strict PKC-date-plate pattern must not be auto-closed and must route to a human agent.
  - Tickets that could be associated with a regulatory inquiry, dispute, or law-enforcement request must never be silently discarded.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.72)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

