---
id: croatian-b2b-parking-ticket-storno-refund
name: croatian_b2b_parking_ticket_storno_refund
title: Zagrebparking B2B Partner Requests Refund After Parking Ticket Cancellation (Croatia)
description: Zagrebparking (a B2B partner) notifies Bmove support that a parking ticket has been cancelled (storniran) and
  requests a monetary refund to a specified end-user bank account (IBAN). Bmove support then processes the transaction cancellation
  in their payment system (IGeus) and initiates a bank transfer refund, confirming completion back to the partner.
category: b2b_operator/billing
ticket_class: b2b_partner
issue_category: billing
resolution_pattern: refund_issued
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:b2b_partner|croatia|storno:c1
project_key: BS
cluster_size: 34
cluster_size_dedup: 34
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.67
median_resolution_minutes: 4596.5
p95_resolution_minutes: 21330.299999999996
cannot_reproduce_rate: 0.0
data_window_start: '2023-05-05'
data_window_end: '2024-03-25'
annual_hours_saved: 1.1
roi:
  baseline_active_hours: 3.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.0
  deflection_hours_range:
  - 0.0
  - 0.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.1
  agent_assist_hours_range:
  - 0.8
  - 1.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.8
  product_fix_hours_range:
  - 2.0
  - 3.3
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.3
  autonomous_resolve_hours_range:
  - 0.2
  - 0.3
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-8584
- BS-18984
- BS-8665
- BS-9283
- BS-10834
- BS-14085
- BS-17809
- BS-14464
- BS-8666
- BS-11352
- BS-7938
- BS-8469
- BS-9602
- BS-12265
- BS-11427
- BS-13792
- BS-13580
- BS-9599
canonical_examples:
- BS-8584
- BS-8584
- BS-18984
vendor_dependency:
  vendor_name: Erste Bank / IGeus
  involves_vendor: true
  typical_wait_days: 1
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Financial action — agent drafts, human approves
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-acknowledge receipt of Zagrebparking storno notification and log ticket number
    + IBAN, pending human approval before any refund is initiated
  autonomous_resolve_safety_constraints:
  - No financial transaction (bank transfer or IGeus storno) may be initiated without human approval
  - IBAN validation must be performed before any data is stored or forwarded
  - Only well-structured, machine-readable storno notifications from verified Zagrebparking sender addresses may trigger automation
  - All automated actions must be fully auditable and reversible before the refund approval step
  - Croatian payment regulation (HNB guidelines) and GDPR handling of IBAN/personal data must be reviewed by compliance before
    deployment
related_playbooks:
- austrian-ticketless-incorrect-charge-refund
- b2b-partner-parking-card-storno-refund
- croatia-b2b-parking-card-refund-request
- croatia-sms-parking-payment-failure
- croatian-b2b-parking-ticket-storno-request
- hr-b2b-parking-card-cancellation-refund
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

# Zagrebparking B2B Partner Requests Refund After Parking Ticket Cancellation (Croatia)

## What this pattern is

Zagrebparking (a B2B partner) notifies Bmove support that a parking ticket has been cancelled (storniran) and requests a monetary refund to a specified end-user bank account (IBAN). Bmove support then processes the transaction cancellation in their payment system (IGeus) and initiates a bank transfer refund, confirming completion back to the partner.

## When this applies

- Zagrebparking cancels a parking ticket on their side and notifies Bmove via email
- Partner provides end-user name and IBAN (or occasionally card details) for the refund
- Ticket amounts range from small hourly fees (e.g. 0.70€) to large annual passes (e.g. 525.60€)

## Typical resolution flow

1. Zagrebparking sends an email to Bmove support stating the ticket number has been cancelled and requesting a refund with end-user payment details
2. Bmove support agent looks up the corresponding Erste bank transaction ID using the ticket number
3. Agent requests cancellation/storno of the Erste transaction in IGeus system (typically via internal colleague)
4. Transaction is cancelled/voided in IGeus
5. Refund bank transfer is initiated to the user's IBAN
6. Bmove support confirms to Zagrebparking that the ticket is cancelled and money has been returned

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Receive storno notification from Zagrebparking with ticket number and end-user IBAN | Bmove support agent | email/ticketing system | 5 min |
| Locate the corresponding Erste payment transaction ID in IGeus for the cancelled parking ticket | Bmove support agent | IGeus | 5 min |
| Request internal colleague (e.g. Lidija Petricević / Anamaria Žigman) to process the storno/refund in IGeus and initiate bank transfer | Bmove support agent | IGeus / internal communication | 10 min |
| Confirm refund completion to Zagrebparking | Bmove support agent | email/ticketing system | 5 min |

## Vendor dependency

- **Vendor:** Erste Bank / IGeus
- **Typical wait:** 1 day(s)

## Evidence

Derived from 34 tickets in cluster `BS:b2b_partner|croatia|storno:c1`. Direct quotes from 5 representative tickets:

- `BS-8584` _[hr]_: "stornirali smo parkirnu kartu 465571. Molimo izvršiti povrat: Šimun Mihanović, HR2823900013218309890."
- `BS-8584` _[hr]_: "karta 465571 je poništena i novac je vraćen korisniku."
- `BS-18984` _[hr]_: "molim storno Erste kupovine z487g-qqpkn-sxf u iznosu od 2.10€ (Satna parkirališna karta; Zona 2; Zagreb, reg. oznaka ZG****). Transakcija je stornirana u IGeusu."
- `BS-8665` _[hr]_: "Ovaj IBAN koji je naveden za povrat je IBAN od Bmove-a, netko je vjerojatno krivo negdje prepisao. Pošaljite mi IBAN korisnice."
- `BS-9599` _[hr]_: "molim te povrat u iznosu od 525.60€ za Erste kupovinu 71cf7-n5rhw-fhc (Godišnja parkirališna karta; Zona 2; Zagreb, ZG****). Transakcija poništena u iGeusu."

## Cluster statistics

- **Volume:** 34 tickets total (34 unique semantic events after dedup)
- **Frequency:** 0.67 tickets/month (over data window 2023-05-05 → 2024-03-25)
- **Median resolution:** 3.2 days
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~3.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.1 (range [0.83, 1.49])
- **Time reduction per ticket:** ~35% (range [25%, 45%])
- **Feasibility:** 0.75
- **Rationale:** The workflow is highly structured: a tool that auto-looks up the Erste/IGeus transaction ID from the storno ticket number (step 2) and pre-drafts the confirmation message to Zagrebparking (step 4) could meaningfully cut active minutes. The internal handoff coordination (step 3) is harder to assist and limits overall savings.
- **Validation:** Run a 4-week shadow-mode pilot where the assist tool pre-populates IGeus transaction lookups and confirmation drafts; measure agent acceptance rate and actual time-on-task vs. baseline 25 min/ticket.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~2.8 (range [2, 3.3])
- **Root cause:** This is a designed B2B process gap, not a product bug: IGeus lacks an automated API or webhook integration with Zagrebparking's storno system, forcing manual transaction lookup and a two-person handoff to trigger refunds. A direct integration between Zagrebparking's cancellation system and IGeus could eliminate all manual steps.
- **Rationale:** Full automation requires a bilateral API integration with Zagrebparking's storno system and IGeus/Erste Bank's refund API, both of which are external dependencies outside Bmove's sole control; this is feasible but non-trivial. Hours eliminated are capped at the 3.3-hour baseline; the upper range equals full baseline elimination, the lower reflects partial automation still requiring human confirmation.
- **Validation:** Engineering should conduct a discovery spike (1 sprint) to confirm Zagrebparking exposes a machine-readable storno webhook and that IGeus/Erste Bank provides a refund API; effort estimate should be revised after spike findings.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0, 0])
- **Form:** `none`
- **Deflection rate:** ~0% (range [0%, 0%])
- **Feasibility:** 0.05
- **Rationale:** This pattern is initiated by a B2B partner (Zagrebparking) via formal storno notification, not by an end-user seeking self-service help; the trigger is an external business event that requires Bmove to act, so a FAQ or chatbot cannot deflect it. There is no end-user self-service path that would eliminate the incoming request.
- **Validation:** No pilot recommended; confirm via partner communication log review that 100% of tickets originate from Zagrebparking's operational system rather than end-user inquiry.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.3 (range [0.19, 0.35])
- **Narrow use case:** Auto-acknowledge receipt of Zagrebparking storno notification and log ticket number + IBAN, pending human approval before any refund is initiated
- **Safety constraints:**
  - No financial transaction (bank transfer or IGeus storno) may be initiated without human approval
  - IBAN validation must be performed before any data is stored or forwarded
  - Only well-structured, machine-readable storno notifications from verified Zagrebparking sender addresses may trigger automation
  - All automated actions must be fully auditable and reversible before the refund approval step
  - Croatian payment regulation (HNB guidelines) and GDPR handling of IBAN/personal data must be reviewed by compliance before deployment
- **Rationale:** Autonomous end-to-end refund processing carries significant financial and regulatory risk given Erste Bank involvement and Croatian banking rules; only the non-financial intake step (parsing and logging the storno notification) is a realistic candidate for autonomy at low volume. This saves roughly the first 5-minute receipt step on ~10% of tickets.
- **Validation:** Pilot with 3 manually-verified test storno notifications in staging; acceptance criteria: 100% correct IBAN capture, zero false-positive triggers, full audit log; expand only after compliance sign-off.

### Risks

- **Compliance concerns:**
  - Croatian National Bank (HNB) regulations govern bank transfer initiation; any automated refund flow must be reviewed for compliance
  - IBAN and personal financial data of end-users must be handled under GDPR; automated storage or forwarding requires a legal basis review
  - Erste Bank / IGeus may have contractual requirements mandating human authorisation for refund transactions
- **Must not automate:**
  - Initiation of any bank transfer or IGeus refund transaction without explicit human approval
  - IBAN routing decisions — incorrect routing causes financial loss and is difficult to reverse
  - The internal colleague approval/processing step (step 3), which may carry financial authorisation responsibility
- **Vendor dependencies blocking automation:**
  - Erste Bank / IGeus: no confirmed refund API exists; integration feasibility is unverified and typical_wait_days of 1 reflects manual bank processing timelines
  - Zagrebparking: no confirmed machine-readable storno webhook or API; partner cooperation required for any integration approach

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Financial action — agent drafts, human approves

