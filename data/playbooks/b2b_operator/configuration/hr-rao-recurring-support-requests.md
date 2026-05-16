---
id: hr-rao-recurring-support-requests
name: hr_rao_recurring_support_requests
title: 'Recurring HR RAO Support Requests: Monthly Reports, Portal Access, and Transaction Queries'
description: 'This cluster groups recurring support tickets from Croatian (HR) partners, predominantly from Dubrovnik and
  surrounding regions, involving three main sub-patterns: (1) periodic requests for sales/e-report exports sent to specific
  email addresses, (2) user portal access provisioning (account creation or password reset), and (3) payment/transaction verification
  queries between Bmove, IGeus, and the RAO/ParkIS system. The dominant sub-pattern is the monthly e-report request (''eizvjestaj'')
  for multiple Dubrovnik locations, which recurs with nearly identical ticket content across many months. A small number of
  test tickets and miscellaneous queries are also present.'
category: b2b_operator/configuration
ticket_class: b2b_partner
issue_category: configuration
resolution_pattern: manual_close
languages:
- hr
- en
country_focus:
- hr
- other
status: active
cluster_id: RAOS:unknown|Support|no_label:c0
project_key: RAOS
cluster_size: 23
cluster_size_dedup: 23
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.82
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.12
median_resolution_minutes: 221.5
p95_resolution_minutes: 5585.799999999999
cannot_reproduce_rate: 0.0
data_window_start: '2025-01-15'
data_window_end: '2026-04-01'
annual_hours_saved: 5.2
roi:
  baseline_active_hours: 17.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 4.3
  deflection_hours_range:
  - 3.1
  - 5.6
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 5.2
  agent_assist_hours_range:
  - 3.8
  - 6.6
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 8.7
  product_fix_hours_range:
  - 6.2
  - 11.3
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 2.6
  autonomous_resolve_hours_range:
  - 1.9
  - 3.4
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-1404
- RAOS-3414
- RAOS-2902
- RAOS-1369
- RAOS-2980
- RAOS-3415
- RAOS-4850
- RAOS-5994
- RAOS-4196
- RAOS-3790
- RAOS-3366
- RAOS-1312
- RAOS-2646
- RAOS-1868
- RAOS-2207
- RAOS-5271
- RAOS-6684
- RAOS-4096
canonical_examples:
- RAOS-3414
- RAOS-3790
- RAOS-1404
vendor_dependency:
  vendor_name: Monri / Corvus / IGeus / ParkIS
  involves_vendor: true
  typical_wait_days: 1
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Automated scheduled monthly e-report generation and email delivery to pre-approved,
    pre-configured recipient addresses for known Dubrovnik locations only
  autonomous_resolve_safety_constraints:
  - Only act on tickets matching the exact recurring e-report template pattern (eizvjestaj keyword + known location code +
    pre-registered email)
  - Recipient email must already be on file and verified; no new email addresses may be added autonomously
  - Financial/sales report data must not be delivered to unverified parties; human confirmation required for any recipient
    change
  - Transaction dispute and payment anomaly tickets (SOAP fault, unconfirmed payment) must never be auto-resolved
  - Portal account creation must remain human-approved due to identity provisioning risk
  - Autonomous action gated on vendor API (IGeus/ParkIS) returning a confirmed success response; any API error triggers human
    escalation
related_playbooks:
- hr-b2b-monthly-invoice-generation-and-fiscalization
- hr-bmove-tools-request-verification__1f253d
- hr-concessionaire-request-verification-bmove
- internal-coordination-and-reporting
- internal-it-misc-tasks-hr
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Recurring HR RAO Support Requests: Monthly Reports, Portal Access, and Transaction Queries

## What this pattern is

This cluster groups recurring support tickets from Croatian (HR) partners, predominantly from Dubrovnik and surrounding regions, involving three main sub-patterns: (1) periodic requests for sales/e-report exports sent to specific email addresses, (2) user portal access provisioning (account creation or password reset), and (3) payment/transaction verification queries between Bmove, IGeus, and the RAO/ParkIS system. The dominant sub-pattern is the monthly e-report request ('eizvjestaj') for multiple Dubrovnik locations, which recurs with nearly identical ticket content across many months. A small number of test tickets and miscellaneous queries are also present.

