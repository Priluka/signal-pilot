---
id: hr-b2b-sms-parking-and-ddpk-issues
name: hr_b2b_sms_parking_and_ddpk_issues
title: Croatian B2B Partner SMS Parking Payment Anomalies and Digital Penalty Ticket (DDPK) Issues
description: B2B parking operator partners in Croatia report recurring problems with SMS-based parking payments, including
  failed transactions, incorrect validity periods shown in confirmation messages, payments not visible to enforcement controllers,
  and delayed/missing SMS notifications. A secondary pattern involves Digital Penalty Ticket (DDPK) issues such as incorrect
  amounts, missing print data, billing discrepancies, and feature requests for DDPK workflow improvements.
category: b2b_operator/integrations
ticket_class: b2b_partner
issue_category: integration_issue
resolution_pattern: vendor_escalation
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:b2b_partner|Support|duplikat:c3
project_key: RAOS
cluster_size: 53
cluster_size_dedup: 53
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.87
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.59
median_resolution_minutes: 1138.0
p95_resolution_minutes: 23508.19999999998
cannot_reproduce_rate: 0.0
data_window_start: '2025-03-04'
data_window_end: '2026-04-13'
annual_hours_saved: 18.1
roi:
  baseline_active_hours: 72.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 7.2
  deflection_hours_range:
  - 5.1
  - 9.4
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 18.1
  agent_assist_hours_range:
  - 13.0
  - 23.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 43.4
  product_fix_hours_range:
  - 30.4
  - 56.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 2.2
  autonomous_resolve_hours_range:
  - 1.5
  - 2.8
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-2684
- RAOS-6151
- RAOS-2573
- RAOS-2148
- RAOS-2280
- RAOS-3617
- RAOS-4840
- RAOS-2598
- RAOS-1923
- RAOS-4114
- RAOS-6835
- RAOS-3277
- RAOS-5169
- RAOS-6113
- RAOS-2377
- RAOS-2189
- RAOS-3098
- RAOS-4121
canonical_examples:
- RAOS-2684
- RAOS-1923
- RAOS-4840
vendor_dependency:
  vendor_name: HT (Hrvatski Telekom) / T-com / A1 / Telemach (mobile operators)
  involves_vendor: true
  typical_wait_days: 3
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-acknowledge DDPK void/cancel requests where partner confirms cancellation intent
    and system confirms ticket not yet printed or enforced — routing confirmation back without agent involvement.
  autonomous_resolve_safety_constraints:
  - Never autonomously escalate to mobile operators (HT/A1/Telemach) without agent review — incorrect escalations damage partner
    relationships.
  - Never autonomously confirm a DDPK as cancelled without verifying enforcement-system status via API; incorrect confirmation
    could create legal liability.
  - Any ticket involving a payment dispute or billing discrepancy must be routed to a human agent before any response is sent.
  - Autonomous handling must not apply when vendor-side SMS outage is suspected — these require manual triage against operator
    status pages.
  - All autonomous actions must be logged and reviewable for Croatian B2B compliance audit purposes.
related_playbooks:
- dubrovnik-pass-website-hours-notice-posting
- dubrovnik-pass-website-notice-management
- hr-b2b-case-status-and-data-correction
- hr-b2b-monthly-invoice-generation-and-fiscalization
- hr-b2b-parking-operations-support
- hr-b2b-parking-price-change-request
- hr-b2b-photo-download-enablement
- hr-b2b-user-account-management
- hr-parking-sms-payment-visibility-issue
- hr-sms-parking-payment-issues
- kml-polygon-upload-correction-hr
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Croatian B2B Partner SMS Parking Payment Anomalies and Digital Penalty Ticket (DDPK) Issues

## What this pattern is

B2B parking operator partners in Croatia report recurring problems with SMS-based parking payments, including failed transactions, incorrect validity periods shown in confirmation messages, payments not visible to enforcement controllers, and delayed/missing SMS notifications. A secondary pattern involves Digital Penalty Ticket (DDPK) issues such as incorrect amounts, missing print data, billing discrepancies, and feature requests for DDPK workflow improvements.

## When this applies

- SMS parking payment not appearing as valid in enforcement controller app
- Incorrect validity period displayed in SMS confirmation message to end user
- SMS transaction rejected with NOK-PO status by parking operator
- SMS payments being processed outside configured working hours
- SMS service outage for one or more mobile operators (HT/T-com, A1)
- Delayed or missing SMS expiry notification to user
- DDPK issued with incorrect amount (wrong zone/article selected)
- DDPK missing validity time information on printout
- DDPK cannot be charged at cashier with partial amount
- Transaction visible in Parkis but missing in Igeus system
- Feature request for automated DDPK digital invoice workflow

## Typical resolution flow

