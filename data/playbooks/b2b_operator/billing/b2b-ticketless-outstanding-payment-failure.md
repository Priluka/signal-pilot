---
id: b2b-ticketless-outstanding-payment-failure
name: b2b_ticketless_outstanding_payment_failure
title: B2B Partner Outstanding Payment Failure for Ticketless Parking (AT/DE)
description: B2B partners using the Bmove ticketless parking service receive automated 'outstanding payment' notifications
  after a payment could not be processed at garage exit due to technical difficulties, expired/blocked/lost credit cards,
  or app errors. Customers are unable to complete the payment through the app and seek alternative payment methods such as
  bank transfer. Support guides them to retry via the app's purchase history or to update their payment card.
category: b2b_operator/billing
ticket_class: b2b_partner
issue_category: billing
resolution_pattern: user_education
languages:
- de
- en
country_focus:
- at
- de
- other
status: active
cluster_id: BS:b2b_partner|austria|ticketless:c2
project_key: BS
cluster_size: 48
cluster_size_dedup: 45
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.91
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.88
median_resolution_minutes: 309.5
p95_resolution_minutes: 13546.099999999995
cannot_reproduce_rate: 0.0208
data_window_start: '2023-08-22'
data_window_end: '2025-08-01'
annual_hours_saved: 2.2
roi:
  baseline_active_hours: 7.2
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 1.8
  deflection_hours_range:
  - 1.3
  - 2.3
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 2.2
  agent_assist_hours_range:
  - 1.6
  - 2.7
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.5
  product_fix_hours_range:
  - 1.8
  - 3.2
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.7
  autonomous_resolve_hours_range:
  - 0.5
  - 0.9
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-33221
- BS-16514
- BS-32946
- BS-12201
- BS-14219
- BS-19131
- BS-20156
- BS-23023
- BS-32999
- BS-25671
- BS-23030
- BS-34002
- BS-24401
- BS-26265
- BS-18746
- BS-22107
- BS-21194
- BS-16312
canonical_examples:
- BS-32946
- BS-32946
- BS-16514
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
  note: User education — safe for self-service deflection
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-send templated retry/card-update instructions when ticket is classified as outstanding
    payment failure with no prior open case for the same partner account
  autonomous_resolve_safety_constraints:
  - Must not autonomously close tickets involving account investigation (lost card, empty purchase history, persistent app
    error)
  - Must not send payment instructions if a duplicate or escalated case exists for the same B2B partner account
  - Must require human review before any communication implying financial obligation or debt collection
  - Must only trigger on confirmed outstanding-payment classification with high-confidence intent score
  - Must log all autonomous actions for weekly audit review
related_playbooks:
- b2b-missing-parking-receipt-request
- b2b-outstanding-payment-failure-app
- b2b-partner-austria-ticketless-open-session-at-exit
- italian-b2b-invoice-billing-question
- outstanding-payment-credit-card-failure
- slovakia-parking-payment-failure-no-ticket
- ticketless-open-session-not-closed-at-exit
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# B2B Partner Outstanding Payment Failure for Ticketless Parking (AT/DE)

## What this pattern is

B2B partners using the Bmove ticketless parking service receive automated 'outstanding payment' notifications after a payment could not be processed at garage exit due to technical difficulties, expired/blocked/lost credit cards, or app errors. Customers are unable to complete the payment through the app and seek alternative payment methods such as bank transfer. Support guides them to retry via the app's purchase history or to update their payment card.

## When this applies

- Automated 'outstanding payment' email sent to customer after ticketless parking payment fails at garage exit
- Credit card expired, blocked, lost, or not properly updated in app
- App payment retry fails with error message (e.g. 'Kauf nicht erfolgreich, Ticket nicht bestätigt')
- In-app payment banner not visible despite outstanding amount
- Purchase history appears empty preventing payment retry
- Customer requests IBAN/wire transfer as alternative payment method

## Typical resolution flow

1. Customer receives automated outstanding payment notification from Bmove
2. Customer attempts to pay via app but encounters error or cannot find the payment option
3. Customer contacts support requesting alternative payment method (wire transfer/IBAN) or help resolving the error
4. Support sends acknowledgement and 1-2 business day SLA response
5. Support instructs customer to retry via app: Main Menu → Purchase History → select date → 'Proceed to Pay', or use in-app banner
6. If card issue: support advises updating/replacing the payment card under Ticketless settings
7. Customer confirms payment success or reports continued failure
8. If still failing, support investigates specific card/account issue (lost card, bank closure, etc.)

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Send automated acknowledgement with 1-2 business day SLA | support_system | Bmove support ticketing system | 1 min |
| Instruct customer to retry payment via app purchase history or in-app banner | support_agent | Bmove app (Purchase History / Banner) | 10 min |
| Advise customer to add/update credit card linked to vehicle/ticketless profile | support_agent | Bmove app (Ticketless settings / Payments section) | 10 min |
| Investigate specific account issues (lost card, empty history, persistent app error) | support_agent | Bmove backend/admin | 20 min |

## Evidence

Derived from 48 tickets in cluster `BS:b2b_partner|austria|ticketless:c2`. Direct quotes from 8 representative tickets:

- `BS-32946` _[de]_: "Zahlung über App funktioniert allerdings nicht 'Der Kauf war nicht erfolgreich. Ticket nicht bestätigt'"
- `BS-32946` _[de]_: "ich würde gern per Überweisung oder in irgendeiner möglichen Weise bezahlen. Verschiedene Kreditkarten sind verfügbar und wurden über app bereits versucht"
- `BS-16514` _[en]_: "I may arrange via wire transfer, please forward bank details."
- `BS-16514` _[en]_: "Sorry, there is no banner!"
- `BS-34002` _[de]_: "Einkaufshistorie ist LEER! Es ist hier KEINE Benachrichtigung über ausstehende Zahlung."
- `BS-24401` _[de]_: "Die Karte die mit dem Kennzeichen verknüpft ist, ist nicht gültig (Verlorene Karte)."
- `BS-32999` _[de]_: "unsere Bank hat fälschlicherweise unser Konto geschlossen und die zugehörige Karte ebenfalls."
- `BS-16312` _[de]_: "wir haben bereits 2x über den Support Kontakt aufgenommen, erhalten jedoch nur die automatisierten Mails"

## Cluster statistics

- **Volume:** 48 tickets total (45 unique semantic events after dedup)
- **Frequency:** 0.88 tickets/month (over data window 2023-08-22 → 2025-08-01)
- **Median resolution:** 5.2 hours
- **Cannot Reproduce rate:** 2.1%
- **Languages:** de, en
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~7.2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~2.2 (range [1.6, 2.7])
- **Time reduction per ticket:** ~30% (range [22%, 38%])
- **Feasibility:** 0.80
- **Rationale:** The resolution pattern is highly templated (two standard instruction sets: retry via purchase history, or update card), making it well-suited for agent-assist macros or auto-drafted responses; time savings would primarily come from eliminating steps 2 and 3 drafting time.
- **Validation:** Run agent-assist in shadow mode for 3 weeks, having agents rate draft accuracy and applicability; target ≥80% usable-without-edit rate before full rollout.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~2.5 (range [1.8, 3.25])
- **Root cause:** Payment processing failures at garage exit due to technical difficulties and app errors prevent customers from completing payments through normal in-app flows; the absence of a reliable alternative payment path (e.g., bank transfer or retry outside purchase history) forces support escalation for a subset of cases.
- **Rationale:** Improving the retry UX (surfacing a persistent, prominent in-app payment retry flow) and adding a secondary payment method fallback would eliminate the need for agent-guided workarounds for the majority of straightforward card-update cases. Edge cases like persistent app errors may remain.
- **Validation:** Engineering team should audit payment failure event logs for AT/DE to quantify failure reason breakdown (card vs. technical vs. app error) before scoping; spike estimate should be validated against payment service architecture review in a 2-sprint discovery.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1.8 (range [1.3, 2.34])
- **Form:** `in_app_help`
- **Deflection rate:** ~25% (range [18%, 32%])
- **Feasibility:** 0.65
- **Rationale:** The resolution is largely procedural (retry via purchase history, update card), making it amenable to an in-app contextual help prompt surfaced directly on the outstanding payment notification. However, B2B partners with account-specific issues (lost card, empty history) will still require agent intervention, capping deflection potential.
- **Validation:** Deploy an in-app help banner on the outstanding payment error screen for 6 weeks; measure ticket creation rate before and after for AT/DE B2B partners to validate deflection rate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.7 (range [0.5, 0.9])
- **Narrow use case:** Auto-send templated retry/card-update instructions when ticket is classified as outstanding payment failure with no prior open case for the same partner account
- **Safety constraints:**
  - Must not autonomously close tickets involving account investigation (lost card, empty purchase history, persistent app error)
  - Must not send payment instructions if a duplicate or escalated case exists for the same B2B partner account
  - Must require human review before any communication implying financial obligation or debt collection
  - Must only trigger on confirmed outstanding-payment classification with high-confidence intent score
  - Must log all autonomous actions for weekly audit review
- **Rationale:** Only a narrow slice of tickets (simple retry cases with clear card-update signal and no account anomalies) can be safely auto-resolved; B2B billing context and financial sensitivity warrant a conservative volume cap and mandatory human oversight for anything beyond the initial acknowledgement.
- **Validation:** Pilot over 8 weeks on ≤20% of incoming tickets matching the narrow use case; acceptance criteria: zero escalations attributable to incorrect autonomous responses, and partner CSAT no lower than agent-handled baseline.

### Risks

- **Compliance concerns:**
  - B2B outstanding payment communications may carry legal implications under AT/DE consumer and commercial credit regulations; automated messages must not be construed as formal debt collection notices
  - GDPR compliance required for any automated processing of B2B partner payment and account data
  - Any autonomous payment-related communication must include clear escalation path to a human agent
- **Must not automate:**
  - Account investigations involving lost or fraudulently blocked credit cards
  - Cases where purchase history is missing or inconsistent, suggesting a data integrity issue
  - Any communication that could be interpreted as a final payment demand or legal notice
  - Tickets where the B2B partner has expressed dispute or dissatisfaction with the charge itself

## Agent compatibility

- **Status:** `active` (extraction confidence 0.91)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