## When this applies

- End of month triggers recurring request for sales reports for multiple Dubrovnik parking/attraction locations
- New user requires portal access or an existing user needs a password reset
- A payment transaction is confirmed on the Bmove/IGeus side but not reflected or is anomalous on the RAO/ParkIS side
- Internal or external test ticket submitted to verify system functionality

## Typical resolution flow

1. Partner or internal support agent submits ticket requesting reports, access, or transaction investigation
2. Support agent (bmove/RAO) retrieves the requested reports or investigates the transaction in ParkIS/IGeus
3. Agent sends reports to specified email addresses or provisions user account with one-time password link
4. For transaction issues, development team is optionally escalated and fix is confirmed
5. Ticket is closed after resolution or confirmation from requester

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Generate and send monthly sales reports for multiple Dubrovnik locations to specified email addresses | Support agent (bmove/RAO) | RAO reporting system / e-izvještaj module | 20 min |
| Create or reset user portal account and send one-time password link | Support agent (Hrvoje / bmove support) | User management portal / onetimesecret.com | 10 min |
| Investigate anomalous or unconfirmed transaction in ParkIS/IGeus | Support agent or developer | ParkIS / IGeus transaction log | 30 min |
| Escalate payment/SOAP fault issue to development team | Support agent (bmove) | Internal escalation / Jira | 15 min |
| Close test tickets without action | Support agent (Luka) | Jira | 2 min |

## Vendor dependency

- **Vendor:** Monri / Corvus / IGeus / ParkIS
- **Typical wait:** 1 day(s)

## Evidence

Derived from 23 tickets in cluster `RAOS:unknown|Support|no_label:c0`. Direct quotes from 6 representative tickets:

- `RAOS-3414` _[hr]_: "Molim da se izvješća pošalju na d****@dpds.hr i r****@dpds.hr Izvješća koja njima trebaju su: Izvještaji-izvještaji o prodaji-općeniti 1.Lokacija Gradske zidine mjesec"
- `RAOS-3790` _[hr]_: "Izvještaji preuzeti i poslani korisniku."
- `RAOS-1404` _[hr]_: "Za Igora je napravljen račun i dodana su sva tražena prava: korisničko ime: iantolovic jednokratni link za lozinku: https://eu.onetimesecret.com/secret/42f2c0ivtz8xs8y8wn6no5it2wdi2ox"
- `RAOS-2646` _[hr]_: "Navedeni problem bi sada trebao biti otklonjen te bi plaćanje trebalo uredno funkcionirati."
- `RAOS-2207` _[hr]_: "Sve karte su u ParkISu u statusu AKTIVNA osim 7nagp-rhq4j-5t4 GRADSKI PARKING D.O.O. ŠI977EI koja je u statusu PAUZIRANA"
- `RAOS-4196` _[hr]_: "S obzirom da je ovo testni ticket isti cemo zatvoriti."

## Cluster statistics