1. B2B partner receives end-user complaint or notices system anomaly
2. Partner opens support ticket with Parkis/RAO support team, often attaching screenshots or transaction details
3. Support team requests additional details (registration plates, transaction times, SMS operator name)
4. Support team checks transaction logs in Parkis/m-uplate system
5. Issue is diagnosed as operator-side rejection (NOK-PO), HT/operator service outage, system misconfiguration, or display bug
6. If vendor-related, issue is escalated to HT or relevant mobile operator
7. If system bug, fix is applied and monitored
8. If DDPK, investigation identifies operator error or hardware fault (e.g., missing printer fonts)
9. Resolution communicated to partner; ticket closed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Check SMS transaction logs and status in Parkis/m-uplate system | RAO support agent | ParkIS / m-uplate | 15 min |
| Request additional details from partner (registration, time, operator) | RAO support agent | Jira/ticketing system | 5 min |
| Escalate SMS service outage or confirmation failure to mobile operator (HT/A1) | RAO support agent | email / phone | 20 min |
| Advise partner to cancel/void incorrectly issued DDPK | RAO support agent | ParkIS | 10 min |
| Identify and fix system misconfiguration (e.g., working hours, font installation on printer) | RAO technical team / support agent | Business administration panel / printer | 30 min |
| Confirm DDPK development completion and arrange integration meeting with partner and Subnet | RAO development team | POINT / Jira | 60 min |

## Vendor dependency

- **Vendor:** HT (Hrvatski Telekom) / T-com / A1 / Telemach (mobile operators)
- **Typical wait:** 3 day(s)

## Evidence

Derived from 53 tickets in cluster `RAOS:b2b_partner|Support|duplikat:c3`. Direct quotes from 10 representative tickets:

- `RAOS-2684` _[hr]_: "Korisnica je platila parkirnu kartu putem sms-a 29.03.2025 te je od operatera dobila povratnu poruku da joj parkirna karta vrijedi do 21.04."
- `RAOS-1923` _[hr]_: "karta s naše strane nije naplaćena jer je u statusu NOK-PO što znači da je odbijena od strane parkirnog operatera."
- `RAOS-4840` _[hr]_: "Opet se SMS-ovi naplaćuju izvan radnog vremena od nekakvog ažuriranja aplikacije prije par dana, tj. prebacuje važenje na idući dan čak i prije isteka radnog vremena."
- `RAOS-3098` _[hr]_: "Kolegi nisu bile vidljive sms uplate prilikom kontrole parkinga te je za iste i ispisao kaznu."
- `RAOS-6113` _[hr]_: "Zatvaramo zahtjev nastavno na otklanjanje poteškoća od strane HT-a."
- `RAOS-5169` _[hr]_: "navedeni problem je bio vezan uz servis operatera i nažalost nismo u mogućnosti utjecati na rad njihovih sustava."
- `RAOS-2598` _[hr]_: "Jedina mogućnost za naplatom DPK u iznosu 22.00 EUR je da kontrolor prilikom izdavanja DPK greškom u koraku odabira artikle te broja DPK, odabere artikl DPK ZONA - DVA MJESTA."
- `RAOS-2280` _[hr]_: "Navedeni problem je nastao zbog toga što na printeru fale određeni fontovi."
- `RAOS-6151` _[hr]_: "u Parkisu su vidljive tri uplate dok ih u Igeusu nema, već samo dvije."
- `RAOS-2573` _[hr]_: "s naše strane razvoj je završen. U narednom periodu javit ćemo vam se radi dogovora online sastanka s vama i Subnetom"

## Cluster statistics

