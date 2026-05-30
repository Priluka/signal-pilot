---
id: parking-payment-failure-end-user
name: parking_payment_failure_end_user
title: End-user parking payment failures in Bmove app leading to fines or double charges
description: End users report that parking payments fail, are declined repeatedly, or appear to succeed in the app but do
  not actually register, often resulting in parking fines. A related variant involves apparent double-charging where one charge
  was only a bank authorization/reservation that should auto-reverse within 3–7 days. Issues span 3DS authentication failures,
  gateway timeouts, card incompatibility, and app errors.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: vendor_escalation
languages:
- other
- en
- de
country_focus:
- other
- at
status: active
cluster_id: BS:end_user|no_value|payment_issue:c0
project_key: BS
cluster_size: 41
cluster_size_dedup: 40
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.91
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.78
median_resolution_minutes: 7996.0
p95_resolution_minutes: 466522.0
cannot_reproduce_rate: 0.0488
data_window_start: '2022-11-29'
data_window_end: '2024-09-18'
annual_hours_saved: 1.6
roi:
  baseline_active_hours: 7.8
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.2
  deflection_hours_range:
  - 0.1
  - 0.3
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.6
  agent_assist_hours_range:
  - 1.1
  - 2.0
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 5.5
  product_fix_hours_range:
  - 3.9
  - 7.1
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.3
  autonomous_resolve_hours_range:
  - 0.2
  - 0.4
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-6340
- BS-9211
- BS-7962
- BS-3400
- BS-4741
- BS-9614
- BS-11489
- BS-11331
- BS-22658
- BS-8187
- BS-7070
- BS-4885
- BS-22996
- BS-22789
- BS-19574
- BS-9960
- BS-21407
- BS-5827
canonical_examples:
- BS-6340
- BS-7962
- BS-22658
vendor_dependency:
  vendor_name: PAAS (Bratislava parking authority) / BratislavaEcvParking gateway
  involves_vendor: true
  typical_wait_days: 5
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-reply to users asking only about a double-charge, confirming it is a bank authorization
    hold and providing the 3–7 day reversal timeline — no transaction investigation or vendor contact required.
  autonomous_resolve_safety_constraints:
  - Must not autonomously contact or submit disputes to PAAS / parking authority on behalf of the user.
  - Must not close tickets where a parking fine has been issued — human review required.
  - Must not handle any ticket where transaction logs show a genuine double debit (not a hold).
  - Must include a clear escalation path to a human agent in every automated response.
  - Classifier confidence threshold ≥ 0.90 required before autonomous send; lower-confidence tickets route to human.
related_playbooks:
- app-payment-failure-parking-ticket
- bmove-app-feedback-mixed-issues__7950cd
- hr-open-session-after-garage-exit
- hr-parking-ticket-fine-after-paid-app
- missing-parking-receipt-email
- parking-fine-received-despite-valid-payment
- prepaid-top-up-and-usage-issues
- slovakia-parking-payment-failure-no-ticket
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

# End-user parking payment failures in Bmove app leading to fines or double charges

## What this pattern is

End users report that parking payments fail, are declined repeatedly, or appear to succeed in the app but do not actually register, often resulting in parking fines. A related variant involves apparent double-charging where one charge was only a bank authorization/reservation that should auto-reverse within 3–7 days. Issues span 3DS authentication failures, gateway timeouts, card incompatibility, and app errors.

## When this applies

- User attempts to pay for parking via Bmove app and payment is declined or times out
- User completes 3DS bank authentication but app still reports failure
- Payment appears confirmed in app but parking ticket is not registered, leading to a fine
- User is charged twice (one real charge + one authorization hold)
- Unsupported card type (e.g. Diners) or bank-side 3DS relay failure
- App crashes or shows error after payment flow, leaving parking status uncertain

## Typical resolution flow

1. User submits feedback via Bmove app or contacts support directly
2. Support agent acknowledges receipt and forwards to technical team (Petar Zrinski / Aleksandar Dukovski / Hrvoje Sirovina)
3. Technical team checks Graylog / DT / backend logs for transaction activity
4. If double-charge: agent explains authorization hold and advises 3–7 day auto-reversal
5. If fine received: agent contacts PAAS (Bratislava parking authority) to verify
6. If gateway timeout confirmed: agent informs user of root cause and resolution
7. If insufficient logs: agent requests screenshot and license plate from user

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Acknowledge ticket and inform user technical team is investigating | support_agent | Jira Service Management | 5 min |
| Check transaction logs for user activity and payment outcome | technical_support | Graylog / DT (transaction monitoring) | 15 min |
| Explain authorization hold and advise on auto-reversal timeline (3–7 days) | support_agent | — | 5 min |
| Contact PAAS / parking authority to verify or dispute fine | support_agent | — | 20 min |
| Request screenshot and license plate from user when logs are insufficient | support_agent | Jira Service Management | 5 min |

## Vendor dependency

- **Vendor:** PAAS (Bratislava parking authority) / BratislavaEcvParking gateway
- **Typical wait:** 5 day(s)

## Evidence

Derived from 41 tickets in cluster `BS:end_user|no_value|payment_issue:c0`. Direct quotes from 7 representative tickets:

- `BS-6340` _[other]_: "Platba vo výške 0,75 bola odúčtovaná 2x, ale platila som len raz a potvrdenku mám tiež iba na jednu platbu."
- `BS-7962` _[en]_: "Payment do fails regularly, problems with the 3DS. I confirm it at the bank, but your application says that it failed. Already got me a ticket as I thought I payed for parking."
- `BS-22658` _[en]_: "app charged me twice for a parking ticket. first time it took the money but failed granting me parking. second time it worked"
- `BS-8187` _[en]_: "the customer had three attempts on 16.5.2023. For every attempt I see a timeout from BratislavaEcvParking, that is why the customer got the error with connection message."
- `BS-22996` _[other]_: "platba zrejme neprebehla, lebo som dostal listok o neuhradeni a spravnom jednani... bolo tam napísané error"
- `BS-4885` _[en]_: "customer claims that the payment was declined, but in app was approved. Customer received a fine."
- `BS-6340` _[other]_: "Jedna platba bola len autorizovaná (rezervovaná), suma by sa mala automaticky vrátiť na Váš účet v priebehu niekoľkých dní (väčsinou je to 3-5 dní)."

## Cluster statistics

- **Volume:** 41 tickets total (40 unique semantic events after dedup)
- **Frequency:** 0.78 tickets/month (over data window 2022-11-29 → 2024-09-18)
- **Median resolution:** 5.6 days
- **Cannot Reproduce rate:** 4.9%
- **Languages:** other, en, de
- **Country focus:** other, at

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~7.8 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.6 (range [1.12, 2])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.75
- **Rationale:** Agent-assist tooling can pre-fill acknowledgment messages, surface transaction-log query templates, and auto-draft the authorization-reversal explanation (actions 1, 3, 5), reducing repetitive writing time. Actions requiring vendor contact (action 4) and log interpretation (action 2) still need human judgment, limiting time savings.
- **Validation:** Run assist templates in shadow mode for 2 weeks across all new tickets in this cluster; measure agent-accepted draft rate and compare handle time against prior 8-week baseline to validate ≥14% reduction.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~5.5 (range [3.9, 7.1])
- **Root cause:** Payment failures stem from a combination of 3DS authentication failures, gateway timeouts with the BratislavaEcvParking gateway, and card-type incompatibilities in the Bmove app. Silent failures (app shows success but payment does not register) suggest inadequate transaction-status confirmation loops between the app and the PAAS gateway.
- **Rationale:** Resolving gateway timeout handling, 3DS retry logic, and adding reliable payment-status confirmation would eliminate the majority of support work, but vendor cooperation from PAAS is required and the fix scope spans both app and gateway layers, making effort highly uncertain. Hours eliminated are capped at the 7.8-hour baseline.
- **Validation:** Engineering team should conduct a spike (1 sprint) to map all failure modes against gateway API documentation and PAAS sandbox logs before committing to a fix estimate; measure post-release ticket volume over one quarter.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.2 (range [0.14, 0.26])
- **Form:** `help_center`
- **Deflection rate:** ~15% (range [10%, 20%])
- **Feasibility:** 0.50
- **Rationale:** Authorization-hold confusion (double-charge perception) is explainable via a clear help-center article and could deflect a subset of tickets, but payment failures requiring log investigation and vendor escalation cannot be self-served. Deflection potential is therefore limited to the informational double-charge variant only.
- **Validation:** Publish a targeted help-center article explaining 3–7 day authorization reversal; tag inbound tickets over 6 weeks to measure what fraction close without agent reply after reading the article (target: ≥10% deflection to validate model).

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.3 (range [0.21, 0.39])
- **Narrow use case:** Auto-reply to users asking only about a double-charge, confirming it is a bank authorization hold and providing the 3–7 day reversal timeline — no transaction investigation or vendor contact required.
- **Safety constraints:**
  - Must not autonomously contact or submit disputes to PAAS / parking authority on behalf of the user.
  - Must not close tickets where a parking fine has been issued — human review required.
  - Must not handle any ticket where transaction logs show a genuine double debit (not a hold).
  - Must include a clear escalation path to a human agent in every automated response.
  - Classifier confidence threshold ≥ 0.90 required before autonomous send; lower-confidence tickets route to human.
- **Rationale:** The only safely automatable slice is the narrow informational double-charge query where no log lookup or vendor action is needed; this represents a small fraction of the cluster and yields modest savings. Financial and fine-related consequences make broader autonomous resolution too risky at this volume.
- **Validation:** Pilot for 4 weeks: auto-reply only to tickets auto-classified as 'authorization hold question' with ≥0.90 confidence; measure CSAT, re-open rate, and false-positive rate; accept if re-open rate ≤ 10% and no fine-related cases are misclassified.

### Risks

- **Compliance concerns:**
  - Parking fines carry legal and financial consequences; incorrect or delayed responses may expose the operator to liability.
  - Payment data handling must comply with PSD2 / 3DS2 requirements and applicable Slovak/EU financial regulation.
  - GDPR applies to any automated processing of transaction records or license plate data.
- **Must not automate:**
  - Disputing or contacting PAAS / parking authority on a user's behalf.
  - Confirming or denying that a genuine double charge occurred without verified transaction log review.
  - Closing tickets where a parking fine has been issued without human confirmation of resolution.
  - Any action involving license plate data or fine reference numbers without human oversight.
- **Vendor dependencies blocking automation:**
  - BratislavaEcvParking gateway API reliability and sandbox access are required before engineering can fully diagnose and fix 3DS / timeout failures.
  - PAAS dispute process requires direct human communication; no API for automated fine disputes is documented.
  - Typical 5-day vendor wait time means ticket wall-clock time cannot be materially reduced without vendor SLA improvement.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.91)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

