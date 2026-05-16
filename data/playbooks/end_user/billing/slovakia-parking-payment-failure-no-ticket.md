---
id: slovakia-parking-payment-failure-no-ticket
name: slovakia_parking_payment_failure_no_ticket
title: Slovak end-users report payment deducted but no parking ticket issued in Bmove app
description: End users in Slovakia (predominantly Bratislava PAAS zone) attempt to purchase a parking ticket via the Bmove
  app, money is charged or reserved from their bank account, but no active ticket appears in the app. This often results in
  parking fines, duplicate payments, or refund requests. The root cause is typically that users do not return to the app after
  bank payment confirmation, or a backend ticket-confirmation failure with the third-party PAAS system.
category: end_user/billing
ticket_class: end_user
issue_category: billing
resolution_pattern: user_education
languages:
- other
country_focus:
- other
status: active
cluster_id: BS:end_user|no_value|payment:c0
project_key: BS
cluster_size: 60
cluster_size_dedup: 56
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.88
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.1
median_resolution_minutes: 4195.0
p95_resolution_minutes: 301498.7999999997
cannot_reproduce_rate: 0.0167
data_window_start: '2023-02-10'
data_window_end: '2024-12-18'
annual_hours_saved: 2.8
roi:
  baseline_active_hours: 11.0
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 1.6
  deflection_hours_range:
  - 1.2
  - 2.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 2.8
  agent_assist_hours_range:
  - 1.9
  - 3.6
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 6.0
  product_fix_hours_range:
  - 4.2
  - 7.9
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.9
  autonomous_resolve_hours_range:
  - 0.6
  - 1.1
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-13451
- BS-27563
- BS-7544
- BS-5905
- BS-8655
- BS-13794
- BS-16520
- BS-20058
- BS-27266
- BS-27588
- BS-18843
- BS-11522
- BS-12200
- BS-15717
- BS-22282
- BS-14538
- BS-11755
- BS-23562
canonical_examples:
- BS-15717
- BS-5905
- BS-18843
vendor_dependency:
  vendor_name: PAAS / xParking / Datatrans
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
  autonomous_resolve_narrow_use_case: Auto-send standardised 'return-to-app to finalise' education message when transaction
    shows reserved-not-captured status in Datatrans within 30 minutes of contact
  autonomous_resolve_safety_constraints:
  - Must not autonomously initiate or confirm refunds; all financial actions require human approval
  - Must not act on cases where Datatrans shows payment captured but no ticket exists — these require engineer investigation
  - Must not send auto-responses when vendor wait dependency is already open (Datatrans/xParking escalation in progress)
  - Must include clear human escalation path in any automated message
  - Must log all automated actions for audit and compliance review
related_playbooks:
- app-payment-failure-parking-ticket
- b2b-ticketless-outstanding-payment-failure
- bmove-app-feedback-mixed-issues__7950cd
- hr-open-session-after-garage-exit
- hr-parking-ticket-fine-after-paid-app
- italian-b2b-invoice-billing-question
- outstanding-payment-credit-card-failure
- parking-fine-received-despite-valid-payment
- parking-payment-failure-end-user
- prepaid-top-up-and-usage-issues
- ticketless-open-session-at-exit__d8d1ba
- ticketless-open-session-at-exit__fd04ac
- wrong-parking-ticket-purchase-redirect
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Slovak end-users report payment deducted but no parking ticket issued in Bmove app

## What this pattern is

End users in Slovakia (predominantly Bratislava PAAS zone) attempt to purchase a parking ticket via the Bmove app, money is charged or reserved from their bank account, but no active ticket appears in the app. This often results in parking fines, duplicate payments, or refund requests. The root cause is typically that users do not return to the app after bank payment confirmation, or a backend ticket-confirmation failure with the third-party PAAS system.

## When this applies

