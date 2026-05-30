---
id: ticketless-open-session-at-exit__d8d1ba
name: ticketless_open_session_at_exit
title: Parking session remains open in Bmove app after user has physically left the garage
description: End users report that their Bmove parking session continues running (timer keeps counting) after they have already
  exited the garage, typically because the exit barrier failed to recognize their license plate or a system/network error
  prevented automatic session closure. In most cases the barrier was opened manually by a garage attendant, leaving the digital
  session unresolved. Support agents must manually close the session and, where payment authorization failed, manually trigger
  the charge.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- de
country_focus:
- at
- de
- other
status: active
cluster_id: BS:end_user|no_value|ticketless:c0
project_key: BS
cluster_size: 20
cluster_size_dedup: 20
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.39
median_resolution_minutes: 4043.0
p95_resolution_minutes: 41349.45000000001
cannot_reproduce_rate: 0.0
data_window_start: '2022-10-19'
data_window_end: '2023-03-28'
annual_hours_saved: 0.4
roi:
  baseline_active_hours: 2.2
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.2
  deflection_hours_range:
  - 0.2
  - 0.3
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.4
  agent_assist_hours_range:
  - 0.3
  - 0.6
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.0
  product_fix_hours_range:
  - 1.4
  - 2.2
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.2
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-5067
- BS-3241
- BS-5718
- BS-4007
- BS-4810
- BS-4796
- BS-6822
- BS-5553
- BS-5036
- BS-2704
- BS-5035
- BS-3726
- BS-6147
- BS-6921
- BS-6468
- BS-6810
- BS-5034
- BS-4035
canonical_examples:
- BS-5067
- BS-3241
- BS-4007
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-send acknowledgement and ETA message to user while routing ticket to operations
    queue — no payment or session actions taken autonomously.
  autonomous_resolve_safety_constraints:
  - No autonomous session closure — must be performed by a verified operations colleague
  - No autonomous payment charge initiation — financial action requires human approval
  - No autonomous handling of failed payment or alternative payment collection
  - Automation limited to informational messaging and ticket routing only
  - Any automation must log all actions for audit trail
related_playbooks:
- app-payment-failure-parking-ticket
- austrian-ticketless-open-session-at-exit__06e3d4
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__7950cd
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
- ticketless-open-session-at-exit__fd04ac
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

# Parking session remains open in Bmove app after user has physically left the garage

## What this pattern is

End users report that their Bmove parking session continues running (timer keeps counting) after they have already exited the garage, typically because the exit barrier failed to recognize their license plate or a system/network error prevented automatic session closure. In most cases the barrier was opened manually by a garage attendant, leaving the digital session unresolved. Support agents must manually close the session and, where payment authorization failed, manually trigger the charge.

## When this applies

- Exit barrier does not open automatically (license plate recognition failure or system crash)
- Garage attendant opens barrier manually, bypassing the automatic session-close trigger
- App network error at time of exit prevents session from closing
- User accidentally uses a different parking ticket (e.g., Best-in-Parking card) alongside Bmove, causing conflicting session state
- Barrier is found open/broken and user drives through without a scan

## Typical resolution flow

1. User exits garage physically but the Bmove app still shows an active session
2. User submits feedback/complaint via Bmove app describing the open session
3. Ticket is created automatically in support system
4. Support agent acknowledges issue and informs user that a colleague will close the session
5. Agent internally tags a colleague (Patrick Aumüller) to close the session and process the charge
6. Colleague attempts to manually end the session and charge the correct amount
7. If payment fails, agent requests updated payment method from user
8. Agent confirms session is closed and asks user to verify in the app

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Acknowledge complaint and inform user that session will be closed manually | support_agent | Zendesk / ticketing system | 5 min |
| Manually close the open parking session in the backend system | operations_colleague (Patrick Aumüller) | Bmove backend / admin panel | 10 min |
| Manually trigger payment charge for the correct parking duration | operations_colleague (Patrick Aumüller) | Bmove backend / payment processor | 5 min |
| Request alternative payment method from user if charge fails | support_agent | Zendesk / email | 5 min |
| Confirm resolution to user and ask them to verify in the app | support_agent | Zendesk / email | 3 min |

## Evidence

Derived from 20 tickets in cluster `BS:end_user|no_value|ticketless:c0`. Direct quotes from 8 representative tickets:

- `BS-5067` _[de]_: "bin längst aus der Garage weg und mein Ticket läuft weiter."
- `BS-3241` _[de]_: "nach mehr als 1 Stunde nachdem dem verlassen der Garage läuft die Session auf der App noch immer und die Stunden werden noch immer gezählt."
- `BS-4007` _[de]_: "bin heute um 00:20 aus der garage gefahren und wurde rausgelasssen weil system abgestürzt war. bitte um beendigung der offenen session."
- `BS-4796` _[de]_: "Schranke hat nicht geöffnet und ich musste ein Ticket ziehen - trotzdem zeigt die App eine aktive Sitzung - bitte um Hilfe"
- `BS-6921` _[de]_: "meine Sitzung ist noch aktiv obwohl ich die Garage bereits um ca 16:30 verlassen habe."
- `BS-6147` _[de]_: "Ich habe noch eine aktive Sitzung, obwohl ich am Do. 16.02. nach 3 Stunden ausgecheckt habe."
- `BS-5034` _[de]_: "Die App meldete einen Netzwerkfehler und man solle es später erneut versuchen. Über die Gegensprechanlage und Bekanntgabe des KFZ Kennzeichen würde mir der Schranken geöffnet. Die App zeigt aber immer"
- `BS-4035` _[de]_: "wir sind draußen, ticket läuft weiter."

## Cluster statistics

- **Volume:** 20 tickets total (20 unique semantic events after dedup)
- **Frequency:** 0.39 tickets/month (over data window 2022-10-19 → 2023-03-28)
- **Median resolution:** 2.8 days
- **Languages:** de
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.4 (range [0.31, 0.57])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.65
- **Rationale:** Agent-assist can provide a pre-filled acknowledgement message template and a step-by-step guided checklist for the manual close + payment trigger workflow, reducing lookup time and errors; however, the bulk of active minutes belong to Patrick's backend operations work, which is less amenable to text-assist tools.
- **Validation:** Run shadow-mode for 3 weeks: surface the macro template and checklist to agents without requiring adoption; measure time-on-ticket before vs. after voluntary adoption to calibrate actual reduction.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~2 (range [1.4, 2.2])
- **Root cause:** Exit barrier fails to trigger automatic session closure when license plate recognition fails or a network error occurs; no fallback reconciliation loop exists to detect sessions where the vehicle has departed but the session remains open.
- **Rationale:** If the product implemented a reliable fallback (e.g., a reconciliation daemon that detects barrier-open events without matched session closure and auto-closes with correct duration), the vast majority of these tickets would be eliminated. The upper bound is capped at the 2.2-hour baseline since hours eliminated cannot exceed the baseline.
- **Validation:** Engineering team should scope effort via a spike: map the barrier event log integration, define reconciliation rules, and prototype in staging; re-estimate sprints after spike before committing.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.2 (range [0.154, 0.286])
- **Form:** `in_app_help`
- **Deflection rate:** ~10% (range [7%, 13%])
- **Feasibility:** 0.30
- **Rationale:** This issue requires active backend intervention to close the session and trigger payment, so self-service content can only help users understand the situation and set expectations — it cannot resolve the underlying problem. A small fraction of users who discover the FAQ may choose to wait or avoid contacting support, yielding modest deflection.
- **Validation:** Deploy an in-app help article explaining the stuck-session scenario for 4 weeks; measure contact rate before vs. after for users who viewed the article to estimate true deflection.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.1 (range [0.091, 0.169])
- **Narrow use case:** Auto-send acknowledgement and ETA message to user while routing ticket to operations queue — no payment or session actions taken autonomously.
- **Safety constraints:**
  - No autonomous session closure — must be performed by a verified operations colleague
  - No autonomous payment charge initiation — financial action requires human approval
  - No autonomous handling of failed payment or alternative payment collection
  - Automation limited to informational messaging and ticket routing only
  - Any automation must log all actions for audit trail
- **Rationale:** Full autonomous resolution is not safe here because it involves financial transactions (charging the correct amount) and backend data mutation (session closure); limited automation can handle the acknowledgement step (~5 min per ticket) without touching money or data. Savings are therefore small.
- **Validation:** Pilot for 4 weeks by automating only the acknowledgement message on ticket creation; measure customer satisfaction and agent confirmation rate to ensure no errors before considering scope expansion.

### Risks

- **Compliance concerns:**
  - Automated or erroneous payment charges may violate consumer protection regulations if the wrong amount is billed
  - Storing and processing payment method data for retry requires PCI-DSS compliance controls
  - GDPR: any logging of vehicle license plates and session data must have a defined retention policy
- **Must not automate:**
  - Initiating or retrying payment charges without human verification of the correct parking duration
  - Closing a parking session in the backend without confirming the vehicle has actually exited
  - Requesting or storing alternative payment methods — must follow secure payment handling procedures
  - Any action that modifies financial records without an auditable human approval step

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

