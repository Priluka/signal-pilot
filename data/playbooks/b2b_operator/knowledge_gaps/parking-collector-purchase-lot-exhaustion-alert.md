---
id: parking-collector-purchase-lot-exhaustion-alert
name: parking_collector_purchase_lot_exhaustion_alert
title: 'Automated alert: Parking Collector purchase lot nearing exhaustion (Bologna/PHONZIE/BMOVE)'
description: The Parking Collector system sends automated email notifications to B2B partners when a purchase lot (lotto d'acquisto)
  in Bologna (BOLOGNA_BOMOB) is approaching exhaustion, triggering a support ticket. The alerts consistently reference a specific
  city, provider (PHONZIE or BMOVE), lot amount, and start date. One ticket (BS-52413) reveals that these notifications were
  at least once sent in error, prompting a retraction communication.
category: b2b_operator/knowledge_gaps
ticket_class: b2b_partner
issue_category: knowledge_gap
resolution_pattern: no_action
languages:
- it
country_focus:
- it
status: active
cluster_id: BS:b2b_partner|italy|no_label:c0
project_key: BS
cluster_size: 15
cluster_size_dedup: 15
sample_size_used: 15
extraction_schema: v1.0
extraction_confidence: 0.88
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.29
median_resolution_minutes: 1684.5
p95_resolution_minutes: 20281.399999999987
cannot_reproduce_rate: 0.0
data_window_start: '2023-05-06'
data_window_end: '2026-04-21'
annual_hours_saved: 0.3
roi:
  baseline_active_hours: 1.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.1
  deflection_hours_range:
  - 0.1
  - 0.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.3
  agent_assist_hours_range:
  - 0.2
  - 0.4
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.0
  product_fix_hours_range:
  - 0.7
  - 1.3
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.1
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-17805
- BS-18938
- BS-19904
- BS-21592
- BS-34839
- BS-36467
- BS-38311
- BS-52413
- BS-7967
- BS-8445
- BS-19391
- BS-52400
- BS-20700
- BS-32761
- BS-33451
canonical_examples:
- BS-17805
- BS-17805
- BS-52413
vendor_dependency:
  vendor_name: PHONZIE / BMOVE
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
  autonomous_resolve_narrow_use_case: Auto-acknowledge and route genuine lot-exhaustion alerts to a designated internal stakeholder
    with no further agent action required
  autonomous_resolve_safety_constraints:
  - Must not auto-send retraction emails to B2B partners without human review — erroneous retractions damage partner trust
  - Must not act on ambiguous alerts without confirming inventory state via an API or database check
  - Vendor dependency on PHONZIE/BMOVE means alert data accuracy cannot be fully controlled internally
  - Any autonomous action must be logged and reviewable for audit purposes
related_playbooks:
- bmove-heartbeat-api-anomaly-italy__412abb
- bmove-heartbeat-api-anomaly-italy__a1951a
- bmove-production-anomaly-restoration-notification-it
- croatia-bmove-app-feedback-miscellaneous
- gtt-skidata-is-alive-timeout-error
- italian-b2b-invoice-billing-question
- italian-b2b-unsolicited-procurement-marketing-emails
- italy-gtt-parking-stop-threshold-alert
- italy-gtt-skidata-invalid-timestamp-anomaly
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
# Skills enabled — reads auto-execute, writes are HITL.
allowed_skills:
  - graylog_search
  - parkis_lookup
  - skidata_session_lookup
  - bmove_user_lookup
  - datatrans_transaction
  - jira_get_history
  - jira_add_internal_comment
  - jira_add_public_comment
  - jira_transition
---

# Automated alert: Parking Collector purchase lot nearing exhaustion (Bologna/PHONZIE/BMOVE)

## What this pattern is

The Parking Collector system sends automated email notifications to B2B partners when a purchase lot (lotto d'acquisto) in Bologna (BOLOGNA_BOMOB) is approaching exhaustion, triggering a support ticket. The alerts consistently reference a specific city, provider (PHONZIE or BMOVE), lot amount, and start date. One ticket (BS-52413) reveals that these notifications were at least once sent in error, prompting a retraction communication.

## When this applies

- Automated Parking Collector system email sent when a purchase lot balance is nearly depleted
- Email arrives at partner/internal mailbox and is forwarded or logged as a support ticket
- Erroneous notification batch sent due to system misconfiguration (as in BS-52413)

## Typical resolution flow

1. Parking Collector system detects low balance on a purchase lot
2. Automated notification email is sent to recipients (n****@brav.it)
3. Recipient forwards or logs the email as a support ticket in Bmove Support
4. Support team member reviews the ticket and assesses whether action is needed
5. If erroneous, a retraction/clarification email is sent to recipients

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Review the automated alert to determine if the lot exhaustion is genuine or erroneous | support agent | Bmove Support (Jira) | 5 min |
| Escalate or inform internal stakeholder (e.g., Vito Guglielmini) about the notification | support agent | Jira comments (@mention) | 2 min |
| Send retraction email to partners when notifications were sent in error | operations/support team | email (n****@brav.it) | 15 min |

## Vendor dependency

- **Vendor:** PHONZIE / BMOVE

## Evidence

Derived from 15 tickets in cluster `BS:b2b_partner|italy|no_label:c0`. Direct quotes from 5 representative tickets:

- `BS-17805` _[it]_: "Il lotto d'acquisto da 50.000,00 € con data 01/06/2023 nella città di BOLOGNA_BOMOB per il provider PHONZIE è in esaurimento."
- `BS-17805` _[it]_: "@@VITO GUGLIELMINI non capisco cosa sia…"
- `BS-52413` _[it]_: "Vi preghiamo di non tenere in considerazione queste email che sono state inoltrate per errore."
- `BS-33451` _[it]_: "Comunicazione arrivata anche su email ordinaria"
- `BS-36467` _[it]_: "Il lotto d'acquisto da 0,00 € con data 03/03/2025 nella città di BOLOGNA_BOMOB per il provider BMOVE è in esaurimento."

## Cluster statistics

- **Volume:** 15 tickets total (15 unique semantic events after dedup)
- **Frequency:** 0.29 tickets/month (over data window 2023-05-06 → 2026-04-21)
- **Median resolution:** 1.2 days
- **Languages:** it
- **Country focus:** it

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~1.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.3 (range [0.23, 0.416])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.65
- **Rationale:** A pre-built macro or guided checklist could standardize the triage step (genuine vs. erroneous alert) and auto-draft the stakeholder notification or retraction email, reducing the ~17 minutes of manual review and communication work. Gains are modest given the already-low ticket volume and short active time per ticket.
- **Validation:** Deploy a shadow-mode assist tool for 3 weeks that pre-populates the retraction email template and flags alert authenticity based on lot-ID lookup; measure agent acceptance rate and actual time-on-ticket before committing.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~2 (range [1.4, 2.6])
- **Hours eliminated per year:** ~1 (range [0.7, 1.3])
- **Root cause:** The Parking Collector system sends lot-exhaustion alerts that are sometimes erroneous (as evidenced by BS-52413 requiring a retraction), suggesting a defect or missing validation gate in the alert-generation logic before notifications are dispatched to B2B partners.
- **Rationale:** Adding a pre-send validation check (e.g., confirming actual inventory state before dispatching alerts) and suppressing duplicate or erroneous notifications would eliminate the review and retraction workload. Hours eliminated are capped at the 1.3-hour baseline; the range reflects uncertainty about whether all tickets would be resolved or only the erroneous-alert subset.
- **Validation:** Engineering team should audit the alert-trigger logic in Parking Collector for BOLOGNA_BOMOB lots, prototype a validation gate in a staging environment, and measure false-positive alert rate before and after over one sprint cycle.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.042, 0.078])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These tickets are system-generated automated alerts from Parking Collector, not human-initiated support requests; there is no end-user to deflect to self-service. The tickets originate from internal processing of vendor notifications, making FAQ or help-center deflection inapplicable.
- **Validation:** Confirm ticket origination channel (automated vs. human-initiated) over a 4-week observation window; if any human-initiated tickets exist in the cluster, assess a targeted FAQ page for B2B partners about lot-exhaustion notifications.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.1 (range [0.105, 0.19])
- **Narrow use case:** Auto-acknowledge and route genuine lot-exhaustion alerts to a designated internal stakeholder with no further agent action required
- **Safety constraints:**
  - Must not auto-send retraction emails to B2B partners without human review — erroneous retractions damage partner trust
  - Must not act on ambiguous alerts without confirming inventory state via an API or database check
  - Vendor dependency on PHONZIE/BMOVE means alert data accuracy cannot be fully controlled internally
  - Any autonomous action must be logged and reviewable for audit purposes
