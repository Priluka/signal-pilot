---
id: phonzie-to-bmove-credit-refund-request
name: phonzie_to_bmove_credit_refund_request
title: Phonzie residual credit refund request during migration to Bmove
description: Italian end-users who previously had credit on the Phonzie app contact support to recover their residual wallet
  balance after Phonzie was replaced by Bmove. Users are unable to find the refund option because it is only available via
  the Phonzie web portal (not the app), and many are unaware of or cannot locate the correct procedure. Support consistently
  responds with a link to a PDF guide and instructs users to access their reserved area on www.phonzie.eu.
category: end_user/knowledge_gaps
ticket_class: end_user
issue_category: knowledge_gap
resolution_pattern: user_education
languages:
- it
country_focus:
- it
status: active
cluster_id: BS:end_user|italy|no_label:c2
project_key: BS
cluster_size: 235
cluster_size_dedup: 235
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 4.61
median_resolution_minutes: 1136.0
p95_resolution_minutes: 5829.599999999996
cannot_reproduce_rate: 0.0
data_window_start: '2023-01-10'
data_window_end: '2026-02-03'
annual_hours_saved: 1.6
roi:
  baseline_active_hours: 4.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 2.1
  deflection_hours_range:
  - 1.5
  - 2.7
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.6
  agent_assist_hours_range:
  - 1.1
  - 2.1
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.8
  product_fix_hours_range:
  - 1.3
  - 2.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 1.1
  autonomous_resolve_hours_range:
  - 0.8
  - 1.5
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-19589
- BS-27842
- BS-22372
- BS-5686
- BS-7992
- BS-13666
- BS-14089
- BS-36303
- BS-35248
- BS-17359
- BS-5691
- BS-18541
- BS-17755
- BS-34745
- BS-19115
- BS-38738
- BS-17856
- BS-24441
canonical_examples:
- BS-19589
- BS-27842
- BS-14089
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
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-reply with Phonzie refund PDF link and www.phonzie.eu portal instructions when
    ticket is classified as Phonzie residual credit query with no account-specific data required.
  autonomous_resolve_safety_constraints:
  - Bot must not handle any tickets that reference a specific wallet balance amount or dispute a refund already submitted,
    which require human verification.
  - Automated reply must always include a human-escalation path (reply-to-agent option) given financial context.
  - Ticket classification confidence must exceed a defined threshold (e.g. ≥0.85) before autonomous send; low-confidence tickets
    route to agent queue.
  - Compliance with Italian consumer-credit and e-money regulations requires a human audit trail for any ticket that could
    constitute a financial complaint.
related_playbooks:
- bmove-app-negative-feedback-italy
- croatia-ticketless-best-in-parking-knowledge-gap
- croatia-ticketless-rental-car-ghost-charge
- croatian-invoice-download-request
- expired-card-deletion-ticketless-link
- hr-b2b-r1-invoice-request
- igeus-portal-access-credential-management
- italian-ticketless-setup-and-payment-issues
- italy-bmove-payment-method-issues
- microsoft365-quarantine-phishing-meta-impersonation
- prepaid-top-up-and-usage-issues
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Phonzie residual credit refund request during migration to Bmove

## What this pattern is

Italian end-users who previously had credit on the Phonzie app contact support to recover their residual wallet balance after Phonzie was replaced by Bmove. Users are unable to find the refund option because it is only available via the Phonzie web portal (not the app), and many are unaware of or cannot locate the correct procedure. Support consistently responds with a link to a PDF guide and instructs users to access their reserved area on www.phonzie.eu.

## When this applies

- User has residual credit on Phonzie wallet and wants to recover it
- User has migrated or been invited to migrate to Bmove and cannot find the credit refund option
- Local bus operator has switched from Phonzie to a different app (e.g., Bmove), leaving credit stranded
- User cannot find the 'Restituzione credito passaggio a Bmove' menu option in the app or website
- User did not receive or has lost the instruction email sent by Phonzie/Bmove

## Typical resolution flow

