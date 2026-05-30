---
id: croatian-parking-debt-payment-failure
name: croatian_parking_debt_payment_failure
title: Croatian end-users disputing or unable to pay outstanding parking debts in Bmove app
description: End users in Croatia receive notifications about outstanding parking debts, often believing they have already
  paid or that the debt was created in error. The root causes include cancelled/reversed payment transactions that automatically
  open a debt, system errors creating erroneous debts, and card payment failures when trying to settle the outstanding amount
  through the app. Users are frequently confused because their bank shows a charge while Bmove shows an unpaid debt, or they
  receive notifications about debts they cannot see or pay in the app.
category: end_user/billing
ticket_class: end_user
issue_category: billing
resolution_pattern: manual_close
languages:
- hr
- en
country_focus:
- hr
status: active
cluster_id: BS:end_user|croatia|debt:c1
project_key: BS
cluster_size: 91
cluster_size_dedup: 91
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.91
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.78
median_resolution_minutes: 1700.0
p95_resolution_minutes: 19542.599999999988
cannot_reproduce_rate: 0.0
data_window_start: '2023-02-02'
data_window_end: '2026-01-23'
annual_hours_saved: 3.4
roi:
  baseline_active_hours: 13.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 2.0
  deflection_hours_range:
  - 1.4
  - 2.6
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 3.4
  agent_assist_hours_range:
  - 2.4
  - 4.4
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 8.2
  product_fix_hours_range:
  - 5.7
  - 10.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.3
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-22948
- BS-45510
- BS-40073
- BS-5578
- BS-7780
- BS-19882
- BS-22985
- BS-42146
- BS-47729
- BS-41828
- BS-17442
- BS-42657
- BS-42486
- BS-43143
- BS-41824
- BS-34802
- BS-42117
- BS-42093
canonical_examples:
- BS-22948
- BS-45510
- BS-22948
vendor_dependency:
  vendor_name: Payment processing / garage ticketless service (unnamed)
  involves_vendor: true
  typical_wait_days: 3
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-send prepaid top-up instructions when debt status is payable but card payment has
    failed and no bank-statement dispute is indicated
  autonomous_resolve_safety_constraints:
  - Must never autonomously delete or cancel a debt record without human review
  - Must not send transaction-status confirmations without cross-checking payment gateway records
  - Must not act on cases where user has submitted bank statements showing a charge (potential double-charge risk)
  - Vendor dependency on payment processor means autonomous decisions on fund status carry financial liability
  - Must escalate immediately if debt is not visible in app UI (system-error indicator)
related_playbooks:
- b2b-missing-parking-receipt-request
- croatia-bmove-app-feedback-miscellaneous
- croatia-parking-fine-dispute
- croatia-parking-fine-dispute-and-payment
- croatia-parking-fine-payment-failure
- croatia-parking-payment-failure__ffdf4e
- croatia-parking-ticket-storno-user-error
- croatia-ticketless-best-in-parking-knowledge-gap
- croatia-ticketless-open-session-at-exit__f25b63
- croatia-ticketless-rental-car-ghost-charge
- croatian-end-user-wrong-registration-storno-refund
- croatian-invoice-download-request
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__56d2b2
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- hr-b2b-partner-billing-payment-storno
- manual-debt-cancellation-request
- missing-parking-receipt-request
- open-session-at-exit-payment-failure
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

# Croatian end-users disputing or unable to pay outstanding parking debts in Bmove app

## What this pattern is

End users in Croatia receive notifications about outstanding parking debts, often believing they have already paid or that the debt was created in error. The root causes include cancelled/reversed payment transactions that automatically open a debt, system errors creating erroneous debts, and card payment failures when trying to settle the outstanding amount through the app. Users are frequently confused because their bank shows a charge while Bmove shows an unpaid debt, or they receive notifications about debts they cannot see or pay in the app.

## When this applies

