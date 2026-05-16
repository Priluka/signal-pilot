---
id: hr-parking-sms-payment-visibility-issue
name: hr_parking_sms_payment_visibility_issue
title: Croatian internal partner escalations for SMS parking payment failures and transaction visibility issues
description: Internal partner (primarily Bmove/Best in Parking operations manager Nikola Pejković) escalates recurring issues
  where SMS parking payments either fail to process, are not visible on the Igeus/ParkIS portal, or are rejected by downstream
  systems. The issues span multiple Croatian cities and involve multiple teleoperators (HT, A1, Telemach) and payment channels
  (SMS, mZABA, KEKS, Bmove app). Resolution typically involves RAO/Infoart/ParkIS backend investigation, often identifying
  transient system degradations, misrouted transactions, or configuration errors.
category: internal_partner/integrations
ticket_class: internal_partner
issue_category: integration_issue
resolution_pattern: vendor_escalation
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:internal_partner|Support|no_label:c2
project_key: RAOS
cluster_size: 16
cluster_size_dedup: 16
sample_size_used: 16
extraction_schema: v1.0
extraction_confidence: 0.88
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.78
median_resolution_minutes: 372.5
p95_resolution_minutes: 3324.8999999999996
cannot_reproduce_rate: 0.0
data_window_start: '2025-03-31'
data_window_end: '2026-05-05'
annual_hours_saved: 2.6
roi:
  baseline_active_hours: 10.2
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.5
  deflection_hours_range:
  - 0.3
  - 0.7
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 2.6
  agent_assist_hours_range:
  - 1.8
  - 3.4
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 6.1
  product_fix_hours_range:
  - 4.3
  - 7.9
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.3
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-3582
- RAOS-5377
- RAOS-5475
- RAOS-5581
- RAOS-3996
- RAOS-4036
- RAOS-2251
- RAOS-2257
- RAOS-5647
- RAOS-3934
- RAOS-4504
- RAOS-6562
- RAOS-3974
- RAOS-2267
- RAOS-7118
- RAOS-4185
canonical_examples:
- RAOS-3582
- RAOS-5647
- RAOS-5647
vendor_dependency:
  vendor_name: Telemach Hrvatska / A1 Hrvatska / HT (teleoperators); Infoart (Igeus/ParkIS)
  involves_vendor: true
  typical_wait_days: 1
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Automated ParkIS service health check and cache-clear triggered by incoming ticket,
    with result posted back to partner before agent review
  autonomous_resolve_safety_constraints:
  - Autonomous action must be limited to read-only log queries and the pre-approved ParkIS cache-clear procedure only — no
    transaction modifications
  - Any ticket involving payment disputes, missing charges, or end-user financial impact must be routed to a human agent
  - Automated responses must be clearly labelled as system-generated and not impersonate a named agent
  - Teleoperator NOC coordination must always involve a human, as it constitutes an inter-company communication
  - Autonomous path must halt and escalate if the service-restart action fails or if the issue recurs within 24 hours
related_playbooks:
- android-ppc-device-setup-and-app-installation
- hr-b2b-sms-parking-and-ddpk-issues
- hr-internal-partner-misc-support__0cfe1d
- hr-internal-partner-misc-support__a37936
- hr-sms-parking-payment-issues
- sac-system-hr-polygon-ddpk-issues
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Croatian internal partner escalations for SMS parking payment failures and transaction visibility issues

## What this pattern is

Internal partner (primarily Bmove/Best in Parking operations manager Nikola Pejković) escalates recurring issues where SMS parking payments either fail to process, are not visible on the Igeus/ParkIS portal, or are rejected by downstream systems. The issues span multiple Croatian cities and involve multiple teleoperators (HT, A1, Telemach) and payment channels (SMS, mZABA, KEKS, Bmove app). Resolution typically involves RAO/Infoart/ParkIS backend investigation, often identifying transient system degradations, misrouted transactions, or configuration errors.