- **Rationale:** Only the narrow subset of clearly genuine, non-erroneous alerts could be autonomously routed to stakeholders, but the known occurrence of erroneous alerts (BS-52413) makes full autonomous resolution unsafe without a reliable validation signal. Savings are limited by the low annual volume and the mandatory human-in-the-loop for retraction scenarios.
- **Validation:** Run a 6-week pilot where the system auto-routes only alerts confirmed genuine by an inventory API check, with a human reviewer receiving a daily digest; measure false-positive rate and stakeholder satisfaction before expanding scope.

### Risks

- **Compliance concerns:**
  - Erroneous automated notifications sent to B2B partners may carry contractual or SLA implications; any automation of retraction communications must comply with partner agreement terms
  - B2B partner data (lot IDs, purchase amounts, start dates) in tickets must be handled in accordance with applicable data-protection regulations
- **Must not automate:**
  - Sending retraction emails to external B2B partners without human review and approval — one confirmed erroneous retraction in the cluster demonstrates this risk is real
  - Escalation decisions to named internal stakeholders (e.g., Vito Guglielmini) without a human judgment step
- **Vendor dependencies blocking automation:**
  - PHONZIE / BMOVE: alert data accuracy and lot-state information originates from vendor systems; without API access to validate actual lot inventory in real time, autonomous triage cannot reliably distinguish genuine from erroneous alerts

## Agent compatibility

- **Status:** `active` (extraction confidence 0.88)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** Informational — safe for agent self-service

