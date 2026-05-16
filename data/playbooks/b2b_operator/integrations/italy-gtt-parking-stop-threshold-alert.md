---
id: italy-gtt-parking-stop-threshold-alert
name: italy_gtt_parking_stop_threshold_alert
title: Automated GTT parking stop threshold breach alerts for Italian B2B partners
description: These tickets are automated system-generated alerts notifying B2B partners (primarily BMOVE and Lenis srl Phonzie)
  that the number of parking stops ('soste') recorded on a specific day was significantly below the expected threshold. The
  alerts instruct the recipient to contact GTT at a specific email address. They appear to be recurring on holidays, public
  holidays, and low-traffic days.
category: b2b_operator/integrations
ticket_class: b2b_partner
issue_category: integration_issue
resolution_pattern: vendor_escalation
languages:
- it
country_focus:
- it
status: active
cluster_id: BS:b2b_partner|italy|no_label:c3
project_key: BS
cluster_size: 17
cluster_size_dedup: 17
sample_size_used: 17
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.33
median_resolution_minutes: 3564.0
p95_resolution_minutes: 9618.25
cannot_reproduce_rate: 0.0
data_window_start: '2023-12-25'
data_window_end: '2026-05-01'
annual_hours_saved: 0.2
roi:
  baseline_active_hours: 1.0
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.1
  deflection_hours_range:
  - 0.1
  - 0.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.2
  agent_assist_hours_range:
  - 0.1
  - 0.3
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.9
  product_fix_hours_range:
  - 0.7
  - 1.0
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 0.2
  autonomous_resolve_hours_range:
  - 0.2
  - 0.3
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-16916
- BS-16931
- BS-21169
- BS-21405
- BS-44229
- BS-46930
- BS-47257
- BS-47456
- BS-51646
- BS-52602
- BS-46138
- BS-47230
- BS-47323
- BS-19964
- BS-46898
- BS-52910
- BS-23487
canonical_examples:
- BS-16916
- BS-47257
- BS-52910
vendor_dependency:
  vendor_name: GTT (Gruppo Torinese Trasporti)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-acknowledge and close alerts where the trigger date matches a confirmed Italian
    public holiday or a pre-approved partner low-traffic calendar entry, with no GTT escalation required.
  autonomous_resolve_safety_constraints:
  - Only auto-close if trigger date is an exact match in a maintained, audited Italian public-holiday dataset or a partner-approved
    low-traffic date list.
  - Never auto-escalate to GTT p****@gtt.to.it; human must initiate vendor contact for genuine anomalies.
  - Retain a human-review queue for any alert that does not match a known holiday or approved low-traffic date.
  - Audit log all auto-closures with the matched holiday/date rule for partner transparency.
  - Partner (BMOVE, Lenis srl Phonzie) must be notified of auto-closure policy and given opt-out rights.
related_playbooks:
- bmove-heartbeat-api-anomaly-italy__412abb
- bmove-heartbeat-api-anomaly-italy__a1951a
- bmove-production-anomaly-restoration-notification-it
- gtt-skidata-is-alive-timeout-error
- hr-b2b-sms-parking-payment-failure
- italian-b2b-invoice-billing-question
- italian-b2b-unsolicited-procurement-marketing-emails
- italy-gtt-skidata-invalid-timestamp-anomaly
- parking-collector-purchase-lot-exhaustion-alert
- parking-fine-received-despite-valid-payment
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Automated GTT parking stop threshold breach alerts for Italian B2B partners

## What this pattern is

These tickets are automated system-generated alerts notifying B2B partners (primarily BMOVE and Lenis srl Phonzie) that the number of parking stops ('soste') recorded on a specific day was significantly below the expected threshold. The alerts instruct the recipient to contact GTT at a specific email address. They appear to be recurring on holidays, public holidays, and low-traffic days.

## When this applies

- Daily parking stop count falls below the configured threshold for a B2B partner
- Automated monitoring system detects anomalously low stop registrations
- Ticket is generated automatically by the GTT monitoring system, often on public holidays or holiday periods

## Typical resolution flow

1. Automated system detects that recorded stops on a given day are below expected threshold
2. Ticket is automatically created in the support system addressed to the B2B partner operator
3. Ticket instructs the operator to contact GTT at p****@gtt.to.it
4. Partner or support team reviews the alert and contacts GTT if necessary

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Automated alert ticket created notifying operator of below-threshold stop count | automated system | GTT monitoring system | 0 min |
| Review alert and determine if stop count drop is expected (e.g. public holiday) or indicative of a real issue | b2b_partner operator or support agent | — | 10 min |
| Contact GTT via p****@gtt.to.it if issue requires investigation | b2b_partner operator or support agent | email | 5 min |

## Vendor dependency

- **Vendor:** GTT (Gruppo Torinese Trasporti)

## Evidence

Derived from 17 tickets in cluster `BS:b2b_partner|italy|no_label:c3`. Direct quotes from 4 representative tickets:

- `BS-16916` _[it]_: "il giorno 2023-12-25 sono state registrate 0 soste, un quantitativo notevolmente inferiore rispetto al consueto. Per questo motivo si prega di contattare GTT all'indirizzo p****@gtt.to.it."
- `BS-47257` _[it]_: "il giorno 2026-01-01 sono state registrate 1 soste, un quantitativo notevolmente inferiore rispetto al consueto."
- `BS-52910` _[it]_: "il giorno 2026-05-01 sono state registrate 0 soste, un quantitativo notevolmente inferiore rispetto al consueto."
- `BS-23487` _[it]_: "il giorno 2024-06-24 sono state registrate 8 soste, un quantitativo notevolmente inferiore rispetto al consueto."

## Cluster statistics

- **Volume:** 17 tickets total (17 unique semantic events after dedup)
- **Frequency:** 0.33 tickets/month (over data window 2023-12-25 → 2026-05-01)
- **Median resolution:** 2.5 days
- **Languages:** it
- **Country focus:** it

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~1 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.2 (range [0.14, 0.26])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.50
- **Rationale:** At only 4 tickets per year and 15 active minutes each, the absolute savings potential is very small; an assist tool that pre-classifies the alert as holiday-driven versus anomalous and drafts a GTT escalation email would reduce triage time modestly. ROI on building the assist tooling likely does not justify the effort for this cluster alone.
- **Validation:** Run a 2-week shadow mode where an LLM classifier labels each incoming alert as expected (holiday) or investigate, comparing its label against agent disposition to measure precision/recall before enabling any agent-facing recommendation.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~1.5 (range [1.1, 1.9])
- **Hours eliminated per year:** ~0.9 (range [0.7, 1])
- **Root cause:** The alert system does not incorporate a calendar of Italian public holidays and B2B partner-specific low-traffic days, causing expected low-volume days to trigger threshold-breach alerts that require manual triage to dismiss. This is a missing feature (calendar-aware suppression), not a defect.
- **Rationale:** Integrating a maintained Italian public-holiday calendar and configurable partner-level suppression rules into the alert engine would suppress the majority of these tickets automatically, eliminating the review step for expected low-traffic days. Hours eliminated are capped at the 1.0 h baseline; range reflects uncertainty about residual genuine anomalies.
- **Validation:** Engineering should prototype the suppression logic against the 17 historical tickets to confirm what fraction would have been correctly suppressed versus true anomalies, then run a 4-week shadow mode before live deployment.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.035, 0.065])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.15
- **Rationale:** These tickets are system-generated automated alerts, not inbound partner queries, so there is no human initiating a request that could be deflected to self-service. A FAQ explaining the threshold logic might marginally reduce follow-up contact but would not deflect the alert itself.
- **Validation:** Deploy a help-center article explaining holiday-driven threshold breaches and measure whether partner-initiated follow-up emails or calls to support decrease over a 4-week period.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~0.2 (range [0.161, 0.299])
- **Narrow use case:** Auto-acknowledge and close alerts where the trigger date matches a confirmed Italian public holiday or a pre-approved partner low-traffic calendar entry, with no GTT escalation required.
- **Safety constraints:**
  - Only auto-close if trigger date is an exact match in a maintained, audited Italian public-holiday dataset or a partner-approved low-traffic date list.
  - Never auto-escalate to GTT p****@gtt.to.it; human must initiate vendor contact for genuine anomalies.
  - Retain a human-review queue for any alert that does not match a known holiday or approved low-traffic date.
  - Audit log all auto-closures with the matched holiday/date rule for partner transparency.
  - Partner (BMOVE, Lenis srl Phonzie) must be notified of auto-closure policy and given opt-out rights.
- **Rationale:** Autonomous closure is only safe for the well-defined holiday subset; at 25% of 4 annual tickets, the absolute hours saved are minimal (~0.23 h/year). The primary value is eliminating unnecessary human touchpoints on days that are predictably low-traffic, not throughput at scale.
- **Validation:** Pilot over one Italian public-holiday calendar year (12 months): auto-close holiday-matched alerts in shadow mode first, confirm zero false positives against agent ground truth, then enable live auto-closure with a 30-day partner notification period.

### Risks

- **Compliance concerns:**
  - Auto-closing alerts without human review could mask genuine GTT data pipeline failures if the holiday calendar is stale or incorrectly maintained.
  - B2B partner contractual SLAs (if any) may require human acknowledgement of threshold-breach notifications within a defined window.
  - Italian data-processing or transport-regulation requirements may mandate that all threshold breaches be logged and reviewed by a responsible person.
- **Must not automate:**
  - Escalation emails to GTT (p****@gtt.to.it) — vendor contact must remain human-initiated to avoid flooding the GTT inbox with automated messages and to ensure accountability.
  - Closure of alerts on non-holiday dates where the stop-count drop may indicate a real integration or data pipeline failure.
- **Vendor dependencies blocking automation:**
  - GTT (Gruppo Torinese Trasporti) controls the stop-count data feed; any calendar-aware suppression logic depends on GTT confirming that their data pipeline behaves predictably on holidays (i.e., genuinely sends low counts vs. sending no data).
  - Without GTT cooperation on documenting expected holiday behavior, the holiday-suppression rule cannot be safely validated and the product fix and autonomous-resolve opportunities remain speculative.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

