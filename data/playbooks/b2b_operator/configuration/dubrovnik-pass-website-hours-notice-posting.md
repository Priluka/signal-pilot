---
id: dubrovnik-pass-website-hours-notice-posting
name: dubrovnik_pass_website_hours_notice_posting
title: Dubrovnik Pass partner requests posting of special operating hours notices on website
description: B2B partners (primarily Dubrovnik Pass Office staff) submit recurring tickets requesting that temporary or exceptional
  operating hours notices be published on the Dubrovnik Pass website in both Croatian and English. The notices concern specific
  attractions such as the Museum of Modern Art Dubrovnik (Umjetnička galerija Dubrovnik), Fortress Lovrjenac, and the Maritime
  Museum. Support agents manually post the notices and confirm completion via comment.
category: b2b_operator/configuration
ticket_class: b2b_partner
issue_category: configuration
resolution_pattern: configuration_change
languages:
- hr
- en
country_focus:
- hr
status: active
cluster_id: RAOS:b2b_partner|Support|duplikat:c0
project_key: RAOS
cluster_size: 18
cluster_size_dedup: 18
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.88
median_resolution_minutes: 107.5
p95_resolution_minutes: 2351.44999999999
cannot_reproduce_rate: 0.0
data_window_start: '2025-06-02'
data_window_end: '2026-04-08'
annual_hours_saved: 1.2
roi:
  baseline_active_hours: 3.9
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.1
  deflection_hours_range:
  - 0.1
  - 0.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.2
  agent_assist_hours_range:
  - 0.8
  - 1.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 3.1
  product_fix_hours_range:
  - 2.2
  - 3.9
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.8
  autonomous_resolve_hours_range:
  - 0.6
  - 1.1
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-3191
- RAOS-3848
- RAOS-4021
- RAOS-4417
- RAOS-4518
- RAOS-2997
- RAOS-3991
- RAOS-4414
- RAOS-3786
- RAOS-4059
- RAOS-4020
- RAOS-6783
- RAOS-3954
- RAOS-4510
- RAOS-4230
- RAOS-4165
- RAOS-4229
- RAOS-5598
canonical_examples:
- RAOS-3191
- RAOS-3191
- RAOS-4020
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: reference_only
  claude_skill: reference_only
  agent_assist: false
  autonomous_resolve: false
  note: Admin/operator-only configuration change
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Automated publishing of bilingual operating-hours notices submitted via a structured
    intake form by verified B2B partners, limited to pre-approved attraction list.
  autonomous_resolve_safety_constraints:
  - Partner identity must be verified before any web content is published
  - Published notices must be limited to pre-approved attraction list to avoid erroneous public-facing content
  - Automation must require exact bilingual text (HR+EN) provided by partner; no AI-generated translation without human review
  - Removal and correction requests must include a human confirmation step before going live
  - All auto-published notices must trigger an immediate email confirmation to the partner and a support-team audit log entry
related_playbooks:
- android-ppc-device-setup-and-app-installation
- dubrovnik-pass-website-notice-management
- hr-b2b-case-status-and-data-correction
- hr-b2b-monthly-invoice-generation-and-fiscalization
- hr-b2b-parking-operations-support
- hr-b2b-parking-price-change-request
- hr-b2b-photo-download-enablement
- hr-b2b-sms-parking-and-ddpk-issues
- hr-b2b-user-account-management
- hr-internal-partner-misc-support__0cfe1d
- hr-sms-parking-payment-issues
- kml-polygon-upload-correction-hr
- periodic-table-update-lpr-a1-ht
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Dubrovnik Pass partner requests posting of special operating hours notices on website

## What this pattern is

B2B partners (primarily Dubrovnik Pass Office staff) submit recurring tickets requesting that temporary or exceptional operating hours notices be published on the Dubrovnik Pass website in both Croatian and English. The notices concern specific attractions such as the Museum of Modern Art Dubrovnik (Umjetnička galerija Dubrovnik), Fortress Lovrjenac, and the Maritime Museum. Support agents manually post the notices and confirm completion via comment.

## When this applies

- Attraction has a special or modified opening time on a specific date or date range
- Private events or holidays alter standard visiting hours
- Partner needs bilingual (HR+EN) notice published on Dubrovnik Pass website
- test

## Typical resolution flow

1. Partner (Daniela or Ivana from Dubrovnik Pass Office) submits ticket with bilingual notice text (HR and EN)
2. Support agent (typically Luka) receives the ticket
3. Agent publishes the notice on the Dubrovnik Pass website
4. Agent confirms posting in a ticket comment
5. Occasionally partner follows up to correct dates or request removal/modification of the notice

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Partner submits bilingual notice text (HR+EN) with specific dates and opening hours | B2B partner (Dubrovnik Pass Office staff) | Support ticket system | 5 min |
| Agent posts the notice on the Dubrovnik Pass website | Support agent (Luka or other) | Dubrovnik Pass website CMS / API (Postman/JSON referenced in RAOS-3954) | 10 min |
| Agent confirms posting by commenting on the ticket | Support agent | Support ticket system | 2 min |
| Partner requests correction or removal of a previously posted notice | B2B partner | Support ticket system (follow-up comment) | 5 min |

