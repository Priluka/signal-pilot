---
id: croatian-ticketless-open-session-at-exit__e3afed
name: croatian_ticketless_open_session_at_exit
title: Ticketless parking session remains open after user exits garage (Croatia)
description: End users park using the Bmove Ticketless feature and physically exit the garage (typically after a garage attendant
  manually lifts the barrier because the license plate reader failed to recognize their vehicle), but the app session remains
  open and continues counting time. This prevents users from starting new sessions at other garages and causes concern about
  inflated charges. Resolution typically involves support agents manually closing or charging the session on the backend.
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
cluster_id: BS:end_user|croatia|ticketless:c2
project_key: BS
cluster_size: 166
cluster_size_dedup: 166
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 3.25
median_resolution_minutes: 4056.0
p95_resolution_minutes: 45597.25
cannot_reproduce_rate: 0.0
data_window_start: '2023-01-13'
data_window_end: '2026-01-06'
annual_hours_saved: 4.4
roi:
  baseline_active_hours: 17.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 1.1
  deflection_hours_range:
  - 0.8
  - 1.4
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 4.4
  agent_assist_hours_range:
  - 3.2
  - 5.6
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 15.4
  product_fix_hours_range:
  - 11.7
  - 17.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 1.5
  autonomous_resolve_hours_range:
  - 1.1
  - 1.9
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-24405
- BS-45263
- BS-34097
- BS-4909
- BS-9244
- BS-12754
- BS-16791
- BS-40181
- BS-7511
- BS-20819
- BS-47428
- BS-7725
- BS-36530
- BS-36751
- BS-14216
- BS-36755
- BS-35714
- BS-39049
canonical_examples:
- BS-34097
- BS-7725
- BS-35714
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
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-close sessions with zero-charge when session age exceeds a configurable threshold
    (e.g., >6 hours) AND no active billing amount has accrued — purely administrative closure with no financial impact.
  autonomous_resolve_safety_constraints:
  - Autonomous action must never initiate a financial charge; charge step always requires agent or user confirmation.
  - Auto-close only permitted when computed charge amount is exactly €0.00 to avoid billing errors.
  - All autonomous closures must generate an audit log entry with timestamp, session ID, and triggering rule.
  - User must receive an in-app and email notification of the auto-close within 5 minutes.
  - Fallback to agent queue immediately if session data is ambiguous or vehicle/user identity cannot be confirmed.
  - Croatia consumer protection regulations require transparent billing records; auto-close must not overwrite original open-session
    record.
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
- croatian-ticketless-open-session-at-exit__dc548a
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

# Ticketless parking session remains open after user exits garage (Croatia)

## What this pattern is

End users park using the Bmove Ticketless feature and physically exit the garage (typically after a garage attendant manually lifts the barrier because the license plate reader failed to recognize their vehicle), but the app session remains open and continues counting time. This prevents users from starting new sessions at other garages and causes concern about inflated charges. Resolution typically involves support agents manually closing or charging the session on the backend.

## When this applies

- License plate not recognized by the camera system at the exit barrier
- Garage attendant manually lifts the barrier instead of an automated plate read
- Session is not automatically closed/charged because the exit event was not captured by the system
- User exits but the app still shows an active session accumulating time
- User is blocked from entering another garage because an active session is already open

## Typical resolution flow

1. User parks using Bmove Ticketless and enters the garage normally
2. At exit, license plate is not recognized and the barrier does not lift automatically
3. User calls the garage info line or presses the help button on the barrier
4. Garage attendant manually opens the barrier and the user drives out
5. User notices the session is still active in the app (sometimes hours or days later)
6. User submits feedback/support ticket via the Bmove app describing the stuck session
7. Support agent checks the backend system for the open session
8. Agent manually closes the session, attempts manual charge, or creates a debt record for the correct amount
9. Agent notifies user that the session is closed and advises restarting the app if it still appears active

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Check backend system for open/stuck session | support_agent | Bmove backend / Skidati system | 5 min |
| Manually close the session with correct exit time | support_agent | Bmove backend | 10 min |
| Attempt manual charge for the correct parking duration | support_agent | Bmove backend | 10 min |
| Advise user to restart the Bmove app if session still appears active on device | support_agent | email / in-ticket comment | 2 min |

## Evidence

Derived from 166 tickets in cluster `BS:end_user|croatia|ticketless:c2`. Direct quotes from 7 representative tickets:

- `BS-34097` _[hr]_: "Na izlasku mi nije ocitana registracija, nazvao sam operatera, zapisao je registraciju i otvorio mi rampu. Do danas mi se vodi aktivna sesija."
- `BS-7725` _[hr]_: "Zvao u 18:10 službu u garaži koja mi je otvorila rampu, no taj parking mi je još uvijek aktivan u aplikaciji."
- `BS-35714` _[hr]_: "kod izlaza mi nije prepoznalo tablicu. Dosao je gospodin, objasnio sam mu sto se dogodilo i on je digao rampu. Ali ja u aplikaciji i dalje imam aktivnu ticketless sesiju, kojoj tece vrijeme."
- `BS-9244` _[hr]_: "ne dozvoljava mi deaktivaciju ticketless opcije jer pise da je sesija za ZG**** aktivna."
- `BS-24405` _[hr]_: "Pokušat ćemo sesiju ručno naplatiti, a ako ručna naplata ne prođe, tada ćemo morati stvoriti dugovanje u istom iznosu koji ćete moći podmiriti kroz Bmove aplikaciju, a aktivnu sesiju poništiti."
- `BS-39049` _[hr]_: "Dok se iste ne ponište nisam u mogućnosti koristiti ostala parkirališta. Došlo je do problema sa sustavom te je operater otvorio rampu."
- `BS-20819` _[hr]_: "Vaša Bmove Ticketless sesija je zatvorena. Ako je i dalje vidite kao aktivnu, molimo Vas da ponovno pokrenete Bmove aplikaciju."

## Cluster statistics

- **Volume:** 166 tickets total (166 unique semantic events after dedup)
- **Frequency:** 3.25 tickets/month (over data window 2023-01-13 → 2026-01-06)
- **Median resolution:** 2.8 days
- **Languages:** hr
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~17.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~4.4 (range [3.2, 5.6])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.80
- **Rationale:** The resolution workflow is highly repetitive and procedural (check session, close with correct time, charge, advise user), making it well-suited for an agent-assist panel that pre-fills session details and surfaces a one-click close+charge macro, reducing lookup and drafting time. The financial transaction step (charge) requires agent confirmation and cannot be fully automated.
- **Validation:** Run a 3-week shadow-mode pilot surfacing session lookup and close/charge macro suggestions alongside the current workflow; measure average handle time before vs. after for this ticket category with a target of ≥20% AHT reduction.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~15.4 (range [11.7, 17.6])
- **Root cause:** The license-plate-reader failure path at garage exit does not trigger a fallback session-close event; when a garage attendant manually lifts the barrier, no signal is sent to the backend to terminate the ticketless session, leaving it in an indefinitely open state.
- **Rationale:** A robust fix requires adding a fallback exit-detection mechanism (e.g., time-based auto-close, attendant-override API call, or geofence departure trigger) and reconciliation logic to charge correctly, which touches both hardware integration and billing — medium effort. Full resolution of the bug would eliminate nearly all manual-close tickets for this pattern.
- **Validation:** Engineering team should scope via a spike (≤3 days) to map the attendant-barrier-override event path in the LPR integration; prototype fallback session-close in a staging garage and validate zero stuck sessions across 50 simulated manual-lift events before production rollout.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1.1 (range [0.8, 1.4])
- **Form:** `in_app_help`
- **Deflection rate:** ~8% (range [6%, 10%])
- **Feasibility:** 0.25
- **Rationale:** This is a product bug requiring backend intervention; users cannot self-resolve a stuck session, so FAQ or help content can only reassure them and discourage duplicate tickets, not deflect the core request. Deflection potential is therefore very low.
- **Validation:** Deploy an in-app help article explaining the issue for 8 weeks, then compare ticket submission rate per affected session event before and after; target ≥5% reduction in duplicate/follow-up tickets as success signal.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~1.5 (range [1.1, 1.95])
- **Narrow use case:** Auto-close sessions with zero-charge when session age exceeds a configurable threshold (e.g., >6 hours) AND no active billing amount has accrued — purely administrative closure with no financial impact.
- **Safety constraints:**
  - Autonomous action must never initiate a financial charge; charge step always requires agent or user confirmation.
  - Auto-close only permitted when computed charge amount is exactly €0.00 to avoid billing errors.
  - All autonomous closures must generate an audit log entry with timestamp, session ID, and triggering rule.
  - User must receive an in-app and email notification of the auto-close within 5 minutes.
  - Fallback to agent queue immediately if session data is ambiguous or vehicle/user identity cannot be confirmed.
  - Croatia consumer protection regulations require transparent billing records; auto-close must not overwrite original open-session record.
- **Rationale:** Full autonomous resolution is unsafe because most tickets involve a charge transaction requiring human judgment on correct exit time and amount; the narrow zero-charge edge case is rare and only marginally reduces volume. Broader automation should wait until the product fix eliminates the root cause.
- **Validation:** Pilot over 6 weeks on zero-charge stuck sessions only (est. ~15% of cluster); accept criteria: 0 billing disputes attributable to auto-close, 100% audit log coverage, and user satisfaction score on auto-close notification ≥4/5.

### Risks

- **Compliance concerns:**
  - Croatian Consumer Protection Act requires accurate billing records and user notification of any charge or session modification; any automated close-and-charge action must be fully auditable.
  - GDPR: session records contain location and vehicle data; automated processing rules must be documented in the data processing register.
  - Payment Services Directive (PSD2) context: if post-closure charges are initiated programmatically, strong customer authentication or explicit user consent may be required depending on payment method.
- **Must not automate:**
  - Initiating or modifying a financial charge without agent review and confirmation.
  - Determining the correct exit time when it cannot be unambiguously derived from system data (e.g., no geofence or attendant-override timestamp available).
  - Closing sessions where the user disputes the session occurred or alleges the vehicle was not present.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

