---
id: croatia-ticketless-best-in-parking-knowledge-gap
name: croatia_ticketless_best_in_parking_knowledge_gap
title: Croatian users unaware that Best in Parking garages require Ticketless setup in Bmove app
description: End users in Croatia (and occasionally abroad) attempt to pay for parking in Best in Parking-operated garages
  (e.g. Cvjetni, Kaptol, Zagrad, Korzo, Stari Grad, Cambijerijeva, Palmotićeva) via the standard off-street or barcode-scan
  flow in Bmove, and are confused when those garages are not listed or payment fails. The root cause is that Best in Parking
  garages require the dedicated 'Ticketless' feature to be activated in the Bmove app main menu, with a vehicle registration
  plate and payment method configured in advance. Users are unaware of this requirement, often because in-garage advertising
  promotes Bmove without explaining the Ticketless prerequisite.
category: end_user/knowledge_gaps
ticket_class: end_user
issue_category: knowledge_gap
resolution_pattern: user_education
languages:
- hr
- en
country_focus:
- hr
status: active
cluster_id: BS:end_user|croatia|ticketless:c3
project_key: BS
cluster_size: 45
cluster_size_dedup: 45
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.88
median_resolution_minutes: 1449.0
p95_resolution_minutes: 23415.799999999996
cannot_reproduce_rate: 0.0
data_window_start: '2023-01-18'
data_window_end: '2026-01-29'
annual_hours_saved: 0.6
roi:
  baseline_active_hours: 1.4
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.6
  deflection_hours_range:
  - 0.5
  - 0.8
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.6
  agent_assist_hours_range:
  - 0.4
  - 0.7
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.0
  product_fix_hours_range:
  - 0.7
  - 1.3
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 0.3
  autonomous_resolve_hours_range:
  - 0.2
  - 0.5
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-18659
- BS-5078
- BS-15145
- BS-5145
- BS-7909
- BS-11249
- BS-14626
- BS-21705
- BS-39119
- BS-24185
- BS-42120
- BS-21774
- BS-38467
- BS-7862
- BS-46392
- BS-22378
- BS-43667
- BS-36230
canonical_examples:
- BS-5078
- BS-5145
- BS-14626
vendor_dependency:
  vendor_name: Best in Parking
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: User education — safe for self-service deflection
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-reply to tickets that match 'Best in Parking' + 'Ticketless' or known garage names
    with a standardised setup guide, for contacts containing no payment dispute or billing complaint signal.
  autonomous_resolve_safety_constraints:
  - Must not auto-resolve tickets containing any indication of a payment charge, disputed transaction, or financial loss
  - Must not auto-resolve tickets mentioning signage complaints that may require escalation to Best in Parking vendor
  - Human review required if user expresses frustration beyond a single clarification request
  - Auto-reply should include explicit invitation for the user to respond if issue persists, preventing silent closure
related_playbooks:
- croatia-bmove-app-feedback-miscellaneous
- croatia-parking-fine-dispute
- croatia-parking-fine-dispute-and-payment
- croatia-parking-fine-payment-failure
- croatia-parking-payment-failure__ffdf4e
- croatia-parking-ticket-storno-user-error
- croatia-ticketless-open-session-at-exit__f25b63
- croatia-ticketless-rental-car-ghost-charge
- croatian-end-user-wrong-registration-storno-refund
- croatian-invoice-download-request
- croatian-parking-debt-payment-failure
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__56d2b2
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- hr-b2b-r1-invoice-request
- igeus-portal-access-credential-management
- italian-ticketless-setup-and-payment-issues
- open-session-at-exit-payment-failure
- phonzie-to-bmove-credit-refund-request
- prepaid-top-up-and-usage-issues
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

# Croatian users unaware that Best in Parking garages require Ticketless setup in Bmove app

## What this pattern is

