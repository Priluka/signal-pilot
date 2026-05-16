---
id: croatia-parking-payment-failure__e3b934
name: croatia_parking_payment_failure
title: Users unable to complete parking/ticket payments in the Bmove app
description: Users across Croatian cities (Rijeka, Osijek, Pula, Varaždin, Vukovar) and other locations report being unable
  to complete payments for parking or transit tickets via the Bmove app. Issues range from transactions being declined, duplicate
  charges, inability to use prepaid balance, failure to add a payment card, to payments succeeding but the parking barrier
  not lifting. In many cases the issue resolved itself or was fixed by support without major intervention.
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
cluster_id: BS:unknown|croatia|no_label:c1
project_key: BS
cluster_size: 18
cluster_size_dedup: 18
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.87
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.35
median_resolution_minutes: 17048.0
p95_resolution_minutes: 50527.1
cannot_reproduce_rate: 0.0
data_window_start: '2023-07-25'
data_window_end: '2025-10-01'
annual_hours_saved: 0.6
roi:
  baseline_active_hours: 2.8
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.3
  deflection_hours_range:
  - 0.2
  - 0.4
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.6
  agent_assist_hours_range:
  - 0.4
  - 0.7
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.8
  product_fix_hours_range:
  - 2.0
  - 2.8
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.2
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-10787
- BS-11553
- BS-14969
- BS-15064
- BS-16086
- BS-16238
- BS-16345
- BS-17033
- BS-18638
- BS-25228
- BS-25482
- BS-15352
- BS-15439
- BS-25468
- BS-42875
- BS-16543
- BS-12629
- BS-16352
canonical_examples:
- BS-10787
- BS-11553
- BS-25468
vendor_dependency:
  vendor_name: Corvus Pay (corvus play)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-acknowledge receipt and send a structured status-update email when a known Corvus
    Pay outage or incident is already logged.
  autonomous_resolve_safety_constraints:
  - No automated refund or credit issuance without human approval — financial transaction reversals require agent sign-off.
  - No autonomous backend payment-block resolution — risk of unintended account state changes.
  - Must not act on tickets involving barrier failures (potential physical safety implication).
  - Vendor (Corvus Pay) API access required for any transaction lookup; must be scoped read-only for automation.
  - Must escalate immediately if duplicate-charge amount exceeds a configurable threshold (e.g., >50 HRK).
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__7950cd
- bmove-app-feedback-mixed-issues__d6cf0c
- bmove-app-operational-issues-austria
- croatia-ticketless-open-session-at-exit__a7c97e
- croatia-ticketless-open-session-at-exit__f25b63
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
- ticketless-open-session-not-closed-at-exit
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Users unable to complete parking/ticket payments in the Bmove app

## What this pattern is

Users across Croatian cities (Rijeka, Osijek, Pula, Varaždin, Vukovar) and other locations report being unable to complete payments for parking or transit tickets via the Bmove app. Issues range from transactions being declined, duplicate charges, inability to use prepaid balance, failure to add a payment card, to payments succeeding but the parking barrier not lifting. In many cases the issue resolved itself or was fixed by support without major intervention.

## When this applies

- User attempts to pay for parking or a transit ticket via the Bmove app
- Transaction is declined or returns an error message
- App crashes or freezes during the payment flow (white screen)
- Payment succeeds but the parking barrier does not lift
- Duplicate charges appear on the user's bank account
- Prepaid/wallet balance is not offered as a payment option
- Card cannot be added via Corvus Pay or similar payment provider
- Authorization shows as valid (green) but purchase is still rejected

## Typical resolution flow

1. User attempts to purchase a parking ticket or monthly pass in the Bmove app
2. Payment fails with an error, or succeeds but service (barrier) does not activate
3. User submits feedback via the Bmove app's feedback form
4. Ticket is created in Bmove Support system
5. Support agent investigates the user's account and transaction history
6. If duplicate charge: refund or account credit is issued
7. If payment blocked: agent checks card/authorization status and guides user or resolves on backend
8. Ticket is closed once payment confirmed successful or issue resolved

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Investigate user account and transaction records to confirm whether payment was processed | support_agent | Bmove back-office/admin system | 10 min |
| Issue refund or credit for duplicate/incorrectly charged transactions | support_agent | Bmove back-office/admin system | 15 min |
| Manually resolve payment block or card authorization issue on backend | support_agent | Bmove back-office/admin system | 10 min |
| Communicate resolution or ask for more details via email | support_agent | email | 5 min |

## Vendor dependency

- **Vendor:** Corvus Pay (corvus play)

## Evidence

Derived from 18 tickets in cluster `BS:unknown|croatia|no_label:c1`. Direct quotes from 7 representative tickets:

- `BS-10787` _[hr]_: "3 puta skinuto s računa MC. ID transakcije AC91b66577387 09:49, 09:50 i 09:58 sat. poslan je email s detaljima transakcije. molim vratite na račun preplaćeno."
- `BS-11553` _[hr]_: "javlja kako se kupnja preko aplikacije trenutno ne može izvršiti."
- `BS-25468` _[hr]_: "Autorizacija je uredna (zelena), a ne mogu kupiti Povlaštenu kartu stanara (jer, kao nema autorizacije) !!!!!!!!!"
- `BS-18638` _[hr]_: "ne zeli mi dodati karticu na aplikaciju preko servera corvus play"
- `BS-15439` _[hr]_: "uplaćen novac na apliakaciju nisam u mogucnosti koristiti za naplatu parkinga. Aplikacija mi nudi samo plaćanje preko kartice."
- `BS-12629` _[hr]_: "u zadnja dva puta na lokaciji parkiranja Kapucinski trg varaždin nije se digla rampa unatoc tome sto mi je novac naplacen i stigla obavjest o naplati na aplikaciji."
- `BS-16345` _[hr]_: "već par dana ne mogu izvršiti plaćanje u Osijeku"

## Cluster statistics

- **Volume:** 18 tickets total (18 unique semantic events after dedup)
- **Frequency:** 0.35 tickets/month (over data window 2023-07-25 → 2025-10-01)
- **Median resolution:** 11.8 days
- **Languages:** hr
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.8 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.6 (range [0.392, 0.728])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.75
- **Rationale:** Agent assist can meaningfully reduce the communication step (action 4) by pre-drafting resolution emails and can surface a checklist for the investigation step (action 1), but the backend investigation and refund actions require human judgment and system access that limit total time savings.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-drafts resolution emails and suggests investigation checklists; compare agent handle time before and after for this ticket cluster.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~5 (range [3.5, 6.5])
- **Hours eliminated per year:** ~2.8 (range [1.96, 2.8])
- **Root cause:** Integration instability with Corvus Pay gateway causing payment declines, duplicate charges, and barrier-lift failures; likely involves inconsistent transaction state handling and insufficient idempotency checks on payment confirmation callbacks.
- **Rationale:** Because the issue involves a third-party payment gateway (Corvus Pay) and multi-city infrastructure, a full fix requires both internal idempotency/state hardening and coordinated vendor changes, making effort high and timeline uncertain. Full elimination is theoretically achievable but depends on vendor cooperation.
- **Validation:** Engineering team should scope effort via a spike against Corvus Pay API documentation and transaction logs; cross-reference duplicate-charge incidents to determine whether failures originate client-side, server-side, or at the gateway callback.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.3 (range [0.238, 0.442])
- **Form:** `in_app_help`
- **Deflection rate:** ~12% (range [8%, 16%])
- **Feasibility:** 0.35
- **Rationale:** Most tickets involve payment failures or duplicate charges that require backend investigation and refund processing — these are not self-resolvable by the user via FAQ. A small subset (e.g., card-add failures) may be deflected by clear in-app guidance on supported card types and Corvus Pay requirements.
- **Validation:** Deploy a 4-week in-app help article covering common card-add and payment decline scenarios; measure whether contact rate for this pattern drops relative to baseline period.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.1 (range [0.1, 0.18])
- **Narrow use case:** Auto-acknowledge receipt and send a structured status-update email when a known Corvus Pay outage or incident is already logged.
- **Safety constraints:**
  - No automated refund or credit issuance without human approval — financial transaction reversals require agent sign-off.
  - No autonomous backend payment-block resolution — risk of unintended account state changes.
  - Must not act on tickets involving barrier failures (potential physical safety implication).
  - Vendor (Corvus Pay) API access required for any transaction lookup; must be scoped read-only for automation.
  - Must escalate immediately if duplicate-charge amount exceeds a configurable threshold (e.g., >50 HRK).
- **Rationale:** The combination of financial transactions, third-party vendor dependency, and multi-step backend resolution makes full autonomous handling unsafe; only the narrow case of sending a templated acknowledgement during a known outage is low-risk enough to automate at this time.
- **Validation:** Pilot over 6 weeks: auto-send acknowledgement emails only when a Corvus Pay incident flag is active; measure false-positive rate (emails sent when no actual outage) and customer satisfaction scores against manually handled baseline.

### Risks

- **Compliance concerns:**
  - Refund and chargeback processing must comply with Croatian payment services regulations and relevant EU PSD2 requirements — automation of any financial reversal requires compliance review.
  - Storage and access to transaction records must align with GDPR data minimisation and access-control obligations.
- **Must not automate:**
  - Issuing refunds or account credits without human approval.
  - Resolving payment blocks or card authorization holds on the backend without agent oversight.
  - Any action on tickets where a parking barrier failed to lift — potential safety and liability implications require human judgment.
- **Vendor dependencies blocking automation:**
  - Corvus Pay (Corvus Play) — transaction status lookups, refund processing, and root-cause investigation all depend on API or portal access provided by this vendor; delays in vendor cooperation directly block both automation feasibility and product fix timelines.
  - Typical wait days for vendor response is unspecified, introducing unpredictable resolution latency that automation must not mask.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.87)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