- **Volume:** 53 tickets total (53 unique semantic events after dedup)
- **Frequency:** 2.59 tickets/month (over data window 2025-03-04 → 2026-04-13)
- **Median resolution:** 19.0 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~72.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~18.1 (range [13, 23.53])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** Agent assist can meaningfully accelerate the structured, repeatable steps — log lookup prompts, vendor escalation email drafting, DDPK void guidance — reducing time on steps 1–4 by pre-populating templates and surfacing relevant runbooks; steps 5–6 involve technical judgment and coordination that resist templating. A 25% time reduction across the 140-minute active baseline is conservative given the multi-step, vendor-dependent nature of resolutions.
- **Validation:** Run shadow-mode assist (pre-populated log-check checklist, escalation email draft, DDPK cancel script) alongside live agents for 3 weeks on Croatian B2B SMS/DDPK tickets; measure actual handle-time delta against matched control tickets.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~5 (range [3.5, 6.5])
- **Hours eliminated per year:** ~43.4 (range [30.4, 56.4])
- **Root cause:** Multiple partially distinct issues: (1) SMS confirmation messages showing incorrect validity periods suggest a data-mapping or timezone/offset bug in the Parkis/m-uplate notification template layer; (2) payments not visible to enforcement controllers indicate a sync or replication lag between payment processor and enforcement API; (3) DDPK incorrect amounts and missing print data suggest configuration or data-population bugs in the DDPK generation module. These are recurring, reproducible failure modes rather than one-off edge cases.
- **Rationale:** A comprehensive fix addressing SMS template data-mapping, enforcement visibility sync, and DDPK amount/print-data bugs could eliminate the majority of recurring tickets, but the involvement of multiple external mobile operators and a separate Subnet integration means some residual coordination overhead will persist even after product fixes. Estimated elimination covers ~60% of baseline hours, leaving ~40% for novel edge cases and vendor-side issues.
- **Validation:** Engineering team should instrument Parkis/m-uplate SMS confirmation pipeline and DDPK generation endpoints with end-to-end trace logging, reproduce three documented failure cases in a staging environment, and conduct a 2-sprint spike to scope fixes before committing to full effort estimate.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~7.2 (range [5.1, 9.36])
- **Form:** `help_center`
- **Deflection rate:** ~10% (range [7%, 13%])
- **Feasibility:** 0.35
- **Rationale:** Most tickets involve live transaction failures or vendor-dependent SMS outages that require log access beyond self-service; however, a help-center article covering common DDPK void/cancel steps and SMS troubleshooting checklist could deflect a small share of informational inquiries from less technical partner staff. Deflection potential is limited because the root cause almost always requires backend log checks or vendor escalation.
- **Validation:** Publish a structured help-center article covering DDPK cancellation steps and SMS failure checklist, then track inbound ticket volume from Croatian B2B partners over a 6-week period; compare submission rate before and after to estimate deflection.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~2.2 (range [1.54, 2.8])
- **Narrow use case:** Auto-acknowledge DDPK void/cancel requests where partner confirms cancellation intent and system confirms ticket not yet printed or enforced — routing confirmation back without agent involvement.
- **Safety constraints:**
  - Never autonomously escalate to mobile operators (HT/A1/Telemach) without agent review — incorrect escalations damage partner relationships.
  - Never autonomously confirm a DDPK as cancelled without verifying enforcement-system status via API; incorrect confirmation could create legal liability.
  - Any ticket involving a payment dispute or billing discrepancy must be routed to a human agent before any response is sent.
  - Autonomous handling must not apply when vendor-side SMS outage is suspected — these require manual triage against operator status pages.
  - All autonomous actions must be logged and reviewable for Croatian B2B compliance audit purposes.
- **Rationale:** The vast majority of tickets in this cluster require live system log access, vendor coordination, or judgment calls about enforcement legality, making full autonomous resolution unsafe at scale; the narrow DDPK cancel-acknowledgement use case is the only sub-flow with low enough risk for limited automation, but it represents a small share of volume. Savings are modest and the primary value is agent time on the simplest case, not broad deflection.
- **Validation:** Pilot on a maximum of 3–4 tickets/month (≈10% of annual volume) where DDPK cancel intent is unambiguous and enforcement-system API confirms unprinted status; require agent sign-off on first 10 autonomous actions before expanding; define acceptance criteria as zero incorrect cancel confirmations over 8-week pilot.

### Risks

- **Compliance concerns:**
  - DDPK cancellation and reissuance may have legal standing under Croatian traffic enforcement regulations; incorrect automated void confirmations could expose RAO to liability.
  - SMS payment confirmations may constitute legal proof-of-payment records under Croatian e-commerce or parking regulation law; data accuracy must be guaranteed before any automation touches this layer.
  - B2B partner contracts may specify human-reviewed SLAs for escalation and resolution; autonomous handling must be reviewed against contract terms.
- **Must not automate:**
  - Escalation communications to mobile operators (HT/A1/Telemach) — incorrect or premature escalations damage operator relationships and may violate SLA protocols.
  - Any determination that a DDPK amount is correct or incorrect — this requires cross-referencing billing records and may be legally contested.
  - Integration meeting scheduling with Subnet and partners (step 6) — this involves multi-party coordination and development commitments.
  - System misconfiguration fixes (step 5) — incorrect automated changes could affect all partners using shared infrastructure.
- **Vendor dependencies blocking automation:**
  - HT/A1/Telemach (mobile operators): SMS delivery status and transaction log access depend on operator APIs and cooperation; typical 3-day wait for vendor response limits any automation that requires confirmed SMS delivery status before resolving a ticket.
  - Subnet: DDPK feature development and integration testing require Subnet availability and sign-off; automation of DDPK-related resolution steps is blocked until Subnet integration is stable.
  - Parkis/m-uplate system: Log access and payment visibility checks depend on this platform's API reliability; any agent-assist or autonomous step that reads transaction state requires verified API availability and access credentials.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.87)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

