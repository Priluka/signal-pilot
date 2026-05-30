---
id: croatian-ticketless-open-session-at-exit__dc548a
name: croatian_ticketless_open_session_at_exit
title: Bmove Ticketless session remains open after user exits parking garage
description: End users report that their Bmove Ticketless parking session stays active in the app after they have physically
  left the garage. In the majority of cases, the exit barrier (rampa) failed to recognize the vehicle's license plate or the
  LPR camera did not register the exit, requiring parking staff to manually lift the barrier. Users then contact support to
  have the session closed and payment processed.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- hr
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|croatia|skidata:c3
project_key: BS
cluster_size: 146
cluster_size_dedup: 146
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.86
median_resolution_minutes: 1121.5
p95_resolution_minutes: 5369.75
cannot_reproduce_rate: 0.0
data_window_start: '2024-01-17'
data_window_end: '2026-01-26'
annual_hours_saved: 1.7
roi:
  baseline_active_hours: 6.9
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.7
  deflection_hours_range:
  - 0.5
  - 0.9
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.7
  agent_assist_hours_range:
  - 1.2
  - 2.2
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 5.9
  product_fix_hours_range:
  - 4.1
  - 6.9
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.9
  autonomous_resolve_hours_range:
  - 0.6
  - 1.2
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-21668
- BS-39829
- BS-36338
- BS-19007
- BS-22802
- BS-27073
- BS-28092
- BS-38915
- BS-36964
- BS-44504
- BS-45084
- BS-26502
- BS-32773
- BS-26655
- BS-29317
- BS-46252
- BS-44092
- BS-44113
canonical_examples:
- BS-21668
- BS-39829
- BS-27073
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
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Automatically trigger session closure and payment processing for sessions where GPS
    or app telemetry confirms the user has left the garage geofence and no active dispute exists.
  autonomous_resolve_safety_constraints:
  - Payment processing must not proceed without confirmed exit evidence (GPS geofence departure or parking facility confirmation).
  - Any session with a disputed charge or user-flagged error must be routed to a human agent.
  - Autonomous closure must not be attempted if SKIDATA back-office API returns an error or ambiguous session state.
  - A human-reviewable audit log of every automated closure must be maintained for a minimum of 90 days.
  - User must receive a notification with a clear dispute/refund path before finalising payment.
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
- croatia-ticketless-open-session-at-exit__f25b63
- croatia-ticketless-rental-car-ghost-charge
- croatian-end-user-wrong-registration-storno-refund
- croatian-invoice-download-request
- croatian-parking-debt-payment-failure
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__56d2b2
- croatian-ticketless-open-session-at-exit__ab83b0
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

# Bmove Ticketless session remains open after user exits parking garage

## What this pattern is

End users report that their Bmove Ticketless parking session stays active in the app after they have physically left the garage. In the majority of cases, the exit barrier (rampa) failed to recognize the vehicle's license plate or the LPR camera did not register the exit, requiring parking staff to manually lift the barrier. Users then contact support to have the session closed and payment processed.

## When this applies

- Exit barrier does not open automatically for the user's vehicle
- LPR camera fails to read the license plate at exit
- Parking staff manually lifts the barrier but does not close the session in the system
- User notices active session in Bmove app hours, days, or weeks after leaving the garage

## Typical resolution flow

1. User attempts to exit garage; barrier does not open
2. Parking staff manually opens barrier and may promise to close session
3. Session remains open in Bmove app
4. User submits feedback via Bmove App reporting the open session
5. Support agent identifies the session ID and requests billing/closure from internal team
6. Session is billed and closed manually by support staff
7. User is notified that session is closed and advised to restart the app if it still shows as active

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Receive user feedback about open session via Bmove App | automated system | Bmove App feedback form | — |
| Identify session ID and request manual billing and closure | support agent | internal support/billing system | 5 min |
| Process payment and close the session manually | back-office agent (e.g. Hrvoje Sirovina, Emanuel Stojanovic, Paulina Mrnarević) | parking management backend (SKIDATA) | 5 min |
| Notify user that session is closed and advise app restart if still showing active | support agent | ticket comment / email | 2 min |

## Vendor dependency

- **Vendor:** SKIDATA

## Evidence

Derived from 146 tickets in cluster `BS:end_user|croatia|skidata:c3`. Direct quotes from 7 representative tickets:

- `BS-21668` _[hr]_: "Poštovani, prije sat vremena ušao sam u garažu Stari grad rijeka, prilikom izlaska rampa mi se nije htjela dignuti te mi je djelatnik otvorio. U aplikaciji vidim da mi je još uvjek aktivan status?????"
- `BS-39829` _[hr]_: "imam aktivnu ticketless sesiju parkinga, iako je vozilo izaslo iz parkinga."
- `BS-27073` _[hr]_: "Rampa mi se pri izlazu nije dizala stoga mi je dežurni operater podignuo ali nije zatvorio sesiju."
- `BS-19007` _[hr]_: "prikazuje mi aktivnu sesiju za Parking rijeka preko 100 dana a navedeno nije moguce."
- `BS-29317` _[hr]_: "Problem je bio u LPR kameri, kontaktirao nas je u međuvremenu telefonski."
- `BS-22802` _[hr]_: "Poštovani, Vaša Bmove Ticketless sesija je zatvorena. Ako je i dalje vidite kao aktivnu, molimo Vas da ponovno pokrenete Bmove aplikaciju."
- `BS-44504` _[hr]_: "aktivan mi je pqrking vec 6 tjedana na parkingu, a ja sam bio 1 sat i izasao sam."

