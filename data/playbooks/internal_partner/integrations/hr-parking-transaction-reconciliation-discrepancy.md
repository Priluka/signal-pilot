---
id: hr-parking-transaction-reconciliation-discrepancy
name: hr_parking_transaction_reconciliation_discrepancy
title: Croatia parking transaction reconciliation discrepancies between RAO, Payway/Corvus, and Igeus systems
description: Recurring monthly reconciliation tickets identifying transactions where confirmation status differs across RAO
  (ParkIS), Igeus, and Payway/Corvus/Bmove payment systems. The discrepancies include 'illegal state change' errors, 'call
  unsuccessful' failures, and cases where payment was confirmed in one system but not others. Resolution typically involves
  manual investigation, storno (reversal) actions in Igeus and/or RAO, and occasional refunds to end users.
category: internal_partner/integrations
ticket_class: internal_partner
issue_category: integration_issue
resolution_pattern: manual_close
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:unknown|no_value|no_label:c2
project_key: BS
cluster_size: 23
cluster_size_dedup: 23
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.93
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.45
median_resolution_minutes: 2959.0
p95_resolution_minutes: 48761.59999999997
cannot_reproduce_rate: 0.0
data_window_start: '2022-03-28'
data_window_end: '2024-12-16'
annual_hours_saved: 2.5
roi:
  baseline_active_hours: 9.9
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.1
  deflection_hours_range:
  - 0.1
  - 0.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 2.5
  agent_assist_hours_range:
  - 1.8
  - 3.2
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 7.4
  product_fix_hours_range:
  - 5.9
  - 9.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.3
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-9762
- BS-6272
- BS-4350
- BS-284
- BS-1046
- BS-3885
- BS-5498
- BS-7714
- BS-2553
- BS-4645
- BS-3655
- BS-2852
- BS-8642
- BS-12736
- BS-31074
- BS-7103
- BS-3398
- BS-2369
canonical_examples:
- BS-9762
- BS-5498
- BS-8642
vendor_dependency:
  vendor_name: RAO (ParkIS), Igeus, Erste/Payway, A1, Bon bon, Tisak plus
  involves_vendor: true
  typical_wait_days: 3
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Automated storno of Igeus-only-confirmed transactions where Payway shows no charge and
    amount is below a defined threshold (e.g. <50 HRK/€6)
  autonomous_resolve_safety_constraints:
  - Only apply to transactions where Payway/Corvus definitively shows no charge (not ambiguous/pending)
  - Amount must be below a pre-approved threshold to limit financial exposure
  - End-user refund actions must never be autonomous — require human approval
  - Audit log of every automated storno must be retained and reviewed monthly
  - Must not act on RAO/ParkIS discrepancies without human review due to vendor dependency and external legal implications
  - Operator must confirm no active vendor API changes are in flight before enabling
related_playbooks:
- bmove-app-feedback-mixed-issues__d6cf0c
- bmove-skidata-not-recognized-manual-open
- pkc-license-plate-purchase-logging
- russian-spam-suggestion-tickets
- test-and-junk-tickets
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Croatia parking transaction reconciliation discrepancies between RAO, Payway/Corvus, and Igeus systems

## What this pattern is

Recurring monthly reconciliation tickets identifying transactions where confirmation status differs across RAO (ParkIS), Igeus, and Payway/Corvus/Bmove payment systems. The discrepancies include 'illegal state change' errors, 'call unsuccessful' failures, and cases where payment was confirmed in one system but not others. Resolution typically involves manual investigation, storno (reversal) actions in Igeus and/or RAO, and occasional refunds to end users.

## When this applies

- Monthly reconciliation review reveals mismatches between RAO, Igeus, and Payway/Corvus confirmation statuses
- Transaction confirmed in Igeus but not in RAO (or vice versa)
- Transaction shows 'illegal state change' error in reconciliation table
- Transaction shows 'call unsuccessful' error preventing full confirmation
- Payment charged to user but parking permit not properly registered
- Ticketless transactions missing from Igeus portal
- Missing transactions on Igeus portal after a specific timestamp

