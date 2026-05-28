---
id: parking-fine-received-despite-valid-payment
name: parking_fine_received_despite_valid_payment
title: End user receives parking fine despite having paid via Bmove app
description: Customers who paid for parking through the Bmove app receive a physical parking fine, typically due to license
  plate input errors (wrong characters, extra country prefix, Cyrillic alphabet), parking controller errors, wrong city/zone
  selected, or delays/failures in payment data reaching the local parking authority's system. Bmove support verifies the payment,
  identifies the root cause, and redirects the customer to the relevant local parking authority to dispute or cancel the fine.
  Bmove cannot cancel or modify already-issued tickets or fines, as those are in the jurisdiction of the local parking services.
category: end_user/integrations
ticket_class: end_user
issue_category: integration_issue
resolution_pattern: vendor_escalation
languages:
- en
- de
- other
country_focus:
- hr
- other
status: active
# Skills enabled for this playbook — planner sees only these tools.
# All writes are HITL (autonomous_resolve: false below).
allowed_skills:
  - jira_get_history
  - jira_add_internal_comment
  - jira_add_public_comment
  - jira_transition
agent_compatibility:
  autonomous_resolve: false
cluster_id: BS:end_user|no_value|dpk:c0
project_key: BS
cluster_size: 24
cluster_size_dedup: 24
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.47
median_resolution_minutes: 1077.5
p95_resolution_minutes: 8476.299999999997
cannot_reproduce_rate: 0.0
data_window_start: '2022-05-06'
data_window_end: '2023-04-04'
annual_hours_saved: 0.7
roi:
  baseline_active_hours: 2.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.2
  deflection_hours_range:
  - 0.1
  - 0.2
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.7
  agent_assist_hours_range:
  - 0.5
  - 0.9
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.9
  product_fix_hours_range:
  - 0.7
  - 1.1
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.1
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-7221
- BS-2494
- BS-2633
- BS-503
- BS-938
- BS-2986
- BS-5361
- BS-2324
- BS-1308
- BS-1561
- BS-1368
- BS-890
- BS-1835
- BS-1184
- BS-2795
- BS-854
- BS-690
- BS-6200
canonical_examples:
- BS-2494
- BS-2633
- BS-938
vendor_dependency:
  vendor_name: Local Croatian parking authorities (e.g., Splitparking, Zagrebparking, Zadar parking, Makarska parking, Baška
    parking)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-acknowledge receipt of the parking fine photo and send a templated payment-confirmation
    summary with local authority contact details when payment record is unambiguously matched by plate and timestamp — leaving
    final verification and dispatch to an agent.
  autonomous_resolve_safety_constraints:
  - Agent must review and approve before any payment-record details are shared with the customer
  - Autonomous action must never communicate to the customer that the fine will be cancelled — Bmove has no authority to cancel
    fines
  - No automated contact with local parking authorities on the customer's behalf without explicit customer and agent consent
  - Plate-matching must require exact match or flagged human review; fuzzy matching must not trigger autonomous send
  - Any ticket involving a potential integration/API failure must be escalated to a human agent
related_playbooks:
- app-payment-failure-parking-ticket
- bmove-app-feedback-mixed-issues__7950cd
- gtt-skidata-is-alive-timeout-error
- hr-b2b-sms-parking-payment-failure
- hr-open-session-after-garage-exit
- hr-parking-ticket-fine-after-paid-app
- italy-gtt-parking-stop-threshold-alert
- italy-gtt-skidata-invalid-timestamp-anomaly
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
---

# End user receives parking fine despite having paid via Bmove app

## What this pattern is

Customers who paid for parking through the Bmove app receive a physical parking fine, typically due to license plate input errors (wrong characters, extra country prefix, Cyrillic alphabet), parking controller errors, wrong city/zone selected, or delays/failures in payment data reaching the local parking authority's system. Bmove support verifies the payment, identifies the root cause, and redirects the customer to the relevant local parking authority to dispute or cancel the fine. Bmove cannot cancel or modify already-issued tickets or fines, as those are in the jurisdiction of the local parking services.

## When this applies

- Customer pays for parking via Bmove app and receives a physical fine on return to the vehicle
- Customer inputs incorrect or misformatted license plate (extra country prefix, typo, Cyrillic characters, letter/digit confusion)
- Parking controller's system does not show the Bmove payment (sync/integration delay or failure)
- Customer selects wrong city or parking zone in the app
- Parking controller makes an error recording the license plate on the fine

## Typical resolution flow

1. Customer contacts Bmove support reporting a fine received despite having paid
2. Support agent requests a picture of the fine if not already attached
3. Support agent checks the payment record and compares the license plate on the payment vs. the fine
4. Agent identifies root cause: user input error, controller error, Cyrillic plate mismatch, wrong city/zone, or system sync issue
5. Agent confirms whether payment was valid
6. Agent directs customer to the relevant local parking authority with the Bmove receipt and instructions to request cancellation
7. Agent informs customer that Bmove cannot cancel or alter tickets, as this is in the parking authority's jurisdiction

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Request photo of the parking fine from the customer | support_agent | Jira/email | 5 min |
| Verify payment record and compare license plate on payment vs. fine | support_agent | Bmove back-office system | 10 min |
| Explain root cause to customer and advise them to contact local parking authority with receipt | support_agent | Jira/email | 10 min |
| Customer contacts local parking authority to dispute or cancel fine | customer | email to local parking authority | — |

## Vendor dependency

- **Vendor:** Local Croatian parking authorities (e.g., Splitparking, Zagrebparking, Zadar parking, Makarska parking, Baška parking)

## Evidence

Derived from 24 tickets in cluster `BS:end_user|no_value|dpk:c0`. Direct quotes from 7 representative tickets:

- `BS-2494` _[en]_: "as we can see, you did paid for your parking properly. Please contact Splitparking for this since they issued the fine by a mistake."
- `BS-2633` _[en]_: "you bought a parking ticket for the correct license plate, but it was written in cyrillic alphabet, which the parking providers system did not recognize so they issued you a fine."
- `BS-938` _[en]_: "you have written the HR in front of the license plate number. That is incorrect, you only input the letters and numbers from the license plate without any dashes or country letters."
- `BS-1308` _[en]_: "we cannot change or cancel already purchased tickets. We are a selling platform and all of the parking tickets and fines are in the jurisdiction of parking services."
- `BS-1835` _[en]_: "you paid for Krk, and not Baška. That is why you got a fine. On Krk island, there are three different parking services - Krk, Baška, and Vrbnik."
- `BS-1184` _[de]_: "Auf diesen Zettel steht GTHWW508 Aber das PKW Kennzeichen ist GTHVW508"
- `BS-6200` _[en]_: "the parking controller couldn't find your paid parking. We see that you did paid for the parking for the license plate number AP**** but since you use another letter on your phone, the parking syste"

## Cluster statistics

- **Volume:** 24 tickets total (24 unique semantic events after dedup)
- **Frequency:** 0.47 tickets/month (over data window 2022-05-06 → 2023-04-04)
- **Median resolution:** 18.0 hours
- **Languages:** en, de, other
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.7 (range [0.483, 0.897])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.80
- **Rationale:** The resolution workflow is highly structured: retrieve payment record, compare plate, explain root cause, and direct to authority. An assist tool that auto-looks up the payment record by ticket number and pre-fills a response template with the correct local authority contact could reduce active handle time by roughly 30%, primarily on steps 2 and 3.
- **Validation:** Run assist tool in shadow mode for 3 weeks on this cluster, comparing agent-measured handle times with and without the suggested lookup and template; target ≥80% agent acceptance rate on drafted responses before rollout.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~0.9 (range [0.69, 1.15])
- **Root cause:** Root causes are split between user input errors (incorrect plate characters, Cyrillic alphabet, added country prefix, wrong city/zone) and external integration failures (payment data delays or non-delivery to local parking authority systems). Neither constitutes a single fixable product bug, though UX hardening (plate format validation, zone confirmation, retry/status visibility) and improved API reliability with parking authorities could reduce incident frequency.
- **Rationale:** Plate-entry validation (blocking obviously malformed plates), a mandatory zone-confirmation step, and improved delivery-acknowledgement logging from parking authority APIs could eliminate an estimated 40% of incidents; the remaining 60% depend on parking controller errors and authority-side delays outside Bmove's control. Hours eliminated are capped at the 40% midpoint of the 2.3-hour baseline.
- **Validation:** Engineering team should audit parking-authority API failure/timeout logs and measure the share of tickets attributable to data-delivery failures vs. user input errors to calibrate the 40% reduction assumption before committing sprint scope.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.2 (range [0.133, 0.247])
- **Form:** `help_center`
- **Deflection rate:** ~20% (range [14%, 26%])
- **Feasibility:** 0.45
- **Rationale:** A clear help-center article explaining common fine causes (plate typos, wrong city/zone, Cyrillic input) and instructing customers to gather their Bmove receipt and contact the relevant local authority could deflect a minority of tickets; however, many customers will still contact support to get explicit confirmation of their payment record before approaching the parking authority. The vendor-escalation resolution pattern limits full deflection because customers need an agent-verified payment record.
- **Validation:** Publish a dedicated help-center article and track contact rate for this cluster over 8 weeks post-launch; compare ticket volume against the prior 8-week baseline to measure actual deflection.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.1 (range [0.06, 0.104])
- **Narrow use case:** Auto-acknowledge receipt of the parking fine photo and send a templated payment-confirmation summary with local authority contact details when payment record is unambiguously matched by plate and timestamp — leaving final verification and dispatch to an agent.
- **Safety constraints:**
  - Agent must review and approve before any payment-record details are shared with the customer
  - Autonomous action must never communicate to the customer that the fine will be cancelled — Bmove has no authority to cancel fines
  - No automated contact with local parking authorities on the customer's behalf without explicit customer and agent consent
  - Plate-matching must require exact match or flagged human review; fuzzy matching must not trigger autonomous send
  - Any ticket involving a potential integration/API failure must be escalated to a human agent
- **Rationale:** Full autonomous resolution is unsafe because customers could be misled about fine cancellation outcomes, and payment-record verification requires human judgement to confirm ambiguous plate matches. At best, a narrow auto-acknowledgement step (photo received + templated next-steps message) covering ~10% of volume saves a small amount of time on the initial triage step only.
- **Validation:** Pilot auto-acknowledgement on 5 tickets per month with human review of every outbound message; measure customer satisfaction and error rate over 6 weeks before expanding scope.

### Risks

- **Compliance concerns:**
  - Sharing customer payment records or plate data in automated messages must comply with GDPR data-minimisation principles
  - Any communication implying Bmove can influence or cancel a municipal fine could create legal liability if misread as a guarantee
- **Must not automate:**
  - Issuing any statement to the customer that the fine has been or will be cancelled
  - Contacting local parking authorities on the customer's behalf without explicit consent
  - Making final root-cause determinations on ambiguous plate mismatches without human review
- **Vendor dependencies blocking automation:**
  - Local Croatian parking authorities (Splitparking, Zagrebparking, Zadar parking, Makarska parking, Baška parking) control fine cancellation decisions and have no SLA with Bmove, blocking any end-to-end automated resolution
  - Improved API delivery acknowledgement from parking authority systems is required before integration-failure root causes can be detected and handled automatically

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