## Cluster statistics

- **Volume:** 146 tickets total (146 unique semantic events after dedup)
- **Frequency:** 2.86 tickets/month (over data window 2024-01-17 → 2026-01-26)
- **Median resolution:** 18.7 hours
- **Languages:** hr
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~6.9 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.7 (range [1.24, 2.249])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** The resolution workflow is highly structured (session lookup → manual billing trigger → notify user), making it well-suited to an agent-assist panel that pre-fetches the session ID, drafts the back-office closure request, and generates the user notification template, reducing manual lookup and drafting time per ticket.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-populates session details and drafts all outbound messages; measure actual agent active-time per ticket versus the 12-minute baseline to confirm the reduction estimate.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~5.9 (range [4.13, 6.9])
- **Root cause:** LPR (license plate recognition) camera at exit fails to register the vehicle, preventing automatic session closure; the SKIDATA barrier system does not fall back to alternative exit detection, leaving sessions open indefinitely.
- **Rationale:** A reliable fix requires either improving LPR accuracy (hardware/firmware, SKIDATA-dependent) or implementing a robust software fallback (e.g. GPS-based exit detection or timed auto-close with payment prompt), both of which carry significant vendor coordination and integration complexity. Full elimination of manual closures is achievable only if the root LPR failure rate is resolved; partial software fallback could eliminate ~85% of cases.
- **Validation:** Scope a technical spike with the SKIDATA integration team to determine whether LPR improvement requires firmware updates or new hardware; prototype GPS-exit fallback in a staging environment and measure false-positive rate before production rollout.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.7 (range [0.483, 0.897])
- **Form:** `in_app_help`
- **Deflection rate:** ~10% (range [7%, 13%])
- **Feasibility:** 0.30
- **Rationale:** The session cannot be closed by the user themselves — it requires back-office action to process payment and close the session, which severely limits true deflection. An in-app help article can reduce inbound contacts only for users who are reassured while waiting, not for those who still need the session closed.
- **Validation:** Deploy an in-app help banner triggered when a session exceeds expected duration (e.g. >30 min after last known exit attempt), explaining the issue and expected resolution time; measure ticket volume change over 4 weeks against the prior baseline.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.9 (range [0.644, 1.19])
- **Narrow use case:** Automatically trigger session closure and payment processing for sessions where GPS or app telemetry confirms the user has left the garage geofence and no active dispute exists.
- **Safety constraints:**
  - Payment processing must not proceed without confirmed exit evidence (GPS geofence departure or parking facility confirmation).
  - Any session with a disputed charge or user-flagged error must be routed to a human agent.
  - Autonomous closure must not be attempted if SKIDATA back-office API returns an error or ambiguous session state.
  - A human-reviewable audit log of every automated closure must be maintained for a minimum of 90 days.
  - User must receive a notification with a clear dispute/refund path before finalising payment.
- **Rationale:** Autonomous resolution is constrained by the financial transaction involved (payment processing) and the need for SKIDATA API reliability; capping at 20% of volume allows automation only for the clearest exit-confirmed cases while keeping humans in the loop for ambiguous or disputed sessions.
- **Validation:** Pilot with 10% of tickets over 6 weeks using GPS-confirmed exits only; acceptance criteria: zero cases of incorrect charges processed autonomously, user dispute rate on auto-closed sessions ≤ baseline dispute rate, and SKIDATA API call success rate ≥ 99%.

### Risks

- **Compliance concerns:**
  - Automated payment processing must comply with applicable PSD2/SCA requirements for card-not-present transactions if payment is triggered without explicit in-session user confirmation.
  - Storing session and payment data for audit purposes must align with GDPR data retention policies.
  - Any auto-close that results in an incorrect charge creates a chargeback risk; dispute resolution procedures must be documented.
- **Must not automate:**
  - Sessions where the user has raised a payment dispute or claims they never entered the garage.
  - Sessions with ambiguous or conflicting exit signals (e.g. GPS still inside geofence but user reports exit).
  - Any case requiring a refund or charge reversal — these must remain human-approved.
- **Vendor dependencies blocking automation:**
  - SKIDATA back-office API must expose a reliable programmatic endpoint for session closure and payment processing; current vendor dependency and unknown wait-days suggest this integration may not yet be fully available or stable.
  - LPR firmware or hardware improvements are entirely within SKIDATA's control and cannot be unilaterally deployed by the product team.
  - Any autonomous or agent-assisted closure workflow requires SKIDATA API uptime SLAs to be established before production use.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