1. User contacts support requesting how to recover their Phonzie wallet credit
2. Support replies with the refund procedure PDF link (https://www.bmove.com/cdn/Istruzioni_rimborso_borsellino_Phonzie.pdf)
3. Support clarifies that the procedure must be done via the Phonzie website (www.phonzie.eu), not the app
4. User accesses their reserved area on www.phonzie.eu to complete the refund request
5. Ticket is closed after providing instructions

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Reply to user with the Phonzie credit refund PDF instructions and web portal link | support_agent | email/ticketing system | 3 min |
| Clarify that the refund procedure cannot be completed via the mobile app, only via the website | support_agent | email/ticketing system | 2 min |

## Evidence

Derived from 235 tickets in cluster `BS:end_user|italy|no_label:c2`. Direct quotes from 5 representative tickets:

- `BS-19589` _[it]_: "nella mia città (Rieti) la ditta dei bus ha cambiato App grazie"
- `BS-27842` _[it]_: "Non è possibile effettuare la procedura dalla app, ma solo attraverso la propria area riservata sul sito www.phonzie.eu"
- `BS-14089` _[it]_: "sulla mia area riservata non appare 'Restituzione credito passaggio a Bmove' sul menù. Cosa fare?"
- `BS-24441` _[it]_: "ho scaricato App Bmove, ma non trovo la voce 'Restituzione credito passaggio a Bmove' come dalle riportato nelle faq Bmove"
- `BS-7992` _[it]_: "vorrei riavere il mio credito residuo di 12.22 euro che sono rimasti sul borsellino di Phonzie visto che a Modena non è piu' attivo"

## Cluster statistics

- **Volume:** 235 tickets total (235 unique semantic events after dedup)
- **Frequency:** 4.61 tickets/month (over data window 2023-01-10 → 2026-02-03)
- **Median resolution:** 18.9 hours
- **Languages:** it
- **Country focus:** it

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~4.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.6 (range [1.15, 2.07])
- **Time reduction per ticket:** ~35% (range [25%, 45%])
- **Feasibility:** 0.90
- **Rationale:** The resolution is templated and deterministic — the agent sends the same PDF link and web portal instruction every time — making this an ideal candidate for a one-click suggested-reply macro. Time savings come from eliminating manual copy-paste and reducing cognitive effort to verify and send.
- **Validation:** Deploy a suggested-reply macro in shadow mode for 2 weeks, logging agent acceptance rate and time-to-reply delta. Target ≥80% macro acceptance rate before counting full time savings.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~1 (range [0.7, 1.3])
- **Hours eliminated per year:** ~1.8 (range [1.288, 2.392])
- **Root cause:** The refund function is a deliberate design decision to restrict it to the Phonzie web portal only; this is a UX/discoverability gap (knowledge_gap category) rather than a code defect. Engineering could add an in-app banner or deep-link directing users to www.phonzie.eu during the migration window to reduce misdirected contacts.
- **Rationale:** Adding a contextual in-app notice (banner or modal) pointing to the web portal refund flow could eliminate a significant share of contacts from users who attempt the process via mobile first. This is low engineering effort for the Bmove app team but effectiveness depends on user adoption of the app update.
- **Validation:** Engineering estimates sprint cost by scoping an in-app banner; after release, measure ticket volume from this cluster over a 6-week window versus the prior 6-week baseline to confirm reduction.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~2.1 (range [1.47, 2.67])
- **Form:** `help_center`
- **Deflection rate:** ~45% (range [32%, 58%])
- **Feasibility:** 0.85
- **Rationale:** This pattern is highly FAQ-deflectable because the resolution is a single, consistent action — sending a PDF link and a web portal URL — requiring no personalisation or account data. A prominent, searchable help-center article in Italian explaining the Phonzie-to-Bmove migration and the web-only refund path would intercept a meaningful share of tickets before users contact support.
- **Validation:** Publish the help-center article and monitor search-term hits alongside ticket volume for 4 weeks; compare weekly ticket rate before and after launch. A ≥30% reduction in weekly ticket rate from this cluster confirms the deflection hypothesis.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~1.1 (range [0.805, 1.495])
- **Narrow use case:** Auto-reply with Phonzie refund PDF link and www.phonzie.eu portal instructions when ticket is classified as Phonzie residual credit query with no account-specific data required.
- **Safety constraints:**
  - Bot must not handle any tickets that reference a specific wallet balance amount or dispute a refund already submitted, which require human verification.
  - Automated reply must always include a human-escalation path (reply-to-agent option) given financial context.
  - Ticket classification confidence must exceed a defined threshold (e.g. ≥0.85) before autonomous send; low-confidence tickets route to agent queue.
  - Compliance with Italian consumer-credit and e-money regulations requires a human audit trail for any ticket that could constitute a financial complaint.
- **Rationale:** Because the full-resolution action is a standardised informational reply with no account lookup required, autonomous resolution is technically feasible for a capped subset of tickets. The financial nature of the query and Italian consumer-protection context necessitate conservative volume caps and mandatory human escalation paths.
- **Validation:** Run a 4-week pilot with autonomous replies capped at 25% of incoming cluster volume; measure CSAT, re-contact rate within 7 days, and escalation rate. Require re-contact rate ≤15% and CSAT ≥4.0/5.0 before expanding scope.

### Risks

- **Compliance concerns:**
  - Phonzie wallet balances constitute stored e-money or prepaid credit; any automated handling must comply with Italian Banca d'Italia e-money regulations and EU PSD2 provisions on consumer refund rights.
  - Tickets that escalate into formal complaints are subject to Italian Consumer Code (Codice del Consumo) requirements for documented response timelines; automation must not mask complaint-eligible contacts.
  - GDPR: automated replies must not log or echo back any personal financial data the user includes in their message.
- **Must not automate:**
  - Tickets where the user disputes the refund amount they were credited or claims non-receipt of a refund already submitted — these require human account verification.
  - Tickets expressing formal dissatisfaction or using complaint language (reclamo) — these may trigger regulatory response-time obligations.
  - Any ticket where the user provides account credentials or sensitive personal data in the message body.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