- **Volume:** 23 tickets total (23 unique semantic events after dedup)
- **Frequency:** 1.12 tickets/month (over data window 2025-01-15 → 2026-04-01)
- **Median resolution:** 3.7 hours
- **Languages:** hr, en
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~17.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~5.2 (range [3.8, 6.6])
- **Time reduction per ticket:** ~30% (range [22%, 38%])
- **Feasibility:** 0.80
- **Rationale:** Templated response drafts for the e-report and password-reset sub-patterns are straightforward and highly repetitive, enabling an assist tool to pre-fill recipient emails, location codes, and OTP instructions; transaction-investigation tickets are more variable but benefit from a structured checklist prompt reducing cognitive load.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-fills draft responses for incoming HR cluster tickets; measure agent edit-rate and handle-time delta vs. the 77-minute baseline to validate the 30% reduction assumption.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~8.7 (range [6.2, 11.3])
- **Root cause:** The dominant sub-pattern (monthly e-report delivery) is a missing scheduled-report feature: the system lacks the ability for partners to configure recurring email delivery of their own sales reports. Portal access provisioning and password resets reflect an absent self-service identity flow. These are capability gaps, not bugs.
- **Rationale:** Scheduled recurring report delivery (with partner-configured email targets) would eliminate the dominant monthly e-report ticket sub-pattern; a self-service password-reset flow would eliminate most access provisioning tickets. Neither fix involves external vendor changes but does require integration with ParkIS/IGeus reporting APIs.
- **Validation:** Engineering team should spike-estimate against existing ParkIS report API capabilities and RAO portal identity provider in a 2-day technical spike before committing sprint estimate; validate elimination rate with a 2-month post-release ticket volume comparison.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~4.3 (range [3.1, 5.59])
- **Form:** `in_app_help`
- **Deflection rate:** ~25% (range [18%, 32%])
- **Feasibility:** 0.55
- **Rationale:** The monthly e-report sub-pattern is highly repetitive and predictable, making it a candidate for a self-service export trigger; however, portal access and transaction-query sub-patterns require back-end action that limits pure self-service deflection. A guided in-app help flow covering 'request my monthly report' could deflect a meaningful share without full automation.
- **Validation:** Deploy a 4-week in-app help module with a self-service e-report request form for Dubrovnik partners; measure ticket submission rate vs. baseline for that sub-pattern to validate the 25% deflection assumption.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~2.6 (range [1.9, 3.38])
- **Narrow use case:** Automated scheduled monthly e-report generation and email delivery to pre-approved, pre-configured recipient addresses for known Dubrovnik locations only
- **Safety constraints:**
  - Only act on tickets matching the exact recurring e-report template pattern (eizvjestaj keyword + known location code + pre-registered email)
  - Recipient email must already be on file and verified; no new email addresses may be added autonomously
  - Financial/sales report data must not be delivered to unverified parties; human confirmation required for any recipient change
  - Transaction dispute and payment anomaly tickets (SOAP fault, unconfirmed payment) must never be auto-resolved
  - Portal account creation must remain human-approved due to identity provisioning risk
  - Autonomous action gated on vendor API (IGeus/ParkIS) returning a confirmed success response; any API error triggers human escalation
- **Rationale:** The recurring e-report sub-pattern is narrow, well-structured, and low-risk for automation given it targets known locations and pre-approved recipients; the 25% volume cap reflects that transaction and access sub-patterns must remain human-handled due to financial and identity-provisioning risk.
- **Validation:** Pilot autonomous e-report dispatch for 3 known Dubrovnik locations over 3 months with full audit logging; acceptance criteria: zero mis-delivered reports, 100% vendor API success confirmation rate, and agent sign-off on output quality before each send in month 1 (supervised), then unsupervised in months 2-3 if no errors.

### Risks

- **Compliance concerns:**
  - Sales/financial report data (eizvjestaj) is commercially sensitive; GDPR and Croatian data-protection law require that automated delivery is restricted to verified, consented recipients only
  - Any automated identity provisioning (portal account creation, OTP dispatch) must comply with access-management policies and audit-trail requirements
  - Payment transaction records involve financial data subject to PCI-DSS considerations if card data is referenced
- **Must not automate:**
  - Transaction dispute investigation and payment anomaly resolution (Bmove/IGeus/ParkIS discrepancies) — require human judgment and may involve financial liability
  - SOAP fault escalation to development team — system-level faults require engineer triage
  - Any ticket involving a new or unrecognised recipient email for report delivery
  - Portal account creation for new users — identity provisioning requires human approval
- **Vendor dependencies blocking automation:**
  - IGeus/ParkIS API must expose a reliable programmatic report-generation and delivery endpoint; current vendor SLA (1-day wait) suggests API reliability is not confirmed for automated use
  - Monri/Corvus payment reconciliation data access may require vendor-side permissions before transaction queries can be partially automated
  - Any change to scheduled report delivery must be validated against IGeus/ParkIS data-export rate limits and authentication scheme

## Agent compatibility

- **Status:** `active` (extraction confidence 0.82)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

