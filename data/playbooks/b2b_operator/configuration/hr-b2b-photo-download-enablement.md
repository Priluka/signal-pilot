---
id: hr-b2b-photo-download-enablement
name: hr_b2b_photo_download_enablement
title: B2B partner requests enablement of photo download for new client series
description: 'A recurring pattern where a B2B partner (predominantly user ''Marija'') submits tickets requesting that photo
  downloads be enabled for specific clients and series numbers. In the vast majority of cases, the resolution is straightforward:
  support generates the images and notifies the partner they are ready for download. Occasional edge cases involve series
  that failed to generate, requiring escalation to the development team.'
category: b2b_operator/configuration
ticket_class: b2b_partner
issue_category: configuration
resolution_pattern: configuration_change
languages:
- hr
country_focus:
- hr
- other
status: active
cluster_id: RAOS:b2b_partner|Support|duplikat:c4
project_key: RAOS
cluster_size: 28
cluster_size_dedup: 28
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.37
median_resolution_minutes: 110.0
p95_resolution_minutes: 5335.2
cannot_reproduce_rate: 0.0
data_window_start: '2025-03-24'
data_window_end: '2026-03-04'
annual_hours_saved: 1.7
roi:
  baseline_active_hours: 8.7
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.9
  deflection_hours_range:
  - 0.6
  - 1.2
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.7
  agent_assist_hours_range:
  - 1.2
  - 2.2
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 6.5
  product_fix_hours_range:
  - 4.6
  - 8.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 1.8
  autonomous_resolve_hours_range:
  - 1.3
  - 2.3
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-4784
- RAOS-4914
- RAOS-4829
- RAOS-2229
- RAOS-2910
- RAOS-3686
- RAOS-4482
- RAOS-3593
- RAOS-6362
- RAOS-4672
- RAOS-3312
- RAOS-4443
- RAOS-4459
- RAOS-4538
- RAOS-4657
- RAOS-4618
- RAOS-3233
- RAOS-4572
canonical_examples:
- RAOS-4784
- RAOS-2229
- RAOS-4829
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
  autonomous_resolve_narrow_use_case: Auto-trigger image generation and partner notification when an authenticated B2B partner
    submits a well-formed request for a known client series with no prior generation failures.
  autonomous_resolve_safety_constraints:
  - Must validate that the client and series ID are recognized and active before triggering generation
  - Must exclude any series with a prior failed-generation flag, routing those to a human agent
  - Must send a human-reviewable audit log entry for every autonomous action taken
  - Must not expose image assets to unintended parties; confirm partner authorization before notification
  - Must cap at 25% of annual volume until false-positive rate is confirmed below 5% in pilot
related_playbooks:
- android-ppc-device-setup-and-app-installation
- dubrovnik-pass-website-hours-notice-posting
- dubrovnik-pass-website-notice-management
- hr-b2b-case-status-and-data-correction
- hr-b2b-monthly-invoice-generation-and-fiscalization
- hr-b2b-parking-operations-support
- hr-b2b-parking-price-change-request
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

# B2B partner requests enablement of photo download for new client series

## What this pattern is

A recurring pattern where a B2B partner (predominantly user 'Marija') submits tickets requesting that photo downloads be enabled for specific clients and series numbers. In the vast majority of cases, the resolution is straightforward: support generates the images and notifies the partner they are ready for download. Occasional edge cases involve series that failed to generate, requiring escalation to the development team.

## When this applies

- A new series is created for a B2B client and photos are not automatically available for download
- Partner receives notification that a client has created a new series
- Partner attempts to download photos or tables and encounters an error or finds them unavailable

## Typical resolution flow

1. B2B partner submits ticket specifying client name and series number(s) requesting photo download access
2. Support agent triggers image generation for the specified series
3. Support agent notifies partner that images are generated and available for download
4. Partner confirms successful download (or reports residual issues for specific series)

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Submit ticket requesting photo download enablement for specific client and series | b2b_partner | RAO Support ticketing system | 5 min |
| Generate images/photos for the specified client series | support_agent | Internal image generation system | 15 min |
| Notify partner that images are ready for download | support_agent | RAO Support ticketing system | 2 min |
| Escalate failed series generation to development team | support_agent | Internal task/dev escalation system | 10 min |

## Evidence

Derived from 28 tickets in cluster `RAOS:b2b_partner|Support|duplikat:c4`. Direct quotes from 6 representative tickets:

- `RAOS-4784` _[hr]_: "molim da nam omogućite preuzimanje fotografija za seriju broj 117, klijent ROGOZNICA"
- `RAOS-2229` _[hr]_: "Poštovani, slike su generirane te ih možete preuzeti"
- `RAOS-4829` _[hr]_: "nažalost ta serija se nije generirala iz nekog razloga ostale sam uspjela generirat ali na navedenoj seriji je neki prblem tako da otvaram task odjelu za razvoj da oni interventno generiraju seriju"
- `RAOS-4657` _[hr]_: "da li je nužno da prilikom preuzimanja podataka za svakog klijenta otvaramo ticket da se omogući preuzimanje fotografija ili je moguće da to uvijek bude omogućeno?"
- `RAOS-4657` _[hr]_: "Vi svaki put kada zaprimite mail da je korisnik kreirao seriju probajte preuzeti slike jel moguće da se više greška neće pojavljivati pa ukoliko dođe do greške onda nam se javite"
- `RAOS-4538` _[hr]_: "Čiovo nije naš grad i tu Vam nažalost ne možemo pomoći"

## Cluster statistics

- **Volume:** 28 tickets total (28 unique semantic events after dedup)
- **Frequency:** 1.37 tickets/month (over data window 2025-03-24 → 2026-03-04)
- **Median resolution:** 1.8 hours
- **Languages:** hr
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~8.7 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.7 (range [1.2, 2.21])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.75
- **Rationale:** The resolution steps are highly templated (generate images, send notification), making agent-assist tooling—such as a one-click macro that triggers the generation job and pre-populates the notification reply—straightforward to implement and likely to shave the 2-minute notification step and reduce error in the 15-minute generation step.
- **Validation:** Run a 2-week shadow-mode pilot where the assist macro is surfaced to agents on every ticket matching this pattern; measure actual time-to-resolve versus the 32-minute baseline.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~6.5 (range [4.6, 8.45])
- **Root cause:** Photo download enablement for new client series is a deliberate manual workflow, not a bug; the gap is the absence of a self-service or automated provisioning mechanism for B2B partners to trigger image generation directly.
- **Rationale:** Building a B2B partner self-service portal or API endpoint that triggers image generation and notifies the partner would eliminate the majority of support-agent active work for the standard (non-failed) cases. Edge cases involving failed series generation would still require escalation and could not be fully eliminated.
- **Validation:** Engineering team should spike the image-generation API surface area and confirm whether the generation job can be safely exposed to a permissioned partner role; estimate effort after a half-sprint discovery.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.9 (range [0.63, 1.17])
- **Form:** `in_app_help`
- **Deflection rate:** ~10% (range [7%, 13%])
- **Feasibility:** 0.35
- **Rationale:** This pattern is driven by a single named B2B partner triggering a backend action (image generation) that requires internal tooling access; FAQ or self-service content cannot replace that action, so deflection potential is very low. A structured intake form could save the partner's 5-minute submission step but cannot eliminate support-agent effort.
- **Validation:** Deploy a structured in-app request form for Marija's account for 4 weeks and compare ticket volume and resolution time against the prior 4-week baseline.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~1.8 (range [1.3, 2.34])
- **Narrow use case:** Auto-trigger image generation and partner notification when an authenticated B2B partner submits a well-formed request for a known client series with no prior generation failures.
- **Safety constraints:**
  - Must validate that the client and series ID are recognized and active before triggering generation
  - Must exclude any series with a prior failed-generation flag, routing those to a human agent
  - Must send a human-reviewable audit log entry for every autonomous action taken
  - Must not expose image assets to unintended parties; confirm partner authorization before notification
  - Must cap at 25% of annual volume until false-positive rate is confirmed below 5% in pilot
- **Rationale:** The standard (non-failed) case is highly deterministic and confined to a single partner, making narrow autonomous resolution plausible; however, the 25% volume cap reflects uncertainty about edge-case detection reliability until a pilot establishes a safety record.
- **Validation:** Run a 6-week pilot with autonomous resolution enabled for the clean-path case only; accept the automation as safe if zero mis-routed failed-series tickets and fewer than 5% partner-reported errors occur during the pilot window.

### Risks

- **Compliance concerns:**
  - Image assets generated for specific clients may contain sensitive or proprietary content; access controls must ensure only the requesting authorized partner can download them
  - Audit trail of who triggered image generation and when should be retained to support any future data-access disputes
- **Must not automate:**
  - Escalation of failed series generation to the development team — these require human triage and should never be autonomously closed or silently dropped
  - Any request where the client ID or series number cannot be positively matched to an active, authorized record

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Admin/operator-only configuration change

