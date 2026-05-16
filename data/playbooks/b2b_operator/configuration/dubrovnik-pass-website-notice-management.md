---
id: dubrovnik-pass-website-notice-management
name: dubrovnik_pass_website_notice_management
title: Dubrovnik Pass B2B Partners Requesting Website Notice/Content Updates
description: B2B partner staff (primarily Dubrovnik Pass Office and related city institutions) submit tickets requesting that
  support agents post, update, or remove bilingual (HR/EN) notices on the Dubrovnik Pass website. Notices typically cover
  temporary changes to opening hours, closures, or other operational updates for attractions such as Museum of Modern Art
  Dubrovnik, City Walls, Lokrum Island, Lovrjenac Fortress, and House of Marin Držić. A secondary sub-pattern involves system
  configuration issues in the parking permit (PPK) and Bmove app domain, where business rules around purchase limits or zone
  validity are incorrectly applied.
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
cluster_id: RAOS:b2b_partner|Support|no_label:c2
project_key: RAOS
cluster_size: 51
cluster_size_dedup: 51
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.82
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.49
median_resolution_minutes: 270.0
p95_resolution_minutes: 17128.5
cannot_reproduce_rate: 0.0
data_window_start: '2024-09-16'
data_window_end: '2026-04-23'
annual_hours_saved: 6.5
roi:
  baseline_active_hours: 32.4
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 1.6
  deflection_hours_range:
  - 1.1
  - 2.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 6.5
  agent_assist_hours_range:
  - 4.5
  - 8.4
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 18.2
  product_fix_hours_range:
  - 12.8
  - 23.7
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 4.1
  autonomous_resolve_hours_range:
  - 2.9
  - 5.3
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-116
- RAOS-4066
- RAOS-4454
- RAOS-199
- RAOS-1148
- RAOS-1920
- RAOS-3411
- RAOS-6989
- RAOS-144
- RAOS-6974
- RAOS-1859
- RAOS-4151
- RAOS-366
- RAOS-4463
- RAOS-573
- RAOS-2499
- RAOS-243
- RAOS-2549
canonical_examples:
- RAOS-116
- RAOS-144
- RAOS-1148
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
  autonomous_resolve_narrow_use_case: Automated posting/removal of partner-submitted bilingual notices to the website when
    submitted via a structured, validated intake form with explicit approval from an authorised B2B partner contact
  autonomous_resolve_safety_constraints:
  - Must require verified authorisation from a whitelisted B2B partner contact before any website content is published or
    removed
  - All automated notice actions must be logged and immediately reviewable by a human agent
  - System configuration changes (PPK/Bmove) must not be automated without a developer review step — excluded from autonomous
    scope
  - Payment discrepancy investigations (action 4) must remain fully human-handled
  - Bilingual content must pass a format/language validation check before publication to prevent garbled or incomplete notices
related_playbooks:
- android-ppc-device-setup-and-app-installation
- dubrovnik-pass-website-hours-notice-posting
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

# Dubrovnik Pass B2B Partners Requesting Website Notice/Content Updates

## What this pattern is

B2B partner staff (primarily Dubrovnik Pass Office and related city institutions) submit tickets requesting that support agents post, update, or remove bilingual (HR/EN) notices on the Dubrovnik Pass website. Notices typically cover temporary changes to opening hours, closures, or other operational updates for attractions such as Museum of Modern Art Dubrovnik, City Walls, Lokrum Island, Lovrjenac Fortress, and House of Marin Držić. A secondary sub-pattern involves system configuration issues in the parking permit (PPK) and Bmove app domain, where business rules around purchase limits or zone validity are incorrectly applied.

## When this applies

- A partner institution has a temporary change in opening hours for an attraction covered by Dubrovnik Pass
- An attraction will be closed or have modified access on a specific date
- A previously posted notice needs to be removed or replaced
- A system bug allows incorrect PPK/parking permit purchase behaviour (e.g. duplicate permits, wrong zone validation)
- A Bmove app payment is charged but the ticket is not confirmed in the system

## Typical resolution flow

1. Partner submits ticket with exact notice text in both Croatian (HR) and English (EN)
2. Support agent posts the notice on the Dubrovnik Pass website
3. Support agent notifies partner to verify the posted notice
4. Partner confirms the notice is correct, or requests corrections
5. If removal is requested, agent removes the notice and confirms via ticket comment

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Post bilingual notice on Dubrovnik Pass website homepage/notices section | support agent | Dubrovnik Pass web CMS | 10 min |
| Remove an existing notice from the website upon partner request | support agent | Dubrovnik Pass web CMS | 5 min |
| Correct a system configuration for PPK purchase limits or zone validity | support agent / developer | ParkIS / back-end configuration | 30 min |
| Investigate Bmove payment discrepancy and advise partner/customer on refund or card status | support agent | Bmove / ParkIS | 20 min |

## Evidence

Derived from 51 tickets in cluster `RAOS:b2b_partner|Support|no_label:c2`. Direct quotes from 6 representative tickets:

- `RAOS-116` _[hr]_: "ljubazno molim da postavite obavijest na naslovnoj stranici web-a kako slijedi"
- `RAOS-144` _[hr]_: "ljubazno molim da uklonite obavijest o radnom vremenu Arheoloških izložbi HR/EN verzija"
- `RAOS-1148` _[hr]_: "Navedena obavijest je postavljena. Hvala."
- `RAOS-2549` _[hr]_: "opet je omogućena kupnja dvije ppk istoj fizičkoj osobi putem Bmove app. Molio bih vas da onemogućite ovu kupnju."
- `RAOS-4463` _[hr]_: "U 1. zoni kontrolorima se na terminalu prikazuje da je za automobil plaćena PPK iako smo 2024. godine novom Odlukom ukinuli PPK za uposlene u 1. zoni."
- `RAOS-1859` _[hr]_: "karta je kupljena putem Bmove aplikacije ali preko QR koda sa lokacije. Nažalost prodajni distibuter je naplati korisniku ali mi nismo zaprimili potvrdu o plaćanju tako da karta nije ni potvrđena kod "

## Cluster statistics

- **Volume:** 51 tickets total (51 unique semantic events after dedup)
- **Frequency:** 2.49 tickets/month (over data window 2024-09-16 → 2026-04-23)
- **Median resolution:** 4.5 hours
- **Languages:** hr, en
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~32.4 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~6.5 (range [4.55, 8.4])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.65
- **Rationale:** Pre-filled templates for the bilingual notice posts (HR/EN), and guided checklists for PPK configuration changes, could reduce the lookup and formatting time for agents even before a full product fix is available. Savings are moderate because the work is already procedural and not highly variable.
- **Validation:** Run a 3-week shadow-mode pilot in which the assist tool drafts bilingual notice templates and configuration-change checklists; compare active minutes per ticket before and after agent adoption.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~18.2 (range [12.8, 23.66])
- **Root cause:** Two distinct root causes exist: (1) no self-service CMS capability for B2B partner staff to post/update/remove bilingual notices without routing through support agents; (2) misconfigured business rules in the PPK/Bmove system governing purchase limits and zone validity, which should be correctible via an admin configuration interface rather than requiring developer intervention.
- **Rationale:** A lightweight partner-facing CMS for notices (actions 1 & 2, ~15 min/ticket, ~70% of tickets by volume) plus an admin UI for PPK/Bmove rule configuration (action 3, ~30 min/ticket) would eliminate the largest share of active hours; residual investigation work (action 4) would remain. Hours eliminated are capped at baseline (32.4 h).
- **Validation:** Engineering team should spike CMS and admin-UI requirements for 2–3 days, produce a story-point estimate, and confirm feasibility against existing Dubrovnik Pass website architecture before committing sprint allocation.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1.6 (range [1.12, 2.08])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.15
- **Rationale:** These are B2B partner-initiated operational requests requiring an agent to take action on the website or system; they are not informational queries that a FAQ or help-center article can resolve without human intervention. A structured intake form could marginally reduce back-and-forth but cannot deflect the underlying work.
- **Validation:** Deploy a structured intake web form for partners over 4 weeks, measure whether any requests are fully resolved without agent involvement, and track average active minutes per ticket.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~4.1 (range [2.87, 5.3])
- **Narrow use case:** Automated posting/removal of partner-submitted bilingual notices to the website when submitted via a structured, validated intake form with explicit approval from an authorised B2B partner contact
- **Safety constraints:**
  - Must require verified authorisation from a whitelisted B2B partner contact before any website content is published or removed
  - All automated notice actions must be logged and immediately reviewable by a human agent
  - System configuration changes (PPK/Bmove) must not be automated without a developer review step — excluded from autonomous scope
  - Payment discrepancy investigations (action 4) must remain fully human-handled
  - Bilingual content must pass a format/language validation check before publication to prevent garbled or incomplete notices
- **Rationale:** Up to 25% of tickets (primarily straightforward notice-posting and removal requests) could be handled autonomously once a validated intake form and authorisation workflow exist, but the configuration and payment sub-patterns require human judgment and must remain out of scope. Savings are modest because the notice actions are already short (~5–10 min each).
- **Validation:** Pilot with a single partner institution (e.g. Museum of Modern Art Dubrovnik) over 6 weeks using a structured intake form with a human-review step before each publish action; acceptance criterion is zero unauthorised or malformed content appearing on the live site.

### Risks

- **Compliance concerns:**
  - Published notices represent official operational communications for publicly visited cultural sites; errors or unauthorised changes could mislead visitors and create liability for the City of Dubrovnik or pass operators
  - Bilingual (HR/EN) content accuracy is a legal/cultural obligation; automated publication without language validation could result in non-compliant or misleading notices
- **Must not automate:**
  - PPK purchase-limit and zone-validity configuration changes — incorrect settings can affect revenue, access rights, and downstream payment integrity
  - Bmove payment discrepancy investigation and refund advice — requires human judgment on financial and card-status data
  - Any notice publication without explicit, verified authorisation from a whitelisted B2B partner contact

## Agent compatibility

- **Status:** `active` (extraction confidence 0.82)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Admin/operator-only configuration change

