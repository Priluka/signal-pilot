---
id: bmove-app-negative-feedback-italy
name: bmove_app_negative_feedback_italy
title: Italian end-users submitting negative feedback about the Bmove app (usability, bugs, comparison to Phonzie)
description: 'End users, predominantly in Italy, submit in-app feedback expressing dissatisfaction with the Bmove app. Complaints
  cover a wide range: poor usability/UX, functional bugs (notifications not working, profile errors, vehicles not displayed,
  app unusable), and unfavorable comparisons to the predecessor app Phonzie. Responses are mostly templated acknowledgements
  asking for more detail or suggesting app restart/update.'
category: end_user/feature_requests
ticket_class: end_user
issue_category: feature_request
resolution_pattern: no_action
languages:
- it
country_focus:
- it
- other
status: active
cluster_id: BS:end_user|italy|no_label:c4
project_key: BS
cluster_size: 53
cluster_size_dedup: 53
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.82
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.04
median_resolution_minutes: 2492.0
p95_resolution_minutes: 261961.0
cannot_reproduce_rate: 0.0
data_window_start: '2022-12-09'
data_window_end: '2026-02-18'
annual_hours_saved: 0.6
roi:
  baseline_active_hours: 2.1
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.5
  deflection_hours_range:
  - 0.4
  - 0.7
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.6
  agent_assist_hours_range:
  - 0.4
  - 0.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.6
  product_fix_hours_range:
  - 1.1
  - 2.0
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.4
  autonomous_resolve_hours_range:
  - 0.3
  - 0.5
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-21468
- BS-4108
- BS-25568
- BS-4242
- BS-4914
- BS-7971
- BS-12457
- BS-27603
- BS-9111
- BS-22653
- BS-3965
- BS-17426
- BS-38747
- BS-4381
- BS-12341
- BS-4951
- BS-40854
- BS-21680
canonical_examples:
- BS-21468
- BS-4108
- BS-25568
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
  note: Informational — safe for agent self-service
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-send templated acknowledgement + restart/update instructions for tickets matching
    Italian locale + Bmove app + usability/bug keywords, with no further action required
  autonomous_resolve_safety_constraints:
  - Only applies to tickets where no account-specific data (profile errors, billing) is referenced
  - Must not auto-close tickets; human agent reviews all replies before case closure
  - Italian-language NLP classification must meet ≥90% precision on a held-out test set before activation
  - Escalation path required if user replies with account-specific complaint or reports safety-relevant issue
related_playbooks:
- italian-ticketless-setup-and-payment-issues
- italy-bmove-payment-method-issues
- microsoft365-quarantine-phishing-meta-impersonation
- phonzie-to-bmove-credit-refund-request
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Italian end-users submitting negative feedback about the Bmove app (usability, bugs, comparison to Phonzie)

## What this pattern is

End users, predominantly in Italy, submit in-app feedback expressing dissatisfaction with the Bmove app. Complaints cover a wide range: poor usability/UX, functional bugs (notifications not working, profile errors, vehicles not displayed, app unusable), and unfavorable comparisons to the predecessor app Phonzie. Responses are mostly templated acknowledgements asking for more detail or suggesting app restart/update.

## When this applies

- User submits in-app feedback via the Bmove feedback form
- User experiences functional issues (no notifications, app not working, profile error, missing vehicle)
- User is frustrated with UX complexity or lack of intuitiveness
- User compares Bmove unfavorably to predecessor app Phonzie

## Typical resolution flow

1. User submits feedback through Bmove app feedback form with type 'Problemi con l'applicazione', 'Proposta di miglioramento', or 'Altro'
2. Ticket is automatically created in Bmove Support
3. Support agent sends a templated response acknowledging feedback and/or asking for more details
4. No further escalation or product fix is documented in the ticket

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Send templated acknowledgement asking user to elaborate on the issue or suggesting app restart/update | support_agent | Bmove Support ticketing system | 5 min |
| Ask user to provide a screenshot of the issue | support_agent | Bmove Support ticketing system | 5 min |

## Evidence

Derived from 53 tickets in cluster `BS:end_user|italy|no_label:c4`. Direct quotes from 8 representative tickets:

