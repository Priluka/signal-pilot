---
id: missing-parking-receipt-request
name: missing_parking_receipt_request
title: End users requesting missing parking receipts/invoices for completed parking sessions
description: End users (primarily from Austria and Germany) contact support because they did not receive a receipt or invoice
  by email after a completed parking session, or cannot download it from the app's purchase history. They typically need the
  document for accounting/bookkeeping purposes. Support resolves the issue by manually sending a replacement receipt (Ersatzquittung)
  as an email attachment, often also pointing users to the in-app purchase history as an alternative.
category: end_user/billing
ticket_class: end_user
issue_category: billing
resolution_pattern: manual_close
languages:
- de
country_focus:
- at
- de
status: active
cluster_id: BS:end_user|austria|no_label:c4
project_key: BS
cluster_size: 50
cluster_size_dedup: 48
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.94
median_resolution_minutes: 2420.5
p95_resolution_minutes: 16910.749999999996
cannot_reproduce_rate: 0.0
data_window_start: '2025-01-14'
data_window_end: '2026-05-01'
annual_hours_saved: 0.8
roi:
  baseline_active_hours: 2.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.8
  deflection_hours_range:
  - 0.6
  - 1.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.8
  agent_assist_hours_range:
  - 0.6
  - 1.0
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.1
  product_fix_hours_range:
  - 1.5
  - 2.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.3
  - 0.6
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-32177
- BS-49246
- BS-49958
- BS-35036
- BS-35660
- BS-39504
- BS-44300
- BS-47859
- BS-52896
- BS-49347
- BS-46570
- BS-35189
- BS-44211
- BS-49198
- BS-46293
- BS-49830
- BS-44655
- BS-50530
canonical_examples:
- BS-44300
- BS-35036
- BS-35189
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
  autonomous_resolve_narrow_use_case: Authenticated users requesting a re-send of a receipt for a single, unambiguous completed
    session identifiable by account email, where no billing dispute is present.
  autonomous_resolve_safety_constraints:
  - User must be authenticated and account email must match the parking session record before any document is sent.
  - Session must be in a fully completed, non-disputed state — no open refund or complaint flags.
  - Document must be system-generated (not manually edited) and comply with Austrian/German tax receipt requirements (UStG
    / BAO).
  - A human agent review queue must catch any case where session lookup returns ambiguous or multiple matches.
  - Audit log of every autonomously sent receipt must be retained for regulatory compliance.
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-incorrect-charge-refund
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-missing-parking-receipt-request
- bmove-not-recognized-daily-worklog
- croatian-parking-debt-payment-failure
- email-address-change-not-possible
- email-address-change-not-supported
- expired-card-deletion-ticketless-link
- hr-b2b-partner-billing-payment-storno
- manual-debt-cancellation-request
- microsoft365-quarantine-notification-auto-tickets
- missing-parking-invoice-receipt
- missing-parking-receipt-email
- open-session-at-exit-austria
- outstanding-payment-credit-card-failure
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

# End users requesting missing parking receipts/invoices for completed parking sessions

## What this pattern is

End users (primarily from Austria and Germany) contact support because they did not receive a receipt or invoice by email after a completed parking session, or cannot download it from the app's purchase history. They typically need the document for accounting/bookkeeping purposes. Support resolves the issue by manually sending a replacement receipt (Ersatzquittung) as an email attachment, often also pointing users to the in-app purchase history as an alternative.

## When this applies

- User did not receive automated receipt/invoice email after parking session
- User cannot download receipt from app purchase history (Kaufhistorie)
- User needs receipt for business accounting/bookkeeping (Buchhaltung)
- Credit card charge appears without associated receipt
- Multiple parking sessions missing receipts at once

## Typical resolution flow

1. User contacts support via ticket providing parking session details (ticket number, date, license plate, account email)
2. Support acknowledges receipt of inquiry
3. Support agent looks up the parking session in the backend system
4. Support agent generates a replacement receipt (Ersatzquittung)
5. Support sends replacement receipt as PDF attachment in reply email
6. Optionally, support advises user on how to access receipts via app (Hauptmenü → Kaufhistorie)

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Acknowledge ticket receipt and set expectations for response time | support agent (automated or manual) | ticketing system | 2 min |
| Look up parking session by ticket number, date, license plate, or account email | support agent | backend/admin system | 5 min |
| Generate and send replacement receipt (Ersatzquittung) as PDF email attachment | support agent | backend/admin system, email | 5 min |
| Advise user on self-service receipt download via app purchase history | support agent | email / ticket comment | 2 min |

## Evidence

Derived from 50 tickets in cluster `BS:end_user|austria|no_label:c4`. Direct quotes from 6 representative tickets:

- `BS-44300` _[de]_: "Für diese Parkvorgänge habe ich leider nicht wie gewohnt einen Beleg per Mail erhalten. In der App ist der Beleg jeweils ebenfalls nicht ersichtlich."
- `BS-35036` _[de]_: "Im Anhang finden Sie die Ersatzquittung für den Parkvorgang. Alternativ können Sie sich die Quittungen auch in der App im Hauptmenü unter Kaufhistorie und Auswahl des Parkvorgangs herunterladen"
- `BS-35189` _[de]_: "leider wurde bei meinen letzten 2 Garagennutzungen keine Rechnungen ausgestellt, ich benötige diese jedoch für die Buchhaltung."
- `BS-50530` _[de]_: "Ich habe keine email bekommen und kann den Beleg nicht runterladen. Bitte was ist zu tun ? Ich brauche die Quittung für meine Firma"
- `BS-35660` _[de]_: "In der App kann ich die Transaktion zwar ansehen, aber kein Email zuschicken lassen; ich benötige es aber für die Buchhaltung"
- `BS-32177` _[de]_: "Auf meiner Kreditkarte findet sich eine Abbuchung von EUR 15,60 für einen Umsatz vom 23.11.2024. Der zugehörige Beleg fehlt mir. Bitte um Zusendung."

## Cluster statistics

- **Volume:** 50 tickets total (48 unique semantic events after dedup)
- **Frequency:** 0.94 tickets/month (over data window 2025-01-14 → 2026-05-01)
- **Median resolution:** 1.7 days
- **Languages:** de
- **Country focus:** at, de

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.8 (range [0.55, 1.01])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.85
- **Rationale:** The resolution pattern is highly templated — lookup session, generate PDF, send — making it well-suited for an agent-assist tool that pre-populates the session lookup, auto-generates the Ersatzquittung PDF, and drafts the reply email, reducing active work on steps 2–4. Time savings are moderate rather than large because the ticket volume is low and active time per ticket is already short.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-fills session data and drafts the reply for every receipt ticket; measure average handle time before and after, and track draft acceptance rate to validate the 85% quality target.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~2 (range [1.4, 2.6])
- **Hours eliminated per year:** ~2.1 (range [1.5, 2.6])
- **Root cause:** Post-session receipt emails are not reliably delivered (possible delivery failures, missing email addresses, or email filtering), and the in-app purchase history may not surface all completed sessions, preventing self-service download.
- **Rationale:** Fixing email delivery reliability and ensuring all completed sessions appear in purchase history would eliminate the majority of tickets in this cluster, since most users only contact support when both self-service paths have failed. The upper bound is capped at the 2.6 h baseline.
- **Validation:** Engineering should audit email send/delivery logs for a 90-day sample of completed sessions (AT/DE) to measure actual delivery failure rate, and cross-check purchase history completeness; this scopes the fix and validates effort before sprint planning.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.8 (range [0.55, 1.01])
- **Form:** `in_app_help`
- **Deflection rate:** ~30% (range [21%, 39%])
- **Feasibility:** 0.75
- **Rationale:** Many users are unaware of the in-app purchase history download feature; a prominently placed in-app help tip or FAQ entry triggered at session completion could deflect a meaningful share of tickets before they are submitted. However, users who genuinely did not receive an email and cannot find the session in-app still require manual intervention, limiting deflection potential.
- **Validation:** Deploy a 4-week in-app help banner on the purchase history screen (AT/DE locales) and a help-center FAQ entry; measure the ratio of receipt-related tickets opened per parking session before and after deployment.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~0.5 (range [0.343, 0.637])
- **Narrow use case:** Authenticated users requesting a re-send of a receipt for a single, unambiguous completed session identifiable by account email, where no billing dispute is present.
- **Safety constraints:**
  - User must be authenticated and account email must match the parking session record before any document is sent.
  - Session must be in a fully completed, non-disputed state — no open refund or complaint flags.
  - Document must be system-generated (not manually edited) and comply with Austrian/German tax receipt requirements (UStG / BAO).
  - A human agent review queue must catch any case where session lookup returns ambiguous or multiple matches.
  - Audit log of every autonomously sent receipt must be retained for regulatory compliance.
- **Rationale:** Autonomous re-send is technically feasible for clear-cut cases where the session is unambiguous and the user is authenticated, but the low annual volume (11.3 tickets) and legal sensitivity of tax documents under AT/DE law make the absolute hour savings small and the compliance overhead non-trivial. Capping at 25% of volume reflects both the safety cap and the reality that many tickets involve lookup ambiguity.
- **Validation:** Pilot with a 6-week canary deployment handling only authenticated, single-session, no-dispute requests; acceptance criteria: zero incorrect documents sent, ≥90% user satisfaction on post-resolution survey, and confirmation by finance/legal that generated PDFs meet UStG §14 and BAO §132 requirements.

### Risks

- **Compliance concerns:**
  - Replacement receipts (Ersatzquittungen) must comply with Austrian BAO §132 and German UStG §14 invoice requirements, including mandatory fields (VAT ID, date, amount, tax breakdown); automated generation must be validated by finance/legal.
  - Any automated handling of personal data (email addresses, license plates, transaction records) must comply with GDPR (EU 2016/679), including data minimisation and logging obligations.
  - Audit trails for all sent receipts — automated or manual — may be required under AT/DE tax retention rules (7-year retention).
- **Must not automate:**
  - Cases where the session record is ambiguous, disputed, or involves a potential overcharge — these require human judgment.
  - Cases where the user's identity or account ownership cannot be verified — sending a receipt to an unverified email risks a personal data breach.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

