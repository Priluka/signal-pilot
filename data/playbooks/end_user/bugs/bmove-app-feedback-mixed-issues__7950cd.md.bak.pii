---
id: bmove-app-feedback-mixed-issues__7950cd
name: bmove_app_feedback_mixed_issues
title: 'Bmove App In-App Feedback Submissions: Mixed Issues, Payment Failures, and Test Tickets'
description: End users submit feedback directly through the Bmove mobile application covering a wide range of issues including
  app not working, payment/parking ticket purchase failures, vehicle management problems, and requests for contact. A significant
  subset consists of internal test tickets or very low-effort messages ('test', 'super je!', 'ne radi') with little actionable
  content. Payment failure cases often turn out to be resolvable via the web app or are caused by external parking system
  outages.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- hr
- en
- other
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|no_value|no_label:c2
project_key: BS
cluster_size: 29
cluster_size_dedup: 28
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.72
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.55
median_resolution_minutes: 1474.0
p95_resolution_minutes: 215816.19999999984
cannot_reproduce_rate: 0.0
data_window_start: '2022-10-01'
data_window_end: '2025-11-07'
annual_hours_saved: 0.6
roi:
  baseline_active_hours: 2.4
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.4
  deflection_hours_range:
  - 0.3
  - 0.5
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.6
  agent_assist_hours_range:
  - 0.4
  - 0.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.2
  product_fix_hours_range:
  - 0.8
  - 1.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.2
  autonomous_resolve_hours_range:
  - 0.2
  - 0.3
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-26977
- BS-3153
- BS-36151
- BS-4446
- BS-4808
- BS-7177
- BS-16154
- BS-3259
- BS-2405
- BS-4158
- BS-36141
- BS-21025
- BS-36143
- BS-2800
- BS-36132
- BS-4201
- BS-36140
- BS-43763
canonical_examples:
- BS-3153
- BS-4158
- BS-4158
vendor_dependency:
  vendor_name: External parking management systems (e.g., city parking operators)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: 'Auto-close confirmed test/spam tickets (matching heuristic patterns: ''test'', single-word
    nonsense, internal test account identifiers) with no user-facing action'
  autonomous_resolve_safety_constraints:
  - Only auto-close tickets matching high-confidence spam/test heuristics (e.g., exact match on known test strings, internal
    test account IDs)
  - Never auto-close tickets containing payment failure signals or license plate references
  - All auto-closed tickets must be logged and reviewable for 30 days
  - Human review queue for any borderline classification before closure
  - No autonomous actions involving vendor or external parking system communication
related_playbooks:
- app-payment-failure-parking-ticket
- austrian-ticketless-open-session-at-exit__06e3d4
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__d6cf0c
- bmove-app-operational-issues-austria
- croatia-parking-payment-failure__e3b934
- croatia-ticketless-open-session-at-exit__a7c97e
- croatia-ticketless-open-session-at-exit__f25b63
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- hr-open-session-after-garage-exit
- hr-parking-ticket-fine-after-paid-app
- missing-parking-invoice-receipt
- open-session-at-exit-austria
- open-session-at-exit-payment-failure
- parking-fine-received-despite-valid-payment
- parking-payment-failure-end-user
- prepaid-top-up-and-usage-issues
- slovakia-parking-payment-failure-no-ticket
- ticketless-open-session-at-exit__960f17
- ticketless-open-session-at-exit__d8d1ba
- ticketless-open-session-at-exit__fd04ac
- ticketless-open-session-not-closed-at-exit
- wrong-parking-ticket-purchase-redirect
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

# Bmove App In-App Feedback Submissions: Mixed Issues, Payment Failures, and Test Tickets

## What this pattern is

End users submit feedback directly through the Bmove mobile application covering a wide range of issues including app not working, payment/parking ticket purchase failures, vehicle management problems, and requests for contact. A significant subset consists of internal test tickets or very low-effort messages ('test', 'super je!', 'ne radi') with little actionable content. Payment failure cases often turn out to be resolvable via the web app or are caused by external parking system outages.

## When this applies

- User submits in-app feedback via the Bmove mobile application
- User encounters an error or failure when attempting to purchase a parking ticket
- User cannot manage their vehicle (e.g., remove a vehicle from the system)
- User wants to change a purchased voucher type
- Internal or developer test submissions triggered via the feedback form

## Typical resolution flow

1. User submits feedback through the Bmove app feedback form
2. A ticket is automatically created in Bmove Support (Jira) with the user's ID and email
3. Support agent reviews the feedback message and sub-issue type
4. If the issue is a payment failure, agent checks whether the user can complete purchase via the web app (app.bmove.com)
5. If the issue is an external parking system outage, agent identifies the root cause as a third-party system
6. If the ticket is a test submission, agent closes it without action
7. Agent responds to user by email if contact is requested or issue requires follow-up

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Instruct user to retry purchase via the Bmove web application (app.bmove.com) | support_agent | email / Jira comment | 5 min |
| Identify external parking system outage as root cause of payment failure | support_agent | Jira / internal monitoring | 10 min |
| Close test/spam tickets without action | support_agent | Jira | 2 min |
| Request additional information (e.g., license plate) to investigate vehicle management issue | support_agent | email / Jira comment | 5 min |

## Vendor dependency

