---
id: missing-parking-receipt-email
name: missing_parking_receipt_email
title: Users not receiving parking receipts/invoices via email or in-app download
description: End users report that after completing a parking session via the Bmove app, they do not receive an automated
  receipt or invoice by email, and/or the receipt is not downloadable in the app. This affects both individual and business
  users, who often need the receipts for accounting or expense reimbursement purposes. The standard resolution is for support
  staff to manually send a replacement receipt (Ersatzquittung) to the user.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: vendor_escalation
languages:
- de
country_focus:
- at
- de
status: active
cluster_id: BS:end_user|austria|invoice_issue:c0
project_key: BS
cluster_size: 32
cluster_size_dedup: 30
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.59
median_resolution_minutes: 1062.5
p95_resolution_minutes: 67513.89999999997
cannot_reproduce_rate: 0.0312
data_window_start: '2023-11-03'
data_window_end: '2025-07-09'
annual_hours_saved: 1.6
roi:
  baseline_active_hours: 5.4
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.5
  deflection_hours_range:
  - 0.4
  - 0.7
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.6
  agent_assist_hours_range:
  - 1.1
  - 2.1
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 5.4
  product_fix_hours_range:
  - 3.8
  - 5.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.4
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-33821
- BS-33525
- BS-35015
- BS-15144
- BS-21944
- BS-27122
- BS-34905
- BS-22457
- BS-26821
- BS-39438
- BS-22671
- BS-25879
- BS-23633
- BS-34124
- BS-34014
- BS-34649
- BS-39503
- BS-27392
canonical_examples:
- BS-33525
- BS-35015
- BS-35015
vendor_dependency:
  vendor_name: xparking
  involves_vendor: true
  typical_wait_days: 2
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-detect session completion, query xparking API for receipt, and email PDF to user
    without agent involvement — only when session data is unambiguously matched and receipt is available from xparking.
  autonomous_resolve_safety_constraints:
  - Autonomous send only when xparking API returns a confirmed, validated receipt — never fabricate or estimate receipt data.
  - Must verify user identity and email address match the parking session record before sending.
  - Invoices with VAT or business billing must route to a human agent for review due to accounting compliance risk.
  - Any API failure or ambiguous session match must immediately escalate to a human agent.
  - Audit log of all autonomously sent receipts must be retained for at least 12 months.
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-incorrect-charge-refund
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- bmove-not-recognized-daily-worklog
- email-address-change-not-possible
- email-address-change-not-supported
- expired-card-deletion-ticketless-link
- hr-parking-ticket-fine-after-paid-app
- microsoft365-quarantine-notification-auto-tickets
- missing-parking-invoice-receipt
- missing-parking-receipt-request
- open-session-at-exit-austria
- outstanding-payment-credit-card-failure
- parking-payment-failure-end-user
- pkc-vehicle-registration-automated-tickets
- ticketless-open-session-at-exit__960f17
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Users not receiving parking receipts/invoices via email or in-app download

## What this pattern is

End users report that after completing a parking session via the Bmove app, they do not receive an automated receipt or invoice by email, and/or the receipt is not downloadable in the app. This affects both individual and business users, who often need the receipts for accounting or expense reimbursement purposes. The standard resolution is for support staff to manually send a replacement receipt (Ersatzquittung) to the user.

## When this applies

- Automated receipt email not sent after parking session completes
- Receipt not available for download in the Bmove app
- User needs receipt for business accounting or expense reimbursement
- Recurring failure over multiple sessions for the same user

## Typical resolution flow

1. User submits feedback via Bmove app reporting missing receipt(s)
2. Automated acknowledgement sent to user noting 1-2 business day response time
3. Support agent identifies affected parking session(s) using license plate or ticket number
4. Agent attempts to retrieve receipt from backend or escalates to xparking/third-party provider
5. Agent manually sends replacement receipt (Ersatzquittung) as email attachment
6. Ticket closed after receipt delivered

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Send automated acknowledgement to user | system/bot | Bmove support platform | 1 min |
| Look up parking session using license plate or ticket number | support agent | Bmove backend / xParking system | 10 min |
| Escalate to xparking to retrieve receipt data | support agent | internal escalation (e.g. @roland.soter / xParking) | 30 min |
| Send replacement receipt (Ersatzquittung) as PDF attachment via email | support agent | email / support platform | 5 min |

## Vendor dependency

- **Vendor:** xparking
- **Typical wait:** 2 day(s)

## Evidence

Derived from 32 tickets in cluster `BS:end_user|austria|invoice_issue:c0`. Direct quotes from 6 representative tickets:

