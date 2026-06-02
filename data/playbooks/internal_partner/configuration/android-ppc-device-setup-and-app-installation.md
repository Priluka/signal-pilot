---
id: android-ppc-device-setup-and-app-installation
name: android_ppc_device_setup_and_app_installation
title: Android PPC Device Setup, App Installation and Testing for Field Use
description: Internal partner tickets requesting configuration of Android PPC handheld devices, installation of RAO mobile
  applications (RAO.city, RAO.nkp, RAO.park), and execution of all required tests before deployment. Devices are typically
  new, returned from service/repair (e.g. Inf Kod), or require a hard reset and reconfiguration. Once configured and tested,
  devices are shipped by post back to the requesting location.
category: internal_partner/configuration
ticket_class: internal_partner
issue_category: configuration
resolution_pattern: configuration_change
languages:
- hr
country_focus:
- hr
- other
status: active
cluster_id: RAOS:internal_partner|Support|duplikat:c2
project_key: RAOS
cluster_size: 16
cluster_size_dedup: 16
sample_size_used: 16
extraction_schema: v1.0
extraction_confidence: 0.93
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.78
median_resolution_minutes: 59.0
p95_resolution_minutes: 8069.75
cannot_reproduce_rate: 0.0
data_window_start: '2025-03-31'
data_window_end: '2026-04-16'
annual_hours_saved: 0.2
roi:
  baseline_active_hours: 0.9
  baseline_active_source: 'fallback: 10% of wall-clock median (59 min)'
  baseline_is_fallback: true
  baseline_confidence_tier: directional
  deflection_hours_midpoint: 0.0
  deflection_hours_range:
  - 0.0
  - 0.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.2
  agent_assist_hours_range:
  - 0.1
  - 0.2
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.3
  product_fix_hours_range:
  - 0.2
  - 0.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.1
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-3219
- RAOS-3247
- RAOS-5026
- RAOS-2244
- RAOS-3213
- RAOS-3223
- RAOS-3803
- RAOS-5910
- RAOS-3048
- RAOS-6891
- RAOS-3225
- RAOS-4191
- RAOS-3250
- RAOS-6841
- RAOS-3201
- RAOS-3331
canonical_examples:
- RAOS-3219
- RAOS-5026
- RAOS-3213
vendor_dependency:
  vendor_name: Inf Kod / Infokod
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: reference_only
  claude_skill: reference_only
  agent_assist: false
  autonomous_resolve: false
  note: Admin/operator-only configuration change
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-acknowledge ticket receipt and send standardized shipping instructions to the requesting
    location
  autonomous_resolve_safety_constraints:
  - Physical device configuration and testing cannot be performed autonomously — requires trained technician on-site
  - Hardware fault diagnosis and repair/replacement decisions must remain human-reviewed
  - Vendor coordination with Inf Kod for repaired devices must not be automated without explicit approval workflow
  - Shipping and logistics actions (label generation, dispatch confirmation) require human sign-off before execution
  - No autonomous action should be taken on devices not yet physically received by the support team
related_playbooks:
- dubrovnik-pass-website-hours-notice-posting
- dubrovnik-pass-website-notice-management
- hr-b2b-case-status-and-data-correction
- hr-b2b-parking-price-change-request
- hr-b2b-photo-download-enablement
- hr-b2b-user-account-management
- hr-internal-partner-misc-support__0cfe1d
- hr-internal-partner-misc-support__a37936
- hr-parking-sms-payment-visibility-issue
- periodic-table-update-lpr-a1-ht
- sac-system-hr-polygon-ddpk-issues
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Android PPC Device Setup, App Installation and Testing for Field Use

## What this pattern is

Internal partner tickets requesting configuration of Android PPC handheld devices, installation of RAO mobile applications (RAO.city, RAO.nkp, RAO.park), and execution of all required tests before deployment. Devices are typically new, returned from service/repair (e.g. Inf Kod), or require a hard reset and reconfiguration. Once configured and tested, devices are shipped by post back to the requesting location.

## When this applies

- New Android PPC device delivered and needs to be set up for field use
- Device returned from external service/repair center (e.g. Inf Kod) requiring reconfiguration
- Device requires hard reset and reinstallation of RAO application
- New computer/workstation needs to be configured for web system access

## Typical resolution flow

1. Receive the device (new or returned from service) [PROOF-SENTINEL-1780428788]
2. Perform hard reset if required
3. Configure Android PPC device settings
4. Install the appropriate RAO application (RAO.city, RAO.nkp, or RAO.park)
5. Execute all functional tests to verify proper operation
6. Confirm device is ready for field use
7. Ship device back to the requesting location by post

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Configure Android PPC device and install RAO application | internal IT/support technician | Android PPC device, RAO.city/RAO.nkp/RAO.park application | — |
| Execute all functional tests on the configured device | internal IT/support technician | RAO mobile application | — |
| Ship configured device back to requesting location by post | internal IT/support technician | postal service | — |
| Diagnose hardware issue and recommend repair or replacement | internal IT/support technician | — | — |

## Vendor dependency

- **Vendor:** Inf Kod / Infokod

## Evidence

Derived from 16 tickets in cluster `RAOS:internal_partner|Support|duplikat:c2`. Direct quotes from 7 representative tickets:

- `RAOS-3219` _[hr]_: "Oprema je podešena i spremna za rad."
- `RAOS-5026` _[hr]_: "Uređaj je podešen i spreman za rad. Sutra ga se bude poslalo poštom nazad korisniku."
- `RAOS-3213` _[hr]_: "Uređaju je potrebno zamijeniti ekran jer ne radi dobro touch screen. Najbolje je kupiti novi uređaj jer je ovaj već dosta star."
- `RAOS-5026` _[hr]_: "Korisnik je poslao uređaj u kvaru na dijagnozu i reinstalaciju (ako nema fizičkih kvarova na njemu)."
- `RAOS-3201` _[hr]_: "Potrebno je napraviti hard reset uređaja, podesiti ga i pripremiti ga za rad."
- `RAOS-3201` _[hr]_: "Oprema podešena, testirana, spakirana i poslana poštom."
- `RAOS-5910` _[hr]_: "Računalo podešeno i spremno za rad."

## Cluster statistics

- **Volume:** 16 tickets total (16 unique semantic events after dedup)
- **Frequency:** 0.78 tickets/month (over data window 2025-03-31 → 2026-04-16)
- **Median resolution:** 59 min
- **Languages:** hr
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`directional`) ⚠️ fallback heuristic

- **Annual active work:** ~0.9 hours/year
- _Source:_ fallback: 10% of wall-clock median (59 min)
- _Note:_ Sloj 6 did not produce action durations for this cluster, so the baseline is a coarse approximation. Treat the ROI block below as **directional only**.

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.2 (range [0.13, 0.23])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.40
- **Rationale:** Agent assist can surface a pre-filled configuration checklist and shipping label template automatically when a new ticket matches this pattern, reducing lookup and documentation time. However, the dominant work is physical — assist tooling has limited leverage over hands-on device setup and testing steps.
- **Validation:** Run shadow-mode for 4 weeks where the assist tool surfaces the configuration checklist and shipping template on ticket creation; measure technician-reported time savings via post-ticket survey and compare ticket handle times before and after.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~0.3 (range [0.189, 0.351])
- **Root cause:** This is an operational hardware lifecycle process (new device provisioning, post-repair reconfiguration, field deployment), not a software defect. The need arises from physical device events — new purchases, returns from Inf Kod repair, hard resets — which are inherent to field device management.
- **Rationale:** An MDM (Mobile Device Management) solution or zero-touch enrollment profile for the RAO app suite could reduce manual configuration steps, but cannot eliminate shipping, physical inspection, or post-repair validation. Estimated 30% reduction in active configuration minutes is achievable if apps can be pushed remotely post-hardware readiness.
- **Validation:** Engineering team should prototype MDM-based app push for one RAO application on a test device batch and measure active technician minutes before and after; compare against current baseline of ~5.9 min/ticket active work.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0.03, 0.052])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These tickets require physical device handling, app installation, and functional testing by a trained technician — there is no self-service path a remote partner could follow to replace this work. A structured intake form could marginally reduce back-and-forth clarification, but cannot deflect the core work.
- **Validation:** Deploy a structured request form (device serial, reason for reconfiguration, return address) for 8 weeks and measure whether average clarification exchanges per ticket drop; track any tickets fully resolved without technician involvement.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.1 (range [0.035, 0.065])
- **Narrow use case:** Auto-acknowledge ticket receipt and send standardized shipping instructions to the requesting location
- **Safety constraints:**
  - Physical device configuration and testing cannot be performed autonomously — requires trained technician on-site
  - Hardware fault diagnosis and repair/replacement decisions must remain human-reviewed
  - Vendor coordination with Inf Kod for repaired devices must not be automated without explicit approval workflow
  - Shipping and logistics actions (label generation, dispatch confirmation) require human sign-off before execution
  - No autonomous action should be taken on devices not yet physically received by the support team
- **Rationale:** Autonomous resolution is essentially infeasible for this pattern because the work is inherently physical — configuration, testing, and shipping of hardware devices require in-person technician action. The only automatable slice is administrative acknowledgment and status communications, yielding negligible time savings.
- **Validation:** Pilot auto-acknowledgment and shipping instruction dispatch for 6 weeks on all new tickets in this cluster; measure whether it reduces technician time spent on initial communications, targeting ≥1 minute saved per ticket before expanding scope.

### Risks

- **Compliance concerns:**
  - Device configuration may involve access credentials or certificates for RAO applications — improper handling could create security exposure
  - Shipping physical devices via post introduces chain-of-custody risk; devices may contain sensitive configuration data if not wiped before transit
  - Repair vendor (Inf Kod) handling may expose device internals or stored data — data handling agreements should be verified
- **Must not automate:**
  - Hardware fault diagnosis and repair/replacement decisions
  - Functional testing and sign-off before field deployment
  - Physical device configuration and RAO application installation
  - Any action requiring the device to be physically present and verified by a technician
- **Vendor dependencies blocking automation:**
  - Inf Kod / Infokod repair turnaround time is not quantified (typical_wait_days: null), creating unpredictable ticket duration that automation cannot account for
  - MDM or zero-touch enrollment feasibility depends on whether RAO application vendors (RAO.city, RAO.nkp, RAO.park) support enterprise MDM deployment profiles

## Agent compatibility

- **Status:** `active` (extraction confidence 0.93)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Admin/operator-only configuration change

