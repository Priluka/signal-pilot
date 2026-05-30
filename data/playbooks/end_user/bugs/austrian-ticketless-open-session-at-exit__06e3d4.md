---
id: austrian-ticketless-open-session-at-exit__06e3d4
name: austrian_ticketless_open_session_at_exit
title: Ticketless parking session remains active after user has physically exited the garage
description: End users report that their Bmove ticketless parking session continues to show as active in the app even after
  they have already left the garage, often because the exit barrier camera failed to recognise their licence plate and the
  barrier was opened manually by staff. This leaves the session open, prevents re-entry, and risks ongoing billing. Support
  resolves it by manually closing the session with the actual exit time.
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
cluster_id: BS:end_user|austria|no_label:c9
project_key: BS
cluster_size: 357
cluster_size_dedup: 257
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 5.04
median_resolution_minutes: 2586.5
p95_resolution_minutes: 61088.349999999955
cannot_reproduce_rate: 0.0114
data_window_start: '2023-05-18'
data_window_end: '2026-05-05'
annual_hours_saved: 9.1
roi:
  baseline_active_hours: 30.2
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 1.5
  deflection_hours_range:
  - 1.1
  - 1.9
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 9.1
  agent_assist_hours_range:
  - 6.4
  - 11.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 27.2
  product_fix_hours_range:
  - 19.0
  - 30.2
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 6.0
  autonomous_resolve_hours_range:
  - 4.3
  - 7.9
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-50006
- BS-51607
- BS-13560
- BS-8295
- BS-12211
- BS-16068
- BS-19915
- BS-52884
- BS-25939
- BS-49420
- BS-35633
- BS-46869
- BS-20247
- BS-50989
- BS-27828
- BS-46796
- BS-50039
- BS-45338
canonical_examples:
- BS-50006
- BS-12211
- BS-35633
vendor_dependency:
  vendor_name: SKIDATA / Arivo Parking (barrier/camera system)
  involves_vendor: true
  typical_wait_days: 2
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-close sessions where no re-entry has occurred, session age exceeds 6 hours past
    garage closing time, and a staff-manual-override log entry exists confirming physical exit.
  autonomous_resolve_safety_constraints:
  - Must confirm no active billing dispute or chargeback on the session before auto-closing
  - Must use the actual exit timestamp from the barrier override log, not current time, to avoid incorrect billing
  - Must not auto-close if the user has re-entered the same garage after the stuck session was created
  - Must send a confirmation notification to the user and log the automated action for audit review
  - Requires verified API access to SKIDATA/Arivo manual-override event log; if unavailable, autonomous resolution is blocked
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-incorrect-charge-refund
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
- open-session-at-exit-austria
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

# Ticketless parking session remains active after user has physically exited the garage

## What this pattern is

End users report that their Bmove ticketless parking session continues to show as active in the app even after they have already left the garage, often because the exit barrier camera failed to recognise their licence plate and the barrier was opened manually by staff. This leaves the session open, prevents re-entry, and risks ongoing billing. Support resolves it by manually closing the session with the actual exit time.

## When this applies

- Exit barrier camera fails to read the vehicle's licence plate
- User is manually let out by garage staff via intercom/button
- Session is not automatically closed by the system after manual barrier opening
- User notices the session is still active in the app (sometimes days later)

## Typical resolution flow

1. User exits garage but barrier does not open automatically
2. User presses intercom/help button; staff opens barrier manually
3. Staff or system fails to close the parking session
4. User notices active session in app and contacts Bmove support via feedback form
5. Support agent looks up the session in Bmove tools/backend
6. Support agent manually closes the session with the correct exit time
7. Support informs user to restart the app if the session still appears active

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Acknowledge ticket and set expectation of 1-2 business day resolution | support_agent | Jira Service Management / Bmove support portal | 5 min |
| Look up open parking session in Bmove backend tools | support_agent | Bmove tools / Graylog | 10 min |
| Manually close the parking session with the actual exit time | support_agent | Bmove tools / Arivo Parking backend | 10 min |
| Notify user that session has been closed and advise app restart | support_agent | Jira Service Management / email | 5 min |

## Vendor dependency

- **Vendor:** SKIDATA / Arivo Parking (barrier/camera system)
- **Typical wait:** 2 day(s)

## Evidence

Derived from 357 tickets in cluster `BS:end_user|austria|no_label:c9`. Direct quotes from 6 representative tickets:

- `BS-50006` _[de]_: "Die Parksitzung ist aber noch immer aktiv. Bitte um Korrektur und Richtigstellung."
- `BS-12211` _[de]_: "Der Schranken beim Hinausfahren aus der DC Living Garage hat sich leider nicht automatisch geöffnet, so dass mir manuell geöffnet wurde. Meine Sitzung läuft jetzt leider noch immer."
- `BS-35633` _[de]_: "Ich bin schon seit 8 Tagen aktive Session obwohl ich schon am selben Tag nach 1h rausgefahrenen bin!"
- `BS-52884` _[de]_: "der offene Parkvorgang wurde von uns mit der tatsächlichen Ausfahrtzeit aus der Garage abgeschlossen. Sollten Sie im Bmove immer noch eine aktive Sitzung sehen, starten Sie bitte die App neu."
- `BS-46796` _[de]_: "Die Kamera bei der Ausfahrt in der Garage Mariahilf beim C&A funktionierte nicht. Ich wurde manuell rausgelassen."
- `BS-20247` _[de]_: "Ich konnte heute nicht rausfahren und Ihr Kollege hat mich rausfahrenden lassen! Er hat mir die Schranke um 16:39 aufgemacht! Ich bin noch aktiv und kann morgen nicht in die Garage fahren."

## Cluster statistics

- **Volume:** 357 tickets total (257 unique semantic events after dedup)
- **Frequency:** 5.04 tickets/month (over data window 2023-05-18 → 2026-05-05)
- **Median resolution:** 1.8 days
- **Cannot Reproduce rate:** 1.1%
- **Languages:** de
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~30.2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~9.1 (range [6.4, 11.8])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.85
- **Rationale:** The resolution is highly procedural — look up session, close it, notify user — making it well-suited to a guided assist tool that pre-fetches the open session and pre-fills the closure form and response template, saving lookup and drafting time. The main remaining agent effort is verification and judgment on the correct exit timestamp.
- **Validation:** Run in shadow mode for 2 weeks with 10 agents: measure time-on-ticket with and without assist prompts to validate the 30% reduction assumption before full rollout.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~27.2 (range [19.04, 30.2])
- **Root cause:** When the exit barrier camera fails to read the licence plate and staff manually open the barrier, no exit event is sent to the Bmove backend, leaving the session open indefinitely. The fix requires a reliable fallback mechanism — e.g. a manual-override endpoint on the barrier controller that fires a synthetic exit event to Bmove, or a session watchdog that auto-closes sessions exceeding a plausible maximum dwell time.
- **Rationale:** A full fix involves both Bmove backend changes and an integration point with the SKIDATA/Arivo barrier system, making effort high and vendor coordination essential; if successful, the vast majority of tickets in this cluster would be eliminated. The upper bound is capped at the full 30.2 h baseline.
- **Validation:** Engineering team should spike the SKIDATA/Arivo API documentation to confirm whether a manual-override exit event is supported before committing sprint estimates; a 2-sprint proof-of-concept in a test garage environment would validate feasibility.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1.5 (range [1.1, 1.95])
- **Form:** `in_app_help`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.25
- **Rationale:** This is a product-side bug requiring backend session closure, not a user action; a FAQ or in-app message can set expectations and reduce duplicate tickets but cannot resolve the underlying stuck session. Self-service deflection potential is therefore very low.
- **Validation:** Deploy a targeted in-app help article explaining the issue and advising users to submit a single ticket; measure ticket-per-incident rate over 4 weeks to confirm any reduction in duplicate submissions.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~6 (range [4.3, 7.852])
- **Narrow use case:** Auto-close sessions where no re-entry has occurred, session age exceeds 6 hours past garage closing time, and a staff-manual-override log entry exists confirming physical exit.
- **Safety constraints:**
  - Must confirm no active billing dispute or chargeback on the session before auto-closing
  - Must use the actual exit timestamp from the barrier override log, not current time, to avoid incorrect billing
  - Must not auto-close if the user has re-entered the same garage after the stuck session was created
  - Must send a confirmation notification to the user and log the automated action for audit review
  - Requires verified API access to SKIDATA/Arivo manual-override event log; if unavailable, autonomous resolution is blocked
- **Rationale:** Autonomous closure is feasible only for the clearest-cut cases where barrier override logs definitively confirm exit; billing implications and the vendor API dependency limit safe automation to roughly 20% of volume. Broader automation risks incorrect session timestamps and erroneous charges.
- **Validation:** Pilot with 10 manually-reviewed tickets over 4 weeks: an automation candidate is accepted only if the barrier override log timestamp matches the user-reported exit time within ±15 minutes; target zero billing-error incidents as the acceptance criterion before scaling.

### Risks

- **Compliance concerns:**
  - Incorrect exit timestamps used for session closure could result in erroneous billing charges to users, with potential consumer protection or payment regulation implications
  - Automated session modifications must maintain a full audit trail to satisfy any parking dispute resolution or financial reconciliation requirements
- **Must not automate:**
  - Session closure where the correct exit time is ambiguous or cannot be confirmed from barrier logs
  - Any case involving an active billing dispute, refund request, or chargeback
  - Closure actions that would result in a net charge to the user without explicit agent verification
- **Vendor dependencies blocking automation:**
  - SKIDATA / Arivo Parking barrier/camera system must expose a reliable API or event log for manual-override exit events; without this, autonomous resolution and the product fix watchdog approach cannot be implemented
  - Typical vendor coordination wait of ~2 business days per incident currently extends wall-clock resolution time and would also apply to any integration development timeline

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

