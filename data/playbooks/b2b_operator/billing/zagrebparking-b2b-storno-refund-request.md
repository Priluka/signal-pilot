---
id: zagrebparking-b2b-storno-refund-request
name: zagrebparking_b2b_storno_refund_request
title: Zagrebparking B2B Partner Parking Ticket Cancellation and Refund Request
description: Zagrebparking (a B2B partner) submits tickets to Bmove Support notifying them that one or more parking tickets
  have been cancelled (stornirane/poništene) and requesting that the corresponding payment be refunded to the end user's bank
  account via IBAN. The Bmove support team then processes the transaction cancellation in their IGeus back-office system and
  coordinates the bank transfer refund, or in some cases returns funds to the user's Bmove prepaid balance if that was the
  original payment method.
category: b2b_operator/billing
ticket_class: b2b_partner
issue_category: billing
resolution_pattern: refund_issued
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:b2b_partner|no_value|storno:c0
project_key: BS
cluster_size: 33
cluster_size_dedup: 33
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.65
median_resolution_minutes: 4443.0
p95_resolution_minutes: 48725.39999999997
cannot_reproduce_rate: 0.0
data_window_start: '2022-08-31'
data_window_end: '2023-04-21'
annual_hours_saved: 1.7
roi:
  baseline_active_hours: 5.8
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.0
  deflection_hours_range:
  - 0.0
  - 0.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.7
  agent_assist_hours_range:
  - 1.2
  - 2.3
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 3.5
  product_fix_hours_range:
  - 2.5
  - 4.5
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.4
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-3283
- BS-7587
- BS-3883
- BS-2332
- BS-3786
- BS-7109
- BS-7300
- BS-2238
- BS-3273
- BS-2717
- BS-6470
- BS-6282
- BS-2716
- BS-2074
- BS-3013
- BS-3095
- BS-3789
- BS-6299
canonical_examples:
- BS-3283
- BS-3283
- BS-7300
vendor_dependency:
  vendor_name: Zagrebparking
  involves_vendor: true
  typical_wait_days: 1
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Financial action — agent drafts, human approves
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-cancel the IGeus transaction and notify finance via structured message when Zagrebparking
    submits a well-formed, single-ticket cancellation with a valid IBAN — no prepaid balance involved.
  autonomous_resolve_safety_constraints:
  - Autonomous action only when Zagrabparking notification is machine-readable and structurally complete (ticket ID, IBAN,
    amount all present)
  - No autonomous execution of bank transfers; finance team must still approve and execute the IBAN refund
  - Prepaid-balance refund cases must always involve a human agent due to account-state complexity
  - Multi-ticket batch cancellations must be escalated to a human for review
  - Automated cancellation in IGeus must be reversible within 24 hours and include a mandatory audit log entry
  - Mandatory human review if the refund amount exceeds a defined threshold (e.g., >500 EUR)
related_playbooks:
- austrian-ticketless-incorrect-charge-refund
- b2b-parking-invoice-payment-issues
- b2b-partner-parking-card-storno-refund
- b2b-ticketless-open-session-and-permit-conflict
- croatia-b2b-parking-card-refund-request
- croatian-b2b-parking-ticket-storno-refund
- hr-b2b-parking-card-cancellation-refund
- hr-b2b-parking-card-storno-refund
- hr-b2b-parking-ticket-storno-refund
- hr-b2b-partner-billing-payment-storno
- hr-b2b-sms-parking-payment-failure
- skidata-hosted-services-maintenance-notification
- zagreb-parking-cancelled-ticket-refund
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Zagrebparking B2B Partner Parking Ticket Cancellation and Refund Request

## What this pattern is

Zagrebparking (a B2B partner) submits tickets to Bmove Support notifying them that one or more parking tickets have been cancelled (stornirane/poništene) and requesting that the corresponding payment be refunded to the end user's bank account via IBAN. The Bmove support team then processes the transaction cancellation in their IGeus back-office system and coordinates the bank transfer refund, or in some cases returns funds to the user's Bmove prepaid balance if that was the original payment method.