- User receives email notification about an outstanding/unpaid parking debt
- Payment transaction is cancelled/reversed by the payment system, automatically opening a debt
- System error creates an erroneous debt (e.g., licence plate not read correctly at garage exit, manual barrier lift)
- User's card payment fails when attempting to settle the debt in the app
- Debt is visible in notification but not visible inside the app
- User believes they already paid but debt remains open

## Typical resolution flow

1. User receives outstanding payment notification via email or in-app
2. User contacts support, often attaching bank statement showing the charge was made
3. Support agent investigates the specific purchase/session ID in the backend
4. Agent determines whether debt is erroneous (system error) or legitimate (cancelled transaction with returned funds)
5. If erroneous: agent deletes/cancels the debt manually
6. If legitimate: agent explains that the transaction was cancelled, funds were returned, and instructs user to repay via app (card or prepaid top-up)
7. If card payment fails: agent suggests using Bmove prepaid balance as alternative payment method
8. If bank-side issue: agent advises user to contact their bank

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Investigate purchase/session ID and transaction status in backend | support_agent | Bmove backend / Jira (b-i-p.atlassian.net) | 10 min |
| Delete/cancel erroneously created debt | support_agent | Bmove backend | 5 min |
| Send transaction status confirmation to user showing cancellation and return of funds | support_agent | email / Jira | 5 min |
| Instruct user to top up Bmove prepaid and use it to pay debt when card payment fails | support_agent | email | 3 min |
| Verify user-submitted bank statements and cross-check with payment gateway records | support_agent | Bmove backend / payment gateway | 15 min |

## Vendor dependency

- **Vendor:** Payment processing / garage ticketless service (unnamed)
- **Typical wait:** 3 day(s)

## Evidence

Derived from 91 tickets in cluster `BS:end_user|croatia|debt:c1`. Direct quotes from 8 representative tickets:

- `BS-22948` _[hr]_: "aplikacija stalno daje podmirite neplaćene obveze a kad kliknem nista se ne vidi niti razumijem zasto"
- `BS-45510` _[hr]_: "kupovina 14311639 nije naplaćena, transakcija je bila otkazana, sredstva su vraćena, a dug se otvorio automatski."
- `BS-22948` _[hr]_: "navedeno dugovanje nastalo je greškom. Dug smo sada maknuli, tako da Vam više neće nikakva obavijest dolaziti."
- `BS-17442` _[hr]_: "Dug je krivo stvoren i zato ga ne možete vidjeti u aplikaciji. Ovo nije naš problem, već problem naplatnog servisa koji pošalje krivu informaciju."
- `BS-42093` _[hr]_: "S obzirom da Vam plaćanje karticom ne prolazi, predlažemo Vam da napravite uplatu na Bmove prepaid račun u aplikaciji i tim prepaidom odaberete plaćanje duga."
- `BS-40073` _[hr]_: "izvješćujemo Vas kako je nastao tehnički storno od strane prodajnog mjesta, te je iz tog razloga autorizacija odbijena."
- `BS-22985` _[hr]_: "Dolaze mi obavjesti da imam ne podmirena dugovanja, medjutim kada otvorim aplikaciju nemam nis."
- `BS-42657` _[hr]_: "Račun mi se vodi kao nepodmiren u aplikaciji, iako je transakcija prošla i naplaćena što sam potvrdio s bankom."

## Cluster statistics

