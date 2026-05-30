---
id: hr-b2b-monthly-invoice-generation-and-fiscalization
name: hr_b2b_monthly_invoice_generation_and_fiscalization
title: HR B2B Partner Monthly Invoice Generation, Fiscalization & Related Issues
description: B2B partners (municipalities, parking/towing system operators) notify support that a billing month has been closed
  in PARKIS/PAUKIS applications and request monthly invoice generation. The dominant workflow is a routine month-end notification
  followed by support generating and making invoices available for download/printing. A secondary sub-pattern involves fiscalization
  (Fiskalizacija 2.0) questions, e-invoice (eRačun) routing errors, incorrect invoice amounts, and invoice print errors—all
  requiring configuration changes or product fixes.
category: b2b_operator/configuration
ticket_class: b2b_partner
issue_category: configuration
resolution_pattern: manual_close
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:b2b_partner|Support|duplikat:c5
project_key: RAOS
cluster_size: 76
cluster_size_dedup: 76
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.88
extraction_model: claude-sonnet-4-6
frequency_per_month: 3.71
median_resolution_minutes: 1384.5
p95_resolution_minutes: 18589.75
cannot_reproduce_rate: 0.0
data_window_start: '2025-02-20'
data_window_end: '2026-04-15'
annual_hours_saved: 11.1
roi:
  baseline_active_hours: 44.5
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 6.7
  deflection_hours_range:
  - 4.7
  - 8.7
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 11.1
  agent_assist_hours_range:
  - 8.0
  - 14.4
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 9.0
  product_fix_hours_range:
  - 6.3
  - 11.7
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 7.4
  autonomous_resolve_hours_range:
  - 5.2
  - 9.6
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-6175
- RAOS-5423
- RAOS-2077
- RAOS-2026
- RAOS-2450
- RAOS-4241
- RAOS-4985
- RAOS-6135
- RAOS-2802
- RAOS-6148
- RAOS-4762
- RAOS-5792
- RAOS-5393
- RAOS-3137
- RAOS-4541
- RAOS-6178
- RAOS-5088
- RAOS-6146
canonical_examples:
- RAOS-5423
- RAOS-4985
- RAOS-6175
vendor_dependency:
  vendor_name: eRačun intermediary (posrednik)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Automated month-end invoice generation triggered by a structured partner notification
    webhook, for pre-validated partner accounts with no outstanding configuration errors.
  autonomous_resolve_safety_constraints:
  - Only applicable to partners whose fiscalization status is confirmed active and error-free at trigger time
  - Must not proceed if any open e-invoice routing misconfiguration flag is present for that partner
  - Invoice amounts must be validated against a checksum or prior-month delta threshold before generation; halt and escalate
    if threshold exceeded
  - All autonomous actions must produce a full audit log entry attributable to the system actor
  - Partners with pending balance disputes or open ovrha records must be excluded from autonomous path
  - eRačun intermediary availability must be confirmed via health-check before any autonomous invoice submission
related_playbooks:
- dubrovnik-pass-website-hours-notice-posting
- dubrovnik-pass-website-notice-management
- hr-b2b-case-status-and-data-correction
- hr-b2b-parking-operations-support
- hr-b2b-parking-price-change-request
- hr-b2b-photo-download-enablement
- hr-b2b-sms-parking-and-ddpk-issues
- hr-b2b-user-account-management
- hr-bmove-tools-request-verification__1f253d
- hr-concessionaire-request-verification-bmove
- hr-rao-recurring-support-requests
- hr-sms-parking-payment-issues
- internal-coordination-and-reporting
- internal-it-misc-tasks-hr
- kml-polygon-upload-correction-hr
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
# Skills enabled — reads auto-execute, writes are HITL.
allowed_skills:
  - graylog_search
  - parkis_lookup
  - skidata_session_lookup
  - bmove_user_lookup
  - datatrans_transaction
  - jira_get_history
  - jira_add_internal_comment
  - jira_add_public_comment
  - jira_transition
---

# HR B2B Partner Monthly Invoice Generation, Fiscalization & Related Issues

## What this pattern is

B2B partners (municipalities, parking/towing system operators) notify support that a billing month has been closed in PARKIS/PAUKIS applications and request monthly invoice generation. The dominant workflow is a routine month-end notification followed by support generating and making invoices available for download/printing. A secondary sub-pattern involves fiscalization (Fiskalizacija 2.0) questions, e-invoice (eRačun) routing errors, incorrect invoice amounts, and invoice print errors—all requiring configuration changes or product fixes.

## When this applies

