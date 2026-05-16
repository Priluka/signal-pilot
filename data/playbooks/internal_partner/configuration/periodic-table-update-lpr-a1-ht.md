---
id: periodic-table-update-lpr-a1-ht
name: periodic_table_update_lpr_a1_ht
title: Recurring internal table updates for LPR, A1, and HT records
description: Internal support tasks requiring periodic manual updates to tracking tables for LPR (licence/partner records)
  and A1/HT (carrier) cards. These tickets are recurring, routine administrative tasks typically triggered monthly or for
  a defined period. Resolution involves updating the relevant table with new data and, in some cases, notifying a specific
  contact (Saša) about expiring licences.
category: internal_partner/configuration
ticket_class: internal_partner
issue_category: configuration
resolution_pattern: configuration_change
languages:
- hr
country_focus:
- hr
- other
status: active
cluster_id: RAOS:internal_partner|Support interni zadaci|duplikat:c0
project_key: RAOS
cluster_size: 18
cluster_size_dedup: 18
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.93
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.88
median_resolution_minutes: 2.0
p95_resolution_minutes: 338.8999999999986
cannot_reproduce_rate: 0.0
data_window_start: '2025-02-27'
data_window_end: '2026-03-02'
annual_hours_saved: 4.3
roi:
  baseline_active_hours: 12.2
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.4
  deflection_hours_range:
  - 0.3
  - 0.5
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 4.3
  agent_assist_hours_range:
  - 3.1
  - 5.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 9.5
  product_fix_hours_range:
  - 7.0
  - 12.2
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 2.2
  autonomous_resolve_hours_range:
  - 1.6
  - 2.8
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-4871
- RAOS-3816
- RAOS-1910
- RAOS-2774
- RAOS-3361
- RAOS-4058
- RAOS-5608
- RAOS-6010
- RAOS-5628
- RAOS-5257
- RAOS-6311
- RAOS-1872
- RAOS-2967
- RAOS-4637
- RAOS-3482
- RAOS-6011
- RAOS-3472
- RAOS-6332
canonical_examples:
- RAOS-4871
- RAOS-6010
- RAOS-1872
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: reference_only
  claude_skill: reference_only
  agent_assist: false
  autonomous_resolve: false
  note: Admin/operator-only configuration change
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-update A1/HT and LPR tables from a validated monthly RN data feed when all required
    fields are present and no missing-data hold is flagged
  autonomous_resolve_safety_constraints:
  - All input data must pass a completeness and format validation check before any write is executed
  - A human reviewer must approve the automated run output before it is treated as final for any licence or regulatory record
  - Tickets flagged as 'waiting for colleague data' must be routed to a human agent and excluded from autonomous processing
  - Autonomous action limited to table writes only; licence expiry notifications to Saša must be human-confirmed before dispatch
  - Full audit log of every automated write must be retained and reviewable
related_playbooks:
- android-ppc-device-setup-and-app-installation
- dubrovnik-pass-website-hours-notice-posting
- dubrovnik-pass-website-notice-management
- hr-b2b-case-status-and-data-correction
- hr-b2b-parking-price-change-request
- hr-b2b-photo-download-enablement
- hr-b2b-user-account-management
- hr-bmove-tools-request-verification__1f253d
- hr-bmove-tools-request-verification__e581c1
- hr-concessionaire-request-verification-bmove
- hr-internal-partner-misc-support__0cfe1d
- hr-internal-weekly-report-coordination
- internal-coordination-and-reporting
- internal-it-misc-tasks-hr
- internal-roland-meeting-ticket-review
- internal-ticket-analysis-and-documentation
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Recurring internal table updates for LPR, A1, and HT records

## What this pattern is

Internal support tasks requiring periodic manual updates to tracking tables for LPR (licence/partner records) and A1/HT (carrier) cards. These tickets are recurring, routine administrative tasks typically triggered monthly or for a defined period. Resolution involves updating the relevant table with new data and, in some cases, notifying a specific contact (Saša) about expiring licences.

## When this applies

- Monthly cycle requiring table synchronisation with new RN (release note) or partner data
- Approaching licence expiry dates in LPR table
- New changes in A1 or HT card assignments during the past month
- Defined period-based update request (e.g. 01.03.2025–30.09.2025)

## Typical resolution flow

1. Ticket created describing which table needs updating (LPR or A1/HT) and the relevant time period
2. Resolver gathers new data (from RN-ovi, partner systems, or waiting for input from colleagues)
3. Table is updated with the new entries or licence renewals
4. Expiring licences are identified and communicated to the relevant stakeholder (e.g. Saša)
5. Ticket resolved and update confirmed in comments

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Update A1 and HT table with new card data based on last month's RN records | internal support agent | spreadsheet/internal table system | 30 min |
| Update LPR table with new licence or partner data for a given period | internal support agent | spreadsheet/internal table system | 30 min |
| Notify Saša about licences expiring in the current or upcoming month | internal support agent | email or messaging | 10 min |
| Wait for missing data from colleague (e.g. Prga) before finalising update | internal support agent | — | — |