## Typical resolution flow

1. Reconciliation table generated listing all transactions with mismatched confirmation status across RAO, Igeus, Payway, and Parkulator
2. Internal team reviews each discrepant transaction
3. Transactions confirmed only in Igeus (not paid) are storno'd in Igeus
4. Transactions confirmed in Igeus and Payway but not in RAO are escalated to RAO via their Jira
5. RAO or concession operator investigated for post-hoc cancellations (storno) in ParkIS
6. If payment was collected but permit not issued, refund is evaluated and issued
7. Edge cases (wrong registration plate, KEKS Pay abort, mGarage mapping error) resolved ad-hoc
8. Ticket closed after all discrepancies are addressed or explained

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Generate and share monthly transaction reconciliation table across RAO, Igeus, Payway, and Parkulator | internal operations/support | IGeus BO / internal reporting | 30 min |
| Storno (reverse) transactions in Igeus that are only Igeus-confirmed but not paid | internal support agent | IGeus BO | 20 min |
| Escalate unresolved RAO discrepancies via RAO Jira ticket | internal support agent | RAO Jira (Jira.rao.hr) | 15 min |
| Investigate individual payment failure in Payway/Corvus/Erste logs | internal developer or support | Bmove/IGeus database, Payway logs | 30 min |
| Issue refund for transaction charged but not confirmed end-to-end | internal support agent | IGeus BO / Corvus | 15 min |

## Vendor dependency

- **Vendor:** RAO (ParkIS), Igeus, Erste/Payway, A1, Bon bon, Tisak plus
- **Typical wait:** 3 day(s)

## Evidence

Derived from 23 tickets in cluster `BS:unknown|no_value|no_label:c2`. Direct quotes from 8 representative tickets:

- `BS-9762` _[hr]_: "Trenutni podaci o razlikama transakcija Rao-Igeus-Payway za 06. mjesec su sljedeći"
- `BS-5498` _[hr]_: "ove koje su u ovoj tablici strikethrough sam stornirao u IGeusu (ove koje su samo IGeus confirmed). Imamo dosta ovih koje su PayWay i IGeus confirmed, ali RAO nisu"
- `BS-8642` _[hr]_: "ovih 5 koje su naplaćene i potvrđene na IGeusu sve su obustavljene od strane koncesionara. Niti jedan od njih nam se nije javio za storno i refund."
- `BS-3398` _[hr]_: "kaže Đuka da su te transakcije naknadno stornirane u ParkIS-u"
- `BS-12736` _[hr]_: "Transakciju zx13v-a6adb-eje sam refundao jer nije bila na RAO potvrđena, a ni na IGeusu, ali je bila na Corvusu naplaćena."
- `BS-3885` _[hr]_: "bila je greška u mapiranju statusa prema A1 operatoru. Ista greška je ispravljena."
- `BS-8642` _[hr]_: "desilo se to da aplikacija nije mogla pozvati celery task"
- `BS-284` _[hr]_: "nedostaju transakcije od 25.03 u 17:43 na dalje na Igeus portalu pa molim provjeru"

## Cluster statistics

