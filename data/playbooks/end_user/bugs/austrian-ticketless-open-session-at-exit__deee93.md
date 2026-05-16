---
id: austrian-ticketless-open-session-at-exit__deee93
name: austrian_ticketless_open_session_at_exit
title: Bmove Ticketless Parking Session Remains Open After Physical Exit
description: End users in Austria (and occasionally Germany) contact support because their Bmove app continues to show an
  active parking session even after they have physically left the garage. The session fails to close automatically, typically
  because the exit camera/license-plate recognition did not trigger correctly or the barrier was opened manually by staff.
  This blocks future re-entry via ticketless parking and causes user concern about ongoing charges.
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
cluster_id: BS:end_user|austria|no_label:c7
project_key: BS
cluster_size: 52
cluster_size_dedup: 49
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.96
median_resolution_minutes: 334.5
p95_resolution_minutes: 10991.399999999985
cannot_reproduce_rate: 0.0
data_window_start: '2025-03-19'
data_window_end: '2026-04-29'
annual_hours_saved: 0.6
roi:
  baseline_active_hours: 2.5
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.2
  deflection_hours_range:
  - 0.2
  - 0.3
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.6
  agent_assist_hours_range:
  - 0.4
  - 0.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.3
  product_fix_hours_range:
  - 1.6
  - 2.5
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.4
  autonomous_resolve_hours_range:
  - 0.3
  - 0.5
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-50520
- BS-39390
- BS-38906
- BS-34997
- BS-38164
- BS-41662
- BS-42864
- BS-40282
- BS-41689
- BS-39322
- BS-52757
- BS-49338
- BS-38066
- BS-51626
- BS-39690
- BS-41721
- BS-42738
- BS-41627
canonical_examples:
- BS-50520
- BS-34997
- BS-40282
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
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-close sessions where exit timestamp can be unambiguously inferred from gate-log
    or camera event data and no billing dispute is present
  autonomous_resolve_safety_constraints:
  - Only close sessions where an exit event (even a failed LPR event) is recorded in gate logs within a configurable window,
    providing an auditable timestamp
  - Never auto-close if the session has already accumulated charges above a configurable threshold without human review
  - Always send a user notification with a clear audit trail and an escalation path if the user disputes the closure
  - Maintain a full log of every automated closure action for at least 90 days to support billing inquiries
  - Restrict automation to garages with confirmed gate-log API access; exclude garages relying solely on manual barrier operation
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-incorrect-charge-refund
- austrian-ticketless-open-session-at-exit__06e3d4
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

# Bmove Ticketless Parking Session Remains Open After Physical Exit

## What this pattern is

End users in Austria (and occasionally Germany) contact support because their Bmove app continues to show an active parking session even after they have physically left the garage. The session fails to close automatically, typically because the exit camera/license-plate recognition did not trigger correctly or the barrier was opened manually by staff. This blocks future re-entry via ticketless parking and causes user concern about ongoing charges.

## When this applies

- Exit camera or license-plate recognition fails to detect the vehicle at the barrier
- Barrier is opened manually by garage staff or via service hotline instead of automatic recognition
- Session is not automatically closed after the vehicle has left the premises
- User attempts a new entry and is blocked with 'vehicle already present' error
- User notices app showing session active for hours or days after departure

## Typical resolution flow

1. User parks using Bmove ticketless (license-plate recognition) and exits the garage
2. Exit barrier opens (automatically or manually via intercom/hotline) but session is not closed in system
3. User later notices the app still shows an active session
4. User contacts Bmove support via email/ticket, providing license plate, ticket number, garage name, and approximate exit time
5. Support agent looks up the session in the backend system
6. Agent manually closes the session with the correct exit timestamp
7. Agent instructs user to restart the Bmove app to refresh the displayed status

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Receive and triage user report of open session, extract license plate, ticket number, garage, and exit time | support_agent | Bmove backend / ticketing system | 5 min |
| Manually close the open parking session with the correct exit timestamp | support_agent | Bmove backend | 5 min |
| Notify user that session has been closed and advise app restart | support_agent | Support ticketing system | 3 min |

## Evidence

Derived from 52 tickets in cluster `BS:end_user|austria|no_label:c7`. Direct quotes from 6 representative tickets:

- `BS-50520` _[de]_: "in meiner Bmove App wird angezeigt, dass ich eine aktive Parksession in der Kärntnerstraße Tiefgarage habe, die seit dem 15. Jänner läuft. Allerdings habe ich die Garage an diesem Tag bereits nach etw"
- `BS-34997` _[de]_: "der offene Parkvorgang wurde von uns mit der Ausfahrtszeit manuell geschlossen. Sollten Sie im Bmove immer noch eine aktive Sitzung sehen, starten Sie bitte die App neu. Jetzt können Sie wieder proble"
- `BS-40282` _[de]_: "Als ich heute wieder reinfahren wollte, öffnete der Schranken nicht und ich sah, dass der Parkvorgang vom 18.7 in der App noch als aktiv und offen gekennzeichnet ist."
- `BS-42864` _[de]_: "Trotz mehrerer Versuche wurde die Schranke nicht automatisch über die Kennzeichenerkennung geöffnet. Ich musste daher die Service-Hotline kontaktieren (über die Säule), woraufhin die Schranke manuell "
- `BS-41689` _[de]_: "ebenso steht in der App das ich eine aktive Sitzung seit 8.7. habe was natürlich nicht stimmt."
- `BS-51626` _[de]_: "ich hab gestern im Prater geparkt. Da beim Ausfahren der Schranken nicht aufging, läutete ich, gab mein Kennzeichen W85DNT durch und der Schranken wurde mir geöffnet. Allerdings läuft immer noch die S"