## When this applies

- Zagrebparking cancels/voids a parking ticket on their side
- Parking ticket was purchased via Bmove app or Bmove prepaid
- End user's IBAN and name are provided by Zagrebparking for the refund
- Sometimes multiple parking tickets are cancelled in a single request

## Typical resolution flow

1. Zagrebparking sends a support ticket listing the cancelled parking ticket number(s) and the end user's IBAN and name for the refund
2. Bmove support agent identifies the corresponding transaction code(s) in the system
3. Agent cancels the transaction(s) in IGeus back-office system
4. Agent requests the finance/payment team member (e.g. Lidija Petricević) to execute the bank transfer to the provided IBAN
5. Finance team confirms the refund has been executed
6. Bmove support replies to Zagrebparking confirming the ticket cancellation and refund
7. If the original payment was via Bmove prepaid, the refund is returned to the prepaid balance instead of IBAN

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Cancel the payment transaction(s) associated with the parking ticket in IGeus | Bmove support agent | IGeus back-office system | 10 min |
| Request bank transfer refund to end user's IBAN | Bmove support agent (via internal mention/comment to finance team member) | Jira ticket comment / internal communication | 5 min |
| Execute bank transfer refund to end user's IBAN | Finance team member (e.g. Lidija Petricević) | Banking system | 15 min |
| Return funds to Bmove prepaid balance (if original payment was via prepaid) | Bmove support agent | Bmove platform | 10 min |
| Confirm resolution to Zagrebparking via ticket reply | Bmove support agent | Jira / email | 5 min |

## Vendor dependency

- **Vendor:** Zagrebparking
- **Typical wait:** 1 day(s)

## Evidence

Derived from 33 tickets in cluster `BS:b2b_partner|no_value|storno:c0`. Direct quotes from 7 representative tickets:

- `BS-3283` _[hr]_: "Stornirali smo parkirnu kartu 5290432. Molimo izvršiti povrat na: IBAN HR85 2402 0063 2113 0639 7"
- `BS-3283` _[hr]_: "navedena karta je poništena i sa naše strane i korisniku je vraćeno 24 kn. Napomena - novac je korisniku vraćen na Bmove prepaid zato što je parking tako platio."
- `BS-7300` _[hr]_: "@@Lidija Petricević molim te povrat za Erste transakciju 8r1sm-1acpx-x51 u iznosu od 47.80€ (Mjesečna parkirališna karta; Zona 2; Zagreb, reg. oznaka ZG****). Transakcija je poništena u IGeusu."
- `BS-7109` _[hr]_: "ne mogu u IGeusu stornirati ove tri transakcije '8nff8-2afpc-pe1', '5teyw-aah9r-1y5', '2uzj7-7x9h3-dyv' Javlja mi HTTP error 500 internal server error"
- `BS-6299` _[hr]_: "Napomena - korisniku je novac vraćen na Bmove prepaid jer je sa Bmove prepaida i platio parking."
- `BS-7587` _[hr]_: "Povrat je izvršen. Potvrda o uplati je u nastavku."
- `BS-3883` _[hr]_: "Odradila sam ja taj povrat 30.12.2022. ali očito nisam napisala u ticket."

## Cluster statistics

