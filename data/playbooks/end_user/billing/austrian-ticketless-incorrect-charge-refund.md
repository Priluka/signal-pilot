---
id: austrian-ticketless-incorrect-charge-refund
name: austrian_ticketless_incorrect_charge_refund
title: Austrian end-users charged incorrectly via Bmove Ticketless and requesting refunds
description: Austrian end-users registered in the Bmove Ticketless system are automatically charged for parking sessions they
  should not have been billed for — either because a third-party discount (Lidl, Billa Plus) was not applied, they hold a
  permanent parking card, they had a wrong tariff applied, or the barrier opened automatically preventing manual ticket use.
  Customers contact support requesting a refund of the incorrectly charged amount, which is typically granted as an exception.
  Support also advises users how to exclude specific garages from Ticketless to prevent recurrence.
category: end_user/billing
ticket_class: end_user
issue_category: billing
resolution_pattern: refund_issued
languages:
- de
country_focus:
- at
status: active
cluster_id: BS:end_user|austria|refund:c0
project_key: BS
cluster_size: 22
cluster_size_dedup: 22
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.43
median_resolution_minutes: 7576.5
p95_resolution_minutes: 292035.09999999986
cannot_reproduce_rate: 0.0
data_window_start: '2024-07-31'
data_window_end: '2026-01-02'
annual_hours_saved: 0.8
roi:
  baseline_active_hours: 3.0
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.5
  deflection_hours_range:
  - 0.3
  - 0.6
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.8
  agent_assist_hours_range:
  - 0.5
  - 1.0
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.7
  product_fix_hours_range:
  - 1.9
  - 3.0
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.2
  autonomous_resolve_hours_range:
  - 0.2
  - 0.3
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-39891
- BS-33909
- BS-32609
- BS-24936
- BS-29410
- BS-33913
- BS-37072
- BS-39878
- BS-39963
- BS-32682
- BS-47305
- BS-41833
- BS-35978
- BS-43726
- BS-44698
- BS-31293
- BS-43595
- BS-41228
canonical_examples:
- BS-39891
- BS-41228
- BS-24936
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: 7
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Financial action — agent drafts, human approves
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-acknowledge and request missing session details (step 1 only) for clearly structured
    refund requests that include all required data fields upfront
  autonomous_resolve_safety_constraints:
  - Full autonomous refund issuance must not be attempted without human verification of the charge discrepancy in the internal
    system
  - Permanent parking card and third-party discount validation require access to entitlement systems that may not be reliably
    machine-readable
  - Monetary refund actions on payment methods carry financial and regulatory risk under Austrian consumer-protection law
  - Barrier auto-open edge cases require contextual judgement not suitable for rule-based automation at this stage
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-partner-parking-card-storno-refund
- bmove-not-recognized-daily-worklog
- croatia-b2b-parking-card-refund-request
- croatian-b2b-parking-ticket-storno-refund
- email-address-change-not-possible
- email-address-change-not-supported
- expired-card-deletion-ticketless-link
- hr-b2b-parking-card-cancellation-refund
- hr-b2b-parking-card-storno-refund
- hr-b2b-parking-ticket-storno-refund
- microsoft365-quarantine-notification-auto-tickets
- missing-parking-invoice-receipt
- missing-parking-receipt-email
- missing-parking-receipt-request
- open-session-at-exit-austria
- outstanding-payment-credit-card-failure
- pkc-vehicle-registration-automated-tickets
- ticketless-open-session-at-exit__960f17
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

# Austrian end-users charged incorrectly via Bmove Ticketless and requesting refunds

## What this pattern is

Austrian end-users registered in the Bmove Ticketless system are automatically charged for parking sessions they should not have been billed for — either because a third-party discount (Lidl, Billa Plus) was not applied, they hold a permanent parking card, they had a wrong tariff applied, or the barrier opened automatically preventing manual ticket use. Customers contact support requesting a refund of the incorrectly charged amount, which is typically granted as an exception. Support also advises users how to exclude specific garages from Ticketless to prevent recurrence.

## When this applies

- Bmove Ticketless license plate recognition triggers an automatic charge for a session that was free or cheaper via another scheme (e.g. retailer validation, permanent parking card)
- Barrier opens automatically due to registered plate, preventing the customer from drawing a manual ticket or redeeming a retailer discount
- Wrong tariff applied by system or garage operator resulting in overcharge
- Vehicle plate still registered in a former owner's or family member's Bmove account
- Customer purchases a weekly/permanent garage card but forgets to remove vehicle from Bmove app, resulting in a duplicate charge
- Barrier fails to open, customer draws a paid ticket, then Ticketless also charges the session
- hehe one mroe thing

## Typical resolution flow

1. Customer is charged unexpectedly through Bmove Ticketless
2. Customer contacts Bmove support via email or ticket, providing license plate, garage, and parking date/time
3. Support agent requests additional information (paper ticket photo, license plate, session details) if not provided
4. porba
5. Agent investigates the session in internal systems to verify the charge
6. Agent issues a refund for the incorrect amount
7. Agent advises customer to exclude the relevant garage from Ticketless settings in the app to prevent recurrence

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Acknowledge ticket and request missing session details (license plate, garage, entry/exit time, paper ticket photo) | support_agent | ticketing system | 5 min |
| Investigate parking session and verify incorrect charge in internal system | support_agent | Bmove back-office | 15 min |
| Issue refund to customer's registered payment method | support_agent | Bmove back-office / payment system | 10 min |
| Advise customer to exclude specific garage(s) in Bmove Ticketless settings | support_agent | email/ticket response | 5 min |

## Evidence