## Cluster statistics

- **Volume:** 52 tickets total (49 unique semantic events after dedup)
- **Frequency:** 0.96 tickets/month (over data window 2025-03-19 → 2026-04-29)
- **Median resolution:** 5.6 hours
- **Languages:** de
- **Country focus:** at, de

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.5 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.6 (range [0.44, 0.806])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.80
- **Rationale:** The resolution workflow is highly templated (extract plate/ticket/garage/exit time → close session → notify user), making it well-suited for an assist tool that pre-fills the close-session form from ticket text and drafts the user-notification reply; this targets the triage and notification steps (~8 of 13 minutes) rather than the backend action itself. Time savings are moderate because active minutes per ticket are already low.
- **Validation:** Run the assist tool in shadow mode for 3 weeks on incoming tickets of this type, measuring auto-extraction accuracy for license plate and exit time, then calculate actual agent time delta via before/after handle-time comparison.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~2.3 (range [1.61, 2.5])
- **Root cause:** Exit camera / license-plate recognition (LPR) intermittently fails to trigger session closure, and manual barrier overrides by garage staff do not propagate a close event to the Bmove backend, leaving sessions orphaned.
- **Rationale:** A reliable fix requires both improving LPR trigger reliability and introducing a fallback mechanism (e.g., staff-override event webhook or time-based auto-close with audit trail) to catch sessions that the camera misses; the integration touches parking-hardware interfaces and backend session state, placing effort in the medium tier. If successful, the fix would eliminate the vast majority of this cluster's tickets, with residual volume from edge cases.
- **Validation:** Engineering should instrument LPR miss-rate and staff-override frequency in production logs for Austria/Germany garages over 4 weeks to size the two sub-problems independently before committing sprint estimates.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.2 (range [0.175, 0.32])
- **Form:** `in_app_help`
- **Deflection rate:** ~10% (range [7%, 13%])
- **Feasibility:** 0.35
- **Rationale:** This issue requires an active backend action (closing the session) that the user cannot perform themselves, so self-service deflection potential is low; however, in-app guidance explaining the manual-close process and setting expectations on charges could reduce anxious follow-up contacts slightly. The root cause is a system bug, not a knowledge gap, so FAQ deflection is structurally limited.
- **Validation:** Deploy an in-app help article triggered when the app detects a session open >2 hours post expected exit; measure contact rate reduction over a 6-week window against the prior baseline.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.4 (range [0.27, 0.494])
- **Narrow use case:** Auto-close sessions where exit timestamp can be unambiguously inferred from gate-log or camera event data and no billing dispute is present
- **Safety constraints:**
  - Only close sessions where an exit event (even a failed LPR event) is recorded in gate logs within a configurable window, providing an auditable timestamp
  - Never auto-close if the session has already accumulated charges above a configurable threshold without human review
  - Always send a user notification with a clear audit trail and an escalation path if the user disputes the closure
  - Maintain a full log of every automated closure action for at least 90 days to support billing inquiries
  - Restrict automation to garages with confirmed gate-log API access; exclude garages relying solely on manual barrier operation
- **Rationale:** Full autonomous resolution is constrained by the need for a trustworthy exit timestamp and the billing sensitivity of incorrectly closing an active session; limiting automation to cases where gate-log data is available caps safe volume at ~20% of tickets and keeps financial risk manageable. Even within this scope, hours saved are modest given the small annual frequency.
- **Validation:** Pilot with a single high-volume Austrian garage that has gate-log API access; require human review of every automated closure for the first 4 weeks, then audit for timestamp accuracy and user dispute rate before expanding scope.

### Risks

- **Compliance concerns:**
  - GDPR: license plate data processed during session lookup and closure must be handled under an appropriate legal basis and minimized in logs; Austrian and German data-protection requirements apply.
  - Billing accuracy: incorrectly closing a genuinely active session or assigning a wrong exit timestamp could constitute a billing error, requiring a clear correction and refund process.
  - Consumer protection: Austrian and German consumer-protection law may require explicit user acknowledgment when session closure affects a financial charge.
- **Must not automate:**
  - Session closures where the exit time is ambiguous or not corroborated by any gate or camera event
  - Cases where the user reports a billing dispute or unexpected charge amount, which require human judgment
  - Closures in garages that rely entirely on manual staff barrier operation with no digital event log

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

