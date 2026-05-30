---
id: croatian-ticketless-open-session-at-exit__56d2b2
name: croatian_ticketless_open_session_at_exit
title: 'Croatia: Ticketless parking session remains open after manual barrier lift at exit'
description: End users in Croatian parking garages (primarily Zagreb and Rijeka) exit the garage after the SKIDATA barrier
  fails to recognise their vehicle, a garage attendant manually lifts the barrier, but the Bmove ticketless session remains
  open in the app. The root cause is consistently a payment authorisation failure (expired/blocked card, insufficient funds,
  or card change), which prevents automatic session closure. Support must manually close the session at €0 in SKIDATA and
  open a debt in the app for the correct parking amount.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:end_user|croatia|skidata:c1
project_key: BS
cluster_size: 22
cluster_size_dedup: 22
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.43
median_resolution_minutes: 1407.0
p95_resolution_minutes: 8752.749999999998
cannot_reproduce_rate: 0.0
data_window_start: '2024-06-26'
data_window_end: '2026-01-13'
annual_hours_saved: 0.6
roi:
  baseline_active_hours: 2.2
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
  - 0.7
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.0
  product_fix_hours_range:
  - 1.4
  - 2.2
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
- BS-28611
- BS-34375
- BS-31606
- BS-23537
- BS-28868
- BS-32506
- BS-37269
- BS-44630
- BS-31178
- BS-46892
- BS-33009
- BS-29477
- BS-39679
- BS-46198
- BS-30255
- BS-44323
- BS-42781
- BS-29159
canonical_examples:
- BS-28611
- BS-28868
- BS-37269
vendor_dependency:
  vendor_name: SKIDATA
  involves_vendor: true
  typical_wait_days: 1
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Automated session closure at €0 and debt creation for confirmed payment-failure exits,
    contingent on SKIDATA API supporting programmatic session close
  autonomous_resolve_safety_constraints:
  - Autonomous action must only trigger when payment authorisation failure is the confirmed root cause (not ambiguous or disputed
    exits)
  - Debt amount must be deterministically retrievable from SKIDATA session data before any automated write
  - All automated closures must be logged and immediately reviewable by Hrvoje Sirovina / Paulina Mrnarević before end-user
    notification is sent
  - SKIDATA API write access for session closure must be granted and scoped under a least-privilege service account
  - No automation if the session involves a disputed or escalated exit event
related_playbooks:
- austrian-ticketless-open-session-at-exit__06e3d4
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
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
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

# Croatia: Ticketless parking session remains open after manual barrier lift at exit

## What this pattern is

End users in Croatian parking garages (primarily Zagreb and Rijeka) exit the garage after the SKIDATA barrier fails to recognise their vehicle, a garage attendant manually lifts the barrier, but the Bmove ticketless session remains open in the app. The root cause is consistently a payment authorisation failure (expired/blocked card, insufficient funds, or card change), which prevents automatic session closure. Support must manually close the session at €0 in SKIDATA and open a debt in the app for the correct parking amount.

## When this applies

- SKIDATA exit barrier does not lift automatically for a Bmove ticketless user
- Garage attendant manually opens barrier without closing/charging the session
- Payment authorisation fails at exit (expired card, blocked card, card recently changed, insufficient funds)
- User notices session still open in Bmove app after leaving the garage

## Typical resolution flow

1. User enters garage using Bmove ticketless (licence plate recognition)
2. At exit, SKIDATA barrier does not recognise vehicle or authorisation fails
3. Garage attendant manually lifts barrier and tells user the system will handle it automatically
4. User leaves garage but session remains active in Bmove app
5. User contacts Bmove support (email) requesting session closure
6. Support agent identifies the session ID and requests billing from colleague
7. Colleague closes session at €0.00 in SKIDATA due to authorisation error
8. Support agent opens a debt in the Bmove app for the correct parking amount
9. Support agent notifies user via email that a debt has been created and instructs them to pay via app

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| User submits support request asking for open session to be closed | end_user | email / Bmove app | 5 min |
| Support agent locates session ID and forwards billing request to billing colleague | support_agent (Zelimir Mateskovic) | Jira / internal comment | 5 min |
| Billing colleague closes session at €0.00 in SKIDATA due to authorisation error | billing_agent (Hrvoje Sirovina / Paulina Mrnarević) | SKIDATA | 10 min |
| Support agent opens a debt in Bmove app for the correct parking fee and notifies user | support_agent | Bmove back-office / email | 5 min |

## Vendor dependency

- **Vendor:** SKIDATA
- **Typical wait:** 1 day(s)

## Evidence

Derived from 22 tickets in cluster `BS:end_user|croatia|skidata:c1`. Direct quotes from 6 representative tickets:

- `BS-28611` _[hr]_: "sesija zatvorena na 0,00 zbog greške u autorizaciji. Možete otvoriti dug na 2,00 €"
- `BS-28868` _[hr]_: "rampa se nije digla pa me djelatnik pustio. Naknadno sam shvatio da mi session i dalje traje."
- `BS-37269` _[hr]_: "zadnja 3 puta kada sam parkirala u garažama s Bmove opcijom, uredno uđem no na izlasku sustav ne funkcionira i moram vas kontaktirati da mi zatvorite sesiju, inače ostaje danima otvorena u aplikaciji."
- `BS-29159` _[hr]_: "ticketless sesija mi je ostala aktivna pet dana nakon izlaska iz garaže te Vas molim da je zaustavite."
- `BS-28611` _[hr]_: "rekao je da ništa ne trebam poduzimati jer ćete vi automatski poništiti sesiju obzirom da pratite lokaciju auta pa imate vidljiv izlaz."
- `BS-29477` _[hr]_: "sesija 202411061736463100219955 nije mogla biti naplaćena automatski i svi pokušaji naplate prema Vašoj kartici su bili neuspješni."

## Cluster statistics

- **Volume:** 22 tickets total (22 unique semantic events after dedup)
- **Frequency:** 0.43 tickets/month (over data window 2024-06-26 → 2026-01-13)
- **Median resolution:** 23.4 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.6 (range [0.39, 0.715])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.70
- **Rationale:** The resolution workflow is highly templated (locate session → forward to billing → close at €0 → open debt → notify user), making it a good candidate for an assist tool that pre-fills session lookup, drafts the billing forward message, and generates the user notification. Time savings are modest because the process is already short and the primary bottleneck is the billing handoff, not message composition.
- **Validation:** Run a 3-week shadow-mode pilot where the assist tool drafts the billing-forward message and user notification for each new ticket; measure agent-perceived draft acceptance rate and actual active-minutes-per-ticket against the 25-minute baseline.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~2 (range [1.39, 2.2])
- **Root cause:** Payment authorisation failure (expired/blocked card, insufficient funds, card change) prevents the Bmove system from automatically closing a ticketless parking session when the SKIDATA barrier is manually lifted, leaving sessions permanently open until manual staff intervention.
- **Rationale:** A fix would need to handle the manual-barrier-lift event from SKIDATA (likely via webhook or polling), detect unresolved payment authorisation, and trigger automatic session closure plus debt creation—requiring coordination with SKIDATA's API capabilities. Full elimination is feasible if SKIDATA can surface the manual-lift event reliably, but vendor dependency introduces meaningful uncertainty.
- **Validation:** Engineering team should validate SKIDATA API event coverage for manual barrier lifts in a staging environment before estimating sprint count; confirm whether the event is already emitted or requires a SKIDATA-side change (which would shift effort tier to high).

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.2 (range [0.154, 0.28])
- **Form:** `in_app_help`
- **Deflection rate:** ~10% (range [7%, 13%])
- **Feasibility:** 0.30
- **Rationale:** The root cause (payment failure leaving session open) requires back-end intervention by billing staff; end users cannot self-resolve even with perfect guidance, so deflection potential is very low. An in-app help article could at best reduce duplicated or confused follow-up contacts, not eliminate the core ticket.
- **Validation:** Deploy a targeted in-app help article in the Croatian locale explaining the open-session scenario and directing users to a structured submission form; measure ticket volume over 8 weeks to detect any reduction in duplicate or mis-routed contacts.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.4 (range [0.26, 0.48])
- **Narrow use case:** Automated session closure at €0 and debt creation for confirmed payment-failure exits, contingent on SKIDATA API supporting programmatic session close
- **Safety constraints:**
  - Autonomous action must only trigger when payment authorisation failure is the confirmed root cause (not ambiguous or disputed exits)
  - Debt amount must be deterministically retrievable from SKIDATA session data before any automated write
  - All automated closures must be logged and immediately reviewable by Hrvoje Sirovina / Paulina Mrnarević before end-user notification is sent
  - SKIDATA API write access for session closure must be granted and scoped under a least-privilege service account
  - No automation if the session involves a disputed or escalated exit event
- **Rationale:** Full automation requires reliable SKIDATA API write access (vendor dependency with typical 1-day wait) and deterministic identification of the payment-failure cause—both are non-trivial and partially outside the team's control. Even if feasible, the financial and compliance sensitivity of opening debts warrants a human-review gate, capping autonomous volume conservatively.
- **Validation:** Pilot with 5 manually selected low-ambiguity tickets: run the automation end-to-end in staging, have billing agents verify each closure and debt amount matches expected values, and confirm SKIDATA audit logs capture the automated action before enabling in production.

### Risks

- **Compliance concerns:**
  - Opening a debt in the Bmove app constitutes a financial obligation on the end user; automated debt creation must comply with Croatian consumer credit and payment regulations
  - GDPR: session and payment failure data processed during automation must be handled under the existing data processing agreement with SKIDATA
  - Any automated closure at €0 in SKIDATA must produce an auditable record for Croatian VAT and parking revenue reconciliation purposes
- **Must not automate:**
  - Cases where the payment failure cause is ambiguous or where the user disputes the session occurred
  - Debt creation for amounts that differ from the SKIDATA-recorded session fee without human review
  - End-user notification of debt before a billing agent has reviewed and approved the automated closure
- **Vendor dependencies blocking automation:**
  - SKIDATA must expose a reliable API event for manual barrier lifts and a write endpoint for programmatic session closure; without this, both the product fix and autonomous resolve opportunities are blocked
  - SKIDATA typical response/change lead time is ~1 day for operational requests but potentially multiple sprints for API feature additions, which could delay engineering effort estimates significantly

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

