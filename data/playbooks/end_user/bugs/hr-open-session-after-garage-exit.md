---
id: hr-open-session-after-garage-exit
name: hr_open_session_after_garage_exit
title: Session remains open in app after user exits parking garage (Croatia)
description: End users report that after physically exiting a parking garage, the Bmove app continues to show their vehicle
  as still parked/active in the garage, meaning the session does not automatically close upon exit. The pattern is dominated
  by a single user (id=1514647) submitting the same complaint repeatedly across multiple tickets, but a separate user (id=2108075)
  confirms the issue is not isolated. Tickets are predominantly from Croatia and relate to the Kaptol Centre garage location.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: product_fix_required
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:end_user|no_value|no_label:c3
project_key: BS
cluster_size: 27
cluster_size_dedup: 27
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.92
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.53
median_resolution_minutes: 858.0
p95_resolution_minutes: 862.7
cannot_reproduce_rate: 0.0
data_window_start: '2025-11-11'
data_window_end: '2025-11-13'
annual_hours_saved: null
roi:
  baseline_active_hours: 9.2
  baseline_active_source: 'fallback: 10% of wall-clock median (858 min)'
  baseline_is_fallback: true
  baseline_confidence_tier: directional
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
    burst_window_start: '2025-11-11'
    burst_window_count: 27
    burst_max_window_pct: 1.0
    burst_window_days: 7
    burst_threshold_pct: 0.8
    note: Cluster represents a one-off operational incident, not a recurring pattern. Annualized ROI is not meaningful. Treat
      as postmortem.
evidence_tickets:
- BS-44884
- BS-44881
- BS-44751
- BS-44892
- BS-44880
- BS-44869
- BS-44878
- BS-44888
- BS-44885
- BS-44872
- BS-44873
- BS-44876
- BS-44874
- BS-44877
- BS-44882
- BS-44891
- BS-44889
- BS-44886
canonical_examples:
- BS-44881
- BS-44751
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: reference_only
  claude_skill: reference_only
  agent_assist: false
  autonomous_resolve: false
  note: Engineering backlog — not for runtime agents
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Automatically close a stuck parking session and notify the user when a confirmed exit
    event is detected but the session remains open after a 5-minute grace period.
  autonomous_resolve_safety_constraints:
  - Only trigger auto-close if a verifiable exit signal (geofence departure or barrier event) is present; do not act on user
    complaint alone.
  - Notify the user immediately upon auto-close with a clear explanation and a dispute/reversal option.
  - Do not auto-close sessions with active billing discrepancies or amounts above a defined threshold without human review.
  - Log all autonomous closures for audit; flag repeat auto-closures on the same user/garage for human inspection.
  - Limit autonomous resolution to cases where session duration and charge are within expected norms to avoid financial errors.
related_playbooks:
- app-payment-failure-parking-ticket
- b2b-outstanding-payment-failure-app
- bmove-app-feedback-mixed-issues__7950cd
- croatia-parking-payment-failure__ffdf4e
- hr-parking-ticket-fine-after-paid-app
- parking-fine-received-despite-valid-payment
- parking-payment-failure-end-user
- prepaid-top-up-and-usage-issues
- slovakia-parking-payment-failure-no-ticket
- ticketless-open-session-at-exit__d8d1ba
- ticketless-open-session-at-exit__fd04ac
- wrong-parking-ticket-purchase-redirect
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
incident_pattern: one_off_burst
---

# Session remains open in app after user exits parking garage (Croatia)

> ⚠️ **ONE-OFF INCIDENT — NOT A RECURRING PATTERN**
>
> 27 of 27 tickets (100%) arrived within a 7-day window starting 2025-11-11. Treat this as an incident postmortem, not a candidate for automation. Annualized ROI is **not applicable** for this cluster.

## What this pattern is

End users report that after physically exiting a parking garage, the Bmove app continues to show their vehicle as still parked/active in the garage, meaning the session does not automatically close upon exit. The pattern is dominated by a single user (id=1514647) submitting the same complaint repeatedly across multiple tickets, but a separate user (id=2108075) confirms the issue is not isolated. Tickets are predominantly from Croatia and relate to the Kaptol Centre garage location.

## When this applies

- User physically exits a parking garage but the app does not register the exit
- Parking session remains open/active in the app after the vehicle has left the garage
- User submits feedback via Bmove app reporting the stuck session

## Typical resolution flow

1. User parks vehicle and starts a session in the Bmove app
2. User exits the garage within the allotted time (e.g. within 1 hour)
3. App fails to detect or register the exit event
4. Session continues to show as active/open in the app
5. User submits feedback through the app reporting the issue
6. Ticket is created in the support system

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Receive repeated feedback submissions from user reporting stuck session | support_system | Bmove App feedback pipeline | — |
| Investigate why exit event did not close the session in the app | support_agent or developer | Atlassian Jira (linked ticket BS-44895) | — |
| Manually close or correct the stuck parking session for the affected user | support_agent | backend admin tool | — |

## Evidence

Derived from 27 tickets in cluster `BS:end_user|no_value|no_label:c3`. Direct quotes from 2 representative tickets:

- `BS-44881` _[hr]_: "Još uvije mi stoji u app da je vozilo ZG**** u garaži u Kaptol centru, izašao sam unutar 1h"
- `BS-44751` _[hr]_: "Izasao sam iz garaze a i dalje mi se broji da sam tamo"

## Cluster statistics

- **Volume:** 27 tickets total (27 unique semantic events after dedup)
- **Frequency:** 0.53 tickets/month (over data window 2025-11-11 → 2025-11-13)
- **Median resolution:** 14.3 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

_Not applicable._ This cluster represents a one-off operational incident (see banner at top). Recurring-volume ROI estimates are not meaningful here. If you want a savings number for the *postmortem* itself, compute it from the incident's actual ticket volume × per-ticket handling cost, not from annualized frequency.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.92)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Engineering backlog — not for runtime agents

