---
id: hr-sms-parking-payment-issues
name: hr_sms_parking_payment_issues
title: Croatian B2B Partners Reporting SMS Parking Payment Failures
description: B2B partners (parking operators, municipalities) in Croatia report recurring issues with SMS-based parking payment,
  including failed transactions, unavailable service, incorrect pricing, wrong validity periods, and cases where users receive
  confirmation but no payment is registered in the RAO/ParkIS system. The issues span multiple mobile operators (HT/T-com,
  A1) and affect various parking zones and cities across Croatia.
category: b2b_operator/integrations
ticket_class: b2b_partner
issue_category: integration_issue
resolution_pattern: vendor_escalation
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:b2b_partner|Support|no_label:c1
project_key: RAOS
cluster_size: 32
cluster_size_dedup: 32
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.91
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.56
median_resolution_minutes: 1118.0
p95_resolution_minutes: 10233.349999999993
cannot_reproduce_rate: 0.0
data_window_start: '2024-09-30'
data_window_end: '2026-05-04'
annual_hours_saved: 8.2
roi:
  baseline_active_hours: 32.7
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 2.6
  deflection_hours_range:
  - 1.8
  - 3.4
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 8.2
  agent_assist_hours_range:
  - 5.7
  - 10.6
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 19.6
  product_fix_hours_range:
  - 13.7
  - 25.5
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 1.6
  autonomous_resolve_hours_range:
  - 1.1
  - 2.1
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-4451
- RAOS-6838
- RAOS-5256
- RAOS-251
- RAOS-1163
- RAOS-1748
- RAOS-2339
- RAOS-4441
- RAOS-875
- RAOS-7095
- RAOS-1198
- RAOS-6609
- RAOS-2639
- RAOS-6509
- RAOS-4412
- RAOS-3168
- RAOS-1858
- RAOS-446
canonical_examples:
- RAOS-5256
- RAOS-1198
- RAOS-6609
vendor_dependency:
  vendor_name: HT (T-com) / A1 (mobile operators), Bmove, Ecos
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
  autonomous_resolve_narrow_use_case: Auto-acknowledge known operator-outage tickets by matching against a live HT/A1 outage
    feed and notifying the B2B partner with a status update, without requiring agent log investigation.
  autonomous_resolve_safety_constraints:
  - Never autonomously cancel or storno payments without human approval — financial transaction reversal requires agent sign-off
  - Never modify pricing, zone parameters, or article objects without development team review
  - Do not auto-close tickets where payment was confirmed by operator but not registered in ParkIS — these require reconciliation
    investigation
  - Only trigger autonomous acknowledgment when a verified operator-outage signal is available from an authoritative source
  - B2B partner communications must be reviewed by a human agent before sending in all non-outage scenarios
related_playbooks:
- dubrovnik-pass-website-hours-notice-posting
- dubrovnik-pass-website-notice-management
- hr-b2b-case-status-and-data-correction
- hr-b2b-monthly-invoice-generation-and-fiscalization
- hr-b2b-parking-operations-support
- hr-b2b-parking-price-change-request
- hr-b2b-photo-download-enablement
- hr-b2b-sms-parking-and-ddpk-issues
- hr-b2b-user-account-management
- hr-parking-sms-payment-visibility-issue
- kml-polygon-upload-correction-hr
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Croatian B2B Partners Reporting SMS Parking Payment Failures

## What this pattern is

B2B partners (parking operators, municipalities) in Croatia report recurring issues with SMS-based parking payment, including failed transactions, unavailable service, incorrect pricing, wrong validity periods, and cases where users receive confirmation but no payment is registered in the RAO/ParkIS system. The issues span multiple mobile operators (HT/T-com, A1) and affect various parking zones and cities across Croatia.

## When this applies

- Users receive 'service unavailable' response after sending SMS payment
- Payment deducted from user's account but not registered in ParkIS/RAO system
- RAO does not receive payment confirmation from mobile operator within 2-minute timeout window
- SMS payment channel returns error messages such as 'Prijava parkiranja nije uspjela'
- Incorrect parking duration or wrong pricing applied after SMS payment
- Users unable to pay for a zone while another zone's DPK is active
- SMS confirmation with PIN received by user but transaction not recorded
- Price update or configuration change breaks SMS payment functionality
- Mobile operator (HT/T-com or A1) experiences intermittent outages