- **Volume:** 23 tickets total (23 unique semantic events after dedup)
- **Frequency:** 0.45 tickets/month (over data window 2022-03-28 → 2024-12-16)
- **Median resolution:** 2.1 days
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~9.9 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~2.5 (range [1.8, 3.2])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.70
- **Rationale:** The reconciliation table generation (step 1, ~30 min) and RAO Jira escalation drafting (step 3, ~15 min) are templated, structured tasks well-suited to agent-assist tooling; auto-populating the reconciliation template from system exports and pre-filling the Jira escalation form could cut active time by roughly 25% per ticket.
- **Validation:** Run shadow-mode for 4 weeks: have the tool auto-generate the reconciliation table draft and Jira template alongside the agent's manual process; measure time delta and error rate before enabling in live workflow.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~8 (range [6, 10])
- **Hours eliminated per year:** ~7.4 (range [5.9, 9.62])
- **Root cause:** Asynchronous confirmation handshakes between RAO/ParkIS, Igeus, and Payway/Corvus lack reliable idempotent reconciliation: partial failures ('illegal state change', 'call unsuccessful') leave transactions in inconsistent states across systems with no automated compensating transaction. This is a multi-vendor integration design gap rather than a single-codebase bug.
- **Rationale:** Implementing a robust saga/outbox pattern or automated nightly reconciliation job that auto-resolves known-safe discrepancy types (e.g. Igeus-confirmed but not paid → auto-storno) would eliminate the majority of manual steps, but requires coordination with RAO and Igeus vendors and cannot exceed the 9.9-hour baseline. Full elimination is capped at baseline.
- **Validation:** Run a 2-sprint spike to instrument the Payway/Igeus/RAO handshake with structured logging; measure actual failure-mode distribution before committing to full fix scope. Vendor API change feasibility must be confirmed with RAO and Igeus before sprint commitment.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.04, 0.065])
- **Form:** `none`
- **Deflection rate:** ~3% (range [2%, 4%])
- **Feasibility:** 0.05
- **Rationale:** These tickets originate from internal operations staff performing monthly reconciliation, not from end-user confusion — there is no self-service channel that would intercept or deflect them. The discrepancies require cross-system investigation that cannot be resolved by reading documentation.
- **Validation:** Confirm ticket origin (internal ops vs external users) by tagging submitter type on next 10 tickets; if >90% internal, deflection feasibility remains near zero.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.5 (range [0.35, 0.65])
- **Narrow use case:** Automated storno of Igeus-only-confirmed transactions where Payway shows no charge and amount is below a defined threshold (e.g. <50 HRK/€6)
- **Safety constraints:**
  - Only apply to transactions where Payway/Corvus definitively shows no charge (not ambiguous/pending)
  - Amount must be below a pre-approved threshold to limit financial exposure
  - End-user refund actions must never be autonomous — require human approval
  - Audit log of every automated storno must be retained and reviewed monthly
  - Must not act on RAO/ParkIS discrepancies without human review due to vendor dependency and external legal implications
  - Operator must confirm no active vendor API changes are in flight before enabling
- **Rationale:** Only the narrowest subset — clear Igeus-only confirmations with no Payway charge — is safe to automate given multi-vendor dependencies, financial reversal risk, and the need for human judgment on ambiguous states. Expected volume of qualifying cases is low, limiting hour savings.
- **Validation:** Pilot over 3 months with human-in-the-loop approval required for every automated storno candidate; acceptance criteria: 0 incorrect reversals, 100% audit trail coverage, confirmed Payway 'no charge' signal reliability ≥98% before removing human gate.

### Risks

- **Compliance concerns:**
  - Automated financial reversals (storno) may require audit trail under Croatian payment regulations and PSD2 requirements
  - Refunds to end users must comply with consumer protection rules and Erste/Payway contractual terms
  - Multi-vendor transaction data sharing (RAO, Igeus, Payway) may have data processing agreement implications under GDPR
- **Must not automate:**
  - End-user refund issuance — requires human review of charge confirmation and user communication
  - RAO/ParkIS storno or state changes — vendor dependency means automated actions risk creating further illegal state changes
  - Any transaction where payment status in Payway is ambiguous or pending (not definitively confirmed or denied)
- **Vendor dependencies blocking automation:**
  - RAO (ParkIS) requires Jira-based escalation with typical 3-day wait; no API for automated state correction currently described
  - Igeus storno capability depends on API access and idempotency guarantees not yet confirmed
  - Erste/Payway/Corvus log access for automated reconciliation requires confirmed API or export integration
  - A1, Bon bon, Tisak plus involvement suggests multi-channel payment paths that may have separate reconciliation protocols not covered by a single automation

## Agent compatibility

- **Status:** `active` (extraction confidence 0.93)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

