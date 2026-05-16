---
id: croatia-ticketless-open-session-at-exit__f25b63
name: croatia_ticketless_open_session_at_exit
title: Ticketless parking session remains open after user has exited the garage
description: End users report that their Bmove Ticketless parking session is still shown as active in the app even though
  they have physically left the garage, often because the exit barrier malfunctioned and a garage attendant manually opened
  the ramp. The stuck session blocks the user from starting new Ticketless sessions at any garage. Resolution requires a support
  agent to manually locate and close (and charge or write off) the session on the backend.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- hr
- en
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|croatia|no_label:c1
project_key: BS
cluster_size: 211
cluster_size_dedup: 181
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 3.55
median_resolution_minutes: 1083.0
p95_resolution_minutes: 9964.89999999999
cannot_reproduce_rate: 0.0
data_window_start: '2023-04-05'
data_window_end: '2026-05-08'
annual_hours_saved: 7.5
roi:
  baseline_active_hours: 24.9
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 2.0
  deflection_hours_range:
  - 1.5
  - 2.5
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 7.5
  agent_assist_hours_range:
  - 5.5
  - 9.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 22.4
  product_fix_hours_range:
  - 17.4
  - 24.9
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 2.5
  autonomous_resolve_hours_range:
  - 1.8
  - 3.2
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-33341
- BS-53127
- BS-29877
- BS-7261
- BS-10123
- BS-22126
- BS-26574
- BS-52580
- BS-49378
- BS-39243
- BS-51230
- BS-52851
- BS-28832
- BS-50115
- BS-47864
- BS-50503
- BS-39770
- BS-24698
canonical_examples:
- BS-33341
- BS-52580
- BS-49378
vendor_dependency:
  vendor_name: SKIDATA
  involves_vendor: true
  typical_wait_days: 1
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-close sessions where payment succeeds on first automated charge attempt and no
    disputed amount exists
  autonomous_resolve_safety_constraints:
  - Autonomous action must only trigger when automated payment succeeds in full; any failed or partial payment must route
    to a human agent
  - Session duration must be within a plausible exit-delay window (e.g., opened >30 min and <24 hours ago) to avoid closing
    legitimately open sessions
  - A full audit log of every autonomous close action must be retained and reviewable
  - User must receive an immediate in-app notification of the closure with a dispute link
  - SKIDATA API must confirm session closure before the app unblocks new Ticketless sessions
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__7950cd
- bmove-app-feedback-mixed-issues__d6cf0c
- bmove-app-operational-issues-austria
- croatia-bmove-app-feedback-miscellaneous
- croatia-parking-fine-dispute
- croatia-parking-fine-dispute-and-payment
- croatia-parking-fine-payment-failure
- croatia-parking-payment-failure__e3b934
- croatia-parking-payment-failure__ffdf4e
- croatia-parking-ticket-storno-user-error
- croatia-ticketless-best-in-parking-knowledge-gap
- croatia-ticketless-open-session-at-exit__a7c97e
- croatia-ticketless-rental-car-ghost-charge
- croatian-end-user-wrong-registration-storno-refund
- croatian-invoice-download-request
- croatian-parking-debt-payment-failure
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__56d2b2
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

# Ticketless parking session remains open after user has exited the garage

## What this pattern is

End users report that their Bmove Ticketless parking session is still shown as active in the app even though they have physically left the garage, often because the exit barrier malfunctioned and a garage attendant manually opened the ramp. The stuck session blocks the user from starting new Ticketless sessions at any garage. Resolution requires a support agent to manually locate and close (and charge or write off) the session on the backend.

## When this applies

- Exit barrier fails to open automatically, garage attendant opens it manually
- Ticketless session is not closed automatically when the vehicle licence plate is not recognised on exit
- Payment attempt at exit fails, leaving session open
- User manually disables Ticketless option for a location but existing session is not terminated
- System/SKIDATA server issue prevents normal session closure

## Typical resolution flow