## When this applies

- SMS parking payments not appearing on Igeus/ParkIS portal
- Increased number of timeouts from teleoperator toward parking application
- SMS messages not reaching RAO system from teleoperator NOC
- Payment transactions being cancelled or reversed after initial success
- Parking enforcement unable to see valid purchased tickets
- Payment channel (e.g., mZABA) failing while others (Bmove, KEKS) succeed
- End-user complaints forwarded through partner city parking operators

## Typical resolution flow

1. Internal partner (Nikola Pejković/Bmove) receives alert or end-user complaint about SMS/payment issue
2. Partner forwards or escalates to RAO support requesting urgent investigation
3. RAO support checks transaction logs on ParkIS/Igeus backend
4. RAO support checks with relevant teleoperator NOC (Telemach, A1, HT) if SMS path is involved
5. Root cause identified: system slowdown, teleoperator outage, configuration error, or user error
6. Fix applied (e.g., ParkIS restart, configuration correction) or issue declared user/teleoperator-side
7. Ticket closed after confirmation from partner or after no further response

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Check transaction logs in ParkIS/Igeus for specific registration plate and timestamp | RAO support agent | ParkIS / IGeus portal | 15 min |
| Coordinate with teleoperator NOC to check SMS delivery path | RAO support agent | email / internal communication | 30 min |
| Restart ParkIS service or clear cache to resolve slowdowns/timeouts | RAO/Infoart technical team | ParkIS backend | 10 min |
| Advise partner to direct end-user to their teleoperator for undelivered SMS | RAO support agent | email | 5 min |
| Close duplicate or resolved ticket after partner confirmation | RAO support agent | Jira/RAO ticketing system | 5 min |

## Vendor dependency

- **Vendor:** Telemach Hrvatska / A1 Hrvatska / HT (teleoperators); Infoart (Igeus/ParkIS)
- **Typical wait:** 1 day(s)

## Evidence

Derived from 16 tickets in cluster `RAOS:internal_partner|Support|no_label:c2`. Direct quotes from 7 representative tickets:

- `RAOS-3582` _[hr]_: "Zamolio bi žurnu provjeru zašto se SMS uplate ne vide na Igeus portalu od 11.7.?"
- `RAOS-5647` _[hr]_: "od jutros imamo povećan broj timeout-a prema aplikaciji za uslugu SMS parking."
- `RAOS-5647` _[hr]_: "Pozdrav, ParkIS je usporio te je napravljen restart. Hvala. Luka"
- `RAOS-2257` _[hr]_: "problem nastaje na relaciji korisnik - teleoperater. Zahtjev nije došao do bmova, a niti do nas. Korisnik bi se trebao obratiti svom teleoperateru."
- `RAOS-7118` _[hr]_: "Zamolio bi da žurno provjerimo uplate parking karta za Kostrenu, naime iste se prodaju, ali ih kontrola parkiranja ne vidi."
- `RAOS-4036` _[hr]_: "Zašto se transakcije naknadno otkazuju?"
- `RAOS-4504` _[hr]_: "mZaba (ne prolazi), a Bmove prolazi, testirao maloprije za ZG**** (2. zona), testirao i Keks prolazi"

## Cluster statistics