- `BS-21468` _[it]_: "non ricevo notifiche e non riesco a operare."
- `BS-4108` _[it]_: "Phonzie era superiore come interfaccia e semplicità di uso e ricarica"
- `BS-25568` _[it]_: "App troppo macchinosa"
- `BS-9111` _[it]_: "l'applicazione non è di facile utilizzo e appare poco chiara"
- `BS-7971` _[it]_: "Per niente pratica... Appena recupero i crediti disinstallo tutto. Molto meglio Phonzie..."
- `BS-3965` _[it]_: "da errore nel completamento del profilo"
- `BS-40854` _[it]_: "in questo momento è da più giorni inutilizzabile"
- `BS-38747` _[it]_: "pur avendo inseriti due veicoli all'avvio della sosta compare soltanto uno"

## Cluster statistics

- **Volume:** 53 tickets total (53 unique semantic events after dedup)
- **Frequency:** 1.04 tickets/month (over data window 2022-12-09 → 2026-02-18)
- **Median resolution:** 1.7 days
- **Languages:** it
- **Country focus:** it, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.1 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.6 (range [0.441, 0.819])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.85
- **Rationale:** Responses are already highly templated (acknowledgement + restart/update suggestion), making this an excellent candidate for agent-assist auto-drafting; the agent's main remaining task is light personalisation and screenshot requests, so time savings are real but modest given the already-short active time per ticket.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-populates the templated acknowledgement and screenshot-request message; measure agent edit rate and time-to-send versus baseline to confirm the 30% time reduction assumption.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~1.6 (range [1.1, 2.041])
- **Root cause:** Multiple functional bugs reported: push notifications not firing, profile errors, vehicles not displaying, and app becoming unusable — likely stemming from migration or compatibility issues introduced during the transition from Phonzie to Bmove. UX regressions may also be contributing to dissatisfaction.
- **Rationale:** If the known functional bugs (notifications, profile, vehicle display) are resolved and UX parity with Phonzie is improved, the majority of this ticket cluster would likely disappear; however, some residual feedback about preferences or minor UX differences would persist. Hours eliminated are capped at baseline (2.1 h/yr) and discounted conservatively for residual volume.
- **Validation:** Engineering team should audit the bug backlog against reported symptoms, estimate per-bug fix effort in a sprint-planning session, and run a beta release with Italian users to measure ticket volume reduction before full rollout.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.5 (range [0.38, 0.676])
- **Form:** `in_app_help`
- **Deflection rate:** ~25% (range [18%, 32%])
- **Feasibility:** 0.55
- **Rationale:** Many complaints are repeat usability frustrations and bug reports that could be partially addressed by an in-app FAQ or known-issues notice; however, the emotional dissatisfaction and Phonzie comparison complaints are unlikely to be deflected by self-service content alone. Deflection potential is moderate at best given the venting nature of many submissions.
- **Validation:** Deploy a 4-week in-app help banner listing known issues and workarounds (restart, update steps) in the Italian locale; measure the ratio of feedback submissions before vs. after and track whether tickets referencing those issues decline.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.4 (range [0.294, 0.54])
- **Narrow use case:** Auto-send templated acknowledgement + restart/update instructions for tickets matching Italian locale + Bmove app + usability/bug keywords, with no further action required
- **Safety constraints:**
  - Only applies to tickets where no account-specific data (profile errors, billing) is referenced
  - Must not auto-close tickets; human agent reviews all replies before case closure
  - Italian-language NLP classification must meet ≥90% precision on a held-out test set before activation
  - Escalation path required if user replies with account-specific complaint or reports safety-relevant issue
- **Rationale:** The narrow scope of auto-sending a first-response acknowledgement is feasible given the repetitive templated nature of current responses, but full autonomous resolution is inappropriate because many tickets contain bug reports requiring triage and the emotional dissatisfaction context warrants human oversight. Savings are modest given low annual volume and 10-minute active time.
- **Validation:** Pilot over 6 weeks targeting only tickets from Italian locale flagged as Bmove feedback with no account-specific identifiers; measure false-positive escalation rate and user satisfaction scores versus agent-handled controls, accepting the autonomous path only if false-positive rate stays below 5%.

### Risks

- **Compliance concerns:**
  - Italian/EU users are covered by GDPR; any automated processing of feedback data must comply with data minimisation and purpose-limitation principles
  - Automated responses in Italian must be reviewed for language accuracy to avoid misleading users about bug fix timelines or commitments
- **Must not automate:**
  - Tickets referencing account-specific errors (profile corruption, vehicle access loss) that may indicate data integrity issues requiring human investigation
  - Tickets expressing severe dissatisfaction or explicit churn intent, which warrant personalised human response
  - Any feedback that could indicate a safety-relevant malfunction of mobility vehicles

## Agent compatibility

- **Status:** `active` (extraction confidence 0.82)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** Informational — safe for agent self-service