- User initiates parking ticket purchase via Bmove app and pays via card or Apple Pay
- Payment is authorized/reserved by the bank but user does not return to the app to confirm
- Third-party ticket confirmation with PAAS/xParking fails at the backend
- User purchases duplicate ticket after first appears to fail
- User requests refund or cancellation of an already-issued or overpaid ticket

## Typical resolution flow

1. User pays for parking via Bmove app (card/Apple Pay)
2. Payment is deducted or reserved from bank account
3. No active ticket appears in the app
4. User may buy a second ticket or receive a parking fine
5. User contacts support requesting explanation, refund, or ticket confirmation
6. Support checks Datatrans/xParking transaction logs
7. Support explains that user must return to app after bank confirmation for ticket to be issued
8. If payment was only reserved (not captured), support advises it will auto-return within 3-7 days
9. If double-charged, support escalates to technical team for refund processing
10. If third-party confirm failed, support captures and refunds the bad transaction

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Check payment transaction status in Datatrans and xParking logs | support_engineer | Datatrans / xParking backend | 15 min |
| Explain to user that they must return to the Bmove app after bank confirmation to finalize ticket purchase | support_agent | email/Jira | 5 min |
| Advise user that reserved (uncaptured) payment will auto-return within 3-7 days | support_agent | email/Jira | 5 min |
| Capture and refund bad transaction where third-party ticket confirmation failed | support_engineer | Datatrans / xParking backend | 20 min |
| Inform user that issued tickets cannot be cancelled, refunded, or modified per PAAS policy | support_agent | email/Jira | 5 min |

## Vendor dependency

- **Vendor:** PAAS / xParking / Datatrans
- **Typical wait:** 7 day(s)

## Evidence

Derived from 60 tickets in cluster `BS:end_user|no_value|payment:c0`. Direct quotes from 7 representative tickets:

- `BS-15717` _[other]_: "peniaze mi strhlo, ale v aplikacii mi neukazalo, ze mam parkovne uhradene"
- `BS-5905` _[en]_: "ticket confirm in third party didn't work at this moment. We captured that bad transaction and refund money because there was no ticket for this purchase."
- `BS-18843` _[other]_: "Po uskutočnení (potvrdení) platby v banke sa musíte vrátiť do aplikácie Bmove, aby sa potvrdila platba. Len vtedy sa považuje lístok za oficiálne zakúpený."
- `BS-11755` _[other]_: "V tomto prípade úhrada za lístok bola len rezervovaná a v priebehu 3-7 dní systém automaticky pošle platbu spať na Váš účet."
- `BS-20058` _[other]_: "dnes ste mi strhli z účtu 1€ o chvíľu ste mi ho poslali späť a o ďalších pár minút ste mi ho opäť strhli. Prečo?"
- `BS-15717` _[other]_: "Musel som to zaplatit druhy krat za 6€.. to mi uz v apke ukazalo.."
- `BS-11522` _[other]_: "2krat mi strhli s účtu platbu Prvý krát strhol 6,46 a vypísalo že stala sa chyba peniaze mi bohužiaľ doteraz neprišli"

## Cluster statistics