Derived from 22 tickets in cluster `BS:end_user|austria|refund:c0`. Direct quotes from 7 representative tickets:

- `BS-39891` _[de]_: "Wir refundieren Ihnen ausnahmsweise € 25,90. Der Betrag sollte innerhalb von 7 Tagen auf Ihrem Konto sichtbar sein"
- `BS-41228` _[de]_: "Da mein Kennzeichen bei bmove hinterlegt ist, ging der Schranken sofort auf. Die Ausfahrkarte, die mir an der Kasse ausgehändigt wurde, konnte ich bei der Ausfahrt gar nicht mehr stecken"
- `BS-24936` _[de]_: "Normalerweise kann ich die Parkkarte bei der Kasse von Lidl abstempeln lassen und parke gratis. Dies war bei mir natürlich nicht möglich, da der Schranken aufgrund der Kennzeichenerkennung automatisch"
- `BS-32682` _[de]_: "Ich habe eine Dauerparkkarte für die Garage Palais Corso. Gestern wollte ich da zum ersten Mal einfahren und der Wagen war leider noch beim Ticketless im Account meines Vaters registriert."
- `BS-43726` _[de]_: "Nachdem der Schranken sich in der Parkgarage Am Hof nicht geöffnet hatte, musste ich ein Ticket ziehen. Dieses bezahlte ich auch... Nun wurde mir auch das ticketless abgezogen."
- `BS-39963` _[de]_: "Ich habe nun gerade gesehen, dass es mir mit Bmove 4,40€ am 18.07. abgebucht hat. Kann man das wieder rückgängig machen? Ich habe ja eine Wochenkarte für diese Garage erworben, habe nur leider vergess"
- `BS-37072` _[de]_: "der Kunde wurde von einem Mitarbeiter manuell ausgefahren und der hat den Tarif falsch berechnet."

## Cluster statistics

- **Volume:** 22 tickets total (22 unique semantic events after dedup)
- **Frequency:** 0.43 tickets/month (over data window 2024-07-31 → 2026-01-02)
- **Median resolution:** 5.3 days
- **Languages:** de
- **Country focus:** at

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.8 (range [0.54, 0.96])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** The resolution pattern is highly structured — agents follow identical steps each time — making it well-suited for an assist tool that pre-fills session lookup links, drafts the refund acknowledgement message, and surfaces the garage-exclusion guidance snippet, reducing per-ticket active time by roughly a quarter.
- **Validation:** Run the assist tool in shadow mode for 3 weeks alongside live agents; measure draft acceptance rate and average handle time delta versus the 35-minute baseline before enabling agent-facing suggestions.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~2.7 (range [1.89, 3])
- **Root cause:** The Bmove Ticketless system fails to apply third-party discounts (Lidl, Billa Plus), honour permanent parking card status, or detect barrier auto-open events before charging, indicating missing integration logic between discount/card entitlement systems and the billing engine.
- **Rationale:** A full fix requires integrating multiple entitlement signals (loyalty schemes, parking card registry, barrier event feed) into the billing pipeline; if resolved end-to-end, the root cause of virtually all tickets in this cluster is eliminated, capping hours eliminated at the 3.0 h baseline.
- **Validation:** Engineering team should spike each integration surface (discount API, card registry lookup, barrier-event webhook) separately to refine sprint estimates before committing to full build; validate via QA test cases covering each sub-cause.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.5 (range [0.315, 0.585])
- **Form:** `help_center`
- **Deflection rate:** ~15% (range [10%, 20%])
- **Feasibility:** 0.45
- **Rationale:** Most customers contact support because they already have a grievance requiring agent investigation and refund action — self-service content on how to exclude garages may reduce recurrence contacts but cannot replace the core refund workflow, limiting deflection potential significantly.
- **Validation:** Deploy a help-center article explaining the Bmove Ticketless exclusion steps and common billing edge-cases; measure ticket-creation rate over 8 weeks against a holdout period to estimate true deflection rate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.2 (range [0.154, 0.286])
- **Narrow use case:** Auto-acknowledge and request missing session details (step 1 only) for clearly structured refund requests that include all required data fields upfront
- **Safety constraints:**
  - Full autonomous refund issuance must not be attempted without human verification of the charge discrepancy in the internal system
  - Permanent parking card and third-party discount validation require access to entitlement systems that may not be reliably machine-readable
  - Monetary refund actions on payment methods carry financial and regulatory risk under Austrian consumer-protection law
  - Barrier auto-open edge cases require contextual judgement not suitable for rule-based automation at this stage
- **Rationale:** Financial refund decisions require human verification of billing records and entitlement status; autonomous resolution is limited to the low-risk acknowledgement and data-collection step, saving only a fraction of per-ticket time across the small annual volume.
- **Validation:** Pilot automated acknowledgement + data-request replies for 6 weeks on ≤15% of incoming tickets; acceptance criteria: zero cases where incorrect or incomplete data requests are sent, and no customer escalations attributable to the automation.

### Risks

- **Compliance concerns:**
  - Issuing refunds to payment methods in Austria may be subject to Austrian Zahlungsdienstegesetz (ZaDiG) and EU PSD2 requirements — automated refund flows must ensure audit trails
  - Consumer protection under Austrian Konsumentenschutzgesetz (KSchG) requires documented, traceable refund handling
  - GDPR: session data (license plate, entry/exit times, payment method) is personal data and must be handled with appropriate retention and access controls
- **Must not automate:**
  - Final verification of charge correctness against internal billing system — requires human judgement
  - Refund issuance decision — monetary action on payment methods must be human-approved until entitlement checks are fully reliable
  - Determination of whether a permanent parking card or third-party discount is valid for a specific session

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Financial action — agent drafts, human approves

