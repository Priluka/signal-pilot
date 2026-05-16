---
id: open-session-at-exit-austria
name: open_session_at_exit_austria
title: Parking session remains active in Bmove app after user has exited the garage
description: End users report that their parking session in the Bmove app continues to show as active even after they have
  physically exited the garage, typically because the license plate recognition system at the exit barrier failed to register
  the departure. Support resolves these by manually closing the open session with the actual exit timestamp, then advising
  the user to restart the app to refresh the display.
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
cluster_id: BS:end_user|austria|open_session:c1
project_key: BS
cluster_size: 148
cluster_size_dedup: 143
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.8
median_resolution_minutes: 3923.0
p95_resolution_minutes: 79258.85000000022
cannot_reproduce_rate: 0.0
data_window_start: '2024-04-04'
data_window_end: '2025-12-16'
annual_hours_saved: 2.0
roi:
  baseline_active_hours: 6.7
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.8
  deflection_hours_range:
  - 0.6
  - 1.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 2.0
  agent_assist_hours_range:
  - 1.4
  - 2.6
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 5.7
  product_fix_hours_range:
  - 4.0
  - 6.7
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 1.3
  autonomous_resolve_hours_range:
  - 0.9
  - 1.7
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-35229
- BS-37378
- BS-20111
- BS-24646
- BS-33067
- BS-36080
- BS-38818
- BS-43177
- BS-25183
- BS-42685
- BS-38475
- BS-33800
- BS-33361
- BS-41519
- BS-43298
- BS-40495
- BS-39357
- BS-32319
canonical_examples:
- BS-20111
- BS-36080
- BS-38818
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-close sessions where exit timestamp can be inferred unambiguously from a corroborating
    signal (e.g. barrier-open event logged within a short window) and elapsed session time is within a normal range (e.g.
    <24 hours).
  autonomous_resolve_safety_constraints:
  - Only auto-close sessions where a corroborating exit signal (barrier event or loop detector) is present and timestamped
  - Never auto-close sessions with elapsed time >24 hours without human review — potential billing disputes
  - Always send the user a post-closure notification with the applied exit timestamp and an explicit dispute/appeal link
  - Require idempotency check to prevent double-closure if LPR later also fires
  - Maintain full audit log of autonomous closures for billing compliance
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-incorrect-charge-refund
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__7950cd
- bmove-app-feedback-mixed-issues__d6cf0c
- bmove-app-operational-issues-austria
- bmove-not-recognized-daily-worklog
- croatia-parking-payment-failure__e3b934
- croatia-ticketless-open-session-at-exit__a7c97e
- croatia-ticketless-open-session-at-exit__f25b63
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__56d2b2
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- email-address-change-not-possible
- email-address-change-not-supported
- expired-card-deletion-ticketless-link
- microsoft365-quarantine-notification-auto-tickets
- missing-parking-invoice-receipt
- missing-parking-receipt-email
- missing-parking-receipt-request
- open-session-at-exit-payment-failure
- outstanding-payment-credit-card-failure
- pkc-vehicle-registration-automated-tickets
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

# Parking session remains active in Bmove app after user has exited the garage

## What this pattern is

End users report that their parking session in the Bmove app continues to show as active even after they have physically exited the garage, typically because the license plate recognition system at the exit barrier failed to register the departure. Support resolves these by manually closing the open session with the actual exit timestamp, then advising the user to restart the app to refresh the display.

## When this applies

- License plate recognition at the exit barrier fails to capture the vehicle's departure
- Barrier opens manually (by staff or override) without registering the exit in the system
- Ticketless validity date was set incorrectly by the user, preventing automatic exit processing
- System/app does not automatically close the session after the vehicle leaves

## Typical resolution flow

1. User exits garage; barrier opens but session is not closed in app
2. User notices active session in Bmove app after leaving
3. User contacts support via in-app feedback or email requesting session closure
4. Support agent identifies the open session and the actual exit time
5. Support agent manually closes the session with the correct exit timestamp
6. Support notifies user that the session has been closed and advises app restart
7. User restarts app to confirm session is resolved

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Identify open session using user ID, license plate, or ticket number | support_agent | Bmove backend/admin system | 5 min |
| Manually close the parking session with the actual exit time | support_agent | Bmove backend/admin system | 5 min |
| Notify user that session has been closed and instruct them to restart the app | support_agent | Jira/email reply | 2 min |

## Evidence

Derived from 148 tickets in cluster `BS:end_user|austria|open_session:c1`. Direct quotes from 6 representative tickets:

- `BS-20111` _[de]_: "Ich habe vor einer Viertelstunde die Parkgarage verlassen aber der Zähler in der App läuft weiter und der Parkvorgang wurde nicht abgeschlossen."
- `BS-36080` _[de]_: "der offene Parkvorgang wurde von uns mit der tatsächlichen Ausfahrtzeit aus der Garage abgeschlossen. Sollten Sie im Bmove immer noch eine aktive Sitzung sehen, starten Sie bitte die App neu."
- `BS-38818` _[de]_: "Ich habe gestern, 21. 6., vor 22 Uhr die Garage verlassen, der Schranken öffnete sich nach der Kennzeichenerkennung. Wieso wird mein Garagenaufenthalt noch immer als aktiv angezeigt?"
- `BS-33361` _[de]_: "jetzt sehe ich in die App dass mein parkvorgang weiter läuft nach 5 Tage, obwohl ich nur drei Stunden geparkt habe"
- `BS-36080` _[de]_: "Sie läuft seit 2 Tagen"
- `BS-40495` _[de]_: "Da sich der Schranken nicht automatisch geöffnet hat, wurde mir von einem Mitarbeiter die Ausfahrt ermöglicht, aber er konnte das Kennzeichen L**** nicht im System finden und mich ausloggen."

## Cluster statistics

- **Volume:** 148 tickets total (143 unique semantic events after dedup)
- **Frequency:** 2.8 tickets/month (over data window 2024-04-04 → 2025-12-16)
- **Median resolution:** 2.7 days
- **Languages:** de
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~6.7 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~2 (range [1.4, 2.6])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.80
- **Rationale:** The resolution workflow is highly templated — session lookup, manual close, user notification — making it well-suited for an agent-assist panel that pre-fetches the open session record and pre-drafts the closure confirmation message, reducing active work primarily on steps 1 and 3. The 30% time reduction reflects that step 2 (manual close action in the admin tool) still requires human confirmation.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-fetches session data and drafts the notification; compare average handle time against a control group of agents without the tool, targeting ≥20% reduction to validate.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~5.7 (range [4, 6.7])
- **Root cause:** License plate recognition (LPR) at the exit barrier intermittently fails to register departures, leaving parking sessions in an open state in the Bmove backend; no fallback mechanism exists to auto-close sessions when physical exit is detected by other means (e.g. barrier lift event, loop detector, timeout heuristic).
- **Rationale:** A reliable fix would require either improving LPR recognition accuracy or adding a fallback auto-close trigger (e.g. corroborating the barrier-open signal with a timeout) — medium engineering scope involving hardware integration and edge-case handling. If the fix reduces miss-rate by ~85%, the majority of support tickets in this cluster would be eliminated; the ceiling is capped at baseline 6.7 hours/year.
- **Validation:** Engineering team should instrument LPR miss-rate on a test exit lane for 4 weeks pre- and post-fix, measuring percentage of sessions that still require manual closure as the acceptance criterion (target <5% of exits).

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.8 (range [0.56, 1.04])
- **Form:** `in_app_help`
- **Deflection rate:** ~12% (range [8%, 16%])
- **Feasibility:** 0.35
- **Rationale:** Because the root cause is a backend LPR failure — not user error — most users will still need manual session closure even after reading help content; self-service deflection potential is therefore low, limited to users who simply want confirmation that the session will be closed. An in-app help article explaining the issue and providing a self-service 'report stuck session' form could capture a small fraction before they open a ticket.
- **Validation:** Deploy a 4-week in-app help banner triggered when session duration exceeds typical max (e.g. >6 hours after entry), measuring ratio of form submissions that avoid ticket creation versus those that still escalate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~1.3 (range [0.91, 1.69])
- **Narrow use case:** Auto-close sessions where exit timestamp can be inferred unambiguously from a corroborating signal (e.g. barrier-open event logged within a short window) and elapsed session time is within a normal range (e.g. <24 hours).
- **Safety constraints:**
  - Only auto-close sessions where a corroborating exit signal (barrier event or loop detector) is present and timestamped
  - Never auto-close sessions with elapsed time >24 hours without human review — potential billing disputes
  - Always send the user a post-closure notification with the applied exit timestamp and an explicit dispute/appeal link
  - Require idempotency check to prevent double-closure if LPR later also fires
  - Maintain full audit log of autonomous closures for billing compliance
- **Rationale:** Autonomous resolution is feasible only for the narrow subset of tickets where a reliable exit signal exists to anchor the correct timestamp; without that signal, automated closure risks applying a wrong exit time and triggering billing errors or disputes. Limiting scope to 25% of volume reflects uncertainty about how often a corroborating signal is actually available.
- **Validation:** Run a 4-week supervised pilot: bot identifies candidate tickets and proposes a closure action but requires one-click agent approval; measure agreement rate between bot-proposed timestamp and agent-confirmed timestamp — target ≥95% agreement before enabling fully autonomous closure.

### Risks

- **Compliance concerns:**
  - Incorrect exit timestamps could result in overbilling or underbilling users, creating financial liability and potential regulatory issues in jurisdictions with strict consumer billing rules
  - Audit trails for session modifications must be retained to support billing disputes or chargebacks
- **Must not automate:**
  - Session closures where the inferred exit timestamp is ambiguous or unsupported by a corroborating hardware signal
  - Cases where the session duration exceeds 24 hours — these warrant human review for potential fraud, vehicle abandonment, or system anomalies
  - Any closure that would result in a refund or credit without explicit human approval

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