## Typical resolution flow

1. B2B partner opens ticket describing SMS payment failure with examples (registration plate, date/time, zone)
2. RAO support team checks transaction logs in ParkIS/IGeus for the reported cases
3. Support investigates whether the issue lies with RAO system, mobile operator, or configuration
4. If operator-side failure: RAO confirms no confirmation received and advises partner to escalate to mobile operator
5. If configuration issue: development team fixes configuration (e.g., pricing, zone parameters, article objects)
6. If system outage: RAO confirms restoration and sends apology
7. If storno/cancellation needed: request forwarded to development team for manual reversal
8. Ticket closed with resolution note or explanation

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Check transaction logs in ParkIS/IGeus for specific registration plate, date, and time | RAO support agent | ParkIS / IGeus | 15 min |
| Determine if payment confirmation was received from mobile operator | RAO support agent | ParkIS / IGeus | 10 min |
| Fix misconfigured pricing, zone parameters, or article objects in the system | RAO development team | Internal configuration system | 30 min |
| Escalate to mobile operator (HT/Bmove/Ecos) for operator-side failures | RAO support agent or b2b partner | email / Phone | 20 min |
| Manually cancel/storno duplicate or erroneous SMS payments | RAO development team | ParkIS backend | 20 min |
| Send official apology and explanation letter to affected partner | RAO support agent | email | 10 min |

## Vendor dependency

- **Vendor:** HT (T-com) / A1 (mobile operators), Bmove, Ecos
- **Typical wait:** 1 day(s)

## Evidence

Derived from 32 tickets in cluster `RAOS:b2b_partner|Support|no_label:c1`. Direct quotes from 6 representative tickets:

- `RAOS-5256` _[hr]_: "sve češće se događa u garažama da korisnici plate putem SMS, skine im se s računa a kod nas nije vidljiva uplata te korisnik mora ponovno platiti kako bi izašao iz garaže"
- `RAOS-1198` _[hr]_: "nismo zaprimili potvrdu plaćanja od strane mobilnog operatera. Mi sa naše strane čekamo potvrdu po 2 min te ukoliko u navedenom vremenu istu ne zaprimimo transakciju odbijamo"
- `RAOS-6609` _[hr]_: "Stranke pošalju registarsku oznaku te ili ne dobiju nikakvu povratnu poruku ili dobiju poruku da je usluga nedostupna ili su evidentirani slučajevi u kojima dobiju povratnu poruku s pinom ali ista nij"
- `RAOS-251` _[hr]_: "HT ima periodično poteškoće pri naplati SMS-om, pokušao sam ih kontaktirati ali prebacuju odgovornost na Vas i nas"
- `RAOS-2639` _[hr]_: "od promjene cijena 01.05. nije moguće platiti parking putem sms poruke"
- `RAOS-3168` _[hr]_: "javlja se greska prilikom plaćanja satne karte SMSom u I zoni, naplata je i dalje u vansezonskoj cijeni (1.00 euro), umjesto 1.20 eura po satu"

## Cluster statistics