End users in Croatia (and occasionally abroad) attempt to pay for parking in Best in Parking-operated garages (e.g. Cvjetni, Kaptol, Zagrad, Korzo, Stari Grad, Cambijerijeva, Palmotićeva) via the standard off-street or barcode-scan flow in Bmove, and are confused when those garages are not listed or payment fails. The root cause is that Best in Parking garages require the dedicated 'Ticketless' feature to be activated in the Bmove app main menu, with a vehicle registration plate and payment method configured in advance. Users are unaware of this requirement, often because in-garage advertising promotes Bmove without explaining the Ticketless prerequisite.

## When this applies

- User cannot find a Best in Parking garage (Cvjetni, Kaptol, Zagrad, Stari Grad, Korzo, Kapucinski trg, Palmotićeva, etc.) in the Bmove off-street parking list
- User attempts to pay via barcode/QR scan at a Best in Parking garage and receives an error or no recognition
- User arrives at a Best in Parking garage, takes a physical ticket at the barrier, and tries to pay via the app at exit
- User sees Bmove advertising inside a Best in Parking garage but cannot locate the garage in the app
- Barrier/ramp does not open because vehicle plate is not registered in an active Ticketless session

## Typical resolution flow

1. User installs or opens Bmove app and navigates to off-street parking or attempts barcode scan
2. User cannot find the desired Best in Parking garage in the standard listing, or scan/payment fails
3. User submits feedback or support ticket describing the missing garage or failed payment
4. Support agent responds explaining that Best in Parking garages require the Ticketless feature
5. Support agent instructs user to open Ticketless in the Bmove main menu, add vehicle registration plate, and add a payment method (card or Bmove prepaid)
6. User activates Ticketless and can subsequently enter/exit Best in Parking garages automatically

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Send standardised explanation that Best in Parking garages require Ticketless activation, with step-by-step setup instructions (add plate + payment method) | support_agent | Jira Service Management / email | 5 min |
| Clarify that in-garage advertising and pricing info is managed by Best in Parking and outside Bmove's control when user complains about misleading signage | support_agent | Jira Service Management / email | 3 min |

## Vendor dependency

- **Vendor:** Best in Parking

## Evidence

Derived from 45 tickets in cluster `BS:end_user|croatia|ticketless:c3`. Direct quotes from 7 representative tickets:

- `BS-5078` _[hr]_: "zašto odnedavno u sistemu više nisu Best in garaže Stari grad i Zagrad u Rijeci?"
- `BS-5145` _[hr]_: "u aplikaciji više nema Garaže Cvjetni pod gumbom off-street parking (kao ni nekih drugih parkinga koji su prije bili prisutni)"
- `BS-14626` _[hr]_: "skeniram karticu za platiti parking i konstantno dobivam poruku da taj nalog ne postoji. Riječ je o kartici garaže Kaptol Zagreb."
- `BS-42120` _[hr]_: "aplikacija ne nudi mogucnost placanja na parkingu Palmoticeva u Zagrebu, iako je navedeji da je sat preko aplikacijd 2e"
- `BS-21774` _[hr]_: "Tablica Vam nije skenirana zato što nemate aktiviranu Ticketless uslugu, pa sustav nije ni podignuo rampu jer nije pronašao Vašu tablicu među aktivnim Ticketlessima."
- `BS-15145` _[hr]_: "Aplikacija ne dozvoljava plaćanje skeniranjem bar coda pri parkiranju u Centar Cvjetni. U čemu je problem? Je li ticketless bas neophodan?"
- `BS-46392` _[hr]_: "u aplikaciji nisu dostupne sve garaze za zagreb (npr kaptol centar, cvijetni....). ljubazno molim popravak."

## Cluster statistics