- **Vendor:** External parking management systems (e.g., city parking operators)

## Evidence

Derived from 29 tickets in cluster `BS:end_user|no_value|no_label:c2`. Direct quotes from 8 representative tickets:

- `BS-3153` _[hr]_: "Ne mogu kupiti mjesečnu parkirnu kartu Sisak 2. zona."
- `BS-4158` _[hr]_: "u Rijeci zona 3. nije moguće platiti parking aplikacijom"
- `BS-4158` _[hr]_: "navedeni problem je bio na strani vanjskog sustava koji upravlja parking artiklima"
- `BS-16154` _[other]_: "Neviem odstranit vozidlo zo systemu."
- `BS-36141` _[en]_: "testing tickets => closing"
- `BS-4201` _[hr]_: "molim da me kontaktirate 0989224024"
- `BS-4808` _[hr]_: "pokusao sam platiti parking za solin ali ne radi..."
- `BS-26977` _[hr]_: "ne radi Bmove App"

## Cluster statistics

- **Volume:** 29 tickets total (28 unique semantic events after dedup)
- **Frequency:** 0.55 tickets/month (over data window 2022-10-01 → 2025-11-07)
- **Median resolution:** 1.0 days
- **Languages:** hr, en, other
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.4 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.6 (range [0.42, 0.78])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.70
- **Rationale:** Agent assist can meaningfully reduce handling time by auto-classifying tickets (test/spam vs. payment vs. vehicle management), pre-populating the web-app retry instruction, and surfacing known outage status — but the small volume means absolute savings are modest. The high heterogeneity of messages limits the ceiling on time reduction.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool classifies and drafts responses alongside agents; measure accepted-draft rate and compare active handling minutes per ticket vs. the 22-minute baseline.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~2 (range [1.5, 2.5])
- **Hours eliminated per year:** ~1.2 (range [0.84, 1.56])
- **Root cause:** The mobile app's payment flow is fragile against external parking system outages and does not gracefully fall back to the web app, leaving users stranded with no actionable guidance. Additionally, the in-app feedback form accepts test/low-effort submissions that generate zero-value tickets.
- **Rationale:** Fixing the payment flow to surface outage status in-app and auto-suggest the web app fallback would eliminate the largest resolution action category; adding a minimum-content guard on the feedback form would reduce zero-value test tickets. Full elimination is unlikely due to residual vehicle management issues and genuine bugs.
- **Validation:** Engineering team should instrument payment-failure events in production to baseline outage-driven failure rate, then A/B test the outage-status banner and web-app redirect prompt to measure ticket reduction per sprint before committing to full rollout.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.4 (range [0.252, 0.468])
- **Form:** `in_app_help`
- **Deflection rate:** ~30% (range [21%, 39%])
- **Feasibility:** 0.55
- **Rationale:** A meaningful subset of tickets (test/spam plus simple payment retry cases) could be deflected by in-app guidance directing users to app.bmove.com for purchases and by a prominent outage status banner; however, the mixed and low-signal nature of many submissions limits overall deflection potential. Vehicle management and ambiguous messages are harder to self-serve.
- **Validation:** Deploy a 4-week in-app help overlay with a 'having trouble paying?' prompt linking to the web app and a live outage status feed; measure ticket submission rate before and after to validate deflection rate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.2 (range [0.154, 0.286])
- **Narrow use case:** Auto-close confirmed test/spam tickets (matching heuristic patterns: 'test', single-word nonsense, internal test account identifiers) with no user-facing action
- **Safety constraints:**
  - Only auto-close tickets matching high-confidence spam/test heuristics (e.g., exact match on known test strings, internal test account IDs)
  - Never auto-close tickets containing payment failure signals or license plate references
  - All auto-closed tickets must be logged and reviewable for 30 days
  - Human review queue for any borderline classification before closure
  - No autonomous actions involving vendor or external parking system communication
- **Rationale:** Only the test/spam subset is safe to resolve autonomously given the mixed-issue nature of this cluster and the presence of real payment failures that require human judgment; autonomous resolution of payment or vehicle cases carries too high a risk of incorrect closure and user harm. At an estimated 20% of volume, absolute savings are small but the pattern is clean and low-risk.
- **Validation:** Pilot over 6 weeks with a manually reviewed shadow list of auto-close candidates; require >95% precision on spam classification before enabling live auto-close, with a human spot-check of 10% of auto-closed tickets each week.

### Risks

- **Compliance concerns:**
  - Payment failure tickets may have consumer protection implications if closed without resolution — must not be auto-dismissed without investigation
  - User-submitted feedback may contain personal data (license plates, contact info) requiring GDPR-compliant handling and retention limits
- **Must not automate:**
  - Any ticket containing a payment failure or purchase error signal — requires human triage to distinguish app bug from vendor outage from user error
  - Vehicle management issues — incorrect data or missed follow-up could leave users unable to manage registered vehicles
  - Tickets where it is unclear whether the submission is a test or a real user issue
- **Vendor dependencies blocking automation:**
  - External parking management system (city parking operators) outage status is not programmatically accessible, blocking automated outage detection and any autonomous payment-resolution flow that depends on real-time vendor health checks

## Agent compatibility

- **Status:** `active` (extraction confidence 0.72)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