1. User exits garage (often with attendant-assisted barrier opening) and notices the session is still active in the Bmove app
2. User submits feedback via Bmove App reporting the stuck open session
3. Support agent identifies the open session ID(s) from user's registration plate or account
4. Agent routes the closure request internally (e.g. tags colleague Zelimir Mateskovic or similar)
5. Backend agent attempts automatic payment/closure via SKIDATA or internal tools
6. If payment succeeds, session is closed and user is notified to restart the app
7. If payment fails, session is closed at €0.00 and a debt is opened in the user's account for manual payment
8. User is instructed to restart the Bmove app to see the updated session status

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| User reports stuck open session via in-app feedback | end_user | Bmove App | 5 min |
| Support agent identifies session ID(s) from user's vehicle registration or account | support_agent | Bmove back-office / SKIDATA | 10 min |
| Attempt to charge and close the session automatically | support_agent | SKIDATA / internal tools | 5 min |
| If payment fails, close session at €0.00 and open outstanding debt in user account | support_agent | Bmove back-office tools | 10 min |
| Notify user that session is closed and ask them to restart the app | support_agent | Jira / email | 5 min |

## Vendor dependency

- **Vendor:** SKIDATA
- **Typical wait:** 1 day(s)

## Evidence

Derived from 211 tickets in cluster `BS:end_user|croatia|no_label:c1`. Direct quotes from 8 representative tickets:

- `BS-33341` _[hr]_: "Zašto mi piše da je aktivna sesija a izišao sam iz garaže jučer"
- `BS-52580` _[hr]_: "Imam aktivnu sesiju 9 Dana a na parkingu sam bio koliko se sjecam ne vise od 2h"
- `BS-49378` _[hr]_: "sesija 202512181250397300218692 nije mogla biti naplaćena automatski i svi pokušaji naplate prema Vašoj kartici su bili neuspješni. Sesiju smo zatvorili i otvorili smo dug u iznosu sesije (1.60€)."
- `BS-26574` _[hr]_: "na izlasku mi nije htjelo naplatiti, pa je djelatnik garaže zabilježio registraciju i otvorio rampu. sesija je još uvijek aktivna."
- `BS-39243` _[hr]_: "Ponovno se javljam vezano za ticketless sesiju koja je u tijeku, a auto je odavno izasao iz garaze! Ulazak u garazu u Petrinjskoj je bio u 13:44, 02.07.2025., a izlazak u 13:50 - rampu je otvorio radn"
- `BS-49378` _[hr]_: "Jos od prosinca mi stoji aktivna sesija a ocigledno vise nisam u garazi. Taj dan se rampa nije podizala pa ju je djelatnik aktivirao i normalno sam izisla."
- `BS-28832` _[hr]_: "5 dana mi stoji otvorena sesija nakon 3 poslana upita. Molim zatvaranje iste."
- `BS-53127` _[hr]_: "Vaše Bmove Ticketless sesije su zatvorene. Ako ih dalje vidite kao aktivne, molimo Vas da ponovno pokrenete Bmove aplikaciju."

## Cluster statistics

