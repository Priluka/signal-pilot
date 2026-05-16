---
id: kml-polygon-upload-correction-hr
name: kml_polygon_upload_correction_hr
title: KML Polygon Upload and Correction Requests for Scan-a-Car Working Streets (Croatia)
description: B2B partners (primarily from Croatian parking/enforcement operations) regularly submit KML polygon files for
  parking enforcement zones (sectors and streets) to be loaded or corrected in the scan-a-car system. Tickets cover both first-time
  uploads of new streets and corrections/replacements of previously loaded polygons. Resolution requires internal processing
  plus a final insert step handled by a Dutch (Netherlands-based) vendor team.
category: b2b_operator/configuration
ticket_class: b2b_partner
issue_category: configuration
resolution_pattern: vendor_escalation
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:b2b_partner|Support|no_label:c0
project_key: RAOS
cluster_size: 41
cluster_size_dedup: 41
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.0
median_resolution_minutes: 8260.0
p95_resolution_minutes: 60060.0
cannot_reproduce_rate: 0.0
data_window_start: '2024-10-08'
data_window_end: '2026-04-28'
annual_hours_saved: 6.4
roi:
  baseline_active_hours: 32.0
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 2.6
  deflection_hours_range:
  - 1.8
  - 3.2
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 6.4
  agent_assist_hours_range:
  - 4.5
  - 8.3
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 14.0
  product_fix_hours_range:
  - 10.0
  - 18.0
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 1.6
  autonomous_resolve_hours_range:
  - 1.1
  - 2.1
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-1383
- RAOS-2175
- RAOS-5470
- RAOS-370
- RAOS-1373
- RAOS-3062
- RAOS-3998
- RAOS-1746
- RAOS-2420
- RAOS-7045
- RAOS-2138
- RAOS-6579
- RAOS-2976
- RAOS-1601
- RAOS-1703
- RAOS-2021
- RAOS-1563
- RAOS-2255
canonical_examples:
- RAOS-1383
- RAOS-2175
- RAOS-5470
vendor_dependency:
  vendor_name: Scan-a-Car (Netherlands/Dutch team)
  involves_vendor: true
  typical_wait_days: 2
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-acknowledge receipt and validate KML file format/schema on inbound submission,
    routing to the correct internal agent queue without human triage.
  autonomous_resolve_safety_constraints:
  - Final polygon insert must always be performed by the Dutch vendor team — no autonomous system may bypass this step.
  - Any polygon modification affects live parking enforcement zones; erroneous data could result in illegal enforcement actions.
  - B2B partner identity and file authenticity must be verified before any automated processing.
  - Autonomous actions limited to acknowledgement and format validation only — no system changes to live geographic data.
related_playbooks:
- dubrovnik-pass-website-hours-notice-posting
- dubrovnik-pass-website-notice-management
- hr-b2b-case-status-and-data-correction
- hr-b2b-monthly-invoice-generation-and-fiscalization
- hr-b2b-parking-operations-support
- hr-b2b-parking-price-change-request
- hr-b2b-photo-download-enablement
- hr-b2b-sms-parking-and-ddpk-issues
- hr-b2b-user-account-management
- hr-sms-parking-payment-issues
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# KML Polygon Upload and Correction Requests for Scan-a-Car Working Streets (Croatia)

## What this pattern is

B2B partners (primarily from Croatian parking/enforcement operations) regularly submit KML polygon files for parking enforcement zones (sectors and streets) to be loaded or corrected in the scan-a-car system. Tickets cover both first-time uploads of new streets and corrections/replacements of previously loaded polygons. Resolution requires internal processing plus a final insert step handled by a Dutch (Netherlands-based) vendor team.

## When this applies

- B2B partner submits new KML polygon files for streets not yet in the system
- B2B partner submits corrected KML polygon files to replace previously uploaded (incorrect or inactive) polygons
- Scan-a-car observations are not being recorded for certain streets, prompting polygon investigation
- New working streets are added to parking zones requiring polygon upload

## Typical resolution flow

1. B2B partner creates ticket with list of sectors and street names plus attached KML/KMZ file(s)
2. Internal support agent reviews the request and assigns/prepares polygons
3. Internal agent loads/replaces polygons in the system (old polygons with same ID deleted if correction)
4. For new streets, agent waits for Dutch vendor (Netherlands team) to perform final/concluding insert
5. Ticket is confirmed resolved and closed after all uploads are confirmed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Submit KML/KMZ polygon files for new or corrected streets by sector | B2B partner | Jira ticket with file attachment | 15 min |
| Review request, prepare and upload/replace polygons in the system | Internal support agent (e.g. Luka, Gabrijel) | Internal polygon management system | 60 min |
| Perform final/concluding insert for new street polygons | Dutch vendor team (Netherlands) | Vendor backend system | — |
| Confirm completion and close the ticket | Internal support agent | Jira | 5 min |

## Vendor dependency

- **Vendor:** Scan-a-Car (Netherlands/Dutch team)
- **Typical wait:** 2 day(s)

## Evidence

Derived from 41 tickets in cluster `RAOS:b2b_partner|Support|no_label:c0`. Direct quotes from 6 representative tickets:

