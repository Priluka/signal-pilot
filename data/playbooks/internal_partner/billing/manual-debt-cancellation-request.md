---
id: manual-debt-cancellation-request
name: manual_debt_cancellation_request
title: Internal requests to manually cancel parking debts for whitelisted or BIP vehicles
description: Support agents or internal partners submit tickets requesting manual cancellation of outstanding parking debts
  for specific license plates, often because the vehicle is on a whitelist, belongs to a BIP employee/company car, or the
  debt was incorrectly created. Resolvers (typically Hrvoje Sirovina, Paulina Mrnarević, or roland.soter) cancel the debt
  directly in the backend system. In some cases, the root cause is traced to the third-party system xparking sending incorrect
  pricing data despite the license plate being whitelisted.
category: internal_partner/billing
ticket_class: internal_partner
issue_category: billing
resolution_pattern: manual_close
languages:
- en
- de
country_focus:
- at
- de
- hr
- other
status: active
cluster_id: BS:unknown|austria|no_label:c2
project_key: BS
cluster_size: 45
cluster_size_dedup: 45
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.92
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.88
median_resolution_minutes: 212.5
p95_resolution_minutes: 138441.00000000012
cannot_reproduce_rate: 0.0222
data_window_start: '2024-11-28'
data_window_end: '2026-02-27'
annual_hours_saved: 0.7
roi:
  baseline_active_hours: 2.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.1
  deflection_hours_range:
  - 0.1
  - 0.2
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.7
  agent_assist_hours_range:
  - 0.5
  - 0.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.2
  product_fix_hours_range:
  - 1.6
  - 2.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
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
- BS-37439
- BS-46220
- BS-35168
- BS-30235
- BS-32372
- BS-37701
- BS-41263
- BS-39624
- BS-39639
- BS-33772
- BS-46160
- BS-38150
- BS-47732
- BS-39528
- BS-49323
- BS-32010
- BS-39470
- BS-44068
canonical_examples:
- BS-37439
- BS-30235
- BS-32372
vendor_dependency:
  vendor_name: xparking
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-cancel debts for plates with active, verified whitelist or BIP employee status
    where the debt was created within 24 hours and amount is below a defined threshold.
  autonomous_resolve_safety_constraints:
  - Plate must have a current, verified whitelist or BIP employee flag in the authoritative internal registry at time of automation
    — no external xparking whitelist data trusted without verification.
  - Debt must be below a monetary threshold (to be defined by finance/compliance) to limit financial exposure from erroneous
    auto-cancellations.
  - Debt creation timestamp must be within 24 hours (reduces risk of cancelling legitimately accrued charges).
  - Full audit log of every automated cancellation must be written and reviewed weekly by a named resolver.
  - Any plate with a prior disputed cancellation must be excluded from autonomous handling and routed to human resolver.
  - xparking vendor dependency means incorrect data may trigger automation incorrectly; a circuit-breaker should pause automation
    if error rate exceeds a threshold.
related_playbooks:
- b2b-missing-parking-receipt-request
- bmove-app-operational-issues-austria
- bmove-skidata-not-recognized-manual-open
- croatian-parking-debt-payment-failure
- hr-b2b-partner-billing-payment-storno
- missing-parking-receipt-request
- pkc-license-plate-purchase-logging
- scs-westfield-open-session-daily-check__a69ff7
- scs-westfield-open-session-daily-check__c72ee4
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Internal requests to manually cancel parking debts for whitelisted or BIP vehicles

## What this pattern is

Support agents or internal partners submit tickets requesting manual cancellation of outstanding parking debts for specific license plates, often because the vehicle is on a whitelist, belongs to a BIP employee/company car, or the debt was incorrectly created. Resolvers (typically Hrvoje Sirovina, Paulina Mrnarević, or roland.soter) cancel the debt directly in the backend system. In some cases, the root cause is traced to the third-party system xparking sending incorrect pricing data despite the license plate being whitelisted.

## When this applies

- A whitelisted license plate is charged a parking debt it should not have incurred
- A BIP company car or employee vehicle receives an unexpected debt
- A garage is not on the whitelist, causing incorrect debt creation
- A customer account has a debt that needs to be canceled for operational or GDPR reasons
- No payment method selected in Ticketless, resulting in outstanding payment

## Typical resolution flow

1. Internal agent identifies a debt on a license plate and creates or comments on a ticket
2. Agent tags a resolver (e.g., @Hrvoje Sirovina, @Paulina Mrnarević) with a cancellation request
3. Resolver checks the account for debts and verifies the license plate
4. Resolver manually cancels the debt in the backend system
5. Resolver confirms cancellation via comment; ticket is closed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Request debt cancellation by tagging a resolver in ticket comments | internal support agent or partner | Jira (Bmove Support) | 5 min |
| Look up license plate account and verify outstanding debts | resolver (e.g., Hrvoje Sirovina, Paulina Mrnarević, roland.soter) | Bmove backend / admin system | 5 min |
| Manually cancel the debt in the backend system | resolver | Bmove backend / admin system | 5 min |
| Escalate whitelist recognition issue to xparking | resolver or support agent | xParking communication channel | — |

## Vendor dependency

- **Vendor:** xparking

## Evidence

Derived from 45 tickets in cluster `BS:unknown|austria|no_label:c2`. Direct quotes from 6 representative tickets:

- `BS-37439` _[en]_: "please cancel debt, thank you  garage not on whitelist"
- `BS-30235` _[en]_: "debt is canceled. For these whitelist issues please check with xparking. We get a price from xparking that we charge. If the lpn is whitelisted, then the xparking should send zero or nothing."
- `BS-32372` _[en]_: "please cancel the debt, its a BIP car, thank you garage was not on whitelist"
- `BS-33772` _[en]_: "please cancel debts for LP W**** (is employee of BIP)"
- `BS-49323` _[en]_: "debt is canceled, no other debt is opened. The customer hasn't selected any payment method for TL, although he has added a card to his account."
- `BS-44068` _[en]_: "W**** - debt of 42,00 € canceled, customer had two more outstanding payments of 2,50 and 7,50 €."

## Cluster statistics

- **Volume:** 45 tickets total (45 unique semantic events after dedup)
- **Frequency:** 0.88 tickets/month (over data window 2024-11-28 → 2026-02-27)
- **Median resolution:** 3.5 hours
- **Cannot Reproduce rate:** 2.2%
- **Languages:** en, de
- **Country focus:** at, de, hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.7 (range [0.47, 0.845])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.65
- **Rationale:** An assist tool that pre-fetches the license plate's account status and outstanding debts upon ticket creation would compress the lookup step (~5 min) and auto-populate the cancellation request template, reducing active time per ticket meaningfully. The remaining manual cancellation action still requires resolver judgment and backend access, limiting total savings.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-fetches account data and surfaces it alongside the ticket; compare resolver time-on-ticket before and after, targeting ≥20% reduction to validate the midpoint estimate.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~2.2 (range [1.6, 2.6])
- **Root cause:** Third-party system xparking sends incorrect pricing data for license plates that are already on the whitelist or belong to BIP employees/company cars, causing debts to be incorrectly created in the first place. A reliable fix would require xparking to correctly honour whitelist status before generating debt records, or a backend rule to suppress debt creation for whitelisted plates.
- **Rationale:** If xparking correctly propagates whitelist data or the backend automatically voids debts for whitelisted plates before they reach support, the majority of tickets in this cluster would be eliminated; however, a residual volume of edge cases (e.g., newly added plates with sync lag) is expected. Hours eliminated are capped at baseline 2.6 h/year.
- **Validation:** Engineering should audit xparking API contracts and whitelist sync frequency; estimate sprint effort by scoping whether the fix lives in the integration layer (lower effort) or requires xparking vendor changes (higher effort and timeline uncertainty).

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.091, 0.169])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These are internal agent-to-resolver requests requiring privileged backend access; end-user self-service cannot perform debt cancellations and the submitters are already trained internal staff, leaving negligible deflection opportunity. An FAQ or chatbot cannot substitute for backend system access.
- **Validation:** Document whether any submitted tickets already contained sufficient information to be auto-routed directly to resolvers without agent involvement; measure ticket volume over 4 weeks to confirm the internal-only nature of the flow.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.2 (range [0.18, 0.312])
- **Narrow use case:** Auto-cancel debts for plates with active, verified whitelist or BIP employee status where the debt was created within 24 hours and amount is below a defined threshold.
- **Safety constraints:**
  - Plate must have a current, verified whitelist or BIP employee flag in the authoritative internal registry at time of automation — no external xparking whitelist data trusted without verification.
  - Debt must be below a monetary threshold (to be defined by finance/compliance) to limit financial exposure from erroneous auto-cancellations.
  - Debt creation timestamp must be within 24 hours (reduces risk of cancelling legitimately accrued charges).
  - Full audit log of every automated cancellation must be written and reviewed weekly by a named resolver.
  - Any plate with a prior disputed cancellation must be excluded from autonomous handling and routed to human resolver.
  - xparking vendor dependency means incorrect data may trigger automation incorrectly; a circuit-breaker should pause automation if error rate exceeds a threshold.
- **Rationale:** Given the financial sensitivity of debt cancellation and the known unreliability of xparking whitelist data, only a narrow, low-risk subset should be considered for autonomous resolution; the safety cap and constraints significantly limit achievable volume, making actual hour savings modest relative to baseline. Over-automating in this pattern risks incorrectly cancelling legitimate debts.
- **Validation:** Pilot with 4-week dry-run (log proposed auto-cancellations without executing them); compare proposed actions against resolver decisions to measure false-positive rate; only proceed to live automation if false-positive rate is under 2%.

### Risks

- **Compliance concerns:**
  - Automated or semi-automated debt cancellation creates an audit trail requirement — each cancellation must be attributable to an authorised action or rule.
  - Incorrectly cancelling a legitimate debt constitutes a financial write-off; finance/legal must approve thresholds and automation scope.
  - GDPR/data-handling: license plate lookups involve personal data; automation must not log or expose plate data beyond what is necessary.
- **Must not automate:**
  - Debt cancellations where whitelist status cannot be confirmed in the internal authoritative registry (xparking data alone is insufficient given known data quality issues).
  - Cancellations above the agreed monetary threshold without explicit human resolver approval.
  - Cases where the debt may be legitimate (e.g., plate recently removed from whitelist, or BIP employee personal use scenario).
- **Vendor dependencies blocking automation:**
  - xparking sends incorrect pricing data for whitelisted plates — any automation relying on xparking data for whitelist status is unreliable until the vendor fixes the data feed.
  - No SLA or typical_wait_days is defined for xparking issue resolution, creating uncertainty on when the root-cause product fix could be validated.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.92)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

