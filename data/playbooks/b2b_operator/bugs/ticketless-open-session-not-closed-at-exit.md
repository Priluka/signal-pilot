---
id: ticketless-open-session-not-closed-at-exit
name: ticketless_open_session_not_closed_at_exit
title: Ticketless parking session not closed after vehicle exit
description: B2B partner customers (primarily in Austria, some in Germany) report that their bmove ticketless parking session
  remains open/active in the app after they have physically exited the garage. This prevents them from entering another garage
  as the system believes the vehicle is still parked. The root cause is typically a failure in license plate recognition at
  exit, a manually operated barrier bypass by garage staff, or a system/camera defect that does not trigger session closure.
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
status: active
cluster_id: BS:b2b_partner|austria|no_label:c0
project_key: BS
cluster_size: 38
cluster_size_dedup: 34
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.67
median_resolution_minutes: 4118.0
p95_resolution_minutes: 89024.04999999999
cannot_reproduce_rate: 0.0
data_window_start: '2022-09-23'
data_window_end: '2026-04-22'
annual_hours_saved: 0.6
roi:
  baseline_active_hours: 2.9
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.2
  deflection_hours_range:
  - 0.1
  - 0.2
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.6
  agent_assist_hours_range:
  - 0.4
  - 0.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.3
  product_fix_hours_range:
  - 1.7
  - 2.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.3
  autonomous_resolve_hours_range:
  - 0.2
  - 0.4
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-52438
- BS-48383
- BS-29752
- BS-2252
- BS-25678
- BS-30533
- BS-35035
- BS-41691
- BS-45831
- BS-34588
- BS-37173
- BS-48349
- BS-37014
- BS-43549
- BS-45944
- BS-45319
- BS-44854
- BS-48567
canonical_examples:
- BS-52438
- BS-48383
- BS-43549
vendor_dependency:
  vendor_name: Skidata / Arivo
  involves_vendor: true
  typical_wait_days: 2
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-close sessions where vehicle exit is confirmed by a secondary signal (e.g., garage
    CCTV timestamp or partner API exit event) and no payment dispute is open
  autonomous_resolve_safety_constraints:
  - Must not auto-close sessions where a billing dispute or overcharge is flagged
  - Requires explicit exit confirmation from a second data source (not solely customer assertion)
  - Must not auto-close if session duration exceeds a configurable threshold (e.g., >24 h) without human review
  - B2B partner account changes must be logged with full audit trail for partner billing reconciliation
  - Skidata/Arivo API must be available and return a confirmed exit event before automation triggers
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-missing-parking-receipt-request
- b2b-outstanding-payment-failure-app
- b2b-partner-austria-ticketless-open-session-at-exit
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

# Ticketless parking session not closed after vehicle exit

## What this pattern is

B2B partner customers (primarily in Austria, some in Germany) report that their bmove ticketless parking session remains open/active in the app after they have physically exited the garage. This prevents them from entering another garage as the system believes the vehicle is still parked. The root cause is typically a failure in license plate recognition at exit, a manually operated barrier bypass by garage staff, or a system/camera defect that does not trigger session closure.

## When this applies

- Vehicle exits garage but license plate camera fails to recognize the plate at exit
- Garage staff manually opens barrier without triggering session closure in the system
- Technical defect in the garage video/camera system at exit
- Duplicate session created at entry (e.g. both ticket and ticketless registered simultaneously)
- Session remains open for days or weeks without being auto-closed

## Typical resolution flow

1. Customer notices active session in bmove app long after exiting the garage
2. Customer is blocked from entering another garage because system shows vehicle already inside
3. Customer contacts bmove support via email or in-app feedback
4. Support agent locates the open session in the backend system (Arivo, Skidata, or bmove tools)
5. Support agent manually closes the session, typically with €0 charge
6. Support agent instructs customer to restart the bmove app to sync the status
7. Customer confirms session is no longer visible (optional follow-up)

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Manually close the open parking session in the backend system | support_agent | Arivo / SKIDATA / Bmove backend | 15 min |
| Instruct customer to restart the bmove app to sync session status | support_agent | — | 2 min |
| Request additional information (license plate, garage, entry/exit time, screenshots) if not provided | support_agent | email | 5 min |

## Vendor dependency

- **Vendor:** Skidata / Arivo
- **Typical wait:** 2 day(s)

## Evidence

Derived from 38 tickets in cluster `BS:b2b_partner|austria|no_label:c0`. Direct quotes from 7 representative tickets:

- `BS-52438` _[de]_: "In der bmove-App wird jedoch weiterhin seit nunmehr 42 Tagen eine aktive Sitzung für das Kennzeichen W**** seit 11.03.2026, 08:39 Uhr angezeigt"
- `BS-48383` _[de]_: "Beim Ausfahren vom Parkplatz um circa 23:45 Uhr wurde der Parkvorgang in der App nicht beendet. Ich ersuche Sie daher unverzüglich um Beendigung des Parkens."
- `BS-43549` _[de]_: "Der Schranken in der Garage Mariahilfer Straße wurde am 16.10.2025 um 20:20 Uhr vom Mitarbeiter händisch geöffnet, da es automatisch nicht funktionierte. Das Ticket wurde aber leider nicht beendet."
- `BS-45944` _[de]_: "Das Fahrzeug steht nicht seit 833 Tagen in der Garage."
- `BS-48349` _[de]_: "Infolgedessen kann ich derzeit über Bmove keine Garage mehr befahren, da das System davon ausgeht, dass sich mein Fahrzeug noch in der Garage befindet."
- `BS-37014` _[de]_: "Auf Grund eines Defekts beim Videosystem hat mir die Garagenverwaltung den Schranken geöffnet."
- `BS-44854` _[en]_: "I can NOT use BMove for parking this week as the plate UU**** is still locked to previous parking"

