---
id: ticketless-open-session-at-exit__960f17
name: ticketless_open_session_at_exit
title: Ticketless parking session not closed after manual exit by garage staff
description: End users parked ticketlessly via the Bmove app but the exit camera failed to recognize their license plate,
  requiring a garage attendant to manually open the barrier. As a result, the parking session remains active in the app, continuing
  to accrue charges and blocking future re-entry. Users contact support to request manual session closure.
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
cluster_id: BS:end_user|austria|ticketless:c2
project_key: BS
cluster_size: 726
cluster_size_dedup: 644
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 12.62
median_resolution_minutes: 2323.5
p95_resolution_minutes: 130416.55000000031
cannot_reproduce_rate: 0.0055
data_window_start: '2023-04-06'
data_window_end: '2025-12-18'
annual_hours_saved: 25.0
roi:
  baseline_active_hours: 83.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 4.2
  deflection_hours_range:
  - 2.9
  - 4.8
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 25.0
  agent_assist_hours_range:
  - 17.5
  - 32.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 75.0
  product_fix_hours_range:
  - 58.0
  - 83.3
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 7.6
  autonomous_resolve_hours_range:
  - 5.3
  - 9.9
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-36169
- BS-14989
- BS-8679
- BS-9208
- BS-12846
- BS-15167
- BS-19527
- BS-13201
- BS-14006
- BS-41468
- BS-20416
- BS-24627
- BS-41055
- BS-15966
- BS-15321
- BS-13533
- BS-12880
- BS-17361
canonical_examples:
- BS-14989
- BS-8679
- BS-9208
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: 2
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-close sessions only when backend system confirms a manual barrier-lift event was
    logged within the last 2 hours and no active charge dispute exists
  autonomous_resolve_safety_constraints:
  - Session closure must not be performed autonomously if the exit timestamp is ambiguous or missing from system logs
  - Any session where the user reports a charge dispute must be routed to a human agent before closure
  - Autonomous closure must apply €0 charge only when the manual exit is confirmed; fare-adjustment cases require human review
  - All autonomous closures must be logged and reviewable by a backend operator within 24 hours
  - A hard volume cap of 15% of annual tickets (≈23 tickets/year) should apply until pilot data validates safety
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
- open-session-at-exit-austria
- open-session-at-exit-payment-failure
- outstanding-payment-credit-card-failure
- pkc-vehicle-registration-automated-tickets
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

# Ticketless parking session not closed after manual exit by garage staff

## What this pattern is

End users parked ticketlessly via the Bmove app but the exit camera failed to recognize their license plate, requiring a garage attendant to manually open the barrier. As a result, the parking session remains active in the app, continuing to accrue charges and blocking future re-entry. Users contact support to request manual session closure.

## When this applies

- Exit camera fails to recognize the vehicle's license plate at a ticketless-enabled garage
- Garage staff or intercom operator manually opens the barrier without triggering a system exit event
- Parking session remains in 'active' state in the Bmove app after the user has physically left the garage
- User notices ongoing charges or is blocked from re-entering the garage due to still-active session

## Typical resolution flow

1. User exits garage but camera does not recognize license plate
2. User presses help/emergency button or contacts garage staff, who manually open the barrier
3. Session stays open in the Bmove app and continues running
4. User contacts Bmove support (via app feedback form or direct message) requesting manual session closure
5. Support agent acknowledges the issue and promises 1-2 business day resolution
6. Support agent internally tags a colleague (e.g. @Patrick Aumüller) with license plate and actual exit timestamp
7. Colleague manually closes the session in the backend system using the correct exit time (and €0 or correct fare)
8. Support agent confirms to the user that the session has been closed and asks them to verify in the app

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Acknowledge ticket and set expectations for 1-2 business day resolution | support_agent | Jira/helpdesk | 5 min |
| Identify correct exit timestamp and license plate from user message or system logs | support_agent | Bmove backend / Arivo / SKIDATA | 10 min |
| Internally assign task to backend operator (e.g. @Patrick Aumüller) with license plate and exit time | support_agent | Jira comment / internal tagging | 3 min |
| Manually close the open parking session with the correct exit time and appropriate charge (often €0 or actual fare) | backend_operator | Bmove backend system (Arivo/SKIDATA) | 10 min |
| Notify user that session has been closed and ask them to verify in the app | support_agent | Jira/helpdesk | 5 min |

## Evidence

Derived from 726 tickets in cluster `BS:end_user|austria|ticketless:c2`. Direct quotes from 6 representative tickets:

- `BS-14989` _[de]_: "Beim Verlassen der Garage Zieglergasse heute um ca. 18:00 wurde mein Kennzeichen nicht erkannt. Der Schranken wurde von einem Service-Mitarbeiter geöffnet, aber anscheinend wurde meine Session nicht b"
- `BS-8679` _[de]_: "Ich bin am 24.05.23 ticketless in die Garage Neuer Markt Wien gefahren. Das System hat mein Fahrzeug nicht ausgebucht, so dass ich für das System noch in der Garage stehe (1 Woche)."
- `BS-9208` _[de]_: "ich habe die Garage bereits verlassen aber es wird immer noch aktiv angezeigt. Bitte Ticket ausbuchen mit 16:30."
- `BS-19527` _[de]_: "ein Garagenmitarbeiter um 17:00 Uhr zirka manuell aus der Garage am Fiakerplatz hinaus gelassen hat, weil es wieder mal nicht funktioniert hat. Nun habe ich eine offene Sitzung."
- `BS-13201` _[de]_: "ich bin seit über 200 Tagen in der Garage Neuer Markt eingebucht. Ein Mitarbeiter der Garage hat gemeint ich soll mich an sie wenden."
- `BS-14006` _[de]_: "Parksitzung wird mit der Ausfahrtzeit beendet. Obwohl die Parkzeit in der App noch läuft"

## Cluster statistics

- **Volume:** 726 tickets total (644 unique semantic events after dedup)
- **Frequency:** 12.62 tickets/month (over data window 2023-04-06 → 2025-12-18)
- **Median resolution:** 1.6 days
- **Cannot Reproduce rate:** 0.5%
- **Languages:** de
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~83.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~25 (range [17.5, 32.5])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.85
- **Rationale:** The resolution steps are highly templated — acknowledge, look up exit timestamp + plate, assign to backend operator, notify user — making this pattern well-suited for an assist tool that auto-populates the acknowledgement, extracts plate and timestamp from the ticket, and drafts the internal assignment and user closure messages. This could meaningfully compress the ~18 min of agent drafting and lookup time per ticket.
- **Validation:** Run assist tooling in shadow mode for 2 weeks on this ticket category; measure draft acceptance rate and per-ticket handle time versus the 33-minute baseline before enabling send.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~75 (range [58, 83.3])
- **Root cause:** Exit camera fails to recognize license plates for ticketless sessions in certain conditions (lighting, plate format, obstruction), leaving sessions open indefinitely after a manual barrier lift by garage staff; the system has no fallback to auto-close the session when a manual exit event is logged.
- **Rationale:** A robust fix requires either improving license-plate recognition reliability or, more tractably, implementing an automatic session-close trigger when a garage attendant manually opens the barrier — both paths eliminate the root cause of the support contact. If the barrier-lift event is already logged, the latter could be medium-effort and would eliminate the majority of this cluster.
- **Validation:** Engineering should audit whether manual barrier-lift events are already captured in backend logs; a spike ticket (1–2 days) can determine feasibility and sharpen the sprint estimate before committing.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~4.2 (range [2.94, 4.8])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** This issue requires a backend operator to manually close the session in the system; users cannot self-serve the resolution, making FAQ or in-app help largely ineffective beyond setting expectations. Minimal deflection is possible only if a help article prevents duplicate or follow-up tickets once a user understands the 1-2 day SLA.
- **Validation:** Deploy a help-center article explaining the manual-exit session delay and monitor ticket volume for 4 weeks to measure whether duplicate or impatient follow-up contacts decrease.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~7.6 (range [5.32, 9.88])
- **Narrow use case:** Auto-close sessions only when backend system confirms a manual barrier-lift event was logged within the last 2 hours and no active charge dispute exists
- **Safety constraints:**
  - Session closure must not be performed autonomously if the exit timestamp is ambiguous or missing from system logs
  - Any session where the user reports a charge dispute must be routed to a human agent before closure
  - Autonomous closure must apply €0 charge only when the manual exit is confirmed; fare-adjustment cases require human review
  - All autonomous closures must be logged and reviewable by a backend operator within 24 hours
  - A hard volume cap of 15% of annual tickets (≈23 tickets/year) should apply until pilot data validates safety
- **Rationale:** Full autonomous resolution is risky because it involves financial adjustments (zeroing or correcting charges) and depends on accurate exit-timestamp data not always present in the inbound ticket; a narrow pilot scoped to unambiguous, log-confirmed manual exits with no charge dispute is the only defensible starting point. The low feasibility score reflects dependency on structured backend log access and the financial-action risk.
- **Validation:** Pilot with ≤15% of volume: run for 6 weeks with every autonomous closure reviewed by a backend operator within 24 hours; acceptance criteria are zero erroneous charge adjustments and user confirmation of session closure in ≥95% of cases.

### Risks

- **Compliance concerns:**
  - Automated financial adjustments (zeroing or modifying parking charges) may require audit trails under applicable payment and consumer-protection regulations
  - Storing and processing license plate data in automation pipelines may implicate GDPR/local data-minimization requirements
- **Must not automate:**
  - Any ticket where the user is disputing the charge amount rather than simply requesting session closure
  - Cases where the exit timestamp cannot be confirmed from system logs — ambiguity must route to human review
  - Repeated offenders or accounts flagged for fraud review must not receive autonomous session closure

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

