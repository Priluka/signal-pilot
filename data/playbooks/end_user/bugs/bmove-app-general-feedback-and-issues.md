---
id: bmove-app-general-feedback-and-issues
name: bmove_app_general_feedback_and_issues
title: Bmove App General Feedback, Payment Issues, and Miscellaneous User Problems
description: Italian users (primarily) submit feedback or complaints via the Bmove app feedback form or web form covering
  a wide range of issues including payment failures, billing questions, app usability problems, permit management errors,
  and general feature requests. Most tickets originate from the automated app feedback pipeline and are classified as 'unknown'
  with no consistent resolution class. Responses typically involve user education about payment processes, pre-authorization
  mechanics, or basic app troubleshooting.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: user_education
languages:
- it
- en
- de
country_focus:
- it
- at
- other
status: active
cluster_id: BS:unknown|italy|no_label:c0
project_key: BS
cluster_size: 104
cluster_size_dedup: 102
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.72
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.0
median_resolution_minutes: 1726.0
p95_resolution_minutes: 139641.0
cannot_reproduce_rate: 0.0096
data_window_start: '2023-01-12'
data_window_end: '2026-01-16'
annual_hours_saved: 6.6
roi:
  baseline_active_hours: 22.0
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 2.8
  deflection_hours_range:
  - 2.0
  - 3.5
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 6.6
  agent_assist_hours_range:
  - 4.8
  - 8.4
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 8.0
  product_fix_hours_range:
  - 5.6
  - 10.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 1.5
  autonomous_resolve_hours_range:
  - 1.1
  - 1.9
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-17987
- BS-18728
- BS-17533
- BS-6528
- BS-11120
- BS-16827
- BS-18248
- BS-14149
- BS-11605
- BS-10934
- BS-38273
- BS-43435
- BS-15544
- BS-16533
- BS-12565
- BS-12782
- BS-16243
- BS-19414
canonical_examples:
- BS-17987
- BS-6528
- BS-12782
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: User education — safe for self-service deflection
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-respond to payment pre-authorization and receipt retrieval inquiries detected via
    intent classification, with no account changes required
  autonomous_resolve_safety_constraints:
  - Autonomous responses must not make any changes to user account, billing, or payment records
  - Any ticket containing a specific charge dispute or refund request must be escalated to a human agent
  - LPN misrecognition tickets must always be routed to an internal engineer — never autonomously closed
  - Italian-language intent classification must be validated for accuracy before deployment
  - User must always receive a clear escalation path to a human in the automated reply
  - Confidence threshold for intent match must be ≥ 0.85 before autonomous send
related_playbooks:
- b2b-parking-invoice-payment-issues
- italy-bmove-payment-method-issues
- unsolicited-spam-marketing-emails
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

# Bmove App General Feedback, Payment Issues, and Miscellaneous User Problems

## What this pattern is

Italian users (primarily) submit feedback or complaints via the Bmove app feedback form or web form covering a wide range of issues including payment failures, billing questions, app usability problems, permit management errors, and general feature requests. Most tickets originate from the automated app feedback pipeline and are classified as 'unknown' with no consistent resolution class. Responses typically involve user education about payment processes, pre-authorization mechanics, or basic app troubleshooting.

## When this applies

- User submits feedback via Bmove app feedback form
- User encounters payment failure or card authorization issue
- User cannot start or stop a parking session
- User is confused about pricing (minimum charge vs per-minute billing)
- User cannot register or log in to the app
- User receives unexpected charge or pre-authorization hold
- User requests a feature or improvement (e.g. prepaid wallet, bank transfer payment)
- User cannot purchase ZTL permit after app update
- User cannot download a receipt for a parking session
- User reports incorrect map data or LPN recognition error
- User submits web contact form about an open/stuck session

## Typical resolution flow

1. Automated system captures app feedback and creates a ticket
2. Support team reviews the ticket and identifies the sub-issue
3. Support agent responds with standard educational message or troubleshooting steps
4. If technical issue is confirmed, ticket may be escalated internally
5. Ticket is closed after user reply or after standard response is sent

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Send standard response explaining pre-authorization / payment process | support_agent | helpdesk / email | 5 min |
| Request screenshot or additional details to reproduce app issue | support_agent | helpdesk / email | 5 min |
| Provide parking receipt retrieval instructions | support_agent | helpdesk / email | 5 min |
| Forward feature request or map error to technical/product team | support_agent | internal escalation | 10 min |
| Investigate LPN misrecognition (wrong country assigned to license plate) | internal_engineer | web_tools / backend system | 30 min |

## Evidence

Derived from 104 tickets in cluster `BS:unknown|italy|no_label:c0`. Direct quotes from 8 representative tickets:

- `BS-17987` _[it]_: "Rispetto a Phonzie non si paga al minuto bensì si parte da una spesa minina di 50 centesimi !!! Già da questo punto di vista conviene poco !!!!"
- `BS-6528` _[it]_: "Il pagamento della sosta molto spesso non va a buon fine. Il mio istituto di credito è Banca Intesa."
- `BS-12782` _[it]_: "non si riesce a pagare con la carta di credito, dall'app di home banking"
- `BS-18728` _[it]_: "col nuovo aggiornamento non riesce più ad acquisare permessi ztl."
- `BS-17533` _[en]_: "I got one bill from u 4,40€ It's not possible. I am in Austria and not in Italy."
- `BS-16533` _[it]_: "impegnativo pagare ogni parcheggio. fonzie aveva un carrello prepagato! si perde un casino di tempo."
- `BS-43435` _[it]_: "Stamattina ho parcheggiato in Città Alta Via Fara alle ore 9 e sono uscita alle 11 tramite ticketless. Nonostante sia uscita però ho ancora attiva la sosta."
- `BS-12565` _[it]_: "non riesco a scaricare la ricevuta che devo allegare alla mail da inviare al comando di polizia che ci ha multati"

## Cluster statistics

- **Volume:** 104 tickets total (102 unique semantic events after dedup)
- **Frequency:** 2.0 tickets/month (over data window 2023-01-12 → 2026-01-16)
- **Median resolution:** 1.2 days
- **Cannot Reproduce rate:** 1.0%
- **Languages:** it, en, de
- **Country focus:** it, at, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~22 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~6.6 (range [4.84, 8.36])
- **Time reduction per ticket:** ~30% (range [22%, 38%])
- **Feasibility:** 0.80
- **Rationale:** Most resolution actions (pre-auth explanation, receipt retrieval instructions, screenshot request) are templated, language-specific (Italian) responses that a well-prompted LLM assistant can draft with high accuracy, reducing active agent time on the majority of tickets. LPN and bug-reproduction steps are less templatable and constrain the ceiling.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool auto-drafts responses for the three highest-frequency action types; measure agent edit rate and time-to-send versus the prior 2-week baseline to validate the 30% reduction assumption.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~8 (range [5.6, 10.4])
- **Root cause:** Multiple distinct product defects are present: payment/pre-authorization failures or unclear feedback in the app, permit management errors, LPN (license plate number) country misrecognition, and map errors — each requiring separate engineering investigation and resolution.
- **Rationale:** The cluster conflates several independent product bugs (LPN misrecognition alone involves 30 min of engineer time per ticket); fixing the highest-frequency bugs (payment UX clarity, LPN country detection) could eliminate a meaningful share of tickets, but the heterogeneous root causes make full elimination unlikely within any single fix cycle. Hours eliminated are capped at 22.0 (the baseline).
- **Validation:** Engineering should instrument app payment flows and LPN recognition errors to get precise failure-rate telemetry; a spike sprint of 3–5 days can validate root causes and refine the effort estimate before committing to a fix roadmap.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~2.8 (range [1.98, 3.52])
- **Form:** `in_app_help`
- **Deflection rate:** ~25% (range [18%, 32%])
- **Feasibility:** 0.65
- **Rationale:** A significant share of tickets concern payment pre-authorization mechanics and receipt retrieval — well-documented, repeated topics that translate well to in-app FAQ or guided help flows. However, the broad 'unknown' classification and mix of bug reports, feature requests, and LPN issues means a meaningful portion of contacts cannot be deflected by self-service content alone.
- **Validation:** Deploy an in-app help article covering pre-authorization, receipt retrieval, and common payment FAQs for 4 weeks; measure the ratio of article views to tickets submitted from the same session to calibrate deflection lift.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~1.5 (range [1.06, 1.87])
- **Narrow use case:** Auto-respond to payment pre-authorization and receipt retrieval inquiries detected via intent classification, with no account changes required
- **Safety constraints:**
  - Autonomous responses must not make any changes to user account, billing, or payment records
  - Any ticket containing a specific charge dispute or refund request must be escalated to a human agent
  - LPN misrecognition tickets must always be routed to an internal engineer — never autonomously closed
  - Italian-language intent classification must be validated for accuracy before deployment
  - User must always receive a clear escalation path to a human in the automated reply
  - Confidence threshold for intent match must be ≥ 0.85 before autonomous send
- **Rationale:** Only a narrow subset of tickets — those clearly seeking informational answers about pre-authorization or receipt retrieval with no account action needed — are safe to resolve autonomously; the cluster's heterogeneity and bug-in-product classification make broader autonomous resolution risky and premature. Estimated savings reflect 20% of 24 tickets/year × 10 active minutes saved per ticket (sending a pre-drafted reply vs. full agent work).
- **Validation:** Pilot with a 4-week intent-classification experiment: label incoming tickets and measure what fraction confidently match the narrow use case; require ≥ 90% precision on held-out set before enabling autonomous send, and monitor CSAT on auto-resolved tickets versus agent-resolved for the following 4 weeks.

### Risks

- **Compliance concerns:**
  - Payment pre-authorization explanations must be accurate under Italian and EU consumer protection law (PSD2, Consumer Rights Directive); incorrect automated explanations of billing mechanics could create legal exposure
  - Any automated handling of payment data references must comply with GDPR data minimisation principles — do not log or store payment details captured in free-text feedback
- **Must not automate:**
  - LPN misrecognition investigation — requires internal engineer access to backend vehicle recognition systems
  - Specific charge disputes or refund requests — require human judgment and account access
  - Permit management errors that could affect a user's legal parking status
  - Bug reproduction requiring screenshot analysis or device-specific diagnosis

## Agent compatibility

- **Status:** `active` (extraction confidence 0.72)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

