---
id: skidata-hosted-services-maintenance-notification
name: skidata_hosted_services_maintenance_notification
title: SKIDATA Hosted Services Scheduled Maintenance Notifications Routed to Bmove Support
description: B2B partners receive automated scheduled maintenance notifications from SKIDATA's hosting team (GTS + Hosting
  Team) regarding planned downtime windows for SKIDATA hosted environments (car access, people access, integrated billing,
  etc.). These notifications are forwarded or end up as tickets in Bmove Support, where they receive a standard acknowledgement
  response but require no actual support action. The tickets span from late 2023 through early 2025 and cover recurring maintenance
  events affecting SKIDATA's EMEA production environments.
category: b2b_operator/vendor_issues
ticket_class: b2b_partner
issue_category: vendor_failure
resolution_pattern: no_action
languages:
- en
- de
country_focus:
- other
- at
status: active
cluster_id: BS:b2b_partner|no_value|no_label:c1
project_key: BS
cluster_size: 17
cluster_size_dedup: 17
sample_size_used: 17
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.33
median_resolution_minutes: 762711.0
p95_resolution_minutes: 861988.2
cannot_reproduce_rate: 0.4118
data_window_start: '2023-10-02'
data_window_end: '2025-01-16'
annual_hours_saved: 0.1
roi:
  baseline_active_hours: 0.2
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
  - 0.1
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.2
  product_fix_hours_range:
  - 0.1
  - 0.2
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.1
  autonomous_resolve_max_safe_volume_pct: 0.3
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-13942
- BS-14198
- BS-15675
- BS-15688
- BS-18445
- BS-18446
- BS-18459
- BS-19641
- BS-22925
- BS-24142
- BS-24361
- BS-27972
- BS-32351
- BS-15973
- BS-22806
- BS-15377
- BS-22621
canonical_examples:
- BS-13942
- BS-15675
- BS-22925
vendor_dependency:
  vendor_name: SKIDATA
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Informational — safe for agent self-service
  autonomous_resolve_max_safe_volume_pct: 0.3
  autonomous_resolve_narrow_use_case: Auto-acknowledge and auto-close inbound tickets identified as SKIDATA scheduled-maintenance
    notifications (matched by sender domain + subject-line pattern) with no partner-facing escalation path
  autonomous_resolve_safety_constraints:
  - Pattern match must require both sender-domain (skidata.com / skidata.net or known GTS alias) AND subject-line keyword
    match to minimise false positives
  - Any ticket containing a partner-authored question or complaint body must be routed to a human agent, not auto-closed
  - Auto-close must send a pre-approved acknowledgement reply so the B2B partner has a record
  - A daily digest of auto-resolved tickets must be reviewed by a support lead for the first 90 days
  - 'Volume cap: autonomous resolution applied to at most 30% of ingested tickets matching the pattern until false-positive
    rate is confirmed below 2%'
related_playbooks:
- b2b-parking-invoice-payment-issues
- b2b-partner-parking-card-storno-refund
- b2b-ticketless-open-session-and-permit-conflict
- hr-b2b-partner-billing-payment-storno
- hr-b2b-sms-parking-payment-failure
- zagreb-parking-cancelled-ticket-refund
- zagrebparking-b2b-storno-refund-request
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# SKIDATA Hosted Services Scheduled Maintenance Notifications Routed to Bmove Support

## What this pattern is

B2B partners receive automated scheduled maintenance notifications from SKIDATA's hosting team (GTS + Hosting Team) regarding planned downtime windows for SKIDATA hosted environments (car access, people access, integrated billing, etc.). These notifications are forwarded or end up as tickets in Bmove Support, where they receive a standard acknowledgement response but require no actual support action. The tickets span from late 2023 through early 2025 and cover recurring maintenance events affecting SKIDATA's EMEA production environments.

## When this applies

- SKIDATA GTS + Hosting Team sends a maintenance notification email to b2b partners
- B2b partner forwards or submits the maintenance notification into Bmove Support ticketing system
- Scheduled maintenance windows for SKIDATA hosted environments (EMEA production, sandbox, staging)

## Typical resolution flow

1. SKIDATA GTS + Hosting Team schedules a maintenance window and sends notification to affected partners
2. Notification is received and a ticket is created in Bmove Support
3. Bmove Support sends a standard acknowledgement reply (1-2 business days processing time)
4. Ticket is closed, often via bulk close, with no further action taken

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Send standard acknowledgement response to the b2b partner | Bmove Support agent | Bmove Support ticketing system | 2 min |
| Bulk close ticket without further investigation | Bmove Support agent | Bmove Support ticketing system | 1 min |

## Vendor dependency

- **Vendor:** SKIDATA

## Evidence

Derived from 17 tickets in cluster `BS:b2b_partner|no_value|no_label:c1`. Direct quotes from 6 representative tickets:

- `BS-13942` _[en]_: "We hereby inform you that a new maintenance has been scheduled. Maintenance period: Monday, 2023-10-09 between 22:00 and 24:00 (CEST)"
- `BS-15675` _[de]_: "Gerne kümmern wir uns um Ihr Anliegen. Bitte erlauben Sie uns eine Bearbeitungszeit von 1-2 Werktagen."
- `BS-22925` _[en]_: "We finished with all updates and verified services. All systems green – no outage could be detected."
- `BS-18459` _[en]_: "The maintenance work is finished. All systems reporting healthy state."
- `BS-14198` _[en]_: "The service will be migrated into a different cloud"
- `BS-27972` _[en]_: "bulk_close on 08.01.2026"

## Cluster statistics

- **Volume:** 17 tickets total (17 unique semantic events after dedup)
- **Frequency:** 0.33 tickets/month (over data window 2023-10-02 → 2025-01-16)
- **Median resolution:** 529.7 days
- **Cannot Reproduce rate:** 41.2%
- **Languages:** en, de
- **Country focus:** other, at

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~0.2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.1 (range [0.07, 0.13])
- **Time reduction per ticket:** ~50% (range [35%, 65%])
- **Feasibility:** 0.75
- **Rationale:** Because every ticket receives an identical acknowledgement and a bulk-close, an AI assistant can pre-draft the acknowledgement and flag the ticket for one-click close, reducing per-ticket active time from ~3 min to ~1.5 min. The pattern is highly templated, making draft quality achievable at 90%+.
- **Validation:** Run shadow-mode for 2 weeks: assistant pre-drafts the acknowledgement alongside the agent's normal workflow; measure acceptance rate and time-to-close versus the prior 8-week baseline before enabling agent-facing suggestions.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~0.5 (range [0.3, 0.7])
- **Hours eliminated per year:** ~0.2 (range [0.13, 0.2])
- **Root cause:** SKIDATA's GTS/Hosting Team sends automated maintenance notifications to B2B partner email addresses that are configured to create Bmove Support tickets; the routing is a configuration/process gap, not a product defect in Bmove's platform.
- **Rationale:** The fix is an email-routing or ticket-ingestion rule: detect SKIDATA maintenance notification patterns (sender domain, subject-line keywords) and suppress ticket creation or auto-close before agent touch. Engineering effort is low because no product logic changes are needed, only an inbound filter rule; elimination rate is estimated at ~90% of baseline.
- **Validation:** Engineering team spikes the filter rule in staging against the 17 historical ticket emails to measure false-positive rate before deploying; acceptance criterion is <5% false positives on a hold-out set.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0.007, 0.013])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These tickets originate from SKIDATA's automated hosting-team notifications, not from partners seeking help; self-service content cannot intercept an inbound automated email. Deflection potential is near-zero because the submitter is a machine or a B2B admin relaying a vendor notice, not an end-user with a solvable question.
- **Validation:** Add a 4-week FAQ article explaining that SKIDATA maintenance notices require no action from Bmove Support and monitor whether inbound ticket volume falls; if partners are manually forwarding, a targeted email campaign could substitute.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 30% of tickets
- **Hours saved per year:** ~0.1 (range [0.042, 0.078])
- **Narrow use case:** Auto-acknowledge and auto-close inbound tickets identified as SKIDATA scheduled-maintenance notifications (matched by sender domain + subject-line pattern) with no partner-facing escalation path
- **Safety constraints:**
  - Pattern match must require both sender-domain (skidata.com / skidata.net or known GTS alias) AND subject-line keyword match to minimise false positives
  - Any ticket containing a partner-authored question or complaint body must be routed to a human agent, not auto-closed
  - Auto-close must send a pre-approved acknowledgement reply so the B2B partner has a record
  - A daily digest of auto-resolved tickets must be reviewed by a support lead for the first 90 days
  - Volume cap: autonomous resolution applied to at most 30% of ingested tickets matching the pattern until false-positive rate is confirmed below 2%
- **Rationale:** Given the ultra-low baseline (0.2 hours/year), autonomous resolution yields minimal absolute savings; however, it sets a precedent for zero-touch vendor-notification handling. Feasibility is moderate-high because the resolution action is always identical and carries no customer-harm risk if a maintenance notice is auto-acknowledged.
- **Validation:** Pilot for 8 weeks in shadow mode (resolve action logged but not executed); accept into production only if false-positive rate on matched tickets is <2% and no B2B partner raises a missed-escalation complaint during the pilot window.

### Risks

- **Compliance concerns:**
  - B2B partner SLAs may require a human-acknowledged response within a defined window; auto-responses must meet any contractual SLA wording
  - Audit trail: auto-closed tickets must be retained and attributable for any future vendor dispute resolution
- **Must not automate:**
  - Any ticket where the B2B partner has appended their own question, incident report, or escalation request to the forwarded SKIDATA notice — these require human triage
  - Tickets where the maintenance window overlaps with a known live incident or active partner complaint
- **Vendor dependencies blocking automation:**
  - SKIDATA does not provide a machine-readable API or webhook for maintenance notices; pattern matching depends on email formatting remaining stable — any change to SKIDATA's notification template could break the filter rule and requires re-validation
  - Bmove has no control over SKIDATA's notification distribution list; the root fix (removing Bmove Support from the recipient list) depends on SKIDATA's GTS/Hosting Team cooperation

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** Informational — safe for agent self-service

