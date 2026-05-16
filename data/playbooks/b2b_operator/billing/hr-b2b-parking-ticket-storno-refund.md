---
id: hr-b2b-parking-ticket-storno-refund
name: hr_b2b_parking_ticket_storno_refund
title: B2B Partner Requests Parking Ticket Cancellation and Refund on Behalf of End User
description: B2B parking concession partners (koncesionari) submit storno (cancellation) requests to Bmove Support on behalf
  of end users who purchased incorrect or erroneous parking tickets via the Bmove application. The requests typically include
  the vehicle license plate, PIN or ticket number, and sometimes the reason (e.g., wrong plate entered, wrong zone/type selected).
  Bmove Support cancels the ticket in their system and processes the refund back to the user.
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
cluster_id: BS:b2b_partner|croatia|koncesionar:c2
project_key: BS
cluster_size: 19
cluster_size_dedup: 19
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.37
median_resolution_minutes: 4346.0
p95_resolution_minutes: 25260.899999999954
cannot_reproduce_rate: 0.0
data_window_start: '2023-06-26'
data_window_end: '2025-12-11'
annual_hours_saved: 0.4
roi:
  baseline_active_hours: 1.5
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.1
  deflection_hours_range:
  - 0.1
  - 0.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.4
  agent_assist_hours_range:
  - 0.3
  - 0.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.5
  product_fix_hours_range:
  - 0.4
  - 0.7
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.1
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-38433
- BS-12166
- BS-9571
- BS-11358
- BS-24619
- BS-30413
- BS-12164
- BS-13146
- BS-10648
- BS-40766
- BS-10442
- BS-11014
- BS-26489
- BS-11428
- BS-10659
- BS-12234
- BS-11404
- BS-46281
canonical_examples:
- BS-38433
- BS-10442
- BS-40766
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
  autonomous_resolve_narrow_use_case: Auto-process storno and refund for B2B partner requests that include a valid ticket
    number, matching plate, and reason code, submitted within a configurable time window (e.g., ≤ 30 minutes of purchase).
  autonomous_resolve_safety_constraints:
  - Refund transactions must be validated against payment gateway before autonomous execution
  - Only tickets purchased within a short configurable window (e.g., ≤ 30 min) are eligible to limit fraud exposure
  - Requests must include a verified B2B partner identifier (authenticated API key or session token)
  - Automatic ParkIS cancellation trigger requires confirmed bi-directional API integration with ParkIS
  - All autonomous actions must be logged with full audit trail for financial reconciliation
  - Tickets flagged as disputed or involving amounts above a defined threshold must route to a human agent
  - Human review required for any storno where plate or ticket number cannot be matched unambiguously
related_playbooks:
- austrian-ticketless-incorrect-charge-refund
- b2b-partner-parking-card-storno-refund
- croatia-b2b-parking-card-refund-request
- croatia-sms-parking-payment-failure
- croatian-b2b-parking-ticket-storno-refund
- croatian-b2b-parking-ticket-storno-request
- hr-b2b-parking-card-cancellation-refund
- hr-b2b-parking-card-storno-refund
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

# B2B Partner Requests Parking Ticket Cancellation and Refund on Behalf of End User

## What this pattern is

B2B parking concession partners (koncesionari) submit storno (cancellation) requests to Bmove Support on behalf of end users who purchased incorrect or erroneous parking tickets via the Bmove application. The requests typically include the vehicle license plate, PIN or ticket number, and sometimes the reason (e.g., wrong plate entered, wrong zone/type selected). Bmove Support cancels the ticket in their system and processes the refund back to the user.

## When this applies

- End user purchased a parking ticket with a wrong license plate
- End user purchased a wrong type of parking ticket (e.g., annual instead of PPK, wrong zone)
- B2B partner has already approved or processed the cancellation on their own system and requests Bmove to mirror the action
- End user requests cancellation directly from the concession partner, who then forwards the request to Bmove Support

## Typical resolution flow

1. B2B partner identifies an erroneous parking ticket purchase by an end user
2. B2B partner optionally cancels the ticket in their own ParkIS or internal system
3. B2B partner sends an email/ticket to Bmove Support with vehicle registration, ticket PIN or number, and cancellation reason
4. Bmove Support locates the ticket in their system
5. Bmove Support cancels (stornira) the parking ticket
6. Bmove Support initiates refund to the user's bank account or payment method
7. Bmove Support confirms cancellation and refund to the B2B partner via ticket comment

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Locate and cancel (storno) the parking ticket in Bmove system | Bmove Support agent | Bmove backend / IGeus | 10 min |
| Process refund to end user | Bmove Support agent | Bmove payment system | 5 min |
| Confirm cancellation and refund to B2B partner via ticket comment | Bmove Support agent | Support ticketing system | 3 min |
| Request B2B partner to also cancel ticket on their side in ParkIS to avoid reconciliation discrepancy | Bmove Support agent | Support ticketing system | 2 min |

## Evidence

Derived from 19 tickets in cluster `BS:b2b_partner|croatia|koncesionar:c2`. Direct quotes from 6 representative tickets:

- `BS-38433` _[hr]_: "Molim da poništite parkirnu kartu za vozilo 997RU i izvršite povrat sredstava korisniku. Mi smo u našem sustavu istu poništili."
- `BS-10442` _[hr]_: "Karta je izdana na krivu reg. oznaku."
- `BS-40766` _[hr]_: "korisnik je putem Bmove aplikacije greškom kupio godišnju kartu za zonu 3 umjesto PPK pa molim storno računa i povrat novca."
- `BS-10648` _[hr]_: "karta je poništena i novac je vraćen. Molimo da i Vi poništite tu kartu na svojoj strani u ParkIS sustavu. Ako ne možete, javite se u RAO kako ne bi nastala razlika na obračunu za ovaj mjesec."
- `BS-11358` _[hr]_: "Na zahtjev stranke odobrili smo storno, odnosno povrat za krivo kupljenu Dnevnu parkirnu kartu za period od 02.08.-03.08. za vozilo reg.oznaka QZD691MV sukladno transkciji u prilogu."
- `BS-12166` _[hr]_: "Molimo Vas storno parkirnih karata i povrat sredstava korisniku - RI****, PIN:8b7n7-uk16q-yuu"

## Cluster statistics

- **Volume:** 19 tickets total (19 unique semantic events after dedup)
- **Frequency:** 0.37 tickets/month (over data window 2023-06-26 → 2025-12-11)
- **Median resolution:** 3.0 days
- **Languages:** hr
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~1.5 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.4 (range [0.27, 0.49])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.70
- **Rationale:** The resolution workflow is highly templated — locate ticket, cancel, refund, send confirmation, request ParkIS cancellation — making it well-suited for an agent-assist tool that pre-populates the ticket lookup, drafts the confirmation comment, and generates the ParkIS reminder message. Time savings are modest in absolute hours given low annual frequency, but per-ticket efficiency gains are meaningful.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-drafts confirmation comments and ParkIS reminders; measure agent acceptance rate and compare actual handle time against the 20-minute baseline using a paired sample.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~2 (range [1.4, 2.6])
- **Hours eliminated per year:** ~0.5 (range [0.371, 0.689])
- **Root cause:** Root cause is end-user error at ticket-purchase time (wrong plate, wrong zone/type) in the Bmove app, not a software defect. The cancellation workflow is a designed support process. A UX improvement — such as a confirmation screen with plate/zone/type summary before purchase — could reduce error rates upstream.
- **Rationale:** Adding a pre-purchase confirmation screen in the Bmove app could reduce erroneous ticket purchases, shrinking the volume of storno requests; however, some errors (e.g., typos not caught by the user on review) will persist, so full elimination is not expected. The eliminated-hours ceiling is capped at the 1.5 h baseline.
- **Validation:** Engineering team should instrument error-reason data on storno tickets for 2–3 months to quantify what fraction of errors a confirmation screen would catch, then size the sprint effort against that yield; A/B test the UX change against a control cohort.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.056, 0.104])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These requests are submitted by authenticated B2B partners acting on behalf of end users, requiring back-end system access to cancel tickets and process refunds — tasks that cannot be completed through self-service FAQs or chatbots without deep system integration. The end user has no direct channel and the partner's role as intermediary makes self-service deflection structurally infeasible.
- **Validation:** Deploy a partner-facing help article explaining the storno process for 4 weeks and measure whether inbound ticket volume decreases; if submission format errors (e.g., missing PIN) also drop, that partial benefit can be counted separately.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.1 (range [0.077, 0.143])
- **Narrow use case:** Auto-process storno and refund for B2B partner requests that include a valid ticket number, matching plate, and reason code, submitted within a configurable time window (e.g., ≤ 30 minutes of purchase).
- **Safety constraints:**
  - Refund transactions must be validated against payment gateway before autonomous execution
  - Only tickets purchased within a short configurable window (e.g., ≤ 30 min) are eligible to limit fraud exposure
  - Requests must include a verified B2B partner identifier (authenticated API key or session token)
  - Automatic ParkIS cancellation trigger requires confirmed bi-directional API integration with ParkIS
  - All autonomous actions must be logged with full audit trail for financial reconciliation
  - Tickets flagged as disputed or involving amounts above a defined threshold must route to a human agent
  - Human review required for any storno where plate or ticket number cannot be matched unambiguously
- **Rationale:** Full autonomous resolution requires system-to-system integration with both Bmove and ParkIS, plus secure B2B partner authentication, making technical prerequisites significant relative to the low annual ticket volume (4.5/year). At a conservative 15% safe automation rate, the absolute hours saved are minimal (~0.11 h/year), so ROI depends on whether the integration infrastructure delivers value across other patterns.
- **Validation:** Pilot with a single B2B partner via authenticated API for 60 days, targeting only requests with complete structured data (ticket number + plate + reason code); acceptance criteria: zero erroneous refunds, 100% ParkIS sync confirmation, audit log completeness verified by finance team.

### Risks

- **Compliance concerns:**
  - Refund processing must comply with applicable payment card industry (PCI-DSS) rules and local consumer protection regulations governing cancellation rights
  - Financial audit trail is required for all storno and refund transactions; any automation must preserve complete, tamper-evident logs
  - B2B partner authentication must meet data-access control requirements to prevent unauthorized cancellations on behalf of users
- **Must not automate:**
  - Storno requests where the ticket number or plate cannot be unambiguously matched in the Bmove system
  - Requests involving amounts above a defined financial threshold without human sign-off
  - Cases where the stated reason is ambiguous or potentially indicates fraud (e.g., repeated cancellations by same partner for same plate)
  - ParkIS-side cancellation instruction without confirmed API acknowledgment from ParkIS
- **Vendor dependencies blocking automation:**
  - No external vendor dependency identified; however, bi-directional API integration with ParkIS (partner system) is a prerequisite for any autonomous or semi-autonomous workflow — absence of a stable ParkIS API blocks full automation

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Financial action — agent drafts, human approves