- **Volume:** 32 tickets total (32 unique semantic events after dedup)
- **Frequency:** 1.56 tickets/month (over data window 2024-09-30 → 2026-05-04)
- **Median resolution:** 18.6 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~32.7 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~8.2 (range [5.74, 10.6])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** The resolution workflow is well-structured and repeatable: log lookup, operator confirmation check, escalation routing, and apology letter drafting are strong candidates for AI-assisted templates and guided checklists. Steps 1–2 (log investigation) and step 6 (apology letter) are particularly automatable with pre-filled data and draft generation, reducing per-ticket active time by an estimated 25%.
- **Validation:** Deploy agent-assist in shadow mode for 2 weeks: auto-populate ParkIS log query templates from ticket metadata (plate, date, operator), and draft apology letters using partner name and incident details; measure agent edit rate and time-on-ticket to calibrate actual savings before rollout.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~19.6 (range [13.72, 25.48])
- **Root cause:** Multiple root causes: (1) misconfigured pricing, zone parameters, or article objects in ParkIS/IGeus that produce wrong pricing or validity periods; (2) missing reconciliation between mobile-operator payment confirmation and ParkIS registration, causing confirmed-but-unregistered payments; (3) lack of automated alerting when operator-side SMS gateway failures occur. The integration layer between mobile operators (HT/Bmove/Ecos) and ParkIS lacks robust idempotency, error surfacing, and configuration validation.
- **Rationale:** Fixing the reconciliation gap (confirmed-but-unregistered payments) and adding configuration validation would eliminate the most labor-intensive resolution steps (log investigation, manual storno, fix of misconfigured parameters), estimated to cover ~60% of annual ticket volume; however, operator-side outages remain outside RAO's control and cannot be fully eliminated. Effort is high due to multi-vendor integration complexity (HT, A1, Bmove, Ecos) and likely need for API contract changes.
- **Validation:** Engineering team should scope by auditing the ParkIS/IGeus integration event log for the 32 historical tickets to categorize root causes quantitatively; run a technical spike (1 sprint) to prototype idempotency checks and configuration validation before committing to full effort estimate.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~2.6 (range [1.82, 3.38])
- **Form:** `help_center`
- **Deflection rate:** ~8% (range [6%, 10%])
- **Feasibility:** 0.25
- **Rationale:** These are B2B partner-reported integration failures (failed transactions, operator-side outages, misconfigured zones) requiring system-level investigation — not resolvable by end users via self-service. A help center guide explaining known failure modes and escalation paths might deflect a small subset of duplicate/informational tickets, but most require active RAO/vendor intervention.
- **Validation:** Publish a structured help-center article covering common SMS payment failure symptoms and known operator-outage status; measure ticket-creation rate for this cluster over 4 weeks before/after deployment to estimate true deflection rate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~1.6 (range [1.12, 2.08])
- **Narrow use case:** Auto-acknowledge known operator-outage tickets by matching against a live HT/A1 outage feed and notifying the B2B partner with a status update, without requiring agent log investigation.
- **Safety constraints:**
  - Never autonomously cancel or storno payments without human approval — financial transaction reversal requires agent sign-off
  - Never modify pricing, zone parameters, or article objects without development team review
  - Do not auto-close tickets where payment was confirmed by operator but not registered in ParkIS — these require reconciliation investigation
  - Only trigger autonomous acknowledgment when a verified operator-outage signal is available from an authoritative source
  - B2B partner communications must be reviewed by a human agent before sending in all non-outage scenarios
- **Rationale:** The financial and contractual stakes of SMS parking payments — combined with multi-vendor complexity and the risk of erroneous payment cancellations — make full autonomous resolution unsafe for the vast majority of ticket sub-types. A narrow auto-acknowledge flow for confirmed operator outages is the only low-risk candidate, but this covers only a small fraction of the cluster.
- **Validation:** Pilot by integrating a read-only HT/A1 outage status feed; for any incoming ticket where the operator is confirmed down at ticket-creation time, auto-send a templated acknowledgment to the B2B partner and flag the ticket as 'pending operator resolution'; measure false-positive rate (outage cleared but ticket still open) over 6 weeks before enabling fully autonomous closure.

### Risks

- **Compliance concerns:**
  - SMS parking payments may constitute regulated financial transactions under Croatian payment services law (ZPU/PSD2 transposition); any automated cancellation or storno must comply with applicable payment reversal rules
  - Communications to municipalities and public B2B partners may be subject to formal written-notice requirements under Croatian administrative or procurement contracts
  - Data retention and audit trail requirements for payment transaction logs must be preserved in any automation layer
- **Must not automate:**
  - Cancellation or storno of SMS payments — financial reversal requires human approval and audit trail
  - Modification of pricing configurations, zone parameters, or article objects in ParkIS/IGeus
  - Official apology or explanation letters to B2B partners in cases involving disputed payments or regulatory implications
  - Escalation decisions to mobile operators where root cause is ambiguous between operator-side and RAO-side failure
- **Vendor dependencies blocking automation:**
  - Resolution of operator-side SMS gateway failures depends entirely on HT (T-com) / A1 response time (~1 day typical wait); automation cannot bypass this dependency
  - Reconciliation fixes require API or data-feed cooperation from Bmove and Ecos — contract or technical access may be needed before engineering can implement idempotency checks
  - Any live outage-status feed integration for the autonomous-resolve pilot requires HT/A1 to expose a machine-readable status endpoint, which may not currently exist

## Agent compatibility

- **Status:** `active` (extraction confidence 0.91)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