- `BS-33525` _[de]_: "Ich bekomme leider seit gestern Dienstag, den 11.02.2025 keine Rechnungen mehr per Mail zugesandt. Bitte um Aktivierung und Zusendung der beiden Rechnungen, welche ich zur Abrechnung benötige."
- `BS-35015` _[de]_: "Ich erhalte keine Rechnungen per email mehr über abgeschlossene Parkvorgänge, obwohl diese Funktion in der App aktiviert ist."
- `BS-35015` _[en]_: "@@roland.soter check with xparking, the receipts cannot be pulled on our side."
- `BS-22671` _[de]_: "Ich benötige die Rechnung dringend für die Abrechnung mit meiner Firma. Da es sonst eine Abbuchung ohne gültiger Rechnung wäre, müsste ohne Zusendung einer Rechnung der Betrag auf mein Konto zurückgeb"
- `BS-22457` _[de]_: "ich habe heute in der Garage Neuer Markt geparkt und schon wieder keine Quittung per E-Mail bekommen. Ich bitte um Zusendung und rasche Behebung der bereits wiederholt auftretenden Fehlfunktion."
- `BS-34124` _[de]_: "Ich bekomme leider seit ca. 2 Wochen keine Belege mehr per Mail automatisch zugestellt."

## Cluster statistics

- **Volume:** 32 tickets total (30 unique semantic events after dedup)
- **Frequency:** 0.59 tickets/month (over data window 2023-11-03 → 2025-07-09)
- **Median resolution:** 17.7 hours
- **Cannot Reproduce rate:** 3.1%
- **Languages:** de
- **Country focus:** at, de

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~5.4 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.6 (range [1.134, 2.106])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.75
- **Rationale:** The resolution workflow is highly structured: session lookup, xparking escalation template, and PDF dispatch. Agent-assist tooling can pre-populate session lookup, generate the xparking escalation message, and draft the Ersatzquittung email, materially reducing the 30-minute escalation step. The 10-minute lookup and 5-minute send steps are also partially automatable.
- **Validation:** Run shadow-mode assist for 3 weeks on live tickets: measure agent acceptance rate of pre-drafted escalation messages and time-to-resolution versus baseline before enabling in production.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~5.4 (range [3.8, 5.4])
- **Root cause:** Receipt/invoice delivery (email and in-app download) is not triggered reliably after parking session completion, likely due to a missing or failing event handoff between the Bmove app and the xparking vendor system responsible for receipt generation and delivery.
- **Rationale:** A reliable fix requires diagnosing and repairing the integration between Bmove and xparking, including event triggers, retry logic, and delivery confirmation — medium-complexity vendor integration work. If fully resolved, the ticket cluster is eliminated and all 5.4 baseline hours are saved; the lower bound reflects residual edge-case tickets.
- **Validation:** Engineering team should instrument the session-completion → receipt-delivery pipeline end-to-end, run a staged rollout for 2 sprints, and verify receipt delivery rate exceeds 99% in staging and production before closing.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.5 (range [0.38, 0.7])
- **Form:** `in_app_help`
- **Deflection rate:** ~10% (range [7%, 13%])
- **Feasibility:** 0.35
- **Rationale:** Because receipt non-delivery is caused by a product/vendor bug rather than user confusion, self-service content cannot resolve the underlying issue; it may deflect only a small share of users who submit duplicate tickets while awaiting resolution. Deflection potential is therefore very limited.
- **Validation:** Deploy an in-app help article explaining the known delay and manual-receipt request process for 4 weeks; measure whether ticket volume from that cohort drops versus the prior period.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.5 (range [0.378, 0.7])
- **Narrow use case:** Auto-detect session completion, query xparking API for receipt, and email PDF to user without agent involvement — only when session data is unambiguously matched and receipt is available from xparking.
- **Safety constraints:**
  - Autonomous send only when xparking API returns a confirmed, validated receipt — never fabricate or estimate receipt data.
  - Must verify user identity and email address match the parking session record before sending.
  - Invoices with VAT or business billing must route to a human agent for review due to accounting compliance risk.
  - Any API failure or ambiguous session match must immediately escalate to a human agent.
  - Audit log of all autonomously sent receipts must be retained for at least 12 months.
- **Rationale:** Full autonomous resolution is constrained by the vendor dependency on xparking's API reliability and the compliance sensitivity of financial documents; only a small, clean subset of tickets (unambiguous session match, personal billing, API-confirmed receipt) is safe to automate. Volume is low, limiting absolute savings.
- **Validation:** Pilot on 10 manually selected tickets over 4 weeks with human review of every autonomous action; acceptance criterion is 100% receipt accuracy and zero user complaints before expanding to the 15% volume cap.

### Risks

- **Compliance concerns:**
  - Receipts and invoices are financial/tax documents; incorrect or duplicate Ersatzquittungen may create accounting or VAT compliance issues for business users.
  - GDPR: receipt PDFs contain personal data (name, payment details, license plate); transmission must be over encrypted channels to the verified account holder only.
  - Business invoices may require specific legal formatting (e.g., VAT ID, sequential invoice numbers) that automated generation must comply with.
- **Must not automate:**
  - Sending receipts to unverified or unmatched email addresses.
  - Generating or modifying receipt amounts or session data — only pass-through of vendor-confirmed data is permissible.
  - Handling disputes about session charges or billing amounts autonomously.
- **Vendor dependencies blocking automation:**
  - xparking must expose a reliable API endpoint for receipt data retrieval; current typical_wait_days of 2 days indicates manual escalation is the primary path, suggesting no such API is currently available or stable.
  - Any autonomous or agent-assist retrieval of receipt data is blocked until xparking provides a programmatic, authenticated API with confirmed uptime SLAs.
  - Product fix scope and timeline depend on xparking's willingness to invest in the integration and their own delivery reliability.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

