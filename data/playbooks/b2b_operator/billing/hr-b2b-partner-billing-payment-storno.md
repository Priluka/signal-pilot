---
id: hr-b2b-partner-billing-payment-storno
name: hr_b2b_partner_billing_payment_storno
title: Croatian B2B Partner Billing, Payment, and Storno Issues in Bmove Parking App
description: B2B partner accounts in Croatia frequently raise tickets related to invoice discrepancies, failed or incorrectly
  processed payments, and requests to reverse/storno parking ticket purchases. These issues span duplicate charges, missing
  invoices, corporate account payment configuration errors, and refund processing through bank channels. The tickets are predominantly
  in Croatian and involve coordination between the support team, internal systems (Igeus), and occasionally external banks
  or teleoperators.
category: b2b_operator/billing
ticket_class: b2b_partner
issue_category: billing
resolution_pattern: manual_close
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:b2b_partner|no_value|no_label:c4
project_key: BS
cluster_size: 151
cluster_size_dedup: 151
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.82
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.96
median_resolution_minutes: 2837.5
p95_resolution_minutes: 40664.200000000084
cannot_reproduce_rate: 0.0
data_window_start: '2022-02-09'
data_window_end: '2026-03-27'
annual_hours_saved: 9.6
roi:
  baseline_active_hours: 38.5
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 6.9
  deflection_hours_range:
  - 5.0
  - 8.8
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 9.6
  agent_assist_hours_range:
  - 6.9
  - 12.3
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 8.4
  product_fix_hours_range:
  - 6.1
  - 10.7
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 1.8
  autonomous_resolve_hours_range:
  - 1.3
  - 2.3
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-1022
- BS-5072
- BS-395
- BS-212
- BS-796
- BS-1144
- BS-3890
- BS-493
- BS-159
- BS-6623
- BS-1229
- BS-2668
- BS-519
- BS-132
- BS-5900
- BS-7219
- BS-687
- BS-6202
canonical_examples:
- BS-5072
- BS-395
- BS-1144
vendor_dependency:
  vendor_name: Igeus / CorvusPay / Erste Bank / teleoperators (A1, HT, Telemach)
  involves_vendor: true
  typical_wait_days: 2
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Automated redirect to app.bmove.com invoice download page for tickets matching 'invoice
    missing/not received' intent with no payment dispute signal
  autonomous_resolve_safety_constraints:
  - Must not autonomously initiate storno or financial reversals without agent review
  - Must not process or approve bank refund escalations autonomously
  - Must not modify corporate account payment configuration without agent confirmation
  - Must only act on tickets where no disputed charge or financial discrepancy is detected in the message
  - All autonomous actions must be logged and auditable for Croatian GDPR/financial regulation compliance
related_playbooks:
- b2b-missing-parking-receipt-request
- b2b-parking-invoice-payment-issues
- b2b-partner-parking-card-storno-refund
- b2b-ticketless-open-session-and-permit-conflict
- croatian-parking-debt-payment-failure
- hr-b2b-sms-parking-payment-failure
- manual-debt-cancellation-request
- missing-parking-receipt-request
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
---

# Croatian B2B Partner Billing, Payment, and Storno Issues in Bmove Parking App

## What this pattern is

B2B partner accounts in Croatia frequently raise tickets related to invoice discrepancies, failed or incorrectly processed payments, and requests to reverse/storno parking ticket purchases. These issues span duplicate charges, missing invoices, corporate account payment configuration errors, and refund processing through bank channels. The tickets are predominantly in Croatian and involve coordination between the support team, internal systems (Igeus), and occasionally external banks or teleoperators.

## When this applies

- B2B partner user cannot select corporate prepaid account as payment method
- Parking ticket was charged multiple times (duplicate charges)
- Partner requests storno/reversal of a mistakenly purchased parking ticket
- Invoice totals from Bmove do not match partner's internal system records
- Partner cannot locate or access historical invoices
- Bank declines refund reversal requiring written request to bank
- Partner queries number of SMS parking transactions for a specific period
- Corporate user not linked to business account after registration

## Typical resolution flow

1. B2B partner contacts support via email or forwarded complaint
2. Support agent reviews the partner account and transaction data in Igeus portal or CorvusPay
3. Agent checks user/account configuration (e.g., payment permissions, registration plate restrictions)
4. Agent resolves or escalates: performs storno, redirects to correct invoice portal, corrects account settings, or escalates to bank
5. Agent communicates outcome to partner and closes ticket

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Check transaction data and account configuration in Igeus portal | support_agent | IGeus portal | 15 min |
| Perform storno/reversal of mistakenly purchased parking ticket | support_agent | IGeus / internal system | 10 min |
| Correct corporate account user payment configuration (enable payment for any registration plate) | support_agent | Bmove admin panel | 10 min |
| Direct partner to app.bmove.com to download invoices | support_agent | email / app.Bmove.com | 5 min |
| Escalate bank refund rejection to Erste Bank via email with transaction details | support_agent | email to p****@erstecardclub.hr | 20 min |
| Redirect partner to relevant parking operator (e.g., Opatija21) for out-of-scope queries | support_agent | email | 5 min |

## Vendor dependency

- **Vendor:** Igeus / CorvusPay / Erste Bank / teleoperators (A1, HT, Telemach)
- **Typical wait:** 2 day(s)

## Evidence

Derived from 151 tickets in cluster `BS:b2b_partner|no_value|no_label:c4`. Direct quotes from 7 representative tickets:

- `BS-5072` _[hr]_: "iako joj je dodijeljen prepaid račun firme kao način plaćanja, ona je danas pokušala platiti parkiranje i ne može ga odabrati (nudi joj se samo plaćanje karticom)"
- `BS-395` _[hr]_: "Prema Vašem izvještaju ukupno naplaćeni iznos parkinga po svim teleoperaterima iznosi 6.946,00 hrk, međutim prema izvještaju kojeg dobijemo iz sustava Eccos ukupan prihod od parkinga naplaćen putem SM"
- `BS-1144` _[hr]_: "Molim Vas provjeru i storno kupnje parkirne karte koju je korisnik greškom kupio za cijelu sezonu u iznosu 400 kuna."
- `BS-7219` _[hr]_: "Povrat za obje narudžbe odbila je banka navodeći kod 1050 'declined'. Potrebno je poslati pisani zahtjev u banku."
- `BS-5900` _[hr]_: "Poštovana, sve račune možete preuzeti na app.bmove.com nakon što se prijavite Vašim korisničkim podacima."
- `BS-1022` _[hr]_: "molim vas potvrdu da je parkiranje (podaci u prilogu) naplaceno 1x a ne 4x kako je stiglo 4 potvrde na istu parkirnu kartu u razmaku manje od 2 min"
- `BS-5072` _[hr]_: "izgleda kako toj korisnici niste podesili da može plaćati za bilo koju registracijsku oznaku kao što ste ostalim korisnicima to podesili"

## Cluster statistics

- **Volume:** 151 tickets total (151 unique semantic events after dedup)
- **Frequency:** 2.96 tickets/month (over data window 2022-02-09 → 2026-03-27)
- **Median resolution:** 2.0 days
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~38.5 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~9.6 (range [6.9, 12.3])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.80
- **Rationale:** Agents follow largely repeatable lookup-and-respond workflows (Igeus portal check, storno procedure, invoice redirect) that are well-suited to templated response drafting and guided checklists in Croatian; this can meaningfully compress active handle time per ticket.
- **Validation:** Run a 3-week shadow-mode pilot generating draft responses and step-by-step lookup checklists for incoming Croatian billing tickets; measure draft acceptance rate and compare before/after handle time on a matched sample of ≥20 tickets.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~8.4 (range [6.1, 10.7])
- **Root cause:** Corporate account payment configuration defaults do not cover all registration plates, causing payment failures; invoice delivery or visibility gaps in the app generate avoidable download requests; and insufficient pre-purchase confirmations may contribute to accidental parking ticket purchases requiring storno.
- **Rationale:** Fixing the corporate account default configuration, adding a purchase-confirmation step, and surfacing invoices in-app would eliminate a material share of tickets without requiring agent involvement. The multi-system scope (Igeus integration, CorvusPay) moderately increases engineering complexity.
- **Validation:** Engineering team should audit Igeus API documentation and CorvusPay webhook logs to confirm root causes and scope effort; a spike of 2–3 days before sprint commitment is recommended.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~6.9 (range [5, 8.8])
- **Form:** `help_center`
- **Deflection rate:** ~18% (range [13%, 23%])
- **Feasibility:** 0.55
- **Rationale:** A meaningful subset of tickets involves partners not knowing how to download invoices or configure payment settings — these are FAQ-deflectable. However, the majority involve transaction disputes, storno requests, or bank refund escalations that require system access and cannot be self-served.
- **Validation:** Deploy a targeted help-center article and in-app tooltip (in Croatian) covering invoice download via app.bmove.com and corporate account payment configuration; measure ticket volume reduction for those sub-categories over 6 weeks.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~1.8 (range [1.3, 2.34])
- **Narrow use case:** Automated redirect to app.bmove.com invoice download page for tickets matching 'invoice missing/not received' intent with no payment dispute signal
- **Safety constraints:**
  - Must not autonomously initiate storno or financial reversals without agent review
  - Must not process or approve bank refund escalations autonomously
  - Must not modify corporate account payment configuration without agent confirmation
  - Must only act on tickets where no disputed charge or financial discrepancy is detected in the message
  - All autonomous actions must be logged and auditable for Croatian GDPR/financial regulation compliance
- **Rationale:** The overwhelming majority of tickets involve financial transactions, disputes, or vendor coordination that are unsafe to resolve autonomously; only the narrow invoice-redirect use case is low-risk enough to consider at limited volume. Even there, B2B partner context raises expectations for human confirmation.
- **Validation:** Pilot intent classification on 30 historical tickets to confirm what share are unambiguously invoice-download-only with no dispute signal; set autonomous action threshold only after ≥90% precision is confirmed on held-out tickets.

### Risks

- **Compliance concerns:**
  - Croatian and EU financial regulations (PSD2, VAT invoicing rules) require accurate and auditable handling of all billing corrections and refunds
  - GDPR applies to personal and corporate data processed during billing lookups in Igeus and CorvusPay
  - Storno and reversal of transactions may have legal and tax implications under Croatian accounting law requiring human sign-off
- **Must not automate:**
  - Storno or reversal of any parking ticket purchase
  - Escalation emails to Erste Bank containing transaction details
  - Modification of corporate account payment configuration
  - Any action involving disputed charges or duplicate billing without agent review
- **Vendor dependencies blocking automation:**
  - Igeus portal API access is required for any agent-assist or autonomous lookup; no confirmed programmatic access described
  - CorvusPay and Erste Bank refund workflows involve external parties with 2-day typical wait and no automation interface described
  - Teleoperator (A1, HT, Telemach) coordination for out-of-scope queries cannot be automated without formal handoff agreements

## Agent compatibility

- **Status:** `active` (extraction confidence 0.82)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