## Cluster statistics

- **Volume:** 38 tickets total (34 unique semantic events after dedup)
- **Frequency:** 0.67 tickets/month (over data window 2022-09-23 → 2026-04-22)
- **Median resolution:** 2.9 days
- **Languages:** de, en
- **Country focus:** at, de

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.9 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.6 (range [0.44, 0.75])
- **Time reduction per ticket:** ~20% (range [15%, 26%])
- **Feasibility:** 0.80
- **Rationale:** The resolution workflow is highly templated: gather license plate/garage/timestamp, look up session in backend, close it, instruct app restart. An agent-assist tool can pre-fill the backend query, surface the open session record, and draft the closure confirmation reply, reducing cognitive load and copy-paste time by ~20%.
- **Validation:** Run shadow-mode agent-assist for 2 weeks on this ticket cluster, measuring suggested-action acceptance rate and actual handle-time delta vs. the 22-minute baseline; target ≥70% acceptance rate before full rollout.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~2.3 (range [1.74, 2.61])
- **Root cause:** License plate recognition (LPR) failure at exit, manual barrier bypass by garage staff, or camera/system defect fails to trigger session closure in the bmove backend, leaving the session open. Fix requires improved LPR fallback logic, a garage-staff-initiated session-close API call on manual barrier open, and/or a session-timeout watchdog with configurable grace period.
- **Rationale:** A robust fix requires coordination across the bmove backend, Skidata/Arivo integration layer, and potentially camera/LPR firmware — making it a multi-team, high-effort initiative. If successful, it could eliminate ~80% of this cluster (the LPR and manual-bypass root causes), capped at the 2.9 h baseline.
- **Validation:** Engineering team should conduct a spike (≤1 sprint) to map the Skidata/Arivo API surface for manual barrier events and LPR fallback signals, then size implementation; acceptance criteria = zero open sessions after verified vehicle exit in staging environment across ≥50 simulated exit events.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.2 (range [0.15, 0.24])
- **Form:** `in_app_help`
- **Deflection rate:** ~8% (range [6%, 10%])
- **Feasibility:** 0.25
- **Rationale:** The session cannot be closed by the customer themselves — it requires backend access by a support agent — so self-service content can only deflect tickets where the customer is confused or waiting for guidance, not resolve the underlying issue. FAQ or in-app help explaining what to do (contact support immediately with plate/garage details) may marginally reduce repeat contacts or incomplete tickets.
- **Validation:** Deploy an in-app help article for 4 weeks targeting the 'session still active' scenario and track whether contacts per impacted session decrease or whether first-contact resolution time improves due to better-prepared submissions.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.3 (range [0.22, 0.37])
- **Narrow use case:** Auto-close sessions where vehicle exit is confirmed by a secondary signal (e.g., garage CCTV timestamp or partner API exit event) and no payment dispute is open
- **Safety constraints:**
  - Must not auto-close sessions where a billing dispute or overcharge is flagged
  - Requires explicit exit confirmation from a second data source (not solely customer assertion)
  - Must not auto-close if session duration exceeds a configurable threshold (e.g., >24 h) without human review
  - B2B partner account changes must be logged with full audit trail for partner billing reconciliation
  - Skidata/Arivo API must be available and return a confirmed exit event before automation triggers
- **Rationale:** Autonomous resolution is limited by the need for a verified secondary exit signal and the billing sensitivity of B2B accounts; without a confirmed exit event from the vendor system, auto-closure risks incorrectly ending an active session and creating a charge dispute. A narrow pilot covering only the subset where the Skidata/Arivo API does return a late exit event is the safest entry point.
- **Validation:** Run a 4-week pilot with human-in-the-loop approval step: automation prepares the close action and a human approves within 5 minutes; measure false-positive rate (sessions that should not have been closed) targeting <1% before removing the approval gate.

### Risks

- **Compliance concerns:**
  - B2B partner billing records must remain accurate and auditable; incorrect session closure could cause billing errors requiring contractual remedy
  - GDPR: license plate data and session logs constitute personal data under Austrian/German law and must not be retained longer than legally permitted or shared with unauthorized systems
  - Any automated financial transaction (session closure with billing finalization) may require explicit partner consent per B2B contract terms
- **Must not automate:**
  - Session closure where a payment amount is in dispute or the charge amount is ambiguous
  - Cases involving a garage staff manual override where no digital exit record exists — human judgment required
  - Any action that modifies partner billing records without a verified secondary exit signal
- **Vendor dependencies blocking automation:**
  - Skidata/Arivo: typical 2-day vendor response wait means real-time automated exit confirmation is currently unavailable in most cases, blocking autonomous resolve at scale
  - Skidata/Arivo API must expose a reliable exit-event webhook or polling endpoint for any automation to safely verify vehicle departure before session closure

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

