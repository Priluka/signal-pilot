---
id: b2b-outstanding-payment-failure-app
name: b2b_outstanding_payment_failure_app
title: B2B partners unable to complete parking payment via app due to technical difficulties
description: B2B partner users receive automated 'Outstanding payment' notifications from Bmove after a parking session payment
  fails to process due to technical difficulties. The payment method (credit card) is typically valid and on file, but the
  app fails to charge it automatically. Customers reach out asking how to pay manually, requesting bank details for wire transfer,
  or requesting invoices/receipts for bookkeeping purposes.
category: b2b_operator/bugs
ticket_class: b2b_partner
issue_category: bug_in_product
resolution_pattern: product_fix_required
languages:
- de
- en
country_focus:
- at
- de
- other
status: active
cluster_id: BS:b2b_partner|austria|no_label:c3
project_key: BS
cluster_size: 27
cluster_size_dedup: 15
sample_size_used: 15
extraction_schema: v1.0
extraction_confidence: 0.88
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.29
median_resolution_minutes: 311.0
p95_resolution_minutes: 56784.0
cannot_reproduce_rate: 0.037
data_window_start: '2023-10-12'
data_window_end: '2026-01-20'
annual_hours_saved: 0.6
roi:
  baseline_active_hours: 2.4
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.2
  deflection_hours_range:
  - 0.2
  - 0.3
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.6
  agent_assist_hours_range:
  - 0.4
  - 0.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.4
  product_fix_hours_range:
  - 1.7
  - 2.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.2
  autonomous_resolve_hours_range:
  - 0.1
  - 0.2
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-14426
- BS-30872
- BS-46491
- BS-33184
- BS-33165
- BS-43862
- BS-29168
- BS-31318
- BS-29197
- BS-32811
- BS-33101
- BS-31591
- BS-44910
- BS-17187
- BS-16936
canonical_examples:
- BS-14426
- BS-44910
- BS-33101
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: reference_only
  claude_skill: reference_only
  agent_assist: false
  autonomous_resolve: true
  note: Engineering backlog — not for runtime agents
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-send retry-payment instructions and invoice/bank-details link when an 'Outstanding
    payment' notification is confirmed for a B2B partner with a valid card on file
  autonomous_resolve_safety_constraints:
  - Must never autonomously initiate a financial transaction or charge on behalf of the customer
  - Must confirm card-on-file validity via read-only API check before sending retry instructions
  - Must escalate to human agent if the customer has already attempted manual payment or disputes the charge
  - Must not send bank wire details autonomously without identity verification of the requestor
  - Must log all autonomous actions for audit and compliance review
related_playbooks:
- b2b-missing-parking-receipt-request
- b2b-partner-austria-ticketless-open-session-at-exit
- b2b-ticketless-outstanding-payment-failure
- croatia-parking-payment-failure__ffdf4e
- hr-open-session-after-garage-exit
- ticketless-open-session-not-closed-at-exit
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

# B2B partners unable to complete parking payment via app due to technical difficulties

## What this pattern is

B2B partner users receive automated 'Outstanding payment' notifications from Bmove after a parking session payment fails to process due to technical difficulties. The payment method (credit card) is typically valid and on file, but the app fails to charge it automatically. Customers reach out asking how to pay manually, requesting bank details for wire transfer, or requesting invoices/receipts for bookkeeping purposes.

## When this applies

- Bmove system sends automated 'Outstanding payment' email after payment processing fails during or after a parking session
- Customer's credit card is on file but was not charged successfully
- Customer receives repeated automated reminders without the underlying payment issue being resolved
- Customer updates their credit card but system still cannot process the outstanding payment
- Customer cannot access the app or payment history to manually settle the outstanding amount

## Typical resolution flow

1. Bmove system fails to process payment and sends automated outstanding payment notification to customer
2. Customer replies to the notification or contacts support asking how to pay or why payment failed
3. Customer may attempt to update or re-add credit card without success
4. Customer requests bank account details for manual wire transfer or requests a formal invoice
5. Support team sends automated acknowledgement (1–5 business day response time)
6. Support agent investigates and may instruct customer to use 'Purchase History → Continue to Payment' flow in the app
7. If issue persists, agent may need to manually process or resolve the outstanding amount

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Send automated acknowledgement of received ticket | system | Bmove support ticketing system | 1 min |
| Instruct customer to navigate to Purchase History and retry payment manually via app | support_agent | Bmove app | 10 min |
| Investigate why automatic payment charge failed despite valid credit card on file | support_agent | Bmove backend/admin system | 20 min |
| Provide bank details or invoice for manual wire transfer if app payment remains impossible | support_agent | — | 10 min |

## Evidence

Derived from 27 tickets in cluster `BS:b2b_partner|austria|no_label:c3`. Direct quotes from 6 representative tickets:

- `BS-14426` _[de]_: "ich schreibe Ihnen jetzt zum zweiten Mal, dass die Zahlung über die App nicht möglich ist. Bitte senden Sie mir Ihre Kontonummer, damit ich den Betrag begleichen kann."
- `BS-44910` _[de]_: "Bitte buchen sie endlich von der hinterlegten Zahlungsweise ab. Die mail nerven langsam!"
- `BS-33101` _[de]_: "Ich ersuche daher zum wiederholten Mal, mir eine Rechnung (brauche ich für die Firma) mit Bankverbindung zukommen zu lassen, damit ich die offene Forderung bezahlen kann."
- `BS-31318` _[en]_: "we have a valid payment method saved in the account and he has setup 'ticketless' for his car – why do we have such difficulty with the app?"
- `BS-17187` _[de]_: "obwohl ich bereits die neue Kreditkarte hinzugefügt und mit den Fahrzeugen verknüpft habe, ist die Bezahlung des u.a. Parkvorgangs noch immer nicht möglich."
- `BS-31591` _[de]_: "das ganze BMove geht nicht mehr für mich, sie müssen das endlich reparieren, dass ich das wieder verwenden kann"

## Cluster statistics

- **Volume:** 27 tickets total (15 unique semantic events after dedup)
- **Frequency:** 0.29 tickets/month (over data window 2023-10-12 → 2026-01-20)
- **Median resolution:** 5.2 hours
- **Cannot Reproduce rate:** 3.7%
- **Languages:** de, en
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.4 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.6 (range [0.43, 0.77])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.70
- **Rationale:** Agent-assist can accelerate the two templated response steps (retry instructions and bank-detail/invoice provision) by pre-drafting replies, reducing active writing time; however, the investigation step (diagnosing why the charge failed) requires manual account lookup and cannot be meaningfully assisted without deep system integration.
- **Validation:** Run shadow-mode agent-assist for 2 weeks on incoming tickets of this type, measuring time-to-send for templated responses vs. the 41-minute baseline; a ≥20% reduction in active minutes per ticket validates feasibility.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~2 (range [1.4, 2.6])
- **Hours eliminated per year:** ~2.4 (range [1.7, 2.4])
- **Root cause:** Automatic payment charging fails despite a valid credit card on file, suggesting a bug in the payment-processing flow (e.g., tokenisation failure, silent retry exhaustion, or webhook miscommunication with the payment gateway) that triggers erroneous 'Outstanding payment' notifications.
- **Rationale:** A product fix addressing the root-cause payment-charge failure would eliminate the entire cluster of tickets; hours eliminated are capped at the 2.4-hour baseline, with a conservative low reflecting residual edge cases that may persist post-fix.
- **Validation:** Engineering team should reproduce the failure in a staging environment using a known-valid card, instrument payment-charge retries with structured logging, and confirm fix coverage via a regression test suite before release; monitor ticket volume for 4 weeks post-deploy.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.2 (range [0.17, 0.31])
- **Form:** `help_center`
- **Deflection rate:** ~20% (range [14%, 26%])
- **Feasibility:** 0.45
- **Rationale:** A help-center article explaining how to manually retry payment via Purchase History could deflect a fraction of tickets from users who simply do not know the self-service path; however, the underlying bug means many users will still need agent help even after reading the article, limiting deflection potential significantly.
- **Validation:** Publish a targeted help-center article and track ticket-open rate vs. article views over 4 weeks; a deflection rate above 15% would validate the estimate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.2 (range [0.112, 0.208])
- **Narrow use case:** Auto-send retry-payment instructions and invoice/bank-details link when an 'Outstanding payment' notification is confirmed for a B2B partner with a valid card on file
- **Safety constraints:**
  - Must never autonomously initiate a financial transaction or charge on behalf of the customer
  - Must confirm card-on-file validity via read-only API check before sending retry instructions
  - Must escalate to human agent if the customer has already attempted manual payment or disputes the charge
  - Must not send bank wire details autonomously without identity verification of the requestor
  - Must log all autonomous actions for audit and compliance review
- **Rationale:** Full autonomous resolution is inadvisable given the payment-failure bug context and financial sensitivity; a narrow bot could safely auto-send acknowledgement and basic retry instructions to a small subset of straightforward cases, but investigation and wire-transfer provision require human judgement.
- **Validation:** Pilot on ≤15% of incoming tickets for 4 weeks with human review of every autonomous action; acceptance criteria: zero incorrect financial instructions sent, customer satisfaction score ≥ matched human-handled baseline.

### Risks

- **Compliance concerns:**
  - Sharing bank wire-transfer details must comply with data protection regulations (e.g., GDPR) and internal financial controls to prevent fraud
  - Invoice and receipt generation may carry VAT/tax compliance obligations depending on partner jurisdiction
  - Automated handling of payment failures may need to align with PSD2 or local electronic payment regulations
- **Must not automate:**
  - Root-cause investigation of payment charge failures (requires account-level system access and judgement)
  - Provision of bank wire-transfer details without human verification of requestor identity
  - Any action that initiates, retries, or cancels a financial transaction on behalf of the customer

## Agent compatibility

- **Status:** `active` (extraction confidence 0.88)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Engineering backlog — not for runtime agents

