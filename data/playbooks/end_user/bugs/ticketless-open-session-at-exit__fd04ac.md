---
id: ticketless-open-session-at-exit__fd04ac
name: ticketless_open_session_at_exit
title: Ticketless parking session not closed after vehicle exit
description: End users of the Bmove ticketless parking system exit a garage (barrier opened automatically or manually by staff),
  but the app session remains active and shows the vehicle still parked. This prevents the user from re-entering on their
  next visit, as the system displays 'already parked'. Users contact support to have the session manually closed and correctly
  charged.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- de
- en
country_focus:
- at
- de
status: active
cluster_id: BS:end_user|no_value|ticketless:c1
project_key: BS
cluster_size: 16
cluster_size_dedup: 16
sample_size_used: 16
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.31
median_resolution_minutes: 2434.5
p95_resolution_minutes: 17734.5
cannot_reproduce_rate: 0.0
data_window_start: '2023-01-12'
data_window_end: '2023-04-04'
annual_hours_saved: 0.3
roi:
  baseline_active_hours: 1.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.0
  deflection_hours_range:
  - 0.0
  - 0.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.3
  agent_assist_hours_range:
  - 0.2
  - 0.4
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.6
  product_fix_hours_range:
  - 1.1
  - 1.6
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
- BS-4850
- BS-5257
- BS-6080
- BS-6455
- BS-6608
- BS-6675
- BS-6977
- BS-7122
- BS-7133
- BS-7143
- BS-6250
- BS-4830
- BS-6201
- BS-6962
- BS-7204
- BS-6401
canonical_examples:
- BS-4850
- BS-5257
- BS-6080
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
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Automated session-closure API call triggered by verified barrier-exit event, limited
    to cases with unambiguous exit telemetry and no billing anomalies
  autonomous_resolve_safety_constraints:
  - Autonomous closure must only trigger when exit event is confirmed by barrier telemetry — never on user assertion alone
  - Billing amount must be computed and logged before closure; any discrepancy above a defined threshold must escalate to
    ops
  - Named ops colleague (Patrick Aumüller) must remain the fallback for all edge cases, manual overrides, and billing disputes
  - Audit trail of automated closures and charges must be retained and reviewable
  - User notification must be sent post-closure and must include charge details for verification
related_playbooks:
- app-payment-failure-parking-ticket
- austrian-ticketless-open-session-at-exit__06e3d4
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__7950cd
- bmove-app-operational-issues-austria
- croatia-ticketless-open-session-at-exit__f25b63
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- hr-open-session-after-garage-exit
- hr-parking-ticket-fine-after-paid-app
- missing-parking-invoice-receipt
- open-session-at-exit-austria
- open-session-at-exit-payment-failure
- parking-fine-received-despite-valid-payment
- parking-payment-failure-end-user
- prepaid-top-up-and-usage-issues
- slovakia-parking-payment-failure-no-ticket
- ticketless-open-session-at-exit__960f17
- ticketless-open-session-at-exit__d8d1ba
- wrong-parking-ticket-purchase-redirect
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Ticketless parking session not closed after vehicle exit

## What this pattern is

End users of the Bmove ticketless parking system exit a garage (barrier opened automatically or manually by staff), but the app session remains active and shows the vehicle still parked. This prevents the user from re-entering on their next visit, as the system displays 'already parked'. Users contact support to have the session manually closed and correctly charged.

## When this applies

- Vehicle exits garage but exit is not registered by the license plate recognition system
- Barrier opened manually by garage staff (e.g. due to system failure or maintenance) instead of automatically
- Barrier opens automatically but session is not closed in the app
- User attempts to re-enter garage on subsequent visit and receives 'vehicle already parked' error

## Typical resolution flow

1. User exits garage (barrier opened automatically or manually by staff)
2. App still shows active parking session
3. User attempts re-entry on next visit and is blocked by 'already parked' message
4. User contacts Bmove support requesting session closure
5. Support agent tags colleague (Patrick Aumüller) internally with plate number, garage, and exit timestamp
6. Colleague manually closes the session and processes payment
7. Support agent notifies user that session has been closed and asks them to verify in the app

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Receive and triage user complaint about unclosed session | support_agent | helpdesk (Jira/email) | 5 min |
| Tag Patrick Aumüller with license plate, garage name, and exit time for manual session closure and charge | support_agent | internal comment/helpdesk | 5 min |
| Manually close the parking session and charge the correct amount | ops_colleague (Patrick Aumüller) | Bmove backend system | 10 min |
| Notify user that session has been closed and ask them to verify in the app | support_agent | helpdesk (email) | 5 min |

## Evidence

Derived from 16 tickets in cluster `BS:end_user|no_value|ticketless:c1`. Direct quotes from 7 representative tickets:

- `BS-4850` _[de]_: "Nun ist die Sitzung in der Garage bereits seit fast 2 Tagen aktiv. Wie kann ich diese nun beenden?"
- `BS-5257` _[de]_: "ich bin gestern wie gewohnt aus der Parkgarage raus gefahren, jedoch steht die Sitzung in meiner App noch als offen auf!"
- `BS-6080` _[de]_: "Das Parken läuft noch in der App!! Ich bin heute um 18:00 Uhr rausgefahren (ein Herr hat mir den Schranken geöffnet weil bei mehrfachen Versuchen sich der Schranken nicht geöffnet hat)"
- `BS-6608` _[de]_: "In der App steht, dass ich bereits seit 11.3 durchgehend dort stehe."
- `BS-6675` _[de]_: "Mein Kollege wird bald die offene Parksitzung beenden. Ich melde mich noch, wenn es fertig ist."
- `BS-6201` _[de]_: "Der Schranken hob sich automatisch. In der App allerdings scheint die Parkzeit weiterzulaufen."
- `BS-6962` _[de]_: "Heute wollte ich in die Garage wieder einfahren, doch leider funktioniert es wieder nicht, da noch immer in der Bmove App anzeigt, ich stehe in der Garage."

## Cluster statistics

- **Volume:** 16 tickets total (16 unique semantic events after dedup)
- **Frequency:** 0.31 tickets/month (over data window 2023-01-12 → 2023-04-04)
- **Median resolution:** 1.7 days
- **Languages:** de, en
- **Country focus:** at, de

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~1.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.3 (range [0.224, 0.416])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.65
- **Rationale:** Assist tooling can auto-populate the hand-off message to Patrick Aumüller (license plate, garage, exit time) from ticket metadata and pre-draft the user notification, reducing the two agent-authored steps (~10 min combined) by roughly 20%. The manual ops closure step by a named colleague cannot be assisted away.
- **Validation:** Run shadow-mode draft suggestions for the tagging message and user-notification steps over 2–3 weeks; measure agent-accepted draft rate and time-on-ticket before and after activation.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~1.6 (range [1.12, 1.6])
- **Root cause:** The ticketless parking system fails to close the active app session when the barrier is opened (automatically or manually) upon vehicle exit, indicating the exit-event signal is not reliably triggering session-closure logic in the backend.
- **Rationale:** A reliable fix — ensuring barrier-open exit events always trigger session closure and accurate billing — would eliminate virtually all tickets in this cluster; the upper bound is capped at the 1.6-hour baseline. Engineering effort is rated medium because it likely involves event-pipeline debugging, edge-case handling for manual staff overrides, and billing reconciliation logic.
- **Validation:** Engineering team should instrument barrier-exit events end-to-end in a staging environment, run regression tests covering both automated and manual barrier opens, and monitor production for two weeks post-deploy tracking residual unclosed-session reports.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0.021, 0.039])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** The unclosed session cannot be resolved by the user themselves — it requires privileged backend access by ops staff to close and charge; an FAQ or self-service form cannot substitute for the required manual intervention. Deflection potential is near zero for this pattern.
- **Validation:** Deploy a help-center article explaining the issue and asking users to contact support; measure whether any tickets are avoided over a 4-week window before concluding deflection is negligible.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.2 (range [0.126, 0.234])
- **Narrow use case:** Automated session-closure API call triggered by verified barrier-exit event, limited to cases with unambiguous exit telemetry and no billing anomalies
- **Safety constraints:**
  - Autonomous closure must only trigger when exit event is confirmed by barrier telemetry — never on user assertion alone
  - Billing amount must be computed and logged before closure; any discrepancy above a defined threshold must escalate to ops
  - Named ops colleague (Patrick Aumüller) must remain the fallback for all edge cases, manual overrides, and billing disputes
  - Audit trail of automated closures and charges must be retained and reviewable
  - User notification must be sent post-closure and must include charge details for verification
- **Rationale:** Full autonomous resolution is risky because it involves financial transactions (charging the user) and relies on backend access currently delegated to a single named operator; a partial automation could handle the session-closure API call for clean-telemetry cases but must not bypass billing review. Given the very low annual frequency (3.8 tickets/year), the absolute hours saved are modest even if feasible.
- **Validation:** Pilot with a read-only shadow mode for 4 weeks: the system proposes a closure and charge amount but ops colleague approves before execution; measure proposal accuracy rate and proceed to limited live automation only if accuracy exceeds 95% on at least 10 cases.

### Risks

- **Compliance concerns:**
  - Automated or semi-automated billing actions must comply with applicable payment regulations and user consent terms for post-exit charges
  - Incorrect charge amounts resulting from automation errors could trigger disputes or regulatory complaints
  - Audit logs of session closures and charges must be retained per applicable data-retention requirements
- **Must not automate:**
  - Any session closure where exit telemetry is ambiguous or missing — user assertion alone is insufficient
  - Billing steps where the computed charge deviates from expected range without human review
  - Overriding the ops colleague's manual judgement in disputed or complex cases

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

