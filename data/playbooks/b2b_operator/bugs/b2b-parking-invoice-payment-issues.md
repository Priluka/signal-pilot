---
id: b2b-parking-invoice-payment-issues
name: b2b_parking_invoice_payment_issues
title: B2B Partners Unable to Obtain Invoices or Complete Parking Payments via Bmove App
description: 'Business users of the Bmove parking app repeatedly encounter two main problems: inability to download or receive
  payment confirmation documents (invoices/receipts) needed for employer expense reporting or VAT purposes, and payment failures
  where card transactions fail silently, require repeated 3D Secure authorization, or are not processed at all. These issues
  disproportionately affect B2B partners using Bmove for company vehicles or business travel, who require formal documentation
  and reliable payment flows.'
category: b2b_operator/bugs
ticket_class: b2b_partner
issue_category: bug_in_product
resolution_pattern: user_education
languages:
- other
- de
- en
country_focus:
- other
- at
status: active
cluster_id: BS:b2b_partner|no_value|no_label:c5
project_key: BS
cluster_size: 21
cluster_size_dedup: 20
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.85
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.39
median_resolution_minutes: 7234.0
p95_resolution_minutes: 223140.0
cannot_reproduce_rate: 0.0
data_window_start: '2022-03-30'
data_window_end: '2026-01-21'
annual_hours_saved: 1.4
roi:
  baseline_active_hours: 5.5
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 1.6
  deflection_hours_range:
  - 1.2
  - 2.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.4
  agent_assist_hours_range:
  - 1.0
  - 1.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 3.3
  product_fix_hours_range:
  - 2.3
  - 4.3
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.3
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-28372
- BS-1070
- BS-10968
- BS-317
- BS-355
- BS-2400
- BS-2665
- BS-4267
- BS-32494
- BS-19778
- BS-11862
- BS-48256
- BS-43914
- BS-5074
- BS-2543
- BS-5753
- BS-17600
- BS-19659
canonical_examples:
- BS-28372
- BS-19659
- BS-1070
vendor_dependency:
  vendor_name: PAAS (Bratislavský parkovací asistent) / issuing banks
  involves_vendor: true
  typical_wait_days: 7
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: User education — safe for self-service deflection
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-send PDF receipt/invoice to verified registered user email upon pattern-matched
    ticket submission, without human review
  autonomous_resolve_safety_constraints:
  - Only trigger for verified registered accounts with confirmed email address on file
  - Never autonomously cancel or dispute a parking fine; always escalate to human agent
  - Do not attempt automated card or payment investigation; flag for agent
  - Limit to invoice/receipt dispatch action only — no payment-side actions
  - Require audit log of every autonomous action for compliance and VAT documentation purposes
related_playbooks:
- b2b-partner-parking-card-storno-refund
- b2b-ticketless-open-session-and-permit-conflict
- bmove-app-general-feedback-and-issues
- hr-b2b-partner-billing-payment-storno
- hr-b2b-sms-parking-payment-failure
- italy-bmove-payment-method-issues
- skidata-hosted-services-maintenance-notification
- zagreb-parking-cancelled-ticket-refund
- zagrebparking-b2b-storno-refund-request
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

# B2B Partners Unable to Obtain Invoices or Complete Parking Payments via Bmove App

## What this pattern is

Business users of the Bmove parking app repeatedly encounter two main problems: inability to download or receive payment confirmation documents (invoices/receipts) needed for employer expense reporting or VAT purposes, and payment failures where card transactions fail silently, require repeated 3D Secure authorization, or are not processed at all. These issues disproportionately affect B2B partners using Bmove for company vehicles or business travel, who require formal documentation and reliable payment flows.

## When this applies

