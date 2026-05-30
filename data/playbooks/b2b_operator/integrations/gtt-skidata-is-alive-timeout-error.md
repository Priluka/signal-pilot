---
id: gtt-skidata-is-alive-timeout-error
name: gtt_skidata_is_alive_timeout_error
title: GTT Parking Control Platform IsAlive Service Timeout Errors (Italy)
description: The GTT parking control platform (controllo soste) operated by B2B partner PHONZIE generates automated alerts
  whenever the IsAlive health-check service fails to reach its backend, resulting in either 'connect timed out' or 'Read timed
  out' errors. These alerts are fired automatically and repeatedly — sometimes dozens of times in a single day — creating
  high ticket volume for what appears to be a recurring connectivity or service availability issue. Escalation typically involves
  forwarding details to an internal HD team and a contact named Daniele Maggioni for investigation.
category: b2b_operator/integrations
ticket_class: b2b_partner
issue_category: integration_issue
resolution_pattern: vendor_escalation
languages:
- it
country_focus:
- it
status: active
cluster_id: BS:b2b_partner|italy|no_label:c5
project_key: BS
cluster_size: 86
cluster_size_dedup: 86
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.93
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.69
median_resolution_minutes: 12416.0
p95_resolution_minutes: 233028.34999999992
cannot_reproduce_rate: 0.0
data_window_start: '2024-09-12'
data_window_end: '2025-07-12'
annual_hours_saved: null
roi:
  baseline_active_hours: 8.8
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: null
  deflection_hours_range: null
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: null
  agent_assist_hours_range: null
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: null
  product_fix_hours_range: null
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: null
  autonomous_resolve_hours_range: null
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
  _meta:
    incident_pattern: one_off_burst
    burst_window_start: '2025-04-02'
    burst_window_count: 81
    burst_max_window_pct: 0.942
    burst_window_days: 7
    burst_threshold_pct: 0.8
    note: Cluster represents a one-off operational incident, not a recurring pattern. Annualized ROI is not meaningful. Treat
      as postmortem.
evidence_tickets:
- BS-39688
- BS-26814
- BS-35526
- BS-28085
- BS-34131
- BS-35576
- BS-35507
- BS-35538
- BS-35583
- BS-35598
- BS-35594
- BS-35551
- BS-35567
- BS-35570
- BS-35595
- BS-35569
- BS-35577
- BS-35520
canonical_examples:
- BS-39688
- BS-26814
- BS-35526
vendor_dependency:
  vendor_name: GTT (Gruppo Torinese Trasporti) / SKIDATA
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: false
  autonomous_resolve: true
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-group duplicate IsAlive alert tickets from the same outage window into a single
    parent ticket and auto-send a standardised acknowledgement to HD/Daniele Maggioni, with no resolution claimed until human
    confirmation.
  autonomous_resolve_safety_constraints:
  - Never close or resolve tickets autonomously — only group and acknowledge; human must confirm resolution.
  - Do not suppress alerts that may indicate a new or distinct outage event.
  - Maintain full audit trail of all auto-grouped tickets for vendor accountability.
  - Require human sign-off before any escalation email is sent to external parties (GTT/SKIDATA).
  - Cap autonomous handling at 20% of annual volume until pilot validates false-grouping rate <5%.
related_playbooks:
- bmove-heartbeat-api-anomaly-italy__412abb
- bmove-heartbeat-api-anomaly-italy__a1951a
- bmove-production-anomaly-restoration-notification-it
- hr-b2b-sms-parking-payment-failure
- italian-b2b-invoice-billing-question
- italian-b2b-unsolicited-procurement-marketing-emails
- italy-gtt-parking-stop-threshold-alert
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
incident_pattern: one_off_burst
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

# GTT Parking Control Platform IsAlive Service Timeout Errors (Italy)

> ⚠️ **ONE-OFF INCIDENT — NOT A RECURRING PATTERN**
>
> 81 of 86 tickets (94%) arrived within a 7-day window starting 2025-04-02. Treat this as an incident postmortem, not a candidate for automation. Annualized ROI is **not applicable** for this cluster.

## What this pattern is

The GTT parking control platform (controllo soste) operated by B2B partner PHONZIE generates automated alerts whenever the IsAlive health-check service fails to reach its backend, resulting in either 'connect timed out' or 'Read timed out' errors. These alerts are fired automatically and repeatedly — sometimes dozens of times in a single day — creating high ticket volume for what appears to be a recurring connectivity or service availability issue. Escalation typically involves forwarding details to an internal HD team and a contact named Daniele Maggioni for investigation.

## When this applies

- GTT parking control platform (controllo soste) fails its periodic IsAlive health-check against the backend service
- Network timeout occurs between the GTT platform and its dependent service (connect timed out or Read timed out)
- Automated alert generated by operator PHONZIE and submitted as a support ticket

## Typical resolution flow

1. Automated system detects IsAlive service failure and generates a ticket with error type, detail, and timestamp
2. Ticket is assigned/reviewed by support agent (e.g., Maddalena Sgambato)
3. Agent requests clarification or groups multiple alerts and escalates to HD/Daniele Maggioni
4. Resolution awaits response from HD or technical team responsible for the GTT backend service

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Automated ticket creation triggered by IsAlive health-check failure on GTT platform | Automated system (operator: PHONZIE) | GTT controllo soste platform | 1 min |
| Review and grouping of multiple related alerts; request to collect Excel report files | Support agent (e.g., Maddalena Sgambato) | Bmove Support ticketing system | 15 min |
| Escalation of grouped incidents to HD and Daniele Maggioni via email | Support agent | email | 10 min |

## Vendor dependency

- **Vendor:** GTT (Gruppo Torinese Trasporti) / SKIDATA

## Evidence

Derived from 86 tickets in cluster `BS:b2b_partner|italy|no_label:c5`. Direct quotes from 5 representative tickets:

- `BS-39688` _[it]_: "Tipo errore: Errore IsAlive Dettaglio: Unable to execute service: Read timed out Data/Ora: 2025-07-12 19:25:06.215 Operatore: PHONZIE"
- `BS-26814` _[it]_: "Tipo errore: Errore IsAlive Dettaglio: Unable to execute service: connect timed out Data/Ora: 2024-09-12 19:25:03.728 Operatore: PHONZIE"
- `BS-35526` _[it]_: "Ne ho ricevute tante, una quindicina almeno…cosa bisogna fare?"
- `BS-28085` _[it]_: "inviata richiesta di chiarimento ad hd/daniele maggioni in data 16/10/2024"
- `BS-35526` _[it]_: "allega per favore tutti i file Excel con le segnalazioni in una mail per Daniele e HD"

## Cluster statistics

- **Volume:** 86 tickets total (86 unique semantic events after dedup)
- **Frequency:** 1.69 tickets/month (over data window 2024-09-12 → 2025-07-12)
- **Median resolution:** 8.6 days
- **Languages:** it
- **Country focus:** it

## Automation opportunity

_Not applicable._ This cluster represents a one-off operational incident (see banner at top). Recurring-volume ROI estimates are not meaningful here. If you want a savings number for the *postmortem* itself, compute it from the incident's actual ticket volume × per-ticket handling cost, not from annualized frequency.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.93)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