## Evidence

Derived from 18 tickets in cluster `RAOS:b2b_partner|Support|duplikat:c0`. Direct quotes from 6 representative tickets:

- `RAOS-3191` _[hr]_: "ljubazno vas molim da na web stranicu Dubrovnik Pass-a postavite slijedeću obavijest , i to na HR I ENG. jeziku"
- `RAOS-3191` _[hr]_: "Obavijest postavljena. Hvala. Luka."
- `RAOS-4020` _[hr]_: "ljubazno molim izmjeniti obavijest na web-u"
- `RAOS-2997` _[hr]_: "Poštovani Luka, molim što prije maknuti obavijest an HR i ENG"
- `RAOS-3954` _[hr]_: "Ovdje ti je json datoteka za Visual Studio u kojoj samo dodaješ novije obavijesti, tako da imamo povijest starih."
- `RAOS-6783` _[hr]_: "Zamolio bih da ubuduće stavite i datum od kad do kad bi željeli da vam stoji obavijest na stranici kako bi mogli staviti točan datum trajanja obavijesti."

## Cluster statistics

- **Volume:** 18 tickets total (18 unique semantic events after dedup)
- **Frequency:** 0.88 tickets/month (over data window 2025-06-02 → 2026-04-08)
- **Median resolution:** 1.8 hours
- **Languages:** hr, en
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~3.9 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.2 (range [0.82, 1.52])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.75
- **Rationale:** A templated bilingual notice scaffold (auto-populated from structured intake fields: attraction name, dates, hours) would reduce copy-paste and formatting time for agents; the remaining work—navigating the CMS and confirming posting—still requires human action. A 30% time reduction is a conservative estimate for a structured but manual workflow.
- **Validation:** Deploy a shadow-mode template suggester for 3 weeks; compare average handle time before and after using ticket timestamps to validate the 30% reduction assumption.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~3.1 (range [2.2, 3.9])
- **Root cause:** No CMS self-service interface exists for B2B partners to publish their own temporary operating-hours notices; the gap is a missing product capability, not a bug.
- **Rationale:** A partner-facing CMS feature (bilingual notice form with publish/remove/schedule controls scoped to authorised B2B accounts) would let partners self-publish notices without agent involvement, eliminating the agent-posting and confirmation steps (~12 of 22 active minutes) and likely most ticket volume. Hours eliminated are capped at the 3.9-hour baseline.
- **Validation:** Engineering spikes a lightweight CMS role-permission prototype in Sprint 1; measure build effort against estimate before committing to full delivery.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.049, 0.091])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These are B2B partner action requests requiring agent-side website publishing, not informational questions; a self-service FAQ cannot substitute for the actual content-posting step that partners depend on support staff to execute. Deflection potential is negligible.
- **Validation:** Publish a help-center article explaining the notice-submission process and monitor whether ticket volume decreases over a 4-week window; expect near-zero deflection.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~0.8 (range [0.57, 1.05])
- **Narrow use case:** Automated publishing of bilingual operating-hours notices submitted via a structured intake form by verified B2B partners, limited to pre-approved attraction list.
- **Safety constraints:**
  - Partner identity must be verified before any web content is published
  - Published notices must be limited to pre-approved attraction list to avoid erroneous public-facing content
  - Automation must require exact bilingual text (HR+EN) provided by partner; no AI-generated translation without human review
  - Removal and correction requests must include a human confirmation step before going live
  - All auto-published notices must trigger an immediate email confirmation to the partner and a support-team audit log entry
- **Rationale:** Autonomous publishing is technically feasible for well-structured, low-ambiguity notice requests, but the small annual volume (10.5 tickets) and public-facing content risk justify limiting scope to 25% of tickets; corrections and removals should remain agent-supervised. Savings reflect eliminating agent posting and confirmation steps (~12 min) on the capped 25% volume.
- **Validation:** Pilot with 3-month supervised automation: automation drafts and queues the notice, agent approves with one click; graduate to full auto-publish only if zero erroneous postings occur over the pilot period.

### Risks

- **Compliance concerns:**
  - Published operating hours are public-facing tourist information; inaccurate notices could harm visitor experience and partner reputation
  - Bilingual accuracy (Croatian + English) must be maintained; automated or agent-assisted translation without review risks factual errors
  - Notices concern named public institutions (Museum of Modern Art Dubrovnik, Fortress Lovrjenac, Maritime Museum); incorrect information may have reputational or contractual implications for Dubrovnik Pass
- **Must not automate:**
  - Translation or language generation of notice content without human review
  - Correction or removal of already-published notices without agent or partner confirmation
  - Publishing requests from unverified or unauthenticated senders

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Admin/operator-only configuration change