- User attempts to download invoice/receipt from app Purchase History but download fails or button is non-functional
- User is a guest (unregistered) and did not receive invoice automatically after purchase
- User needs formal tax/VAT document but only receives a parking confirmation email
- Company card requires 3D Secure authorization on every transaction, blocking drivers without bank access
- Payment card stored in app is outdated/blocked causing silent payment failure
- App fails to process payment at garage exit, requiring manual card payment at barrier
- User reinstalls app and old card is not properly replaced

## Typical resolution flow

1. User contacts support explaining they cannot download invoice or payment failed
2. Support asks for licence plate number and/or specific transaction date
3. Support checks user registration status (guest vs registered account)
4. Support directs user to Purchase History in app (Menu > Purchase History) or web app at app.bmove.com
5. Support checks app storage/permission settings if download still fails
6. For payment failures, support investigates whether issue is app bug, bank 3DS policy, or expired card
7. If invoice is missing, support manually sends PDF receipt or escalates to technical team
8. For penalty/fine resulting from payment failure, support contacts city authority (PAAS) on user's behalf

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Redirect user to Purchase History section in app or web app for invoice download | support_agent | Bmove app / app.Bmove.com | 5 min |
| Manually send PDF receipt/invoice to user via email | support_agent | email / Jira Service Desk | 10 min |
| Verify user registration status and explain that registered users receive invoices automatically by email | support_agent | Bmove backend | 5 min |
| Investigate payment failure by checking licence plate and stored card validity | support_agent | Bmove backend | 15 min |
| Contact PAAS or garage operator on behalf of user to cancel fine issued due to app payment failure | support_agent | email / phone to PAAS | 30 min |
| Advise user to update app to latest version to resolve payment/tokenization issues | support_agent | — | 5 min |

## Vendor dependency

- **Vendor:** PAAS (Bratislavský parkovací asistent) / issuing banks
- **Typical wait:** 7 day(s)

## Evidence

Derived from 21 tickets in cluster `BS:b2b_partner|no_value|no_label:c5`. Direct quotes from 7 representative tickets:

- `BS-28372` _[other]_: "Chcela som si stiahnuť potvrdenie o zaplatení parkovania a v aplikácií Bmove to nefunguje. Potvrdenia potrebujem dokladovať zamestnávateľovi keďže ide o služobné vozidlo"
- `BS-19659` _[other]_: "V histórii platieb sa nedá stiahnuť potvrdenie. Je nevyhnutné ho priložiť k vyúčtovaniu ako daňový doklad."
- `BS-1070` _[other]_: "mám 2 šoférov ktorí jazdia do BA za zákazníkmi... pri kúpe lístka chce odo mňa za každým potvrdenie autorizácie v internet bankingu banky a takto sa nám fungovať nedá"
- `BS-4267` _[de]_: "Ist das eine Rechnung? Es hat kein USt. Ausgewiesen. Wie bekomme ich eine Rechnung?"
- `BS-48256` _[other]_: "Rampa sa otvorila, vozidlo bolo zaregistrované, ale pri odchode nebola platba cez aplikáciu zrealizovaná. Šofér vozidla musel použiť na úhradu platobnú kartu."
- `BS-32494` _[other]_: "15.1.2025 prišilo k čiastočnému výpadu komunikácie zo strany mesta. Nemáme ešte oficiálne stanovisko od nich, ale určite nechceme aby ste znášal následky vy."
- `BS-43914` _[other]_: "prosím o zaslanie mesačného výpisu platieb za mesiac september. V aplikácii mi chýba parkovanie 04.09.2025 v garáži Centrum v Bratislave"

## Cluster statistics

