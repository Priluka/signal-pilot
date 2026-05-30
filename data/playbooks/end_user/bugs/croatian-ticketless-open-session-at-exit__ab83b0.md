---
id: croatian-ticketless-open-session-at-exit__ab83b0
name: croatian_ticketless_open_session_at_exit
title: Croatian Bmove Ticketless parking session remains open after vehicle exit
description: End users in Croatia report that their Bmove Ticketless parking session stays active after they have physically
  exited the garage, typically because the exit barrier failed to read the licence plate or trigger automatic session closure.
  In many cases a garage attendant manually raised the barrier, but the system did not register the exit. Support resolves
  the issue by manually closing the session on the backend and instructing the user to restart the app if it still appears
  active.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:end_user|croatia|ticketless:c1
project_key: BS
cluster_size: 27
cluster_size_dedup: 27
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.53
median_resolution_minutes: 1550.0
p95_resolution_minutes: 17967.499999999993
cannot_reproduce_rate: 0.0
data_window_start: '2024-02-01'
data_window_end: '2026-01-14'
annual_hours_saved: 0.2
roi:
  baseline_active_hours: 0.7
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.1
  deflection_hours_range:
  - 0.1
  - 0.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.2
  agent_assist_hours_range:
  - 0.1
  - 0.2
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.7
  product_fix_hours_range:
  - 0.5
  - 0.7
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.1
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-35222
- BS-23706
- BS-35436
- BS-18131
- BS-22011
- BS-25626
- BS-27793
- BS-20737
- BS-35727
- BS-43638
- BS-32692
- BS-28891
- BS-43302
- BS-32321
- BS-25679
- BS-28022
- BS-22977
- BS-31957
canonical_examples:
- BS-35436
- BS-20737
- BS-25626
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
  autonomous_resolve_narrow_use_case: Auto-close an open Ticketless session when backend logs confirm a vehicle exit event
    was recorded but session closure failed, and no payment discrepancy is detected.
  autonomous_resolve_safety_constraints:
  - Only trigger auto-close when an exit event is positively confirmed in backend logs — do not act on user assertion alone.
  - Require zero outstanding payment balance before autonomous closure to avoid financial disputes.
  - Log all autonomous closures for audit and flag any reversal within 24 hours for human review.
  - Exclude cases where the attendant manually raised the barrier without any system exit record, as these may indicate payment
    bypass.
related_playbooks:
- austrian-ticketless-open-session-at-exit__06e3d4
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__d6cf0c
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
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- open-session-at-exit-austria
- open-session-at-exit-payment-failure
- ticketless-open-session-at-exit__960f17
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

# Croatian Bmove Ticketless parking session remains open after vehicle exit

## What this pattern is

End users in Croatia report that their Bmove Ticketless parking session stays active after they have physically exited the garage, typically because the exit barrier failed to read the licence plate or trigger automatic session closure. In many cases a garage attendant manually raised the barrier, but the system did not register the exit. Support resolves the issue by manually closing the session on the backend and instructing the user to restart the app if it still appears active.

## When this applies

- Exit barrier camera fails to read the vehicle's licence plate
- Garage attendant manually opens barrier without triggering session closure in the system
- Payment/billing failure at exit prevents normal session termination
- User exits garage but Bmove app continues showing an active session

## Typical resolution flow

1. User enters garage using Bmove Ticketless (barrier opens normally)
2. On exit, barrier does not open automatically (camera read failure, app/billing issue)
3. Garage attendant manually raises the barrier to let the vehicle out
4. Session remains open in the Bmove app and continues accruing time/cost
5. User contacts support via email/ticket providing licence plate, garage name, and exit time
6. Support agent manually closes the Ticketless session on the backend
7. Agent replies confirming closure and instructs user to restart the app if session still appears active

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Manually close the open Ticketless parking session in the backend system | support_agent | Bmove backend/admin panel | 5 min |
| Reply to user confirming session closure and advising app restart if still shown as active | support_agent | ticketing system (email) | 2 min |

## Evidence

Derived from 27 tickets in cluster `BS:end_user|croatia|ticketless:c1`. Direct quotes from 6 representative tickets:

- `BS-35436` _[hr]_: "pri izlasku mi nije htjelo otvoriti rampu pa mije gospodja kojatamo radi otvorila. U aplikaciji mi pokazuje da sam jos uvijek parkirana tamo."
- `BS-20737` _[hr]_: "Na odlasku nisam mogao izaci zbog problema sa aplikacijom te mi je Vas djelatnik omogucio izlaz medjutim vidim da mi u aplikaciji jos uvijek prokazuje da mi je u garazi aktivno parkiranje."
- `BS-25626` _[hr]_: "Aparat mi nije htio naplatiti parking pa mi je operater otvorio rampu na daljinu. Tražio je samo moj broj registracije. Ri9953S."
- `BS-43302` _[hr]_: "Parking je danas aktivan u garaži stari grad rijeka za ri77777fl, ali nije mogao izaci. Digli su mu rampu a sesija je jos aktivna."
- `BS-35222` _[hr]_: "Vaša Bmove Ticketless sesija je zatvorena. Ako je i dalje vidite kao aktivnu, molimo Vas da ponovno pokrenete Bmove aplikaciju."
- `BS-31957` _[hr]_: "Krenuo sam s parkirališta u 08:00, ali aktivna sesija nije završila. Možete li pomoći zatvoriti ovu sesiju? Nisam mogao ponovno ući na ovo parkiralište jer me sustav automatski odbio pustiti preko apl"

## Cluster statistics

- **Volume:** 27 tickets total (27 unique semantic events after dedup)
- **Frequency:** 0.53 tickets/month (over data window 2024-02-01 → 2026-01-14)
- **Median resolution:** 1.1 days
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~0.7 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.2 (range [0.13, 0.23])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** The resolution is highly templated (look up session, close it, send confirmation), so an assist tool that auto-drafts the closure-confirmation reply and surfaces the backend deep-link for the session could meaningfully reduce active handle time. Savings are limited by the small annual volume.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool drafts the reply and pre-populates the session lookup; measure agent acceptance rate and actual handle-time reduction via before/after time-tracking.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~0.7 (range [0.5, 0.7])
- **Root cause:** The exit barrier in Croatian Bmove garages fails to reliably trigger licence-plate recognition or automatic session closure when a vehicle exits, leaving the parking session open in the backend; manual barrier raises by attendants are not captured by the system.
- **Rationale:** A reliable fix requires improving licence-plate recognition reliability and/or adding a fallback exit-event trigger (e.g. barrier-open signal integration), which likely involves coordination with garage hardware and the Bmove platform — a non-trivial engineering scope. If fully fixed, virtually all tickets in this cluster would be eliminated.
- **Validation:** Engineering team should spike on the exit-event API contract with the Bmove hardware partner, estimate integration complexity, and run a 2-garage pilot to measure session-closure success rate before and after the fix.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.05, 0.091])
- **Form:** `in_app_help`
- **Deflection rate:** ~10% (range [7%, 13%])
- **Feasibility:** 0.35
- **Rationale:** The session cannot be closed by the user themselves — it requires backend action by an agent — so a help article or chatbot can set expectations but cannot deflect the actual resolution need. Only a small fraction of contacts might self-abandon after reading guidance.
- **Validation:** Deploy a 4-week in-app FAQ article explaining the bug and instructing users to contact support; track whether ticket volume declines relative to baseline before/after.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.1 (range [0.07, 0.13])
- **Narrow use case:** Auto-close an open Ticketless session when backend logs confirm a vehicle exit event was recorded but session closure failed, and no payment discrepancy is detected.
- **Safety constraints:**
  - Only trigger auto-close when an exit event is positively confirmed in backend logs — do not act on user assertion alone.
  - Require zero outstanding payment balance before autonomous closure to avoid financial disputes.
  - Log all autonomous closures for audit and flag any reversal within 24 hours for human review.
  - Exclude cases where the attendant manually raised the barrier without any system exit record, as these may indicate payment bypass.
- **Rationale:** Autonomous resolution is technically plausible for a narrow confirmed-exit subset, but the root cause (unreliable exit signal) means many tickets lack the backend exit record needed to safely auto-close without human verification. The low annual volume further limits ROI.
- **Validation:** Define acceptance criteria (exit-event present + zero balance = eligible); run a 4-week supervised pilot on ≤20% of incoming tickets; measure false-positive closure rate and any payment disputes triggered.

### Risks

- **Compliance concerns:**
  - Autonomous or premature session closure without confirmed exit could result in unbilled parking time, creating revenue loss and potential regulatory issues under Croatian consumer billing rules.
  - Parking session records may need to be retained for a minimum period under local data retention requirements; automated closure must preserve audit logs.
- **Must not automate:**
  - Cases where the attendant manually raised the barrier and no system exit event exists — payment legitimacy cannot be confirmed without human review.
  - Cases with any outstanding or unclear payment balance on the session.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

