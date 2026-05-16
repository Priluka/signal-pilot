---
id: zagreb-parking-cancelled-ticket-refund
name: zagreb_parking_cancelled_ticket_refund
title: Zagreb Parking (Zagrebparking) – Refund request for cancelled/erroneously purchased parking tickets
description: B2B partner (Zagrebparking) submits refund requests on behalf of end-users who accidentally purchased parking
  tickets (hourly, weekly, or monthly) via the Bmove/KEKS Pay app. The partner cancels the ticket in their IGeus back-office
  system and then requests that the payment processor (Erste Bank) reverses the original transaction to the customer's IBAN.
  Resolution is consistently a manual refund execution followed by confirmation.
category: b2b_operator/billing
ticket_class: b2b_partner
issue_category: billing
resolution_pattern: refund_issued
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:b2b_partner|no_value|storno:c1
project_key: BS
cluster_size: 17
cluster_size_dedup: 17
sample_size_used: 17
extraction_schema: v1.0
extraction_confidence: 0.98
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.33
median_resolution_minutes: 2903.0
p95_resolution_minutes: 8882.2
cannot_reproduce_rate: 0.0
data_window_start: '2022-02-17'
data_window_end: '2022-09-05'
annual_hours_saved: 0.2
roi:
  baseline_active_hours: 0.7
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.0
  deflection_hours_range:
  - 0.0
  - 0.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.2
  agent_assist_hours_range:
  - 0.1
  - 0.2
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.3
  product_fix_hours_range:
  - 0.2
  - 0.5
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.1
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-1938
- BS-348
- BS-419
- BS-437
- BS-49
- BS-50
- BS-523
- BS-675
- BS-427
- BS-444
- BS-283
- BS-592
- BS-432
- BS-1720
- BS-185
- BS-389
- BS-818
canonical_examples:
- BS-348
- BS-675
- BS-1720
vendor_dependency:
  vendor_name: Erste Bank
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Financial action — agent drafts, human approves
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-route a validated refund request (with confirmed Erste transaction code and IBAN)
    directly to the internal finance queue without manual agent tagging
  autonomous_resolve_safety_constraints:
  - No autonomous execution of bank refund transactions; Erste Bank reversal must remain human-authorized
  - IBAN and transaction code must be validated against a structured schema before any routing action
  - Automated routing only; no autonomous closure of tickets without human confirmation of refund completion
  - All actions must be fully logged for audit trail given financial transaction context
  - Partner identity (Zagrebparking) must be verified before automated routing proceeds
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
- zagrebparking-b2b-storno-refund-request
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Zagreb Parking (Zagrebparking) – Refund request for cancelled/erroneously purchased parking tickets

## What this pattern is

B2B partner (Zagrebparking) submits refund requests on behalf of end-users who accidentally purchased parking tickets (hourly, weekly, or monthly) via the Bmove/KEKS Pay app. The partner cancels the ticket in their IGeus back-office system and then requests that the payment processor (Erste Bank) reverses the original transaction to the customer's IBAN. Resolution is consistently a manual refund execution followed by confirmation.

## When this applies

- End-user purchases a parking ticket (hourly, weekly, or monthly) in error via the Bmove/KEKS Pay app
- Zagrebparking cancels/voids the ticket in their IGeus back-office system
- Partner submits a refund request to Bmove Support with the Erste transaction code and customer IBAN

## Typical resolution flow

1. Zagrebparking receives a complaint from the end-user about an erroneous parking ticket purchase
2. Zagrebparking voids/cancels the ticket in IGeus back-office
3. Zagrebparking emails Bmove Support with the refund request, including transaction code, amount, zone, vehicle plate, and customer IBAN
4. Bmove support agent tags Lidija Petricević (and sometimes Anamaria Žigman) in the ticket with refund details
5. Refund is executed via Erste Bank back to the customer's IBAN
6. Ticket is resolved with confirmation that the ticket is cancelled and money has been returned to the customer

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Cancel/void the parking ticket in the IGeus back-office system | Zagrebparking partner agent | IGeus | — |
| Submit refund request with Erste transaction code and customer IBAN | Zagrebparking partner agent | Bmove Support ticketing system | — |
| Tag internal refund processor (Lidija Petricević / Anamaria Žigman) with full refund details | Bmove support agent | Bmove Support ticketing system | 5 min |
| Execute bank refund to customer IBAN via Erste Bank transaction reversal | Lidija Petricević / Anamaria Žigman (internal finance/accounting role) | Erste Bank back-office | — |
| Confirm refund completion and close ticket | Bmove support agent or partner | Bmove Support ticketing system | 5 min |

## Vendor dependency

- **Vendor:** Erste Bank

## Evidence

Derived from 17 tickets in cluster `BS:b2b_partner|no_value|storno:c1`. Direct quotes from 5 representative tickets:

- `BS-348` _[hr]_: "Molim izvršiti povrat sredstava pogrešno kupljene KPK u iznosu od 360,00kn. Karta je kod nas poništena."
- `BS-675` _[hr]_: "molim te povrat od 90kn za Erste transakciju tvvwh-yttg7-t2f (Tjedna parkirališna karta; Zona 2; Zagreb, reg. oznaka ZG****). Transakcija je stornirana u IGeusu."
- `BS-1720` _[hr]_: "Poništili smo karte 4876005 i 4876706. Molim izvršiti povrat 24 kn. Uplate su izvršene putem aplikacije Keks Pay"
- `BS-49` _[hr]_: "Novac je vraćen korisniku. Poštovani, parkirna karta je poništena s naše strane i novac je vraćen."
- `BS-1938` _[hr]_: "molim te povrat u iznosu od 24kn za dvije Erste transakcije po 12kn (Satna parkirališna karta; Zona 1; Zagreb, reg. oznaka ST6531-I). Karte su poništene u IGeusu."

## Cluster statistics

- **Volume:** 17 tickets total (17 unique semantic events after dedup)
- **Frequency:** 0.33 tickets/month (over data window 2022-02-17 → 2022-09-05)
- **Median resolution:** 2.0 days
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~0.7 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.2 (range [0.13, 0.23])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.65
- **Rationale:** The two Bmove-agent steps (tagging internal processor with refund details and confirming closure) are highly templated and structured, making them strong candidates for auto-drafted messages and pre-filled routing; however, the total active time per ticket is only 10 minutes, limiting absolute savings. A pre-populated routing template with IBAN, transaction code, and partner details could reduce the tagging step from ~5 minutes to ~2-3 minutes.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool drafts the internal tagging message and closure confirmation; measure draft-acceptance rate and actual time-on-task versus the 5-minute baseline for each step.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~2 (range [1.4, 2.6])
- **Hours eliminated per year:** ~0.3 (range [0.245, 0.455])
- **Root cause:** Root cause is user error in purchasing incorrect parking tickets via the Bmove/KEKS Pay app; there is no documented software defect, but adding an in-app confirmation step or a short cancellation window (e.g., 5-minute self-cancel) could reduce erroneous purchases reaching the refund workflow.
- **Rationale:** A purchase-confirmation prompt or a brief self-cancel window in the app could prevent a meaningful share of accidental purchases before they require a refund; however, given the B2B partner intermediary and the bank reversal requirement, some volume will persist regardless. Hours eliminated are capped at the 0.7-hour baseline and reflect an estimated 50% reduction in incident volume at midpoint.
- **Validation:** Engineering team should instrument the app to capture drop-off and error rates at the ticket-purchase confirmation screen; A/B test a confirmation dialog for 4 weeks to measure reduction in refund-request tickets before committing full sprint allocation.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0.021, 0.039])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** Refund requests originate from a B2B partner (Zagrebparking) acting on behalf of end-users and require manual execution via Erste Bank; no amount of self-service content eliminates the need for partner-initiated action and internal finance involvement. A help-center article or FAQ cannot deflect a workflow that is inherently partner-driven and requires bank transaction reversal.
- **Validation:** Deploy a structured refund-request submission form for Zagrebparking agents for 4 weeks and measure whether it reduces back-and-forth clarification steps; savings would come from reduced rework, not true deflection.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.1 (range [0.049, 0.091])
- **Narrow use case:** Auto-route a validated refund request (with confirmed Erste transaction code and IBAN) directly to the internal finance queue without manual agent tagging
- **Safety constraints:**
  - No autonomous execution of bank refund transactions; Erste Bank reversal must remain human-authorized
  - IBAN and transaction code must be validated against a structured schema before any routing action
  - Automated routing only; no autonomous closure of tickets without human confirmation of refund completion
  - All actions must be fully logged for audit trail given financial transaction context
  - Partner identity (Zagrebparking) must be verified before automated routing proceeds
- **Rationale:** Full autonomous resolution is infeasible because the core action—executing a bank refund via Erste Bank—requires human financial authorization and cannot be safely delegated to automation at this volume or maturity level. The only automation-safe scope is intelligent routing of the validated request to the finance queue, saving a small fraction of the already-short active time.
- **Validation:** Pilot automated routing for 4 weeks on 100% of incoming Zagrebparking refund requests; acceptance criterion is zero mis-routed tickets and measurable reduction in agent time-on-task for the tagging step, with all routed tickets reviewed by finance before bank execution.

### Risks

- **Compliance concerns:**
  - Bank transaction reversals (IBAN-based refunds via Erste Bank) are subject to Croatian financial regulations and PSD2 requirements; any automation touching the payment reversal step requires legal and compliance review
  - Customer IBAN data must be handled in accordance with GDPR; automated pipelines processing IBAN must have appropriate data-minimization and retention controls
  - Audit trail requirements: all refund-related actions must be logged and attributable to a named human approver for financial accountability
- **Must not automate:**
  - Execution of bank refund transactions to customer IBANs — must remain human-authorized by named finance personnel
  - Validation that a parking ticket was genuinely purchased in error — requires partner-side confirmation from Zagrebparking
  - Final ticket closure without confirmed refund receipt — risks closing tickets on unexecuted refunds
- **Vendor dependencies blocking automation:**
  - Erste Bank: all payment reversals depend on Erste Bank's transaction reversal API or manual process; no automation of the refund execution step is possible without Erste Bank's explicit API support and contractual authorization
  - IGeus back-office system: ticket cancellation step is performed by Zagrebparking in their own system; Bmove has no direct integration or control over this step

## Agent compatibility

- **Status:** `active` (extraction confidence 0.98)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Financial action — agent drafts, human approves

