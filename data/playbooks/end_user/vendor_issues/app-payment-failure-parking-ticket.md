---
id: app-payment-failure-parking-ticket
name: app_payment_failure_parking_ticket
title: Bmove App Payment Failure When Purchasing or Extending Parking Ticket
description: End users report being unable to pay for or extend parking tickets via the Bmove app, often due to app malfunction,
  third-party payment processor (Datatrans) errors, or city IT system outages. Users frequently receive or fear parking fines
  as a direct consequence of the failed payment. In some cases, payment is charged by the bank but not confirmed in the app,
  leading to duplicate purchases or refund requests.
category: end_user/vendor_issues
ticket_class: end_user
issue_category: vendor_failure
resolution_pattern: vendor_escalation
languages:
- other
country_focus:
- other
- at
status: active
cluster_id: BS:end_user|no_value|no_label:c1
project_key: BS
cluster_size: 33
cluster_size_dedup: 32
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.92
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.63
median_resolution_minutes: 7074.0
p95_resolution_minutes: 382357.35
cannot_reproduce_rate: 0.0606
data_window_start: '2022-10-13'
data_window_end: '2026-04-14'
annual_hours_saved: 1.4
roi:
  baseline_active_hours: 5.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.7
  deflection_hours_range:
  - 0.5
  - 0.9
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.4
  agent_assist_hours_range:
  - 1.0
  - 1.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 3.9
  product_fix_hours_range:
  - 2.8
  - 5.0
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.3
  autonomous_resolve_hours_range:
  - 0.2
  - 0.4
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-35331
- BS-43932
- BS-11366
- BS-3583
- BS-12420
- BS-18650
- BS-25244
- BS-27717
- BS-33582
- BS-12299
- BS-44868
- BS-38888
- BS-45847
- BS-27431
- BS-42597
- BS-48226
- BS-33510
- BS-2589
canonical_examples:
- BS-43932
- BS-42597
- BS-38888
vendor_dependency:
  vendor_name: Datatrans / Bratislava City IT system
  involves_vendor: true
  typical_wait_days: 1
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Automated outage acknowledgement reply when a confirmed Datatrans or city IT outage
    flag is active, with a status link and ETA — no transaction data accessed.
  autonomous_resolve_safety_constraints:
  - Must never confirm, deny, or process financial transactions autonomously
  - Must not advise on parking fine disputes without human review
  - Must halt autonomous replies if outage flag source is unavailable or ambiguous
  - Must route any ticket mentioning duplicate charge or refund directly to a human agent
  - Must disclose bot-generated response to user
related_playbooks:
- bmove-app-feedback-mixed-issues__7950cd
- croatia-sms-parking-payment-failure
- hr-open-session-after-garage-exit
- hr-parking-ticket-fine-after-paid-app
- parking-fine-received-despite-valid-payment
- parking-payment-failure-end-user
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

# Bmove App Payment Failure When Purchasing or Extending Parking Ticket

## What this pattern is

End users report being unable to pay for or extend parking tickets via the Bmove app, often due to app malfunction, third-party payment processor (Datatrans) errors, or city IT system outages. Users frequently receive or fear parking fines as a direct consequence of the failed payment. In some cases, payment is charged by the bank but not confirmed in the app, leading to duplicate purchases or refund requests.

## When this applies

- User attempts to purchase a parking ticket via the Bmove app and payment fails
- User attempts to extend a parking ticket and the extension fails despite funds being reserved
- City IT system (Bratislava municipality backend) experiences an outage
- Third-party payment processor (Datatrans) experiences network timeouts or errors
- Card registration fails in the app
- Payment is authorized by bank/3DS but not confirmed in the app, resulting in no active ticket

## Typical resolution flow

1. User submits feedback via the Bmove app reporting payment failure
2. Support acknowledges the ticket and investigates whether it is a known outage or isolated issue
3. Support checks internal systems for active outages (city IT or Datatrans)
4. If outage confirmed, user is informed and advised to wait or use alternative payment methods
5. If no outage detected, support requests screenshot or more details from user
6. Internal escalation to technical team or payment provider (Datatrans) if transaction-level failure confirmed
7. User is advised on fine handling if a parking fine was received due to app failure
8. If duplicate charge occurred, user is informed that reserved payments auto-reverse within hours/days

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Acknowledge user feedback and check for known system outages | support_agent | Jira / internal monitoring | 10 min |
| Request screenshot of the error step from user | support_agent | email | 5 min |
| Escalate failed transaction details to technical team or Datatrans | support_agent | Jira internal comment / Datatrans logs | 15 min |
| Inform user that duplicate/reserved payment will auto-reverse | support_agent | email | 5 min |
| Advise user on parking fine dispute and forward relevant information to city | support_agent | email | 10 min |

## Vendor dependency

- **Vendor:** Datatrans / Bratislava City IT system
- **Typical wait:** 1 day(s)

## Evidence

Derived from 33 tickets in cluster `BS:end_user|no_value|no_label:c1`. Direct quotes from 7 representative tickets:

- `BS-43932` _[other]_: "nie je mozne zaplatit kartou , 2hod zdarma prevzalo, listok bezi, ale dlhsia doba zaplatit nie je mozna. aplikacia vypina"
- `BS-42597` _[en]_: "all of his 7 transactions from 26.09.2025 at from 8:09 - 08:19 failed with same error from DT "fail" : { "reason" : "error", "message" : "Communication to Url: Read timed out (java.net.SocketTimeoutEx"
- `BS-38888` _[other]_: "Evidujeme výpadok systému zo strany mesta, ktorý ale už vyzerá byť vyriešený a lístok sa opäť dá zakúpiť."
- `BS-48226` _[other]_: "zakúpil som si parkovanie v Košiciach, platbu mi stiahlo ale lístok nepridalo do aplikácie, musel som si ho zakúpiť znovu"
- `BS-18650` _[other]_: "nefunguje vam aplikacia na nakup listka. pisem Vam to z dovodu pripadnej pokuty za neuhradenie parkovneho, ktore objektivne, z dovodov na Vasej strane, neviem uhradit."
- `BS-27717` _[other]_: "Dobrý deň chcela kúpiť navstevnicku"
- `BS-12420` _[other]_: "aplikacia ma pustila do garaze, aj otvorila dvere pri navrate ale pri rampe si odomna vypytala platbu a z karty stiahla tym padom 2x 6,-"

## Cluster statistics

- **Volume:** 33 tickets total (32 unique semantic events after dedup)
- **Frequency:** 0.63 tickets/month (over data window 2022-10-13 → 2026-04-14)
- **Median resolution:** 4.9 days
- **Cannot Reproduce rate:** 6.1%
- **Languages:** other
- **Country focus:** other, at

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~5.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.4 (range [1.01, 1.79])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** Steps 1, 4, and 5 (outage check, duplicate-payment explanation, fine-dispute guidance) are largely templated and well-suited to AI-drafted responses, reducing lookup and composition time; steps 2 and 3 (screenshot triage and technical escalation) still require agent judgment and vendor coordination, limiting overall time savings. A well-tuned assist tool should achieve ~25% active-time reduction per ticket.
- **Validation:** Run shadow-mode agent-assist for 3 weeks on incoming payment-failure tickets; compare agent accept-rate, edit distance, and handle time against a control group to validate the 25% reduction assumption.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~3.9 (range [2.8, 5])
- **Root cause:** Multi-causal: (1) Datatrans payment gateway returning unconfirmed success states to the Bmove app, causing charged-but-not-confirmed scenarios; (2) insufficient retry/idempotency logic in the app to prevent duplicate charges; (3) no real-time outage detection to surface clear user-facing error messaging and halt payment attempts during known city IT outages.
- **Rationale:** Robust idempotency keys, webhook confirmation handling, and outage detection could eliminate the duplicate-charge and silent-failure sub-types, which account for the majority of escalation work; however, upstream Datatrans and city IT instability means some residual volume will persist regardless of app fixes. Hours eliminated are capped at baseline (5.6 h) and reflect ~70% addressable sub-type estimate.
- **Validation:** Engineering team to audit Datatrans webhook logs and app payment-confirmation flow in staging; estimate sprints after spike; measure post-release ticket rate over 8 weeks compared to pre-fix baseline.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.7 (range [0.476, 0.884])
- **Form:** `in_app_help`
- **Deflection rate:** ~12% (range [8%, 16%])
- **Feasibility:** 0.35
- **Rationale:** Payment failures involving third-party processor and city IT outages are largely vendor-driven, meaning self-service content can inform users but cannot resolve the root cause; a status page or in-app outage banner may reduce contacts only marginally. Users experiencing charged-but-unconfirmed payments require agent intervention for safety and trust reasons, limiting true deflection potential.
- **Validation:** Deploy a 4-week in-app help article and live outage status banner; measure contact-rate change during known outage windows versus baseline to isolate deflection lift.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.3 (range [0.196, 0.364])
- **Narrow use case:** Automated outage acknowledgement reply when a confirmed Datatrans or city IT outage flag is active, with a status link and ETA — no transaction data accessed.
- **Safety constraints:**
  - Must never confirm, deny, or process financial transactions autonomously
  - Must not advise on parking fine disputes without human review
  - Must halt autonomous replies if outage flag source is unavailable or ambiguous
  - Must route any ticket mentioning duplicate charge or refund directly to a human agent
  - Must disclose bot-generated response to user
- **Rationale:** Full autonomous resolution is unsafe given financial transaction disputes, potential parking fines with legal consequences, and vendor-dependent root causes requiring human escalation; only a narrow outage-status acknowledgement use case (step 1 partial) is viable without significant compliance risk. Even within that scope, volume addressable is capped conservatively at 15% of tickets.
- **Validation:** Pilot for 4 weeks on tickets arriving during confirmed outage windows only; accept criteria: 0 autonomous messages sent on tickets involving charge disputes; measure user satisfaction and escalation rate versus control.

### Risks

- **Compliance concerns:**
  - Duplicate bank charges may trigger consumer protection or payment regulation obligations (e.g., PSD2 in EU); agent advice must be reviewed for regulatory accuracy
  - Parking fine disputes may carry legal consequences for users; automated guidance must not constitute legal advice
  - GDPR: transaction screenshots and bank references shared by users are sensitive personal financial data and must be handled per data-retention policy
- **Must not automate:**
  - Confirming or initiating any refund or charge reversal
  - Advising users on formal parking fine appeal processes without human sign-off
  - Accessing or relaying Datatrans transaction IDs or bank reference numbers autonomously
  - Closing tickets involving unresolved duplicate charges without human confirmation
- **Vendor dependencies blocking automation:**
  - Datatrans: no automation of escalation or resolution is possible without a vendor API or status feed exposing real-time outage and transaction confirmation state
  - Bratislava City IT system: outage detection and fine-dispute forwarding depend entirely on city-side cooperation and API availability; no SLA is implied by the 1-day typical_wait_days figure
  - App-side fix feasibility depends on Datatrans providing idempotency-safe webhook contracts — engineering effort estimate assumes vendor cooperation

## Agent compatibility

- **Status:** `active` (extraction confidence 0.92)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