- **Volume:** 33 tickets total (33 unique semantic events after dedup)
- **Frequency:** 0.65 tickets/month (over data window 2022-08-31 → 2023-04-21)
- **Median resolution:** 3.1 days
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~5.8 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.7 (range [1.22, 2.26])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.75
- **Rationale:** Agent assist can meaningfully reduce time on structured, repeatable steps: auto-populating the IGeus cancellation form from ticket data, generating a pre-filled IBAN refund request comment for the finance team, and drafting the confirmation reply to Zagrebparking. Finance execution (action 3, ~15 min) is not agent-facing and is excluded from savings.
- **Validation:** Run a 3-week shadow-mode pilot where the assist tool pre-populates IGeus cancellation fields and drafts the Zagrebparking confirmation reply; measure actual agent minutes saved vs. the 45-min baseline.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~3.5 (range [2.45, 4.55])
- **Root cause:** This is an operational workflow driven by an external vendor (Zagrebparking) cancelling parking tickets and requesting refunds; it is not caused by a product defect. A deeper integration (e.g., a direct API webhook from Zagrebparking triggering automated cancellation and refund in IGeus and the finance system) could reduce manual steps but would require negotiation with the vendor.
- **Rationale:** A full end-to-end integration with Zagrebparking's cancellation API and the bank/prepaid refund system could eliminate most manual steps (actions 1–4), but the engineering effort is high due to multi-system scope and vendor dependency. Hours eliminated are capped at baseline (5.8 h/yr); the estimated range reflects partial automation risk.
- **Validation:** Engineering team should spike on Zagrebparking API availability and IGeus webhook support in a 1-sprint discovery; validate effort range against findings before committing.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0.028, 0.05])
- **Form:** `none`
- **Deflection rate:** ~3% (range [2%, 4%])
- **Feasibility:** 0.05
- **Rationale:** This pattern is initiated by Zagrebparking (a B2B partner), not end users; there is no self-service path an end user can take to prevent or resolve it. Deflection is structurally inapplicable because the trigger is an inbound vendor notification, not a user query.
- **Validation:** No pilot recommended; confirm by reviewing inbound channel data over 4 weeks to verify >95% of tickets originate from Zagrebparking rather than end users.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.5 (range [0.364, 0.676])
- **Narrow use case:** Auto-cancel the IGeus transaction and notify finance via structured message when Zagrebparking submits a well-formed, single-ticket cancellation with a valid IBAN — no prepaid balance involved.
- **Safety constraints:**
  - Autonomous action only when Zagrabparking notification is machine-readable and structurally complete (ticket ID, IBAN, amount all present)
  - No autonomous execution of bank transfers; finance team must still approve and execute the IBAN refund
  - Prepaid-balance refund cases must always involve a human agent due to account-state complexity
  - Multi-ticket batch cancellations must be escalated to a human for review
  - Automated cancellation in IGeus must be reversible within 24 hours and include a mandatory audit log entry
  - Mandatory human review if the refund amount exceeds a defined threshold (e.g., >500 EUR)
- **Rationale:** Only the IGeus transaction cancellation step (action 1, ~10 min) is a realistic candidate for automation given safety constraints; the bank transfer (action 3) requires human finance authorization, and prepaid cases add branching complexity. At 20% volume coverage and 10 min saved per ticket, annual savings are modest given the low base frequency.
- **Validation:** Pilot with 8–10 supervised autonomous cancellations over 6 weeks; acceptance criteria: 100% match between automated cancellation and subsequent human-verified outcome, zero erroneous cancellations, and full audit trail in IGeus.

### Risks

- **Compliance concerns:**
  - Bank transfer refunds to IBANs constitute regulated payment transactions; any automation must comply with applicable EU Payment Services Directive (PSD2) requirements and internal financial controls.
  - GDPR: IBAN and end-user payment data transmitted by Zagrebparking must be handled under a valid data processing agreement and stored only as long as necessary.
  - Audit trail requirements: all transaction cancellations in IGeus must be logged with agent/system identity, timestamp, and linked ticket ID for financial audit purposes.
- **Must not automate:**
  - Execution of bank wire transfers to end-user IBANs — this must remain a human-authorized finance team action.
  - Prepaid balance refunds where the original payment method determination requires account-state verification.
  - Multi-ticket batch cancellation requests without human review of each line item.
  - Any case where the Zagrebparking notification is ambiguous, incomplete, or contains a disputed amount.
- **Vendor dependencies blocking automation:**
  - Zagrebparking does not currently appear to provide a machine-readable API or structured webhook for cancellation notifications; all automation beyond agent-assist requires vendor cooperation to expose a structured integration.
  - IGeus back-office API availability and documented cancellation endpoint must be confirmed before any autonomous-resolve or product-fix work can be scoped accurately.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Financial action — agent drafts, human approves