- **Volume:** 91 tickets total (91 unique semantic events after dedup)
- **Frequency:** 1.78 tickets/month (over data window 2023-02-02 → 2026-01-23)
- **Median resolution:** 1.2 days
- **Languages:** hr, en
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~13.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~3.4 (range [2.4, 4.4])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.80
- **Rationale:** Steps 3 and 4 (confirmation message drafting and prepaid top-up instructions) are templatable and can be pre-drafted by an assist tool once the agent identifies the root cause; steps 1, 2, and 5 require backend lookups that cannot be fully automated but can be streamlined with deep-linked admin views. A 25% time reduction is conservative given that ~40% of active minutes are drafting/instructing tasks.
- **Validation:** Run shadow-mode assist for 3 weeks: pre-populate confirmation email and top-up instruction templates when support agent opens a ticket tagged 'parking debt Croatia'; measure actual handle-time delta vs. control group.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~8.2 (range [5.74, 10.6])
- **Root cause:** Cancelled or reversed payment transactions automatically re-open a debt record without first confirming final settlement status with the payment gateway; additionally, erroneous debts are created by system errors and are not visible or payable in the app UI, trapping users in a broken state.
- **Rationale:** Fixing the automatic debt-creation logic to await confirmed gateway cancellation status, plus surfacing all debt states visibly in the app, would eliminate the majority of erroneous-debt and invisible-debt tickets; the residual cases involving genuine bank-charge discrepancies would remain. Effort estimate is directional pending engineering review of payment-webhook and debt-lifecycle code.
- **Validation:** Engineering team should spike the payment-webhook handling and debt-lifecycle state machine in one sprint to produce a concrete effort estimate; track erroneous-debt ticket volume before and after a staged rollout.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~2 (range [1.4, 2.6])
- **Form:** `in_app_help`
- **Deflection rate:** ~15% (range [10%, 19%])
- **Feasibility:** 0.45
- **Rationale:** Most tickets require backend investigation or cross-referencing payment gateway records, which users cannot perform themselves; however, a small share involving card-failure workarounds (top up prepaid) or FAQ clarification on cancelled-transaction behaviour could be deflected via contextual in-app help. The vendor dependency and need to verify bank statements severely limits self-service ceiling.
- **Validation:** Deploy a 4-week in-app contextual help article triggered by the 'outstanding debt' notification screen explaining cancelled-transaction behaviour and the prepaid top-up workaround; measure ticket submission rate before vs. after for this cluster.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.5 (range [0.35, 0.65])
- **Narrow use case:** Auto-send prepaid top-up instructions when debt status is payable but card payment has failed and no bank-statement dispute is indicated
- **Safety constraints:**
  - Must never autonomously delete or cancel a debt record without human review
  - Must not send transaction-status confirmations without cross-checking payment gateway records
  - Must not act on cases where user has submitted bank statements showing a charge (potential double-charge risk)
  - Vendor dependency on payment processor means autonomous decisions on fund status carry financial liability
  - Must escalate immediately if debt is not visible in app UI (system-error indicator)
- **Rationale:** The financial and vendor-dependency complexity of this pattern makes full autonomous resolution unsafe; only the narrow, low-risk sub-case of routing card-failure users to the prepaid workaround is feasible without human review. Even this carries risk of user confusion if the debt is actually erroneous, limiting safe volume to 10%.
- **Validation:** Pilot over 6 weeks: auto-trigger prepaid top-up guidance message only for tickets where system flags 'card payment failed' with no open bank-statement dispute flag; measure user resolution rate and escalation-back rate; accept if escalation-back rate remains below 15%.

### Risks

- **Compliance concerns:**
  - Erroneous debt collection or failure to promptly cancel erroneous debts may implicate Croatian consumer protection regulations (Zakon o zaštiti potrošača) and EU Payment Services Directive (PSD2) obligations around transaction transparency
  - Handling and cross-referencing user bank statements constitutes processing of sensitive financial personal data under GDPR; retention and access must be controlled
  - Any automated action that results in a user being charged or a debt remaining open when funds were already taken by the bank creates double-charge liability
- **Must not automate:**
  - Cancellation or deletion of debt records without human verification of payment gateway status
  - Confirmation to users that funds have been returned without verified gateway confirmation
  - Any decision on cases where user has provided bank statements showing a charge
  - Escalation to vendor (payment processor) without human review of transaction details
- **Vendor dependencies blocking automation:**
  - Payment processing / garage ticketless service: resolving the root cause of automatic debt creation on cancellation requires API or webhook changes coordinated with this unnamed vendor; 3-day typical wait per case means autonomous resolution is unsafe without real-time gateway status access
  - Without a vendor-provided API for real-time transaction status queries, agent-assist and autonomous tools cannot reliably determine whether a reversal has been finalised

## Agent compatibility

- **Status:** `active` (extraction confidence 0.91)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

