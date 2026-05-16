---
id: hr-b2b-parking-card-cancellation-refund
name: hr_b2b_parking_card_cancellation_refund
title: Croatian B2B Partner Requests Refund for Incorrectly Purchased Parking Card
description: B2B partner (Zagrebački holding d.o.o., acting as intermediary) forwards end-user requests for refunds on incorrectly
  purchased or wrongly registered parking cards on the Bmove platform. The card is first cancelled/voided by the partner,
  then Bmove support processes the storno in IGeus and initiates a bank transfer refund to the customer's provided IBAN. Tickets
  are almost exclusively initiated by a single contact person (Tomislav Hac) at Zagrebački holding and resolved by Bmove support
  staff.
category: b2b_operator/billing
ticket_class: b2b_partner
issue_category: billing
resolution_pattern: refund_issued
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:b2b_partner|croatia|storno:c2
project_key: BS
cluster_size: 177
cluster_size_dedup: 177
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 3.47
median_resolution_minutes: 2966.0
p95_resolution_minutes: 20145.199999999993
cannot_reproduce_rate: 0.0
data_window_start: '2023-10-05'
data_window_end: '2026-01-23'
annual_hours_saved: 3.5
roi:
  baseline_active_hours: 17.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.4
  deflection_hours_range:
  - 0.3
  - 0.5
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 3.5
  agent_assist_hours_range:
  - 2.5
  - 4.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 10.4
  product_fix_hours_range:
  - 7.3
  - 13.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 2.1
  autonomous_resolve_hours_range:
  - 1.5
  - 2.7
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-43055
- BS-25978
- BS-14046
- BS-16934
- BS-19760
- BS-22659
- BS-26972
- BS-27550
- BS-24690
- BS-40563
- BS-24051
- BS-31913
- BS-39928
- BS-38977
- BS-40564
- BS-38722
- BS-42813
- BS-24586
canonical_examples:
- BS-22659
- BS-22659
- BS-43055
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
  note: Financial action — agent drafts, human approves
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Automated confirmation comment to B2B partner after a human agent completes the IGeus
    storno and bank transfer steps
  autonomous_resolve_safety_constraints:
  - Autonomous action strictly limited to posting the resolution confirmation comment; IGeus storno and bank transfer must
    remain human-executed
  - IBAN data must never be logged, stored, or transmitted by the automation layer — handled only by the authorised Bmove
    agent
  - Automation may only trigger after both storno completion and bank transfer confirmation are verified in the ticket workflow
  - Any automation touching financial refund steps is prohibited without explicit GDPR and PCI compliance sign-off
  - Single-partner channel (Zagrebački holding) scope only; must not expand without separate risk assessment
related_playbooks:
- austrian-ticketless-incorrect-charge-refund
- b2b-partner-parking-card-storno-refund
- croatia-b2b-parking-card-refund-request
- croatia-sms-parking-payment-failure
- croatian-b2b-parking-ticket-storno-refund
- croatian-b2b-parking-ticket-storno-request
- hr-b2b-parking-card-storno-refund
- hr-b2b-parking-ticket-storno-refund
- hr-b2b-r1-invoice-request
- igeus-portal-access-credential-management
- zagreb-parking-cancelled-ticket-refund
- zagrebparking-b2b-storno-refund-request
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Croatian B2B Partner Requests Refund for Incorrectly Purchased Parking Card

## What this pattern is

B2B partner (Zagrebački holding d.o.o., acting as intermediary) forwards end-user requests for refunds on incorrectly purchased or wrongly registered parking cards on the Bmove platform. The card is first cancelled/voided by the partner, then Bmove support processes the storno in IGeus and initiates a bank transfer refund to the customer's provided IBAN. Tickets are almost exclusively initiated by a single contact person (Tomislav Hac) at Zagrebački holding and resolved by Bmove support staff.

## When this applies

- End user purchased a parking card with wrong vehicle registration plate
- End user purchased wrong card type (hourly, daily, weekly, monthly) or wrong zone
- End user purchased a duplicate/unnecessary card
- B2B partner (Zagrebački holding) has already voided/cancelled the card on their side and forwards refund request to Bmove support with customer IBAN

## Typical resolution flow

1. End user contacts Zagrebački holding reporting an incorrectly purchased parking card
2. Zagrebački holding voids/cancels the card internally
3. Tomislav Hac (Zagrebački holding) forwards request to Bmove support with customer's IBAN for refund
4. Bmove support agent identifies the transaction in IGeus and processes storno
5. Bmove support agent (or Lidija Petricević) initiates bank transfer refund to provided IBAN via Erste or other bank
6. Bmove support confirms to partner that card is cancelled and money has been returned

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Storno (cancellation) of the parking transaction in IGeus | Bmove support agent | IGeus | 10 min |
| Initiate bank transfer refund to customer IBAN | Bmove support agent (Lidija Petricević or similar) | Erste bank / banking system | 10 min |
| Confirm resolution to B2B partner via ticket comment | Bmove support agent | Bmove Support ticketing system | 5 min |

## Evidence

Derived from 177 tickets in cluster `BS:b2b_partner|croatia|storno:c2`. Direct quotes from 6 representative tickets:

- `BS-22659` _[hr]_: "Molim izvršiti povrat sredstava za pogrešno kupljenu satnu kartu. Karta je kod nas poništena"
- `BS-22659` _[hr]_: "@@Lidija Petricević  molim te povrat u iznosu od 2.10€ za Erste transakciju etfyz-1c556-myf (Satna parkirališna karta; Zona 2; Zagreb, reg. oznaka ZD****). Stornirano u Igeusu."
- `BS-43055` _[hr]_: "Poštovani, karta je poništena i novac je vraćen. Lp, Bmove support"
- `BS-40563` _[hr]_: "Molim da izvršite povrat sredstava za pogrešno kupljenu kartu. Karta je kod nas poništena"
- `BS-42813` _[hr]_: "@@Lidija Petricević  molim te povrat u iznosu od 11.90€ za Erste kupovinu 4p1pc-gxt9h-7he (Tjedna parkirališna karta; Zona 2; Zagreb, ZG****). Stornirano u IGeusu."
- `BS-40564` _[hr]_: "transakcija 1cssg-ge39z-55k je stornirana i povrat je izvršen."

## Cluster statistics

- **Volume:** 177 tickets total (177 unique semantic events after dedup)
- **Frequency:** 3.47 tickets/month (over data window 2023-10-05 → 2026-01-23)
- **Median resolution:** 2.1 days
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~17.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~3.5 (range [2.45, 4.5])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.75
- **Rationale:** The workflow is highly templated (storno in IGeus, bank transfer to IBAN, confirmation comment), so agent-assist tooling could pre-populate the resolution comment, surface the customer IBAN from ticket context, and provide a checklist ensuring both IGeus and banking steps are completed — saving roughly 5 minutes of lookup and typing per ticket. The IGeus action itself still requires human execution, capping total savings.
- **Validation:** Run agent-assist in shadow mode for 2 weeks on all incoming tickets from Tomislav Hac, measuring time from ticket open to resolution comment posted; compare to the 25-minute baseline to validate the 20% reduction estimate.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~10.4 (range [7.3, 13.4])
- **Root cause:** Tickets arise from end-user purchasing errors (wrong card type or incorrect registration) on the Bmove platform, not from a platform defect. The root cause is a UX friction point: insufficient confirmation steps or guardrails at purchase time that would catch selection errors before payment.
- **Rationale:** Adding a prominent purchase-confirmation summary screen (card type, vehicle plate, amount) with an explicit acknowledgement step could reduce incorrect purchases by an estimated 50–65% of current volume, eliminating the downstream refund workflow for those cases. Engineering effort is medium as it involves UI changes across purchase flows and regression testing against the IGeus integration.
- **Validation:** A/B test the confirmation screen with 50% of new B2B-referred end-user purchases for 8 weeks; compare incorrect-purchase rate between treatment and control to validate the 50–65% reduction assumption before full rollout.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.4 (range [0.28, 0.5])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** Tickets originate exclusively from a single B2B intermediary (Tomislav Hac at Zagrebački holding) acting on behalf of end-users; self-service content cannot replace the agent-executed IGeus storno and bank transfer steps that require system access. Deflection potential is minimal because the work is operational processing, not information-seeking.
- **Validation:** Deploy a dedicated B2B partner portal FAQ explaining the refund process for 4 weeks and measure whether any tickets are resolved without Bmove agent intervention; expect near-zero deflection to confirm the directional estimate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~2.1 (range [1.5, 2.7])
- **Narrow use case:** Automated confirmation comment to B2B partner after a human agent completes the IGeus storno and bank transfer steps
- **Safety constraints:**
  - Autonomous action strictly limited to posting the resolution confirmation comment; IGeus storno and bank transfer must remain human-executed
  - IBAN data must never be logged, stored, or transmitted by the automation layer — handled only by the authorised Bmove agent
  - Automation may only trigger after both storno completion and bank transfer confirmation are verified in the ticket workflow
  - Any automation touching financial refund steps is prohibited without explicit GDPR and PCI compliance sign-off
  - Single-partner channel (Zagrebački holding) scope only; must not expand without separate risk assessment
- **Rationale:** Full autonomous resolution is not appropriate here given the bank transfer and IGeus storno steps carry financial and regulatory risk; however, automating the templated confirmation comment (≈5 min/ticket) once a human marks the ticket resolved is a narrow, low-risk application. Broader automation is blocked by the requirement for human authorisation of financial transactions and IBAN handling obligations.
- **Validation:** Pilot automated confirmation comment posting for 6 weeks on this cluster only; acceptance criteria: 100% of comments sent within 2 minutes of agent marking ticket resolved, zero false triggers, partner satisfaction maintained; human review of every auto-sent comment during pilot.

### Risks

- **Compliance concerns:**
  - IBAN and personal financial data are present in tickets; GDPR Article 5 data-minimisation and storage-limitation principles apply — automation must not persist or log IBAN values
  - Bank transfer initiation constitutes a financial transaction; any automation touching this step requires explicit authorisation controls and audit trails under Croatian payment regulations
  - B2B intermediary relationship (Zagrebački holding as processor/controller) may impose contractual constraints on automated processing of end-user refund data
- **Must not automate:**
  - IGeus storno (cancellation) execution — requires trained agent judgement and system access controls
  - Bank transfer initiation to customer IBAN — financial transaction requiring human authorisation
  - IBAN capture, storage, or forwarding by any automation layer
  - Any step that modifies financial records without a complete human-reviewed audit trail

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Financial action — agent drafts, human approves

