---
id: austrian-open-session-at-exit
name: austrian_open_session_at_exit
title: Bmove parking session remains active after customer has physically exited the garage
description: End users in Austria (and occasionally Germany) report that their Bmove parking session stays open in the app
  after they have already left the garage, typically because the exit barrier failed to scan the licence plate or was manually
  opened by staff or emergency services. The customer cannot close the session themselves in the app and contacts support
  to have it closed and the charge corrected. Support resolves the issue by manually closing the session with the actual exit
  time and advising the customer to restart the app.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- de
country_focus:
- at
- de
status: active
cluster_id: BS:end_user|austria|skidata:c1
project_key: BS
cluster_size: 32
cluster_size_dedup: 31
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.61
median_resolution_minutes: 1111.0
p95_resolution_minutes: 52767.69999999998
cannot_reproduce_rate: 0.0
data_window_start: '2024-08-09'
data_window_end: '2025-03-07'
annual_hours_saved: 0.5
roi:
  baseline_active_hours: 2.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.1
  deflection_hours_range:
  - 0.1
  - 0.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.5
  agent_assist_hours_range:
  - 0.3
  - 0.6
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.3
  product_fix_hours_range:
  - 1.6
  - 2.3
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.2
  autonomous_resolve_hours_range:
  - 0.1
  - 0.2
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-30593
- BS-31734
- BS-25290
- BS-30672
- BS-33059
- BS-32015
- BS-28334
- BS-30298
- BS-30256
- BS-28509
- BS-27756
- BS-29746
- BS-34396
- BS-28390
- BS-29250
- BS-32245
- BS-31991
- BS-28745
canonical_examples:
- BS-30593
- BS-31734
- BS-25290
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: 2
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-close sessions only where backend telemetry unambiguously confirms the vehicle
    exited (e.g. barrier loop sensor + ANPR partial match) and elapsed overstay is under a defined threshold (e.g. <30 minutes),
    with automatic charge correction and customer notification.
  autonomous_resolve_safety_constraints:
  - Autonomous close must never occur without corroborating exit evidence from at least one independent backend signal (loop
    sensor, camera timestamp, or manual staff override log).
  - Charge corrections must stay within a pre-approved monetary delta threshold (e.g. ≤ €20) before routing to a human agent.
  - All autonomous actions must be logged with a full audit trail for billing dispute and GDPR compliance.
  - Cases involving emergency-service override must always be routed to a human due to liability ambiguity.
  - Customer must receive an explicit notification and a clear escalation path to dispute the automated decision.
related_playbooks:
- austrian-ticketless-incorrect-charge-refund
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__d6cf0c
- bmove-app-operational-issues-austria
- bmove-not-recognized-daily-worklog
- croatia-parking-payment-failure__e3b934
- croatia-ticketless-open-session-at-exit__a7c97e
- croatia-ticketless-open-session-at-exit__f25b63
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- email-address-change-not-possible
- email-address-change-not-supported
- expired-card-deletion-ticketless-link
- microsoft365-quarantine-notification-auto-tickets
- missing-parking-invoice-receipt
- missing-parking-receipt-email
- missing-parking-receipt-request
- open-session-at-exit-austria
- open-session-at-exit-payment-failure
- outstanding-payment-credit-card-failure
- pkc-vehicle-registration-automated-tickets
- ticketless-open-session-at-exit__960f17
- ticketless-open-session-not-closed-at-exit
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Bmove parking session remains active after customer has physically exited the garage

## What this pattern is

End users in Austria (and occasionally Germany) report that their Bmove parking session stays open in the app after they have already left the garage, typically because the exit barrier failed to scan the licence plate or was manually opened by staff or emergency services. The customer cannot close the session themselves in the app and contacts support to have it closed and the charge corrected. Support resolves the issue by manually closing the session with the actual exit time and advising the customer to restart the app.

## When this applies

- Exit barrier does not open automatically and LPR (licence-plate recognition) fails to register the departure
- Barrier is manually opened by garage staff, hotline operator, or emergency services (e.g. fire brigade) without triggering a system exit event
- Barrier is under maintenance or physically dismantled at time of exit
- System incorrectly starts a new session or retains a ghost session for a vehicle not in the garage

## Typical resolution flow

1. Customer exits garage with barrier opened manually; session remains active in Bmove app
2. Customer notices open session (often hours or days later) and contacts Bmove support
3. Support agent looks up the ticket/session by licence plate and verifies exit evidence (logs, printed ticket, timestamps)
4. Agent manually closes the session in the backend with the actual exit time
5. Agent sends templated reply informing customer the session is closed and to restart the app
6. Customer confirms resolution or, in some cases, follows up due to delayed or incomplete response

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Acknowledge ticket and set expectation of 1–5 business days response time | support_agent | helpdesk (automated response) | 1 min |
| Look up session/licence plate in backend logs to confirm actual exit time | support_agent | Bmove backend / LPR database | 10 min |
| Manually close open parking session with correct exit timestamp | support_agent | Bmove backend | 5 min |
| Send templated reply informing customer of closure and advising app restart | support_agent | helpdesk | 3 min |

## Evidence

Derived from 32 tickets in cluster `BS:end_user|austria|skidata:c1`. Direct quotes from 7 representative tickets:

- `BS-30593` _[de]_: "Der Schranken öffnete sich, ich bekam allerdings keine Bestätigung für die Ausfahrt."
- `BS-31734` _[de]_: "mein Ticket läuft noch immer weiter obwohl ich schon zuhause bin die Schranke wurde geöffnet"
- `BS-25290` _[de]_: "der Schranken war an diesem Tag defekt und wurde von der Feuerwehr manuell geöffnet damit alle hinausfahren können. Deswegen wird mir das Ticket als nicht beendet angezeigt."
- `BS-27756` _[de]_: "Die Sitzung ist leider auch noch immer aktiv, obwohl ich die Garage bereits verlassen habe."
- `BS-28390` _[de]_: "In meiner App ist mittlerweile fehlerhaft schon Tag28 aktiv und es läuft weiter. Bitte stoppen Sie das umgehend."
- `BS-31991` _[de]_: "Die Hotline vom Garagenbetreiber hat dann den Schranken geöffnet und versichert, dass mein Auto im BMOVE ausgebucht wurde. Dem ist leider nicht so, dort steht noch immer ein aktiver Parkvorgang."
- `BS-30593` _[de]_: "Der offene Parkvorgang wurde mit der Ausfahrtzeit aus der Garage abgeschlossen, daher ist der Parktarif korrekt. Überprüfen Sie es bitte in Ihrer Bmove-App."

## Cluster statistics

- **Volume:** 32 tickets total (31 unique semantic events after dedup)
- **Frequency:** 0.61 tickets/month (over data window 2024-08-09 → 2025-03-07)
- **Median resolution:** 18.5 hours
- **Languages:** de
- **Country focus:** at, de

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.5 (range [0.322, 0.598])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.75
- **Rationale:** The resolution is highly templated — backend log lookup, manual close, and a standard reply — making it a good candidate for an agent-assist tool that pre-populates the session lookup link and auto-drafts the closure confirmation email, reducing the templated steps (steps 1 and 4) by roughly 20% of active minutes. The backend close action (step 3) still requires deliberate human confirmation to avoid erroneous charges.
- **Validation:** Run the agent-assist draft tool in shadow mode for 4 weeks: measure actual time-on-ticket with vs. without the tool using support platform timestamps, targeting ≥15% reduction in active handle time before enabling send-on-behalf.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~2.3 (range [1.61, 2.3])
- **Root cause:** Exit barrier ANPR (automatic number plate recognition) scan failure or manual/emergency barrier override leaves the Bmove session in an open state because no authoritative exit event is recorded; the app has no fallback mechanism (e.g. geofence departure, timeout, or customer-initiated close) to handle this edge case.
- **Rationale:** A product fix (e.g. fallback geofence-based session close, customer-initiated dispute flow, or an ANPR missed-scan reconciliation job) could eliminate the majority of support contacts; the upper bound is capped at the full 2.3-hour baseline because the fix cannot save more than what currently exists. Engineering effort is medium because it touches barrier hardware integrations, backend session logic, and the mobile app.
- **Validation:** Engineering team should spike the ANPR miss-rate from barrier telemetry and prototype a geofence-exit fallback in a staging environment; a 2-sprint proof-of-concept with one Austrian garage can validate the approach before full rollout.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.049, 0.09])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** The customer cannot self-resolve this issue — session closure requires backend access held only by support agents, so FAQ or help-center content can at best set expectations but cannot deflect the ticket itself. A small fraction may abandon after reading an explanation, but this is not a true deflection of the support action.
- **Validation:** Deploy a help-center article explaining the known bug and average resolution time for 4 weeks; measure whether ticket submission rate decreases and track bounce rate on the article to estimate true deflection.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.2 (range [0.119, 0.22])
- **Narrow use case:** Auto-close sessions only where backend telemetry unambiguously confirms the vehicle exited (e.g. barrier loop sensor + ANPR partial match) and elapsed overstay is under a defined threshold (e.g. <30 minutes), with automatic charge correction and customer notification.
- **Safety constraints:**
  - Autonomous close must never occur without corroborating exit evidence from at least one independent backend signal (loop sensor, camera timestamp, or manual staff override log).
  - Charge corrections must stay within a pre-approved monetary delta threshold (e.g. ≤ €20) before routing to a human agent.
  - All autonomous actions must be logged with a full audit trail for billing dispute and GDPR compliance.
  - Cases involving emergency-service override must always be routed to a human due to liability ambiguity.
  - Customer must receive an explicit notification and a clear escalation path to dispute the automated decision.
- **Rationale:** Full autonomous resolution is risky because incorrect session closure could result in erroneous billing, which carries financial and GDPR liability in Austria/Germany; only a narrow, high-confidence subset of cases (estimated 15% of annual volume) meets the evidence threshold for safe automation. Savings are correspondingly small given low annual frequency.
- **Validation:** Pilot with 8-week shadow mode: identify tickets where backend logs contain unambiguous exit evidence meeting the defined criteria, simulate the autonomous close decision, and compare against agent-determined exit times; accept the pilot only if simulated close timestamps match agent timestamps within ±5 minutes on ≥95% of shadow cases.

### Risks

- **Compliance concerns:**
  - GDPR (EU): automated processing of personal data (licence plate, location, payment) for billing decisions requires a lawful basis and transparency obligations under GDPR Art. 13/22; automated charge corrections may trigger Art. 22 rights around solely automated decisions affecting individuals.
  - Austrian consumer protection law (KSchG) and German BGB may impose obligations around billing error correction timelines and customer notification requirements.
  - Billing audit trails must be retained per local fiscal/tax regulations; any automated close must preserve an immutable record of who (or what system) authorised the correction.
- **Must not automate:**
  - Session closures where the exit was triggered by emergency services or manual staff override without corroborating sensor data — liability is ambiguous and requires human judgement.
  - Charge corrections exceeding a defined monetary threshold without explicit human approval.
  - Any case where the customer disputes the exit time before a resolution is reached — disputed cases must remain human-handled.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

