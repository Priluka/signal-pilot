---
id: b2b-partner-parking-card-storno-refund
name: b2b_partner_parking_card_storno_refund
title: B2B Partner Requests Storno and/or Refund for Incorrectly Purchased Parking Cards
description: B2B parking concession partners (komunalna poduzeća, parking operators) contact Bmove support to request cancellation
  (storno) of incorrectly purchased or erroneous parking cards on behalf of their end users. The root causes include wrong
  dates, duplicate purchases, wrong period, or already-paid parking. In most cases, a monetary refund to the user's bank account
  follows the storno action, sometimes requiring the user's IBAN for Erste/KeksPay transactions.
category: b2b_operator/billing
ticket_class: b2b_partner
issue_category: billing
resolution_pattern: refund_issued
languages:
- hr
country_focus:
- hr
- other
status: active
cluster_id: BS:b2b_partner|no_value|koncesionar:c1
project_key: BS
cluster_size: 45
cluster_size_dedup: 45
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.88
median_resolution_minutes: 153.0
p95_resolution_minutes: 24447.59999999998
cannot_reproduce_rate: 0.0
data_window_start: '2022-02-23'
data_window_end: '2023-04-14'
annual_hours_saved: 1.6
roi:
  baseline_active_hours: 6.2
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.2
  deflection_hours_range:
  - 0.1
  - 0.2
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.6
  agent_assist_hours_range:
  - 1.1
  - 2.0
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.5
  product_fix_hours_range:
  - 1.8
  - 3.2
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.3
  autonomous_resolve_hours_range:
  - 0.2
  - 0.5
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-499
- BS-192
- BS-6533
- BS-205
- BS-429
- BS-1084
- BS-3167
- BS-6049
- BS-86
- BS-7435
- BS-79
- BS-452
- BS-174
- BS-571
- BS-195
- BS-141
- BS-3169
- BS-2174
canonical_examples:
- BS-6533
- BS-3167
- BS-2174
vendor_dependency:
  vendor_name: Erste Bank / KeksPay
  involves_vendor: true
  typical_wait_days: 3
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Financial action — agent drafts, human approves
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Automated duplicate-purchase detection with immediate self-service cancellation within
    a 15-minute window post-purchase, before refund processing is required
  autonomous_resolve_safety_constraints:
  - Monetary refund to end-user bank account must never be triggered without human finance approval
  - IBAN collection and verification must remain human-in-the-loop due to fraud and data-accuracy risk
  - Storno in ParkIS must only be auto-executed for clear duplicate transactions identified by system ID match, not by free-text
    partner description
  - Any autonomous action touching Erste Bank / KeksPay must comply with applicable Croatian payment regulations and Erste
    API authorization requirements
  - B2B partner identity must be verified before any cancellation is processed
related_playbooks:
- austrian-ticketless-incorrect-charge-refund
- b2b-parking-invoice-payment-issues
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
- zagrebparking-b2b-storno-refund-request
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# B2B Partner Requests Storno and/or Refund for Incorrectly Purchased Parking Cards

## What this pattern is

B2B parking concession partners (komunalna poduzeća, parking operators) contact Bmove support to request cancellation (storno) of incorrectly purchased or erroneous parking cards on behalf of their end users. The root causes include wrong dates, duplicate purchases, wrong period, or already-paid parking. In most cases, a monetary refund to the user's bank account follows the storno action, sometimes requiring the user's IBAN for Erste/KeksPay transactions.

## When this applies

- End user purchased a parking card for the wrong date or period
- End user purchased a duplicate parking card
- End user had already paid parking but was issued a daily ticket (DPK)
- B2B partner identifies erroneous transaction in ParkIS or Bmove system
- Card was auto-cancelled by the system due to lack of timely confirmation
- End user submits complaint/prigovor to the B2B partner who escalates to Bmove

## Typical resolution flow

1. B2B partner receives complaint from end user about erroneous parking card purchase
2. B2B partner contacts Bmove support via email requesting storno and/or refund
3. Bmove support locates the transaction in the system (Bmove/ParkIS/iGeUS)
4. Bmove support cancels (stornira) the parking card
5. If Erste/KeksPay transaction, Bmove requests IBAN from B2B partner or end user
6. Bmove processes monetary refund to user's bank account
7. Bmove notifies B2B partner that storno and refund are completed
8. B2B partner may be asked to storno on their side in ParkIS as well
9. User receives funds within 1-3 business days

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Cancel (stornirati) the parking card in the Bmove/ParkIS system | Bmove support agent | Bmove backend / ParkIS / IGeus | 10 min |
| Request IBAN from B2B partner for Erste/KeksPay transactions | Bmove support agent | email | 5 min |
| Process monetary refund to end user's bank account | Bmove finance/support agent | Bmove payment system / Erste banking | 15 min |
| Notify B2B partner that storno and refund are completed | Bmove support agent | email / Jira | 5 min |

## Vendor dependency

- **Vendor:** Erste Bank / KeksPay
- **Typical wait:** 3 day(s)

## Evidence

Derived from 45 tickets in cluster `BS:b2b_partner|no_value|koncesionar:c1`. Direct quotes from 6 representative tickets:

- `BS-6533` _[hr]_: "Karte su stornirane i novac je vraćen korisnici na bankovni račun."
- `BS-3167` _[hr]_: "Navedene karte su poništene i novac je vraćen korisnici. Novac će korisnici biti vidljiv na bankovnom računu za 1-3 radna dana."
- `BS-2174` _[hr]_: "Ako je Erste transakcija u pitanju (KeksPay), tada nam morate poslati i IBAN korisnika kako bismo odradili povrat."
- `BS-1084` _[hr]_: "Izvršen je storno krivo kupljene Komercijalne parkirne karte br.949 za vozilo ČK323IS VLASNIKA VOZILA Marka Opačaka koju je korisnik greškom kupio za cijelu sezonu u iznosu 400 kuna i korisniku je izv"
- `BS-6049` _[hr]_: "Kupovina je bila u 12:44 i automatizmom je stornirana u 12:46 jer nije bila pravovremeno potvrđena na strani pružatelja usluge."
- `BS-141` _[hr]_: "Karta je poništena, samo trebamo podatke korisnice za povrat jer se radi o Erste transakciji. Dakle osim imena i prezimena korisnice, trebamo i IBAN na koji ćemo izvršiti povrat."

## Cluster statistics

- **Volume:** 45 tickets total (45 unique semantic events after dedup)
- **Frequency:** 0.88 tickets/month (over data window 2022-02-23 → 2023-04-14)
- **Median resolution:** 2.5 hours
- **Languages:** hr
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~6.2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.6 (range [1.12, 2.015])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** The resolution workflow is highly structured (storno in ParkIS → collect IBAN → process refund → notify partner), making it well-suited for a guided checklist or pre-filled response templates that reduce lookup and drafting time; estimated 25% active-time reduction reflects acceleration of steps 2 and 4 (IBAN request and partner notification) while steps 1 and 3 remain human-executed.
- **Validation:** Deploy shadow-mode agent-assist templates for IBAN request and closure notification messages over 4 weeks; measure agent acceptance rate and compare per-ticket active time against the 35-minute baseline using time-tracking in the support tool.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~2.5 (range [1.75, 3.25])
- **Root cause:** Root cause is user/operator error at purchase time (wrong date, duplicate purchase, wrong period) rather than a system defect. A confirmation-flow improvement in the B2B purchase UI — e.g., explicit date/period review screen, duplicate-purchase warning, and undo window — could prevent a meaningful share of erroneous purchases before they require storno.
- **Rationale:** Improved purchase confirmation UX and a short self-service cancellation window (e.g., 15-minute undo) could eliminate roughly 35–60% of storno requests; estimate is directional because actual prevention rate depends on partner adoption and error-type distribution within the 45-ticket cluster. Hours eliminated are capped below the 6.2-hour baseline.
- **Validation:** Engineering team should audit the 45 tickets for root-cause breakdown (wrong date vs. duplicate vs. wrong period); instrument a prototype confirmation modal in staging and run usability testing with 2–3 B2B partner accounts to estimate error reduction before committing to full build.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.2 (range [0.126, 0.234])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These are B2B partner-initiated requests requiring privileged access to ParkIS/Bmove to execute cancellations and coordinate bank refunds; end users and partners cannot self-serve these actions without system access. FAQ or help-center content could marginally reduce clarification back-and-forth but will not deflect the core ticket.
- **Validation:** Publish a structured storno-request submission guide for B2B partners with required fields (IBAN, ticket ID, reason code) and measure over 8 weeks whether average back-and-forth messages per ticket decreases; track deflection rate as tickets where partner resolves without contacting support.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.3 (range [0.245, 0.455])
- **Narrow use case:** Automated duplicate-purchase detection with immediate self-service cancellation within a 15-minute window post-purchase, before refund processing is required
- **Safety constraints:**
  - Monetary refund to end-user bank account must never be triggered without human finance approval
  - IBAN collection and verification must remain human-in-the-loop due to fraud and data-accuracy risk
  - Storno in ParkIS must only be auto-executed for clear duplicate transactions identified by system ID match, not by free-text partner description
  - Any autonomous action touching Erste Bank / KeksPay must comply with applicable Croatian payment regulations and Erste API authorization requirements
  - B2B partner identity must be verified before any cancellation is processed
- **Rationale:** Full autonomous resolution is not feasible due to the mandatory human-approved bank refund step and vendor dependency on Erste/KeksPay; a narrow auto-cancellation path for confirmed duplicates within a short undo window is the only safe scope, covering an estimated 10% of tickets at most. Savings are modest given the low annual frequency.
- **Validation:** Pilot with 2 willing B2B partners over 8 weeks: instrument ParkIS to flag same-partner duplicate card purchases within 15 minutes and surface an auto-storno prompt requiring one-click partner confirmation; measure false-positive rate and ensure zero instances of unchecked refund initiation before expanding scope.

### Risks

- **Compliance concerns:**
  - Monetary refunds to Croatian bank accounts via Erste Bank / KeksPay are subject to Croatian payment services regulations (ZPU) and PSD2; any automated refund flow must be reviewed by a compliance officer
  - Collection and storage of end-user IBANs constitutes processing of financial personal data under GDPR; data minimisation and retention limits must be enforced
  - Storno of parking cards may have legal and fiscal implications (VAT correction, fiscalisation obligations under Croatian law) that require human sign-off
- **Must not automate:**
  - Initiation or execution of bank refund transfers without explicit human finance-team approval
  - Collection or transmission of end-user IBAN data through unverified or unauthenticated channels
  - Cancellation of parking cards based solely on free-text partner request without system-level verification of transaction ID
- **Vendor dependencies blocking automation:**
  - Erste Bank / KeksPay refund processing has a typical wait of 3 days and requires manual coordination; no API for fully automated refund initiation is confirmed available, blocking autonomous end-to-end resolution
  - Any automation touching KeksPay transactions requires explicit API access agreement and security review with Erste Bank

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Financial action — agent drafts, human approves