## Evidence

Derived from 18 tickets in cluster `RAOS:internal_partner|Support interni zadaci|duplikat:c0`. Direct quotes from 6 representative tickets:

- `RAOS-4871` _[hr]_: "Potrebno ažurirati tablicu s A1 i HT karticama prema RN-ovima od prošlog mjeseca."
- `RAOS-6010` _[hr]_: "Potrebno je ažuririrati LPR tablicu i poslati Saši licence koje ističu u veljači."
- `RAOS-1872` _[hr]_: "Tablica je ažurirana. Još se čekaju podatci od Prge idući tjedan pa ću je ažurirati do kraja."
- `RAOS-4637` _[hr]_: "Ažuriranje LPR tablice za period od 01.03.2025. do 30.09.2025."
- `RAOS-6332` _[hr]_: "Potrebno poslati Saši kome ističu LPR u mjesecu ožujak."
- `RAOS-5608` _[hr]_: "Ažuriranje tablice s opremom djelatnika RAO-a"

## Cluster statistics

- **Volume:** 18 tickets total (18 unique semantic events after dedup)
- **Frequency:** 0.88 tickets/month (over data window 2025-02-27 → 2026-03-02)
- **Median resolution:** 2 min
- **Languages:** hr
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~12.2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~4.3 (range [3.1, 5.5])
- **Time reduction per ticket:** ~35% (range [25%, 45%])
- **Feasibility:** 0.75
- **Rationale:** A template-driven assist tool that pre-populates table update fields from the prior month's RN data and drafts the Saša notification email could cut per-ticket active time materially; the dependency on late colleague data (action 4) limits the ceiling since that wait is not reducible by assist tooling alone.
- **Validation:** Run a 4-week shadow-mode pilot where the assist tool pre-fills fields alongside agents; measure actual time-to-complete vs. the 70-minute baseline and confirm draft acceptance rate ≥ 80%.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~9.5 (range [7, 12.2])
- **Root cause:** The root cause is a missing automated pipeline for ingesting monthly RN records and updating LPR, A1, and HT tables — a scheduled-automation gap rather than a product defect. Licence expiry notifications to Saša also lack a triggered alerting mechanism.
- **Rationale:** A scheduled ETL job and expiry-alert rule could fully eliminate the recurring manual update and notification steps; the blocking 'wait for colleague data' step may resist automation until upstream data delivery is also systematised. Hours eliminated are capped at the 12.2 h baseline.
- **Validation:** Engineering team should scope the data source API/schema access for RN records and table write permissions before committing; a spike of 2–3 days would confirm feasibility and refine sprint estimate.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.4 (range [0.28, 0.49])
- **Form:** `none`
- **Deflection rate:** ~3% (range [2%, 4%])
- **Feasibility:** 0.05
- **Rationale:** These tickets are internally triggered administrative tasks (not end-user questions), so there is no external customer to deflect via FAQ or self-service; the work itself is the service. Deflection is structurally inapplicable beyond a negligible rounding margin.
- **Validation:** Confirm ticket origination: if all tickets are internally created by a single team, deflection potential is zero and no pilot is warranted.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~2.2 (range [1.6, 2.8])
- **Narrow use case:** Auto-update A1/HT and LPR tables from a validated monthly RN data feed when all required fields are present and no missing-data hold is flagged
- **Safety constraints:**
  - All input data must pass a completeness and format validation check before any write is executed
  - A human reviewer must approve the automated run output before it is treated as final for any licence or regulatory record
  - Tickets flagged as 'waiting for colleague data' must be routed to a human agent and excluded from autonomous processing
  - Autonomous action limited to table writes only; licence expiry notifications to Saša must be human-confirmed before dispatch
  - Full audit log of every automated write must be retained and reviewable
- **Rationale:** Autonomous resolution is feasible only for the clean-data subset of tickets (estimated ~25% of volume) where the monthly feed arrives complete and validated; the high proportion of structured, repetitive writes makes this viable but the licence/regulatory nature of the records demands human sign-off, capping safe autonomy. Hours saved reflect 25% of baseline with ~35% active-time reduction per automated ticket.
- **Validation:** Pilot on 3 consecutive monthly cycles with human parallel-checks; accept autonomous path only when automated output matches manual output with zero discrepancies across all pilot cycles.

### Risks

- **Compliance concerns:**
  - LPR records may constitute legally binding licence or partner registration data; incorrect automated writes could create compliance or contractual exposure
  - A1 and HT carrier card records may be subject to transport or regulatory record-keeping requirements; data integrity must be guaranteed
  - Licence expiry notifications have a time-sensitive legal or operational character; missed or erroneous notifications could cause regulatory non-compliance
- **Must not automate:**
  - Sending licence expiry notifications to Saša without explicit human review and approval
  - Any table update where the upstream data feed is incomplete, late, or unvalidated
  - Final record finalisation while a 'waiting for colleague data' hold is active

## Agent compatibility

- **Status:** `active` (extraction confidence 0.93)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Admin/operator-only configuration change

