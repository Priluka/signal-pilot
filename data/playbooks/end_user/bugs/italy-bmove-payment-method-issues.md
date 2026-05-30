---
id: italy-bmove-payment-method-issues
name: italy_bmove_payment_method_issues
title: Italian end-users reporting payment failures or dissatisfaction with Bmove payment methods (Google Pay, credit card,
  missing wallet/PayPal)
description: Italian end-users submit feedback reporting inability to complete payments via Google Pay, credit card errors,
  or dissatisfaction with the removal of the pre-loaded wallet (borsellino) from the previous Phonzie app. A secondary theme
  involves requests for PayPal, Satispay, or a top-up wallet as alternatives to direct card charging. Support typically responds
  with standard troubleshooting steps (restart, update app, screenshot request) or explains the new direct-charge model and
  upcoming payment method additions.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: user_education
languages:
- it
country_focus:
- it
status: active
cluster_id: BS:end_user|italy|no_label:c3
project_key: BS
cluster_size: 145
cluster_size_dedup: 145
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.88
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.84
median_resolution_minutes: 1384.5
p95_resolution_minutes: 19278.099999999988
cannot_reproduce_rate: 0.0
data_window_start: '2022-12-08'
data_window_end: '2026-04-07'
annual_hours_saved: 2.4
roi:
  baseline_active_hours: 8.0
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 2.4
  deflection_hours_range:
  - 1.7
  - 3.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 2.4
  agent_assist_hours_range:
  - 1.7
  - 3.1
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 4.0
  product_fix_hours_range:
  - 2.8
  - 5.2
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.6
  autonomous_resolve_hours_range:
  - 0.4
  - 0.8
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-26431
- BS-22241
- BS-4972
- BS-3676
- BS-4949
- BS-7901
- BS-13707
- BS-47644
- BS-18288
- BS-20415
- BS-3969
- BS-18151
- BS-19591
- BS-24098
- BS-17320
- BS-21384
- BS-11296
- BS-8772
canonical_examples:
- BS-26431
- BS-22241
- BS-4972
vendor_dependency:
  vendor_name: Google Pay / PayPal / Satispay / issuing bank
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: User education — safe for self-service deflection
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-acknowledge and send localised Italian educational message (direct-charge model
    explanation + PayPal/Satispay roadmap update) for tickets classified as pure feature-dissatisfaction with no error code
    or screenshot attached.
  autonomous_resolve_safety_constraints:
  - Must not autonomously close tickets involving an actual payment error or reported financial loss
  - Must not make commitments about specific feature release dates for PayPal or Satispay
  - Must route to human agent if user replies with a screenshot or error code
  - Must not handle any ticket where a charge was processed but service not delivered (potential PSD2/consumer-rights implication)
  - 'Confidence threshold gate: autonomous action only if classifier confidence > 0.90'
related_playbooks:
- b2b-parking-invoice-payment-issues
- bmove-app-general-feedback-and-issues
- bmove-app-negative-feedback-italy
- italian-ticketless-setup-and-payment-issues
- microsoft365-quarantine-phishing-meta-impersonation
- phonzie-to-bmove-credit-refund-request
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

# Italian end-users reporting payment failures or dissatisfaction with Bmove payment methods (Google Pay, credit card, missing wallet/PayPal)

## What this pattern is

Italian end-users submit feedback reporting inability to complete payments via Google Pay, credit card errors, or dissatisfaction with the removal of the pre-loaded wallet (borsellino) from the previous Phonzie app. A secondary theme involves requests for PayPal, Satispay, or a top-up wallet as alternatives to direct card charging. Support typically responds with standard troubleshooting steps (restart, update app, screenshot request) or explains the new direct-charge model and upcoming payment method additions.

## When this applies

- User cannot complete payment via Google Pay (button unclickable or non-functional)
- User cannot add or use a credit card (connection error, authentication aborted)
- User receives unexpected bank pre-authorisation notification and is confused
- User misses the old Phonzie pre-loaded wallet/top-up model and finds new direct-charge slower
- User requests PayPal, Satispay, or other alternative payment methods
- User confused about extra fee (e.g. 25 cents) when paying via app

## Typical resolution flow

1. End-user submits feedback via Bmove app feedback form in Italian
2. Support agent acknowledges the report and states no system-wide anomaly is detected
3. Agent asks user for a screenshot of the error or clarification on where the flow fails
4. Agent advises restart of device/app and update to latest app version
5. If card issue, agent asks whether card is Visa or Mastercard
6. Agent explains the direct-charge model (no wallet needed, pay only minutes used)
7. Agent explains available payment methods and notes PayPal surcharge
8. If pre-authorisation confusion, agent explains it is a technical verification not a final charge
9. Agent informs user about planned PayPal/Satispay integration (where applicable)

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Acknowledge feedback and check for known system anomalies | support_agent | Bmove support platform | 5 min |
| Request screenshot of the error from the user | support_agent | email/ticket | 2 min |
| Advise app/device restart and update to latest app version | support_agent | — | 2 min |
| Explain pre-authorisation mechanism and direct-charge payment model | support_agent | — | 3 min |
| Inform user about planned PayPal/Satispay integration as future alternative | support_agent | — | 2 min |

## Vendor dependency

- **Vendor:** Google Pay / PayPal / Satispay / issuing bank

## Evidence

Derived from 145 tickets in cluster `BS:end_user|italy|no_label:c3`. Direct quotes from 8 representative tickets:

- `BS-26431` _[it]_: "google pay non funziona!!!"
- `BS-22241` _[it]_: "non riesco ad abilitare Google pay. non è cliccabile."
- `BS-4972` _[it]_: "nonostante vari tentativi in giornate diverse, non sono riuscita a collegare la carta di credito e pertanto non ho potuto usufruire del pagamento ticket parcheggio tramite applicazione."
- `BS-4949` _[it]_: "non mi va di mettere i dati della carta, perché non c'è l'opzione PayPal, che ormai usano tutti, dove i dati sono più protetti?"
- `BS-18151` _[it]_: "Authentification aborted. The transaction will be aborted. Cosa devo fare?"
- `BS-21384` _[it]_: "era molto meglio phonzie, precaricavi i soldi sull'app e la gestione era più veloce, così perdi tempo a pagare perché devi fare procedure più lunghe per un semplice parcheggio"
- `BS-11296` _[it]_: "create un borsellino o una ricarica per snellire il metodo di pagamento che attualmente è elaborato con la richiesta di autorizzazione."
- `BS-24098` _[it]_: "non capisco perché chi paga con app deve pagare 25 centesimi in più."

## Cluster statistics

- **Volume:** 145 tickets total (145 unique semantic events after dedup)
- **Frequency:** 2.84 tickets/month (over data window 2022-12-08 → 2026-04-07)
- **Median resolution:** 23.1 hours
- **Languages:** it
- **Country focus:** it

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~8 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~2.4 (range [1.7, 3.1])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.80
- **Rationale:** The resolution pattern is highly templated — troubleshooting steps, payment model explanation, and roadmap messaging are reusable across nearly all tickets — making this cluster well-suited to agent-assist draft generation in Italian. The main residual agent effort involves reviewing screenshots and checking for live system anomalies, which cannot be automated away.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-fills draft responses for this cluster; measure agent accept/edit/reject rates and net handle-time delta versus control tickets.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~4 (range [2.8, 5.2])
- **Root cause:** Two distinct root causes: (1) intermittent Google Pay and credit-card errors likely stemming from integration or tokenisation issues with payment processors; (2) deliberate product decision to remove the pre-loaded wallet (borsellino) from the legacy Phonzie app, creating unmet user expectations. The first is a fixable bug; the second requires a product roadmap decision to re-introduce wallet top-up or integrate PayPal/Satispay.
- **Rationale:** Resolving payment-processor integration bugs would eliminate the bug-related subset of tickets; adding PayPal/Satispay and/or a wallet feature would address the feature-gap complaints, though vendor certification timelines introduce significant uncertainty. Full elimination of all 8.0 baseline hours is unlikely because some user-education load will persist even after fixes.
- **Validation:** Engineering team to run payment-failure log analysis to quantify error-rate and root cause split (integration bug vs. user error vs. bank decline); estimate sprint count against that scoped backlog before committing to full integration work.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~2.4 (range [1.7, 3.1])
- **Form:** `help_center`
- **Deflection rate:** ~30% (range [21%, 39%])
- **Feasibility:** 0.65
- **Rationale:** A significant portion of tickets are informational — users seeking explanation of the new direct-charge model or roadmap items like PayPal/Satispay — which maps well to a help centre FAQ. However, genuine payment errors (Google Pay failures, card declines) require interactive troubleshooting and are unlikely to be deflected by static content alone.
- **Validation:** Deploy a localised Italian FAQ page covering the direct-charge model, pre-auth explanation, and planned payment methods; track ticket-to-view ratio and self-resolution rate over a 4-week period against the prior baseline.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.6 (range [0.42, 0.78])
- **Narrow use case:** Auto-acknowledge and send localised Italian educational message (direct-charge model explanation + PayPal/Satispay roadmap update) for tickets classified as pure feature-dissatisfaction with no error code or screenshot attached.
- **Safety constraints:**
  - Must not autonomously close tickets involving an actual payment error or reported financial loss
  - Must not make commitments about specific feature release dates for PayPal or Satispay
  - Must route to human agent if user replies with a screenshot or error code
  - Must not handle any ticket where a charge was processed but service not delivered (potential PSD2/consumer-rights implication)
  - Confidence threshold gate: autonomous action only if classifier confidence > 0.90
- **Rationale:** Autonomous resolution is only viable for a narrow slice of pure-dissatisfaction tickets where no financial error is claimed; payment-related contacts carry regulatory and trust risk that makes full automation unsafe for the majority of the cluster. The expected hours saving is modest given the low safe volume cap and the small annual frequency.
- **Validation:** Pilot over 6 weeks with a binary classifier trained on the 145-ticket cluster; apply autonomous response only to the highest-confidence pure-dissatisfaction cases, measure escalation rate and CSAT versus agent-handled control group.

### Risks

- **Compliance concerns:**
  - PSD2 / EU payment services regulation: any automated response touching a disputed or failed payment transaction must preserve the user's right to escalate to a human agent
  - Italian Consumer Code: automated messaging must not misrepresent feature availability (e.g., confirming PayPal launch date before it is confirmed)
  - GDPR: screenshots containing payment card details must be handled by a human agent and not ingested into automated pipelines without explicit data-minimisation controls
- **Must not automate:**
  - Any ticket where the user reports a charge was debited but the service was not delivered
  - Any ticket referencing a specific card number, IBAN, or bank account detail
  - Escalations involving repeated payment failures suggesting potential fraud or account compromise
  - Any ticket where the user has already expressed frustration with a prior automated response
- **Vendor dependencies blocking automation:**
  - Google Pay integration stability is subject to Google's payment API versioning and the issuing bank's tokenisation support — root-cause resolution requires triaging with Google Pay support
  - PayPal and Satispay integration timelines are entirely vendor-controlled and may shift, making any automated roadmap messaging a compliance and trust risk
  - Issuing-bank-side declines cannot be resolved by Bmove engineering alone and require user action or bank-side investigation

## Agent compatibility

- **Status:** `active` (extraction confidence 0.88)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

