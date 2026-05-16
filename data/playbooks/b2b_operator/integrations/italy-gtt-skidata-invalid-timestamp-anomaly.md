---
id: italy-gtt-skidata-invalid-timestamp-anomaly
name: italy_gtt_skidata_invalid_timestamp_anomaly
title: 'Italy GTT Stop-Check Platform: Invalid Timestamp API Call Errors (SKIDATA/PHONZIE)'
description: A high-volume cluster of automated error notifications from the GTT (Gruppo Torinese Trasporti) stop-control
  platform in Italy, all reporting 'Timestamp chiamata non valido' (Invalid call timestamp) errors via the PHONZIE operator.
  All 67 tickets were generated on 2024-06-01 within a narrow time window (approximately 07:28–08:43), suggesting a systemic
  integration or clock-sync failure rather than isolated incidents. Each ticket represents a single failed API call, auto-generated
  by the platform's anomaly-reporting mechanism.
category: b2b_operator/integrations
ticket_class: b2b_partner
issue_category: integration_issue
resolution_pattern: vendor_escalation
languages:
- it
country_focus:
- it
status: active
cluster_id: BS:b2b_partner|italy|no_label:c6
project_key: BS
cluster_size: 67
cluster_size_dedup: 67
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.31
median_resolution_minutes: 47450.0
p95_resolution_minutes: 47450.0
cannot_reproduce_rate: 0.0
data_window_start: '2024-06-01'
data_window_end: '2024-06-01'
annual_hours_saved: null
roi:
  baseline_active_hours: 32.9
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
  product_fix_is_product_bug: true
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
    burst_window_start: '2024-06-01'
    burst_window_count: 67
    burst_max_window_pct: 1.0
    burst_window_days: 7
    burst_threshold_pct: 0.8
    note: Cluster represents a one-off operational incident, not a recurring pattern. Annualized ROI is not meaningful. Treat
      as postmortem.
evidence_tickets:
- BS-22551
- BS-22539
- BS-22535
- BS-22510
- BS-22555
- BS-22507
- BS-22523
- BS-22531
- BS-22547
- BS-22488
- BS-22495
- BS-22502
- BS-22527
- BS-22509
- BS-22491
- BS-22505
- BS-22550
- BS-22493
canonical_examples:
- BS-22551
- BS-22488
- BS-22488
vendor_dependency:
  vendor_name: GTT / SKIDATA / PHONZIE
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: false
  autonomous_resolve: false
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Automated detection and bulk-close of duplicate auto-generated timestamp-error tickets
    once a parent incident record is confirmed resolved by a human agent.
  autonomous_resolve_safety_constraints:
  - A human agent must first confirm root cause resolution before any autonomous bulk-close action is triggered.
  - Autonomous action is limited to closing duplicate child tickets linked to a human-confirmed parent incident; no autonomous
    vendor escalation or API changes permitted.
  - All autonomous closures must be logged with audit trail and reversible within 24 hours.
  - 'Scope restricted to tickets matching exact pattern signature: auto-generated source, ''Timestamp chiamata non valido''
    error code, burst within a 2-hour window.'
  - Vendor coordination and root-cause investigation must remain human-led due to multi-party dependency (GTT/SKIDATA/PHONZIE).
related_playbooks:
- bmove-heartbeat-api-anomaly-italy__412abb
- bmove-heartbeat-api-anomaly-italy__a1951a
- bmove-production-anomaly-restoration-notification-it
- gtt-skidata-is-alive-timeout-error
- hr-b2b-sms-parking-payment-failure
- italian-b2b-invoice-billing-question
- italian-b2b-unsolicited-procurement-marketing-emails
- italy-gtt-parking-stop-threshold-alert
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
---

# Italy GTT Stop-Check Platform: Invalid Timestamp API Call Errors (SKIDATA/PHONZIE)

> ⚠️ **ONE-OFF INCIDENT — NOT A RECURRING PATTERN**
>
> 67 of 67 tickets (100%) arrived within a 7-day window starting 2024-06-01. Treat this as an incident postmortem, not a candidate for automation. Annualized ROI is **not applicable** for this cluster.

## What this pattern is

A high-volume cluster of automated error notifications from the GTT (Gruppo Torinese Trasporti) stop-control platform in Italy, all reporting 'Timestamp chiamata non valido' (Invalid call timestamp) errors via the PHONZIE operator. All 67 tickets were generated on 2024-06-01 within a narrow time window (approximately 07:28–08:43), suggesting a systemic integration or clock-sync failure rather than isolated incidents. Each ticket represents a single failed API call, auto-generated by the platform's anomaly-reporting mechanism.

## When this applies

- GTT stop-control platform sends an API call with an invalid or out-of-sync timestamp
- PHONZIE operator system submits requests that fail timestamp validation
- Clock synchronization issue between PHONZIE/GTT and the Bmove service endpoint
- Automated anomaly-reporting system generates one ticket per failed API call

## Typical resolution flow

1. GTT platform or PHONZIE operator initiates a service call to the Bmove stop-control API
2. API rejects the call due to an invalid timestamp (possible clock skew or format mismatch)
3. GTT automated anomaly system generates an error notification ticket in Bmove Support
4. Ticket is classified as skidata_issue for b2b_partner in Italy
5. Support team investigates the timestamp validation logic or clock synchronization
6. Issue is escalated to vendor (GTT/SKIDATA/PHONZIE) for timestamp alignment fix

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Identify the burst of auto-generated timestamp error tickets as a single systemic incident | support_agent | Bmove Support (Jira) | 15 min |
| Investigate clock synchronization or timestamp format between PHONZIE and Bmove API | technical_team | API logs / monitoring system | 60 min |
| Escalate to GTT/SKIDATA/PHONZIE vendor for timestamp validation alignment | support_agent | email / vendor portal | 30 min |
| Bulk close duplicate auto-generated tickets once root cause is resolved | support_agent | Bmove Support (Jira) | 20 min |

## Vendor dependency

- **Vendor:** GTT / SKIDATA / PHONZIE

## Evidence

Derived from 67 tickets in cluster `BS:b2b_partner|italy|no_label:c6`. Direct quotes from 4 representative tickets:

- `BS-22551` _[it]_: "Tipo errore: Timestamp chiamata non valido Dettaglio: Timestamp chiamata non valido Data/Ora: 2024-06-01 08:39:52.035 Operatore: PHONZIE"
- `BS-22488` _[it]_: "Si è verificata un'anomalia sulla piattaforma di controllo soste GTT. Tipo errore: Timestamp chiamata non valido"
- `BS-22488` _[it]_: "Data/Ora: 2024-06-01 07:28:31.946 Operatore: PHONZIE"
- `BS-22555` _[it]_: "Data/Ora: 2024-06-01 08:43:14.902 Operatore: PHONZIE"

## Cluster statistics

- **Volume:** 67 tickets total (67 unique semantic events after dedup)
- **Frequency:** 1.31 tickets/month (over data window 2024-06-01 → 2024-06-01)
- **Median resolution:** 33.0 days
- **Languages:** it
- **Country focus:** it

## Automation opportunity

_Not applicable._ This cluster represents a one-off operational incident (see banner at top). Recurring-volume ROI estimates are not meaningful here. If you want a savings number for the *postmortem* itself, compute it from the incident's actual ticket volume × per-ticket handling cost, not from annualized frequency.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