- B2B partner closes the current billing month in PARKIS or PAUKIS and notifies support
- Partner requests permission or confirmation before closing the month
- Partner cannot print an invoice (blocked by pending fiscalization)
- E-invoices are sent to incorrect recipients (e.g., self-issued invoices to own entity)
- Invoice amounts are incorrect due to calculation errors
- Partner requests change of statutory tax disclaimer text on invoices
- Partner queries fiscalization status or JIR/ZKI visibility under Fiskalizacija 2.0
- End customer complains that received e-invoice lacks sufficient description

## Typical resolution flow

1. Partner sends notification email/ticket that month has been closed in PARKIS/PAUKIS
2. Support agent receives notification and triggers monthly invoice generation in the back-end system
3. Support confirms to partner that invoices are generated and available for download/print
4. If fiscalization is pending, support waits for fiscalization to complete before notifying partner
5. For e-invoice routing errors, support adjusts e-invoice parameters so incorrect recipients are excluded in future months
6. For incorrect invoice amounts, support reproduces the issue on a test environment and schedules a fix
7. For text/disclaimer changes, support forwards request to development team and notifies partner when deployed
8. For Fiskalizacija 2.0 queries, support provides guidance directing partner to their intermediary (posrednik) for status checks

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Generate monthly invoices in the back-end system after month-close notification | support agent | RAO back-end / ParkIS / PaukIS admin | 10 min |
| Confirm fiscalization status and unblock invoice printing | support agent | RAO back-end fiscalization module | 5 min |
| Adjust e-invoice recipient parameters to prevent self-invoicing or incorrect routing | support agent | RAO e-invoice configuration | 15 min |
| Escalate incorrect invoice amount to development for investigation and fix | support agent → development team | Internal ticketing / test environment | — |
| Update statutory tax disclaimer text on invoices per partner request | development team | RAO invoice template configuration | — |
| Provide guidance on Fiskalizacija 2.0 status verification and JIR/ZKI visibility | support agent | Knowledge base / intermediary portal | 20 min |
| Update balance/saldo on enforcement (ovrha) record | support agent | RAO back-end | 10 min |

## Vendor dependency

- **Vendor:** eRačun intermediary (posrednik)

## Evidence

Derived from 76 tickets in cluster `RAOS:b2b_partner|Support|duplikat:c5`. Direct quotes from 8 representative tickets:

- `RAOS-5423` _[hr]_: "Poštovani, mjessečni računi za ParkIS su generirani i ispisani tako da ih možete preuzeti"
- `RAOS-4985` _[hr]_: "Obavještavam Vas da je mjesec LISTOPAD 2025. zaključen u aplikaciji PAUKIS."
- `RAOS-6175` _[hr]_: "sustav ne dozvoljava ispis računa prije provedene fiskalizacije te iz tog razuloga niste mogli ispisati račun"
- `RAOS-6135` _[hr]_: "sa tim pravnim osobama su otišla i 3 računa na Grad Omiš za m parking (sami smo sebi poslali račune)"
- `RAOS-6135` _[hr]_: "promjenili smo parametre za izdavanja računa eRačuna tako da više nećete dobivati iste"
- `RAOS-5792` _[hr]_: "Provjeru jesu li računi uspješno prošli fiskalizaciju potrebno je izvršiti kod Vašeg posrednika."
- `RAOS-2077` _[hr]_: "Na računima koji se izdaju od strane parkinga i pauka treba pisati: Porez na dodanu vrijednost nije obračunat temeljem čl.6 st.5 Zakona o porezu na dodanu vrijednost."
- `RAOS-4762` _[hr]_: "Kontrolom umnoška metraže broda i važeće tarife iznos nije točan (m x 26,54Eur)"

## Cluster statistics