- **Volume:** 45 tickets total (45 unique semantic events after dedup)
- **Frequency:** 0.88 tickets/month (over data window 2023-01-18 → 2026-01-29)
- **Median resolution:** 1.0 days
- **Languages:** hr, en
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~1.4 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.6 (range [0.41, 0.72])
- **Time reduction per ticket:** ~40% (range [29%, 51%])
- **Feasibility:** 0.90
- **Rationale:** The response is highly templated — a single canonical explanation covering Ticketless activation, plate registration, and payment setup accounts for the bulk of resolution time. A high-quality macro or AI-drafted reply triggered on 'Best in Parking' or 'Ticketless' keywords could reduce per-ticket active time by ~40%, with the agent reviewing and personalising before send.
- **Validation:** Run shadow-mode draft generation for 2 weeks, scoring agent acceptance rate and edit distance on draft replies; target ≥85% acceptance with minimal edits to confirm quality.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~1 (range [0.7, 1.3])
- **Hours eliminated per year:** ~1 (range [0.7, 1.26])
- **Root cause:** This is a UX/discoverability gap, not a software bug. Best in Parking garages are intentionally served through the Ticketless flow, but the app provides no contextual prompt or warning when a user attempts to pay via the standard off-street or barcode flow for a Ticketless-only garage.
- **Rationale:** A targeted in-app intercept — surfacing a 'This garage requires Ticketless setup' message when a Best in Parking garage is searched or payment fails — could eliminate the majority of contacts by educating users at the moment of confusion. Effort is low if the garage operator mapping already exists in the system.
- **Validation:** Engineering should confirm whether Best in Parking garages are already tagged distinctly in the garage data model; if so, a conditional UI message is a low-effort addition verifiable in a single sprint review.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.6 (range [0.45, 0.81])
- **Form:** `help_center`
- **Deflection rate:** ~45% (range [32%, 58%])
- **Feasibility:** 0.80
- **Rationale:** The resolution is entirely instructional — a step-by-step Ticketless setup guide in a help center or in-app tooltip at the point of garage search failure would address the knowledge gap before a ticket is raised. However, deflection is limited because users may not search help proactively and in-garage advertising triggers direct contact.
- **Validation:** Publish a dedicated 'Best in Parking / Ticketless setup' help-center article and track search-to-deflection rate over 4 weeks; compare incoming ticket volume for this cluster before and after publication.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~0.3 (range [0.25, 0.455])
- **Narrow use case:** Auto-reply to tickets that match 'Best in Parking' + 'Ticketless' or known garage names with a standardised setup guide, for contacts containing no payment dispute or billing complaint signal.
- **Safety constraints:**
  - Must not auto-resolve tickets containing any indication of a payment charge, disputed transaction, or financial loss
  - Must not auto-resolve tickets mentioning signage complaints that may require escalation to Best in Parking vendor
  - Human review required if user expresses frustration beyond a single clarification request
  - Auto-reply should include explicit invitation for the user to respond if issue persists, preventing silent closure
- **Rationale:** A subset of tickets — those with clear knowledge-gap wording and no financial dispute signal — are strong candidates for a fully automated instructional reply. However, the low annual volume (10.6 tickets/year) means absolute hours saved are modest, and caution is warranted given vendor-adjacent complaints about misleading signage.
- **Validation:** Pilot autonomous reply on 25% of incoming tickets for 6 weeks with a mandatory post-resolution CSAT micro-survey; accept only if CSAT matches or exceeds agent-handled baseline and re-open rate stays below 10%.

### Risks

- **Compliance concerns:**
  - Automated responses must not make commitments about Best in Parking pricing, garage access rights, or fee refunds, as these are outside Bmove's contractual scope
  - GDPR: any automation handling vehicle registration plate data (even indirectly referenced in tickets) must not log or store plate numbers beyond what is already permitted under the existing data retention policy
- **Must not automate:**
  - Tickets where the user reports a financial charge or failed payment resulting in a cost — these require human validation and potential vendor escalation
  - Complaints about misleading in-garage advertising that may carry consumer-protection implications requiring a human judgement call
- **Vendor dependencies blocking automation:**
  - In-app UX fixes that display Ticketless-specific messaging depend on Best in Parking garages being consistently and correctly tagged in the Bmove garage data feed; accuracy of this mapping must be confirmed with the vendor
  - Any help-center content about Best in Parking pricing, supported garages, or signage must be validated with Best in Parking before publication, as the vendor controls that information

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

