---
id: missing-parking-invoice-receipt
name: missing_parking_invoice_receipt
title: End users not receiving invoice/receipt after parking session
description: End users (primarily in Austria and Germany) did not receive an invoice or receipt (Rechnung/Quittung) by email
  after completing a parking session via Bmove. Users request the missing document manually by contacting support, often providing
  a ticket number, license plate, parking location, and/or date. The issue is recurring for some users and at specific garages,
  suggesting a systemic delivery or generation failure.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- de
country_focus:
- at
- de
status: active
cluster_id: BS:end_user|austria|invoice_issue:c1
project_key: BS
cluster_size: 102
cluster_size_dedup: 100
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.96
median_resolution_minutes: 1285.0
p95_resolution_minutes: 132003.99999999988
cannot_reproduce_rate: 0.0098
data_window_start: '2023-09-15'
data_window_end: '2025-09-29'
annual_hours_saved: 1.3
roi:
  baseline_active_hours: 4.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.9
  deflection_hours_range:
  - 0.6
  - 1.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.3
  agent_assist_hours_range:
  - 0.9
  - 1.7
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 3.9
  product_fix_hours_range:
  - 2.7
  - 4.3
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 1.1
  autonomous_resolve_hours_range:
  - 0.8
  - 1.4
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-36937
- BS-38859
- BS-33842
- BS-13350
- BS-16869
- BS-17466
- BS-23350
- BS-35563
- BS-36680
- BS-35925
- BS-21598
- BS-24649
- BS-33681
- BS-41023
- BS-35482
- BS-33480
- BS-35749
- BS-39312
canonical_examples:
- BS-23350
- BS-35925
- BS-21598
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: 2
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-resend replacement receipt when user provides ticket number or license plate +
    date and session record is unambiguously matched in the backend
  autonomous_resolve_safety_constraints:
  - Must not send financial documents to unverified email addresses; resend only to the email address registered on the original
    booking
  - Must require unambiguous session match (single record) before auto-generating; do not proceed on partial or multi-match
    lookups
  - Must log every automated resend for audit trail to comply with Austrian and German fiscal/VAT receipt regulations
  - Must escalate to human agent if session record shows payment dispute, chargeback, or anomaly flag
  - Must respect GDPR data minimisation — do not surface full session or payment details in automated reply beyond the attached
    document
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-incorrect-charge-refund
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__7950cd
- bmove-app-feedback-mixed-issues__d6cf0c
- bmove-app-operational-issues-austria
- bmove-not-recognized-daily-worklog
- croatia-parking-payment-failure__e3b934
- croatia-ticketless-open-session-at-exit__a7c97e
- croatia-ticketless-open-session-at-exit__f25b63
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- email-address-change-not-possible
- email-address-change-not-supported
- expired-card-deletion-ticketless-link
- microsoft365-quarantine-notification-auto-tickets
- missing-parking-receipt-email
- missing-parking-receipt-request
- open-session-at-exit-austria
- open-session-at-exit-payment-failure
- outstanding-payment-credit-card-failure
- pkc-vehicle-registration-automated-tickets
- ticketless-open-session-at-exit__960f17
- ticketless-open-session-at-exit__d8d1ba
- ticketless-open-session-at-exit__fd04ac
- ticketless-open-session-not-closed-at-exit
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# End users not receiving invoice/receipt after parking session

## What this pattern is

End users (primarily in Austria and Germany) did not receive an invoice or receipt (Rechnung/Quittung) by email after completing a parking session via Bmove. Users request the missing document manually by contacting support, often providing a ticket number, license plate, parking location, and/or date. The issue is recurring for some users and at specific garages, suggesting a systemic delivery or generation failure.

## When this applies

- User completes a parking session but does not receive an invoice/receipt via email
- Invoice/receipt is not available for download in the Bmove app
- User needs receipt for expense reporting or accounting purposes
- Recurring failure at specific garages (e.g., Atterseehaus Garage, Garage am Hof)
- Multiple sessions missing invoices for the same user

## Typical resolution flow

1. User parks and pays via Bmove app
2. Invoice/receipt is not delivered by email or not visible in app
3. User contacts Bmove support requesting the missing document
4. User provides identifying information (ticket number, license plate, date, garage name)
5. Support agent locates the parking session
6. Support agent manually generates and sends a replacement receipt (Ersatzquittung) as an attachment
7. Ticket is closed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Acknowledge receipt of request and set expectation of 1-2 business day response time | support_agent | automated_response | 1 min |
| Look up parking session using ticket number, license plate, date, or garage name provided by user | support_agent | internal_backoffice_system | 5 min |
| Generate and send replacement receipt (Ersatzquittung) as email attachment | support_agent | internal_backoffice_system | 5 min |

## Evidence

Derived from 102 tickets in cluster `BS:end_user|austria|invoice_issue:c1`. Direct quotes from 6 representative tickets:

- `BS-23350` _[de]_: "Leider habe ich keine Quittungen per Mail bekommen, würde diese aber dringend brauchen."
- `BS-35925` _[de]_: "Vielleicht könnten Sie das Problem bitte bei der Garage melden, denn seit Wochen wird in dieser Garage keine Rechnung mehr ausgestellt und man muss jede einzelne Rechnung manuell über Sie nachfordern."
- `BS-21598` _[de]_: "In Anhang finden Sie die Ersatzquittung für den Parkvorgang."
- `BS-33842` _[de]_: "Bitte vermerken Sie in ihrem System, dass bei jeder Buchung automatisch eine Quittung geschickt werden muss. Die Quittung muss eine Rechnungsnummer enthalten!"
- `BS-35749` _[de]_: "Leider ist schon wieder keine Rechnung ausgestellt wurden."
- `BS-39312` _[de]_: "sie ist auch nicht in der App ersichtlich, wie bei allen anderen Parkvorgängen."

## Cluster statistics

- **Volume:** 102 tickets total (100 unique semantic events after dedup)
- **Frequency:** 1.96 tickets/month (over data window 2023-09-15 → 2025-09-29)
- **Median resolution:** 21.4 hours
- **Cannot Reproduce rate:** 1.0%
- **Languages:** de
- **Country focus:** at, de

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~4.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.3 (range [0.903, 1.677])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.80
- **Rationale:** The resolution is highly templated — session lookup plus receipt generation — making it well-suited for an agent-assist tool that pre-fetches session data from ticket metadata and drafts the acknowledgement reply, reducing active time primarily on steps 1 and 2. The lookup step (5 min) is the largest reduction opportunity if the tool can surface session data automatically.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-populates session lookup results and a draft acknowledgement; compare measured handle time against the 11-min baseline to validate the 30% reduction estimate.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~2 (range [1.4, 2.6])
- **Hours eliminated per year:** ~3.9 (range [2.71, 4.3])
- **Root cause:** Systemic failure in invoice/receipt generation or email delivery after parking session completion, likely affecting specific garages or user accounts in Austria and Germany; may involve email delivery pipeline, invoice generation service, or garage-specific configuration gaps.
- **Rationale:** A confirmed product bug means a fix could eliminate up to 90% of tickets in this cluster; effort estimate is medium because root cause spans potential delivery pipeline and garage configuration issues requiring investigation before a targeted fix. Hours eliminated are capped at 90% of baseline (4.3 h) to account for residual edge cases.
- **Validation:** Engineering team should instrument the invoice generation and email dispatch pipeline for a 2-week observability sprint to confirm failure rate, affected garages, and whether the issue is in generation vs. delivery before committing sprint estimate.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.9 (range [0.602, 1.118])
- **Form:** `in_app_help`
- **Deflection rate:** ~20% (range [14%, 26%])
- **Feasibility:** 0.55
- **Rationale:** Users contacting support already lack the document, so a generic FAQ has limited deflection value; however, an in-app self-service receipt re-send button (if backend supports lookup) could resolve a meaningful share without agent involvement. Deflection potential is dampened because the root cause is a systemic delivery failure, not user confusion.
- **Validation:** Deploy a 4-week in-app 'resend receipt' flow for Austrian and German users; measure contact-rate change for this cluster vs. control period to validate the 20% deflection midpoint.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~1.1 (range [0.75, 1.391])
- **Narrow use case:** Auto-resend replacement receipt when user provides ticket number or license plate + date and session record is unambiguously matched in the backend
- **Safety constraints:**
  - Must not send financial documents to unverified email addresses; resend only to the email address registered on the original booking
  - Must require unambiguous session match (single record) before auto-generating; do not proceed on partial or multi-match lookups
  - Must log every automated resend for audit trail to comply with Austrian and German fiscal/VAT receipt regulations
  - Must escalate to human agent if session record shows payment dispute, chargeback, or anomaly flag
  - Must respect GDPR data minimisation — do not surface full session or payment details in automated reply beyond the attached document
- **Rationale:** For well-defined, unambiguous session matches the workflow is deterministic and low-risk, supporting limited autonomous handling; the 25% volume cap reflects uncertainty about match ambiguity rates and the fiscal-document sensitivity in DACH markets. Hours saved are calculated as 23.5 × 0.25 × 11 / 60 ≈ 1.07 h at midpoint.
- **Validation:** Pilot with 4-week supervised automation on tickets where ticket number is present and session lookup returns exactly one record; acceptance criteria: zero incorrect document deliveries, ≥95% customer acknowledgement of receipt, and audit log completeness verified by compliance review.

### Risks

- **Compliance concerns:**
  - Invoices and receipts in Austria and Germany are fiscal documents subject to UStG (VAT law) and GoBD; incorrect or duplicated documents could create tax compliance issues for end users
  - GDPR Article 5 data minimisation and purpose limitation apply to any automated processing of session and payment data
  - Automated re-delivery must ensure documents are sent only to the verified data subject, not inferred or user-supplied email addresses
- **Must not automate:**
  - Cases where session lookup is ambiguous or returns multiple records
  - Cases involving payment disputes, chargebacks, or anomaly flags on the session
  - Generation of amended or corrected invoices (Stornorechnung / Korrekturrechnung) — these require human review
  - Delivery to an email address different from the one on the original booking record

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