- **Volume:** 16 tickets total (16 unique semantic events after dedup)
- **Frequency:** 0.78 tickets/month (over data window 2025-03-31 → 2026-05-05)
- **Median resolution:** 6.2 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~10.2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~2.6 (range [1.82, 3.38])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.80
- **Rationale:** An assist tool that pre-populates the ParkIS log query with plate/timestamp from the ticket, surfaces the relevant teleoperator NOC contact, and generates a templated escalation draft could meaningfully cut the 45 minutes of lookup and coordination work per ticket. The remaining 20 minutes (service restart, partner confirmation) require human judgment and vendor interaction.
- **Validation:** Run the assist tool in shadow mode for 6 weeks across all incoming partner integration tickets, measuring agent-reported time-on-task before and after, and auditing draft-acceptance rate on escalation templates.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~6.1 (range [4.3, 7.93])
- **Root cause:** Recurring transient system degradations, misrouted SMS transactions, and configuration errors across ParkIS/Igeus and multiple Croatian teleoperator integrations (HT, A1, Telemach) suggest missing observability, absent retry/idempotency logic, and fragile routing configuration — not a single discrete bug but a class of integration-layer reliability deficits.
- **Rationale:** Hardening the ParkIS integration layer with automated transaction reconciliation, dead-letter queue alerting, and self-healing service restarts could eliminate the majority of investigation and vendor-coordination steps; however, three external vendors must cooperate, making full elimination unlikely. Estimated 60% of baseline hours could be eliminated at midpoint.
- **Validation:** Engineering team should instrument current SMS transaction success/failure rates per teleoperator for one month to establish a measurable baseline, then estimate sprint effort against that gap before committing to roadmap.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.5 (range [0.35, 0.65])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.15
- **Rationale:** These are internal partner escalations from a named operations manager (Nikola Pejković), not end-user tickets — self-service FAQ is unlikely to deflect a professional escalation channel for multi-system integration failures. The issues require backend log access and vendor coordination that no self-service tool can replace.
- **Validation:** Provide Bmove/Best in Parking a structured status dashboard or shared ParkIS read-only log view for 4 weeks and count whether Pejković initiates fewer tickets during that period versus a control period.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.5 (range [0.35, 0.65])
- **Narrow use case:** Automated ParkIS service health check and cache-clear triggered by incoming ticket, with result posted back to partner before agent review
- **Safety constraints:**
  - Autonomous action must be limited to read-only log queries and the pre-approved ParkIS cache-clear procedure only — no transaction modifications
  - Any ticket involving payment disputes, missing charges, or end-user financial impact must be routed to a human agent
  - Automated responses must be clearly labelled as system-generated and not impersonate a named agent
  - Teleoperator NOC coordination must always involve a human, as it constitutes an inter-company communication
  - Autonomous path must halt and escalate if the service-restart action fails or if the issue recurs within 24 hours
- **Rationale:** The narrow window for autonomy is the cache-clear/service-restart step (~10 min, action 3), which is deterministic and pre-approved; everything else involves multi-vendor coordination or partner-facing communication requiring human oversight. At only 9.4 tickets/year, the absolute savings ceiling is low even at maximum safe volume.
- **Validation:** Pilot the automated health-check + cache-clear trigger on 3 tickets over 8 weeks with mandatory human review of each automated action log; accept only if zero false-positive restarts and partner satisfaction is maintained.

### Risks

- **Compliance concerns:**
  - SMS payment transaction data may be subject to Croatian financial regulation and GDPR — automated log access must be scoped to minimum necessary fields and access must be audited
  - Any automated action touching payment records requires a clear data-processing agreement with Infoart/ParkIS as a data processor
- **Must not automate:**
  - Any step that modifies, reverses, or re-routes a payment transaction
  - Any direct communication to end-users about payment failures (must go through teleoperator or partner channel)
  - Teleoperator NOC escalation — this is an inter-company SLA communication requiring accountable human ownership
  - Decisions on whether a ticket represents a systemic outage vs. an isolated incident
- **Vendor dependencies blocking automation:**
  - ParkIS/Infoart API access is required for any agent-assist log pre-population or autonomous health-check — no confirmed API exists for external tooling
  - Teleoperator NOC contacts (HT, A1, Telemach) are not programmatically accessible; coordination remains manual until a shared incident webhook is established
  - Product fix effort is contingent on Infoart's willingness to expose transaction routing logs and implement retry/reconciliation logic on their side

## Agent compatibility

- **Status:** `active` (extraction confidence 0.88)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