- **Volume:** 21 tickets total (20 unique semantic events after dedup)
- **Frequency:** 0.39 tickets/month (over data window 2022-03-30 → 2026-01-21)
- **Median resolution:** 5.0 days
- **Languages:** other, de, en
- **Country focus:** other, at

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~5.5 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.4 (range [1, 1.8])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** The resolution steps are procedural and well-documented, making them good candidates for suggested-action macros and pre-filled email templates (e.g. PDF receipt dispatch, app-update advisory). Time savings are limited by the investigative steps (licence plate/card checks, PAAS coordination) that still require human judgment.
- **Validation:** Deploy suggested-action macros in shadow mode for 2 weeks; measure agent acceptance rate and average handle-time delta against a control group on the same ticket pattern.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~3.3 (range [2.31, 4.29])
- **Root cause:** Two distinct bugs: (1) invoices/receipts are not consistently delivered to registered users or surfaced in-app, requiring manual agent dispatch; (2) payment tokenization failures and silent 3DS rejections are not surfaced with actionable error messages, causing repeated failures and downstream parking fines.
- **Rationale:** Reliable automated invoice delivery and meaningful payment-error messaging would eliminate actions 1–3 and reduce action 4–6 significantly, but the 3DS flow depends partly on issuing-bank behaviour, so full elimination of payment-failure tickets is unlikely without vendor coordination. Estimated elimination covers ~60% of baseline hours.
- **Validation:** Engineering team should instrument invoice-delivery success rate and payment-error surfacing in staging; run a two-sprint spike to size the invoice pipeline fix separately from the 3DS error-handling work before committing to full scope.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1.6 (range [1.2, 2.08])
- **Form:** `help_center`
- **Deflection rate:** ~30% (range [21%, 39%])
- **Feasibility:** 0.65
- **Rationale:** Invoice retrieval via Purchase History and app-update guidance are well-suited to a step-by-step help center article, but payment failures involving 3DS or silent card errors require investigation that self-service cannot fully address. Deflection ceiling is modest because a meaningful share of tickets involve bugs rather than user confusion.
- **Validation:** Publish a targeted help center article covering invoice download steps and payment troubleshooting; track article views vs. ticket submissions on this pattern over a 4-week window to measure contact-rate reduction.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.5 (range [0.35, 0.65])
- **Narrow use case:** Auto-send PDF receipt/invoice to verified registered user email upon pattern-matched ticket submission, without human review
- **Safety constraints:**
  - Only trigger for verified registered accounts with confirmed email address on file
  - Never autonomously cancel or dispute a parking fine; always escalate to human agent
  - Do not attempt automated card or payment investigation; flag for agent
  - Limit to invoice/receipt dispatch action only — no payment-side actions
  - Require audit log of every autonomous action for compliance and VAT documentation purposes
- **Rationale:** Autonomous resolution is narrowly viable only for the invoice-resend sub-case where the user is already registered and the document exists in the system; payment failures and fine disputes involve financial and legal risk that requires human oversight. Expected volume eligible for this narrow case is low, yielding modest savings.
- **Validation:** Pilot over 6 weeks on a sample of inbound tickets classified as invoice-only requests; acceptance criteria: zero false-positive sends to unverified emails, >90% user confirmation that correct document was received, no escalations triggered by the autonomous action.

### Risks

- **Compliance concerns:**
  - VAT invoices are legally binding documents in most EU jurisdictions; incorrect or duplicate automated dispatch could create accounting errors for B2B customers
  - GDPR requires that email addresses used for automated document dispatch are verified and consented — no sending to unverified or third-party addresses
  - Audit trails for all automated invoice actions must be retained to satisfy tax authority requests
- **Must not automate:**
  - Cancellation or dispute of parking fines on behalf of users — requires human judgment and vendor coordination
  - Any investigation or modification of stored payment card data or tokenization records
  - Communication with PAAS or garage operators — involves contractual and liability considerations
  - Refund initiation or payment reversal actions
- **Vendor dependencies blocking automation:**
  - 3DS payment failure resolution depends on issuing bank behaviour and PAAS gateway configuration; Bmove engineering cannot unilaterally fix silent failure modes without vendor cooperation (typical wait: 7 days)
  - Fine cancellation workflows require PAAS or garage operator action; autonomous handling is blocked until a formal API or SLA agreement exists with the vendor

## Agent compatibility

- **Status:** `active` (extraction confidence 0.85)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

