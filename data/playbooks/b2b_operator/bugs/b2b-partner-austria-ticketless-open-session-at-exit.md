---
id: b2b-partner-austria-ticketless-open-session-at-exit
name: b2b_partner_austria_ticketless_open_session_at_exit
title: Ticketless parking session remains open after vehicle exits garage (barrier opened manually)
description: B2B partner users of the Bmove ticketless system exit a parking garage but the session is not automatically closed
  because the license plate recognition camera fails at exit, requiring staff to open the barrier manually. The app continues
  to show an active session, potentially blocking re-entry and causing incorrect billing. Support must manually close the
  session and set the correct exit timestamp.
category: b2b_operator/bugs
ticket_class: b2b_partner
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- de
- en
country_focus:
- at
- de
- other
status: active
cluster_id: BS:b2b_partner|austria|ticketless:c1
project_key: BS
cluster_size: 101
cluster_size_dedup: 96
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.88
median_resolution_minutes: 2575.0
p95_resolution_minutes: 231568.0
cannot_reproduce_rate: 0.0
data_window_start: '2023-04-12'
data_window_end: '2025-11-28'
annual_hours_saved: 4.0
roi:
  baseline_active_hours: 13.2
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.2
  deflection_hours_range:
  - 0.1
  - 0.3
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 4.0
  agent_assist_hours_range:
  - 2.9
  - 5.0
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 11.6
  product_fix_hours_range:
  - 9.0
  - 13.2
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 1.4
  autonomous_resolve_hours_range:
  - 1.0
  - 1.8
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-31480
- BS-23475
- BS-11863
- BS-7636
- BS-12874
- BS-14528
- BS-17104
- BS-8237
- BS-10512
- BS-15083
- BS-23066
- BS-45586
- BS-15284
- BS-13917
- BS-20099
- BS-15452
- BS-8672
- BS-12433
canonical_examples:
- BS-11863
- BS-23475
- BS-14528
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
  autonomous_resolve_narrow_use_case: Auto-close session and correct billing when a confirmed manual-barrier-open event is
    logged and customer-provided exit timestamp is validated against CCTV/gate log within a tolerance window.
  autonomous_resolve_safety_constraints:
  - Automated billing correction must never increase the charge above the manually verified amount.
  - Autonomous action requires cross-referencing gate event log to confirm the vehicle actually exited before closing session.
  - All autonomous closures must be logged for audit and reversible within 24 hours.
  - Cases where the exit timestamp is ambiguous or disputed must be escalated to a human agent.
  - B2B partner accounts with contractual billing SLAs must bypass autonomous resolution and follow manual review.
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-missing-parking-receipt-request
- b2b-outstanding-payment-failure-app
- b2b-ticketless-outstanding-payment-failure
- bmove-app-feedback-mixed-issues__7950cd
- bmove-app-feedback-mixed-issues__d6cf0c
- bmove-app-operational-issues-austria
- croatia-parking-payment-failure__e3b934
- croatia-ticketless-open-session-at-exit__a7c97e
- croatia-ticketless-open-session-at-exit__f25b63
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- missing-parking-invoice-receipt
- open-session-at-exit-austria
- open-session-at-exit-payment-failure
- ticketless-open-session-at-exit__960f17
- ticketless-open-session-at-exit__d8d1ba
- ticketless-open-session-at-exit__fd04ac
- ticketless-open-session-not-closed-at-exit
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Ticketless parking session remains open after vehicle exits garage (barrier opened manually)

## What this pattern is

B2B partner users of the Bmove ticketless system exit a parking garage but the session is not automatically closed because the license plate recognition camera fails at exit, requiring staff to open the barrier manually. The app continues to show an active session, potentially blocking re-entry and causing incorrect billing. Support must manually close the session and set the correct exit timestamp.

## When this applies

- License plate recognition camera fails to read the vehicle at exit
- Barrier does not open automatically on exit
- Garage staff manually opens barrier without closing the Bmove session
- Session remains active in app after vehicle has left the garage
- Customer unable to re-enter garage because system shows vehicle already inside

## Typical resolution flow

1. Customer attempts to exit garage; barrier does not open automatically
2. Garage attendant manually opens barrier via intercom/button
3. Customer notices active session still showing in Bmove app hours or days later
4. Customer contacts Bmove support via web form, email, or phone
5. Support agent requests license plate number and exit time from customer
6. Support agent tags internal team member (e.g. @Patrick Aumüller) with plate and estimated exit time
7. Internal operator manually closes the parking session with the correct exit timestamp
8. Billing is corrected to reflect actual parking duration
9. Customer is informed that the session has been closed and asked to verify in the app

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Acknowledge ticket and set expectation of 1-2 business days resolution | support agent | Jira / support ticketing system | 5 min |
| Request license plate number and exit time from customer if not provided | support agent | email / support ticketing system | 5 min |
| Tag internal operator with license plate and exit timestamp to close session manually | support agent | internal comment / back-end parking management system | 10 min |
| Recalculate and correct billing for actual parking duration | internal operator | back-end billing/parking management system | 10 min |
| Notify customer that session has been closed and ask them to verify in app | support agent | email / support ticketing system | 5 min |

## Evidence

Derived from 101 tickets in cluster `BS:b2b_partner|austria|ticketless:c1`. Direct quotes from 7 representative tickets:

- `BS-11863` _[de]_: "Die Einfahrt hat mit Kennzeichenerkennung perfekt funktioniert, nur leider nicht die Ausfahrt, es stand Restpreis offen und der Schranken ging nicht auf. Leider ist aber das Fahrzeug noch immer im Par"
- `BS-23475` _[de]_: "In der App wird ein Ticket noch als aktiv angezeigt, obwohl wir nach 1 Stunde rausgefahren sind. Leider hat die Kennzeichnen Erfassung nicht funktioniert, und wir wurden manuell rausgelassen."
- `BS-14528` _[de]_: "Unser Team wird die offene Parksitzung bald beenden. Ich melde mich noch, wenn es fertig ist. Parksitzung wird mit der Ausfahrtzeit beendet."
- `BS-12433` _[de]_: "@@Patrick Aumüller AF 2023-08-21 21:49 W****"
- `BS-20099` _[de]_: "scheinbar zahle ich jetzt nicht die Zeit in der ich in der Garage stehe, sondern die Zeit, in der ich NICHT dort stehe."
- `BS-8672` _[de]_: "Es gibt momentan zwischendurch Schwierigkeiten mit der Internetverbindung an diesem Standort und dieser verursacht, dass die Kommunikation zwischen der Garage und den für Bmove zuständigen Services zu"
- `BS-23066` _[de]_: "Beim Einfahren in die Garage am 13.06.2024 um ca. 14:00 Uhr kam zunächst die Meldung, dass das Auto bereits in der Garage sei und es musste dann ein neues Ticket gelöst werden."

## Cluster statistics

- **Volume:** 101 tickets total (96 unique semantic events after dedup)
- **Frequency:** 1.88 tickets/month (over data window 2023-04-12 → 2025-11-28)
- **Median resolution:** 1.8 days
- **Languages:** de, en
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~13.2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~4 (range [2.9, 5])
- **Time reduction per ticket:** ~30% (range [22%, 38%])
- **Feasibility:** 0.75
- **Rationale:** An assist tool can pre-fill the acknowledgement message, auto-surface the operator tagging template, and pre-draft the customer closure notification, reducing steps 1, 3, and 5 significantly. Steps 2 and 4 still require human judgment and operator execution.
- **Validation:** Run shadow-mode assist for 2 weeks on all incoming tickets in this cluster; measure agent acceptance rate of pre-drafted messages and average handle-time delta vs. control group.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~11.6 (range [9, 13.2])
- **Root cause:** Exit LPR camera fails to read the plate under certain conditions (lighting, angle, occlusion), leaving the ticketless session open with no fallback auto-close trigger when staff manually raises the barrier.
- **Rationale:** A backend fix could listen for the manual-barrier-open event and automatically close the session with a system-generated exit timestamp, eliminating almost all manual closure work; billing correction logic would also need to be automated. Effort is medium because it touches LPR event integration, session lifecycle, and billing recalculation services.
- **Validation:** Engineering team spikes the event pipeline to confirm manual-barrier signals are reliably emitted and accessible; run a 2-sprint prototype in a staging environment counting session auto-closures vs. missed cases before production rollout.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.2 (range [0.14, 0.26])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** This issue requires privileged backend access to close a session and correct billing; users cannot self-serve the resolution, only submit information. An FAQ might slightly reduce back-and-forth data collection but cannot deflect the ticket itself.
- **Validation:** Deploy an in-app help article for 4 weeks instructing users to include license plate and exit timestamp in their initial report; measure whether info-collection round-trips decrease and whether any tickets are resolved without agent involvement.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~1.4 (range [1, 1.8])
- **Narrow use case:** Auto-close session and correct billing when a confirmed manual-barrier-open event is logged and customer-provided exit timestamp is validated against CCTV/gate log within a tolerance window.
- **Safety constraints:**
  - Automated billing correction must never increase the charge above the manually verified amount.
  - Autonomous action requires cross-referencing gate event log to confirm the vehicle actually exited before closing session.
  - All autonomous closures must be logged for audit and reversible within 24 hours.
  - Cases where the exit timestamp is ambiguous or disputed must be escalated to a human agent.
  - B2B partner accounts with contractual billing SLAs must bypass autonomous resolution and follow manual review.
- **Rationale:** Full autonomous resolution is risky given billing implications and the need to verify the vehicle actually exited; capping at 15% of volume targets only the clearest cases where gate logs unambiguously confirm exit. Hours saved are modest until the underlying product bug is fixed.
- **Validation:** Pilot with 4-week supervised automation on ≤15% of tickets: require a human reviewer to approve each automated closure for the first two weeks, then compare billing accuracy and re-open rates against the manual baseline before expanding scope.

### Risks

- **Compliance concerns:**
  - Incorrect billing corrections could violate B2B partner contracts if not auditable and reversible.
  - Storing and processing license plate data for automated session closure may trigger GDPR or local data-protection obligations depending on jurisdiction.
  - Automated exit timestamps must be defensible if a partner disputes a charge; an audit trail is legally required.
- **Must not automate:**
  - Billing increases or any upward charge adjustment — automation must only reduce or hold charges.
  - Session closure when exit confirmation from gate logs is absent or ambiguous.
  - Cases involving a disputed charge where the customer has already raised a formal billing complaint.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