- **Volume:** 60 tickets total (56 unique semantic events after dedup)
- **Frequency:** 1.1 tickets/month (over data window 2023-02-10 → 2024-12-18)
- **Median resolution:** 2.9 days
- **Cannot Reproduce rate:** 1.7%
- **Languages:** other
- **Country focus:** other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~11 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~2.8 (range [1.93, 3.57])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.80
- **Rationale:** A large share of resolution steps are templated (payment status lookup procedure, standard user explanation scripts, refund policy statement); an assist tool surfacing pre-filled Datatrans/xParking lookup links and approved response drafts could meaningfully cut active minutes, especially for support agents on steps 2, 3, and 5.
- **Validation:** Run shadow-mode assist (drafts shown but not sent) for 3 weeks across all billing tickets in this cluster; measure agent edit rate and time-on-ticket before agents adopt drafts live. Accept if ≥70% of drafts require only minor edits.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~6 (range [4.24, 7.865])
- **Root cause:** Two distinct failure modes: (1) app UX does not auto-finalize ticket purchase upon return from bank payment confirmation, requiring an explicit user action that is easily missed; (2) intermittent backend failures in the PAAS/xParking/Datatrans confirmation flow leave payments captured without ticket issuance.
- **Rationale:** Auto-finalizing the ticket on app resume (deep-link callback handling) would eliminate the user-education class of tickets (~55% of volume); a robust backend retry/reconciliation mechanism with PAAS would address confirmation failures. Full elimination is constrained by vendor API reliability outside engineering control.
- **Validation:** Engineering team should spike on the Datatrans/xParking webhook or polling callback architecture to size backend retry effort; instrument the app resume flow in a staging build to confirm auto-finalization works across iOS and Android before estimating sprint count precisely.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1.6 (range [1.16, 2.145])
- **Form:** `in_app_help`
- **Deflection rate:** ~30% (range [21%, 39%])
- **Feasibility:** 0.72
- **Rationale:** The dominant root cause — users not returning to the app after bank confirmation — is a specific, teachable step well-suited to an in-app nudge or contextual help article shown post-bank-redirect. However, cases involving backend ticket-confirmation failure still require agent investigation, limiting deflection ceiling.
- **Validation:** Deploy an in-app contextual help screen triggered immediately after bank payment redirect for 8 weeks; measure ratio of users who finalize ticket vs. open a support ticket before and after. Target ≥25% reduction in new ticket volume from this cohort.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.9 (range [0.62, 1.144])
- **Narrow use case:** Auto-send standardised 'return-to-app to finalise' education message when transaction shows reserved-not-captured status in Datatrans within 30 minutes of contact
- **Safety constraints:**
  - Must not autonomously initiate or confirm refunds; all financial actions require human approval
  - Must not act on cases where Datatrans shows payment captured but no ticket exists — these require engineer investigation
  - Must not send auto-responses when vendor wait dependency is already open (Datatrans/xParking escalation in progress)
  - Must include clear human escalation path in any automated message
  - Must log all automated actions for audit and compliance review
- **Rationale:** Fully autonomous resolution is severely constrained by the billing/payment nature of tickets, vendor dependency on PAAS/Datatrans, and the need for engineer-level log access in failure cases; only the narrow user-education sub-case (reserved payment, user did not return) is safe to automate at low volume.
- **Validation:** Pilot automated user-education message for 6 weeks on tickets where Datatrans API confirms reserved-not-captured status within 30 min of ticket creation; accept if ≥85% of piloted tickets need no further agent contact and zero complaints about incorrect automated guidance.

### Risks

- **Compliance concerns:**
  - Payment data (transaction IDs, amounts, bank reservation status) is PII/financial data subject to GDPR and Slovak data-protection law; any automated access or logging must be scoped and documented
  - Refund and capture operations on payment instruments must comply with PSD2 and Datatrans contractual terms; autonomous financial actions are prohibited without explicit user consent flows
  - Parking fine liability: if an automated message incorrectly assures a user their ticket is valid and they receive a fine, there is potential legal and reputational exposure
- **Must not automate:**
  - Refund initiation or capture of any payment transaction
  - Cancellation or modification of issued parking tickets (explicitly prohibited by PAAS policy)
  - Any response to cases where backend ticket-confirmation failure is suspected — these require engineer log review
  - Communication to users about fine disputes or liability
- **Vendor dependencies blocking automation:**
  - PAAS / xParking API reliability and webhook/callback support is required for both product fix and autonomous triage; typical vendor response SLA of 7 days limits how quickly automation can be validated
  - Datatrans log access for automated status checks requires confirmed API credentials and rate-limit agreements with vendor
  - Any reconciliation automation between Datatrans payment state and xParking ticket state depends on vendor-provided APIs that may not currently expose sufficient status detail

## Agent compatibility

- **Status:** `active` (extraction confidence 0.88)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