- **Volume:** 76 tickets total (76 unique semantic events after dedup)
- **Frequency:** 3.71 tickets/month (over data window 2025-02-20 → 2026-04-15)
- **Median resolution:** 23.1 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~44.5 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~11.1 (range [8, 14.43])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** Most resolution actions are well-defined and repeatable (invoice generation, fiscalization confirmation, e-invoice parameter adjustment, balance update), making them good candidates for agent-assist macros or guided runbooks that pre-fill steps and surface the correct back-end commands; this reduces per-ticket active time without requiring full automation of billing-critical actions.
- **Validation:** Deploy a shadow-mode agent-assist tool for 3 weeks that suggests the appropriate runbook based on ticket keyword classification; measure actual time-to-resolution versus the 60-minute baseline and record agent acceptance rate of suggestions.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~4 (range [3, 5])
- **Hours eliminated per year:** ~9 (range [6.3, 11.7])
- **Root cause:** Three distinct product gaps drive secondary tickets: (1) fiscalization blocking invoice printing instead of providing a clear in-app status and self-service unblock, (2) e-invoice routing logic that permits self-invoicing or incorrect recipient resolution without validation warnings, and (3) invoice amount calculation errors requiring dev investigation. The dominant month-close workflow is not a bug but a missing self-service trigger surface.
- **Rationale:** Fixing fiscalization unblock UI, adding e-invoice recipient validation, and surfacing invoice calculation audit trails would eliminate the secondary sub-pattern tickets (actions 2, 3, 4 partial); the core month-close notification and invoice generation workflow would remain unless a partner-triggered generation endpoint is also built. Hours eliminated are capped at the portion attributable to secondary sub-patterns (~20% of baseline hours), staying well within the 44.5-hour ceiling.
- **Validation:** Engineering should spike each fix area (fiscalization UI, e-invoice validation, amount audit log) separately to produce story-point estimates; compare estimated sprint cost against projected ticket-reduction measured in a 3-month post-release window.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~6.7 (range [4.69, 8.71])
- **Form:** `help_center`
- **Deflection rate:** ~15% (range [10%, 20%])
- **Feasibility:** 0.45
- **Rationale:** The dominant workflow (month-close notification → invoice generation) requires a human back-end action and cannot be deflected by documentation alone; however, Fiskalizacija 2.0 guidance and JIR/ZKI visibility questions (~action 6) are documentation-addressable for a subset of partners. Overall deflection potential is limited because most tickets require an agent to actually perform a system action, not just answer a question.
- **Validation:** Publish a step-by-step help-center article on Fiskalizacija 2.0 status verification and e-invoice routing checks; measure ticket volume for those sub-topics over a 6-week period and compare against the prior 6-week baseline to assess deflection rate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~7.4 (range [5.2, 9.6])
- **Narrow use case:** Automated month-end invoice generation triggered by a structured partner notification webhook, for pre-validated partner accounts with no outstanding configuration errors.
- **Safety constraints:**
  - Only applicable to partners whose fiscalization status is confirmed active and error-free at trigger time
  - Must not proceed if any open e-invoice routing misconfiguration flag is present for that partner
  - Invoice amounts must be validated against a checksum or prior-month delta threshold before generation; halt and escalate if threshold exceeded
  - All autonomous actions must produce a full audit log entry attributable to the system actor
  - Partners with pending balance disputes or open ovrha records must be excluded from autonomous path
  - eRačun intermediary availability must be confirmed via health-check before any autonomous invoice submission
- **Rationale:** The month-close notification → invoice generation action is highly routine and structurally identical across partners, making it the most automatable slice; however, billing and fiscalization regulatory obligations in Croatia demand strict pre-condition checks and a conservative volume cap to avoid erroneous invoice issuance. The 25% volume cap reflects that only clean, pre-validated partner accounts should enter the autonomous path in early rollout.
- **Validation:** Run a 6-week pilot where the system generates invoices autonomously for 3–5 pre-selected low-risk partner accounts after month-close notification; require agent review and explicit approval before final delivery; measure error rate, partner satisfaction, and time saved before expanding scope.

### Risks

- **Compliance concerns:**
  - Croatian Fiskalizacija 2.0 regulations require every issued invoice to carry a valid JIR (unique invoice identifier) and ZKI (security code); any automated generation must guarantee these are obtained before delivery
  - eRačun (e-invoice) routing is subject to Croatian e-invoicing mandate rules; incorrect recipient assignment may result in legally non-compliant invoice delivery
  - Statutory tax disclaimer text is legally mandated; automated invoice generation must use only approved, currently valid disclaimer versions
  - Invoice amounts directly affect VAT reporting; erroneous autonomous generation could trigger tax authority scrutiny
- **Must not automate:**
  - Adjustment of incorrect invoice amounts—requires developer investigation and may involve credit note issuance under Croatian accounting law
  - Update of statutory tax disclaimer text—must be approved by a qualified accountant or legal representative before deployment
  - Balance/saldo updates on enforcement (ovrha) records—these have legal enforcement implications and require human authorization
  - Any invoice action for partners with open disputes, pending escalations, or unresolved fiscalization errors
- **Vendor dependencies blocking automation:**
  - eRačun intermediary (posrednik) availability and API stability is a prerequisite for any automated e-invoice submission; absence of a defined SLA or health-check endpoint blocks autonomous resolve for e-invoice routing scenarios
  - Fiskalizacija 2.0 service availability (Croatian Tax Authority CIS endpoint) must be confirmed before autonomous invoice generation; downtime would cause JIR acquisition failures and legally invalid invoices

## Agent compatibility

- **Status:** `active` (extraction confidence 0.88)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

