---
id: b2b-missing-parking-receipt-request
name: b2b_missing_parking_receipt_request
title: B2B partners requesting missing or unavailable parking receipts/invoices for accounting purposes
description: B2B partner customers (companies) report that they did not receive a receipt or invoice for a completed parking
  session, or that the document is not available for download in the app/portal. These customers require formal receipts or
  tax invoices to properly book parking expenses in their accounting systems. The support team resolves these requests by
  sending a replacement receipt ('Ersatzquittung') as an email attachment.
category: b2b_operator/billing
ticket_class: b2b_partner
issue_category: billing
resolution_pattern: manual_close
languages:
- de
country_focus:
- at
- de
status: active
cluster_id: BS:b2b_partner|austria|no_label:c2
project_key: BS
cluster_size: 16
cluster_size_dedup: 16
sample_size_used: 16
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.31
median_resolution_minutes: 938.0
p95_resolution_minutes: 39938.75
cannot_reproduce_rate: 0.0
data_window_start: '2025-03-14'
data_window_end: '2026-05-01'
annual_hours_saved: 0.3
roi:
  baseline_active_hours: 1.1
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.2
  deflection_hours_range:
  - 0.1
  - 0.3
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.3
  agent_assist_hours_range:
  - 0.2
  - 0.4
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.9
  product_fix_hours_range:
  - 0.6
  - 1.1
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.3
  autonomous_resolve_hours_range:
  - 0.2
  - 0.3
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-34910
- BS-44469
- BS-45781
- BS-46729
- BS-49090
- BS-50719
- BS-51142
- BS-52086
- BS-52893
- BS-35861
- BS-47536
- BS-50333
- BS-51426
- BS-47504
- BS-45851
- BS-34774
canonical_examples:
- BS-34910
- BS-51142
- BS-46729
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
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-retrieve and email replacement receipt for B2B partners when a matched transaction
    is unambiguously identified by ticket number or license plate + date
  autonomous_resolve_safety_constraints:
  - Must confirm transaction identity match with high confidence before issuing any tax document
  - Tax invoice must be correctly formatted and legally compliant for jurisdiction
  - Ambiguous cases (multiple matching sessions, wrong-date flags) must escalate to human agent
  - B2B partner email address must be verified against account record before sending
  - Must not auto-issue corrected receipts if prior version already sent — requires human review
related_playbooks:
- b2b-outstanding-payment-failure-app
- b2b-partner-austria-ticketless-open-session-at-exit
- b2b-ticketless-outstanding-payment-failure
- croatian-parking-debt-payment-failure
- hr-b2b-partner-billing-payment-storno
- manual-debt-cancellation-request
- missing-parking-receipt-request
- ticketless-open-session-not-closed-at-exit
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# B2B partners requesting missing or unavailable parking receipts/invoices for accounting purposes

## What this pattern is

B2B partner customers (companies) report that they did not receive a receipt or invoice for a completed parking session, or that the document is not available for download in the app/portal. These customers require formal receipts or tax invoices to properly book parking expenses in their accounting systems. The support team resolves these requests by sending a replacement receipt ('Ersatzquittung') as an email attachment.

## When this applies

- Parking receipt/invoice was not delivered automatically after a ticketless parking session
- Receipt is not available for download in the Bmove app or user portal
- Receipt was not received by email (including not in spam folder)
- Monthly billing archive does not contain the individual parking receipt
- Company needs a formal tax document ('Steuerbeleg') for accounting/bookkeeping purposes
- Receipt was previously sent but lost or not forwarded internally

## Typical resolution flow

1. B2B customer contacts support referencing parking ticket number, license plate, date, and/or garage
2. Support agent locates the parking transaction in the internal system
3. Support agent generates or retrieves the replacement receipt ('Ersatzquittung')
4. Support agent sends the replacement receipt as an email attachment
5. If date or details are incorrect on first receipt, customer reports the error and a corrected receipt is reissued
6. If the transaction cannot be found under the provided details, support requests clarification (e.g., correct license plate or date)

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Look up parking transaction by ticket number, license plate, date, or garage in internal system | support_agent | internal Bmove back-office system | 5 min |
| Generate replacement receipt ('Ersatzquittung') for the parking session | support_agent | internal Bmove back-office system | 5 min |
| Send replacement receipt as email attachment to customer | support_agent | email | 2 min |
| Reissue corrected receipt if customer reports an error (e.g., wrong date) | support_agent | internal Bmove back-office system | 5 min |

## Evidence

Derived from 16 tickets in cluster `BS:b2b_partner|austria|no_label:c2`. Direct quotes from 7 representative tickets:

- `BS-34910` _[de]_: "für den Parkschein 202502161606000400231644 wurde bis jetzt keine Rechnung übermittelt und diese steht auch nicht zum Download bereit."
- `BS-51142` _[de]_: "Wir benötigen aber als Firma eine Steuerbeleg damit wir das ordnungsgemäß verbuchen können."
- `BS-46729` _[de]_: "Ich kann ihn leider nicht finden und brauche ihn für die Buchhaltung."
- `BS-46729` _[de]_: "Allerdings ist das Datum auf der Rechnung falsch. Ich habe am 11.12. (nicht 30.12.) in der Garage Palais Corso geparkt. Bitte um erneute, korrekte Zusendung."
- `BS-49090` _[de]_: "leider habe ich für folgende Parkvorgänge keine Quittungen bekommen. Diese sind in der App auch nicht verfügbar"
- `BS-50333` _[de]_: "leider können wir die Rechnung nicht auf dem Benutzerkonto herunterladen"
- `BS-44469` _[de]_: "bis jetzt wurde der Beleg dieses Parkscheins nicht zugemailt (ist auch nicht im Spamordner gelandet)"

## Cluster statistics

- **Volume:** 16 tickets total (16 unique semantic events after dedup)
- **Frequency:** 0.31 tickets/month (over data window 2025-03-14 → 2026-05-01)
- **Median resolution:** 15.6 hours
- **Languages:** de
- **Country focus:** at, de

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~1.1 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.3 (range [0.231, 0.429])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.80
- **Rationale:** The resolution workflow is highly structured — lookup, generate, send — making it well-suited for an assist tool that pre-populates transaction details and drafts the reply with the attachment ready; estimated 30% time reduction assumes lookup and draft steps are largely automated while the agent confirms and sends. Active hours saved are modest given low annual frequency.
- **Validation:** Run shadow-mode assist tool for 2 weeks alongside live agent handling; compare measured active minutes per ticket with and without assist to calibrate actual time reduction.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~0.9 (range [0.62, 1.1])
- **Root cause:** Receipts and invoices for completed parking sessions are either not automatically generated, not delivered, or not accessible in the app/portal — forcing B2B partners to contact support rather than self-serving a document that should be available by default.
- **Rationale:** If receipts were auto-generated and reliably delivered (or downloadable on demand) for all completed B2B sessions, the vast majority of these contacts would not occur; the fix addresses root cause rather than symptoms. Upper bound is capped at the 1.1 h baseline.
- **Validation:** Engineering team estimates effort via spike on receipt-generation pipeline coverage gaps; validate by tracking receipt-related contact rate for B2B partners in the 8 weeks post-fix deployment.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.2 (range [0.15, 0.273])
- **Form:** `in_app_help`
- **Deflection rate:** ~20% (range [14%, 26%])
- **Feasibility:** 0.55
- **Rationale:** B2B partners need formal tax invoices, which requires system lookup and generation — pure FAQ content cannot fully resolve the need, but an in-app self-service receipt download could deflect a meaningful subset where the document already exists but wasn't surfaced. The structural gap (receipt not available) limits deflection ceiling significantly.
- **Validation:** Deploy a self-service 'download receipt' button in the B2B portal for completed sessions over a 4-week pilot; track what fraction of contacts drop after portal improvement vs. the prior-period baseline.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~0.3 (range [0.19, 0.35])
- **Narrow use case:** Auto-retrieve and email replacement receipt for B2B partners when a matched transaction is unambiguously identified by ticket number or license plate + date
- **Safety constraints:**
  - Must confirm transaction identity match with high confidence before issuing any tax document
  - Tax invoice must be correctly formatted and legally compliant for jurisdiction
  - Ambiguous cases (multiple matching sessions, wrong-date flags) must escalate to human agent
  - B2B partner email address must be verified against account record before sending
  - Must not auto-issue corrected receipts if prior version already sent — requires human review
- **Rationale:** Autonomous resolution is technically plausible for clean, unambiguous lookup-and-send cases, but the tax document nature and B2B accounting requirements impose strict accuracy and compliance constraints that limit safe automation to roughly a quarter of volume. The absolute hours saved are small given the low annual frequency.
- **Validation:** Pilot with 6-week shadow mode: system identifies candidate tickets for autonomous handling but human agent executes; measure match accuracy and false-positive rate before enabling auto-send; accept only if precision ≥ 95% on transaction matching.

### Risks

- **Compliance concerns:**
  - Replacement receipts ('Ersatzquittung') and tax invoices must comply with local tax law (e.g., German UStG VAT requirements); incorrect documents could expose B2B partners to accounting or tax audit risk.
  - Sending financial documents to an unverified or incorrect email address may violate GDPR data-handling obligations.
  - Any automated generation of tax-relevant documents must be auditable and retain a complete issuance log.
- **Must not automate:**
  - Issuance of corrected receipts where customer has reported an error (wrong date, wrong amount) — requires human validation before reissue.
  - Cases where multiple transactions match the lookup criteria — ambiguity must be resolved by a human agent.
  - Any case involving disputed charges or potential fraud signals on the parking session.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