- `RAOS-1383` _[hr]_: "dostavljam ispravljene KML poligone za radne ulice zone I po sektorima"
- `RAOS-2175` _[hr]_: "čekamo upload od strane Nizozemaca"
- `RAOS-5470` _[hr]_: "Sve je odrađeno, novo stanje poligona po ulcama je napravljeno prema onome što ste dostavili. Također, čekamo da i kolege iz Nizozemske naprave zaključni insert."
- `RAOS-1746` _[hr]_: "Poligoni u kojima nisu kreirani opažaji korigirani, Bauerova korigirana, G.Bulata će biti vidljiva u narednih dan-dva dok je unesu kolege iz Nizozemske jer se prvi put unosi."
- `RAOS-6579` _[hr]_: "Učitano sve osim Fonove i Sprečke, kad riješimo to, poslati spaces Nizozemcima"
- `RAOS-2175` _[hr]_: "Dostavljam KML poligone za nove radne ulice, koji do sada nisu učitavani u sustav."

## Cluster statistics

- **Volume:** 41 tickets total (41 unique semantic events after dedup)
- **Frequency:** 2.0 tickets/month (over data window 2024-10-08 → 2026-04-28)
- **Median resolution:** 5.7 days
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~32 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~6.4 (range [4.5, 8.3])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.65
- **Rationale:** Agent assist tooling (e.g. pre-populated escalation templates, automated KML validation checks, and structured vendor handoff messages) could reduce the ~60-minute preparation step and the ~5-minute close step, but the core polygon review and upload work is domain-specific and unlikely to be fully assisted.
- **Validation:** Run a 4-week shadow-mode pilot with an auto-drafted vendor escalation email and KML validation pre-check; measure actual time-on-ticket before and after using ticket timestamps.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~8 (range [6, 10])
- **Hours eliminated per year:** ~14 (range [10, 18])
- **Root cause:** This is a workflow gap rather than a bug: there is no self-service portal allowing B2B partners to submit and manage KML polygon files directly, and the final insert step is gated on a third-party vendor (Dutch team), making the process inherently manual and multi-party.
- **Rationale:** Building a B2B self-service portal for KML upload and polygon management would eliminate the internal preparation step (~60 min/ticket), but the vendor's final insert step would remain a dependency unless the API is also opened. Savings are therefore partial and capped at the internal agent portion.
- **Validation:** Engineering team should spike on the Scan-a-Car vendor API capabilities to determine if automated insert is feasible; effort estimate should be revised after vendor API assessment.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~2.6 (range [1.792, 3.2])
- **Form:** `in_app_help`
- **Deflection rate:** ~8% (range [6%, 10%])
- **Feasibility:** 0.35
- **Rationale:** These are operational B2B configuration requests requiring actual file uploads and vendor action — there is no self-service resolution path. A structured submission form or checklist could marginally reduce incomplete submissions and back-and-forth, but cannot deflect the core need.
- **Validation:** Deploy a guided KML submission form for 8 weeks and measure whether re-submission or clarification round-trips decrease; track whether ticket volume changes.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~1.6 (range [1.12, 2.08])
- **Narrow use case:** Auto-acknowledge receipt and validate KML file format/schema on inbound submission, routing to the correct internal agent queue without human triage.
- **Safety constraints:**
  - Final polygon insert must always be performed by the Dutch vendor team — no autonomous system may bypass this step.
  - Any polygon modification affects live parking enforcement zones; erroneous data could result in illegal enforcement actions.
  - B2B partner identity and file authenticity must be verified before any automated processing.
  - Autonomous actions limited to acknowledgement and format validation only — no system changes to live geographic data.
- **Rationale:** Full autonomous resolution is not feasible given the mandatory vendor insert step and the safety-critical nature of enforcement zone data. Limited automation of intake acknowledgement and KML schema validation could save a small fraction of agent time but cannot close tickets end-to-end.
- **Validation:** Pilot an automated KML format validator on 10% of inbound tickets for 6 weeks; measure false-positive rate on file rejection and agent override frequency as acceptance criteria.

### Risks

- **Compliance concerns:**
  - KML polygon data defines legal parking enforcement boundaries; incorrect zones may expose the B2B partner or operator to legal liability for wrongful enforcement.
  - Any automated processing of geospatial enforcement data should be reviewed against Croatian traffic and parking regulations.
  - Data integrity must be maintained across file versions — overwriting a correct polygon with a corrupt one could cause undetected enforcement errors.
- **Must not automate:**
  - Final insert of polygon data into the live Scan-a-Car system — this must remain with the Dutch vendor team.
  - Approval or rejection of polygon corrections without human review, given enforcement zone implications.
  - Any modification of live geographic enforcement zone data without explicit B2B partner confirmation and internal agent sign-off.
- **Vendor dependencies blocking automation:**
  - Scan-a-Car (Netherlands) holds exclusive control over the final insert step; any meaningful end-to-end automation requires vendor API access or workflow integration that has not been established.
  - Typical 2-day vendor wait time dominates wall-clock resolution time (median 8260 min) and cannot be reduced without direct vendor SLA negotiation or API automation.
  - Vendor team capacity and availability is outside internal control; automation savings estimates assume vendor turnaround remains constant.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