- **Volume:** 211 tickets total (181 unique semantic events after dedup)
- **Frequency:** 3.55 tickets/month (over data window 2023-04-05 → 2026-05-08)
- **Median resolution:** 18.1 hours
- **Languages:** hr, en
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~24.9 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~7.5 (range [5.5, 9.5])
- **Time reduction per ticket:** ~30% (range [22%, 38%])
- **Feasibility:** 0.80
- **Rationale:** Steps 2 and 3 (session lookup by VRN/account and auto-charge attempt) are highly structured and repetitive, making them strong candidates for a guided agent-assist tool that pre-fetches the session ID and surfaces a one-click close action. Steps 4 and 5 still require agent judgment on write-off versus debt creation, limiting overall time savings to roughly 30%.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool auto-populates session ID and charge-attempt results alongside each ticket; compare actual handle time for assisted versus unassisted tickets using a holdout group of 20 tickets.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~22.4 (range [17.4, 24.9])
- **Root cause:** When the exit barrier malfunctions and a garage attendant manually opens the ramp, no exit event is transmitted to SKIDATA or the Bmove backend, leaving the parking session in an open state indefinitely. A robust fix requires either (a) a fallback exit-detection signal (e.g., LPR camera confirmation or a time-out heuristic) or (b) an SKIDATA integration that surfaces attendant-override events to close the session automatically.
- **Rationale:** A product fix targeting automatic session closure on barrier-override events could eliminate the majority of this ticket cluster; however, the solution depends on SKIDATA exposing attendant-override events via their API, which introduces vendor uncertainty and scope risk. Hours eliminated are capped at the measured baseline (24.9 h/yr).
- **Validation:** Engineering team should first audit the SKIDATA API sandbox for attendant-event webhooks; if unavailable, re-estimate effort for a LPR-fallback approach before committing to sprint budget.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~2 (range [1.5, 2.5])
- **Form:** `in_app_help`
- **Deflection rate:** ~8% (range [6%, 10%])
- **Feasibility:** 0.25
- **Rationale:** The stuck session actively blocks new Ticketless use, so users are highly motivated to contact support rather than self-serve; in-app guidance explaining the issue exists but cannot resolve it without backend access, meaning deflection potential is low. An informational help article may reduce repeat contacts or misdirected tickets but cannot substitute for agent action.
- **Validation:** Deploy a 4-week in-app help article triggered when a session has been open >4 hours with no movement event; measure ticket volume reduction versus an equivalent prior period as the control.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~2.5 (range [1.75, 3.2])
- **Narrow use case:** Auto-close sessions where payment succeeds on first automated charge attempt and no disputed amount exists
- **Safety constraints:**
  - Autonomous action must only trigger when automated payment succeeds in full; any failed or partial payment must route to a human agent
  - Session duration must be within a plausible exit-delay window (e.g., opened >30 min and <24 hours ago) to avoid closing legitimately open sessions
  - A full audit log of every autonomous close action must be retained and reviewable
  - User must receive an immediate in-app notification of the closure with a dispute link
  - SKIDATA API must confirm session closure before the app unblocks new Ticketless sessions
- **Rationale:** Only the subset of tickets where auto-charge succeeds on the first attempt (estimated ~30–40% historically) is safely automatable, and the safety cap limits this to 20% of annual volume; write-off and debt-creation cases involve financial judgment that must remain with a human agent. Vendor dependency on SKIDATA for session-close confirmation adds additional fragility.
- **Validation:** Pilot over 8 weeks with a maximum of 10 autonomous closures per week; acceptance criteria: zero incorrect closures on still-active sessions, zero cases where the app fails to unblock after autonomous close, and user dispute rate below 5% of autonomous actions.

### Risks

- **Compliance concerns:**
  - Writing off a parking fee at €0.00 without user consent may require documented justification under local consumer-finance or e-money regulations
  - Storing outstanding debt in a user account must comply with applicable consumer-credit notification requirements (e.g., written notice within a defined period)
  - Any autonomous charge attempt must comply with the payment mandate scope authorised by the user at session start
- **Must not automate:**
  - Write-off decisions (closing at €0.00) where the correct charge amount is ambiguous — these require human financial judgment
  - Cases where session duration exceeds 24 hours, as these may represent a genuinely ongoing stay or a fraud signal requiring investigation
  - Debt creation and recovery actions, which carry legal notification obligations
- **Vendor dependencies blocking automation:**
  - SKIDATA must expose attendant-override/manual-barrier events via API for any product-fix or autonomous-close solution to be reliable
  - SKIDATA's typical 1-day response time for backend interventions means any automation that bypasses their API carries risk of state mismatch between Bmove and SKIDATA systems
  - Session-close confirmation from SKIDATA is required before the Bmove app can safely unblock new Ticketless sessions; absence of this confirmation loop is a blocking dependency for autonomous resolve

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

