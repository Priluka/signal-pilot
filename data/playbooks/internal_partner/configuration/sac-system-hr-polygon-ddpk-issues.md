---
id: sac-system-hr-polygon-ddpk-issues
name: sac_system_hr_polygon_ddpk_issues
title: 'SAC System Issues in Croatia: Polygon Configuration and DDPK Operational Problems'
description: Internal partners (parking operators) in Croatia report recurring issues with the SAC (ScanA Car) automated parking
  enforcement system, primarily involving incorrect or missing KML polygon configurations for parking zones across multiple
  cities (Zagreb, Zadar, Šibenik, Varaždin, Rijeka, Opatija). A secondary cluster involves DDPK (daily parking ticket) issuance
  anomalies such as missing photos at issuance time, duplicate tickets, and tickets issued outside working hours. Resolution
  typically requires development team involvement for polygon insertion/correction and configuration changes.
category: internal_partner/configuration
ticket_class: internal_partner
issue_category: configuration
resolution_pattern: product_fix_required
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:internal_partner|Support|no_label:c0
project_key: RAOS
cluster_size: 27
cluster_size_dedup: 27
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.92
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.32
median_resolution_minutes: 4348.0
p95_resolution_minutes: 218131.75
cannot_reproduce_rate: 0.0
data_window_start: '2024-10-15'
data_window_end: '2026-03-30'
annual_hours_saved: 3.3
roi:
  baseline_active_hours: 18.4
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.9
  deflection_hours_range:
  - 0.6
  - 1.2
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 3.3
  agent_assist_hours_range:
  - 2.4
  - 4.2
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 14.0
  product_fix_hours_range:
  - 10.5
  - 18.2
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.3
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-3499
- RAOS-1260
- RAOS-2316
- RAOS-1143
- RAOS-1551
- RAOS-3076
- RAOS-3659
- RAOS-4198
- RAOS-834
- RAOS-2927
- RAOS-4903
- RAOS-1953
- RAOS-1079
- RAOS-2933
- RAOS-4468
- RAOS-2081
- RAOS-810
- RAOS-4480
canonical_examples:
- RAOS-1260
- RAOS-2316
- RAOS-1953
vendor_dependency:
  vendor_name: GDI (polygon export provider) / internal development team
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: reference_only
  claude_skill: reference_only
  agent_assist: false
  autonomous_resolve: false
  note: Engineering backlog — not for runtime agents
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Automated acknowledgement and triage routing of new polygon/DDPK tickets to the correct
    developer queue with pre-filled diagnostic context
  autonomous_resolve_safety_constraints:
  - No autonomous polygon insertion or deletion into ParkIS without developer review; incorrect polygons directly cause wrongful
    parking enforcement
  - No autonomous closure or resolution of DDPK anomaly tickets; duplicate or out-of-hours tickets may have legal/regulatory
    implications in Croatian parking enforcement
  - GDI polygon data must be validated against ParkIS schema before any automated action
  - All autonomous routing actions must be logged and reversible by a human operator
  - Operator field verification step must remain human-gated before any polygon change is considered resolved
related_playbooks:
- android-ppc-device-setup-and-app-installation
- hr-internal-partner-misc-support__0cfe1d
- hr-internal-partner-misc-support__a37936
- hr-parking-sms-payment-visibility-issue
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# SAC System Issues in Croatia: Polygon Configuration and DDPK Operational Problems

## What this pattern is

Internal partners (parking operators) in Croatia report recurring issues with the SAC (ScanA Car) automated parking enforcement system, primarily involving incorrect or missing KML polygon configurations for parking zones across multiple cities (Zagreb, Zadar, Šibenik, Varaždin, Rijeka, Opatija). A secondary cluster involves DDPK (daily parking ticket) issuance anomalies such as missing photos at issuance time, duplicate tickets, and tickets issued outside working hours. Resolution typically requires development team involvement for polygon insertion/correction and configuration changes.

## When this applies

- SAC vehicle scanning incorrect parking zones due to polygon boundary errors (e.g., capturing disabled parking spaces or private areas)
- SAC issuing DDPK without corresponding issuance-time photographs (only observation-time photos present)
- SAC issuing duplicate DDPKs for the same vehicle at the same time
- SAC issuing DDPK outside the zone's operational hours
- New streets or zone changes requiring polygon creation, update, or deactivation in ParkIS
- Mismatch between manually counted vehicles and SAC observations recorded in ParkIS
- Camera or connectivity problems with SAC vehicles in specific cities

## Typical resolution flow

1. Internal partner identifies SAC polygon or DDPK issue in the field or system
2. Partner opens ticket with description and, where applicable, KML/KMZ files or evidence
3. Customer support team assesses if resolvable at support level or escalates to development
4. If polygon issue: support or GDI team provides corrected KMZ files; old polygons deactivated and new ones inserted
5. If DDPK/system issue: development team investigates configuration or software bug
6. Fix deployed to production; partner notified to verify in field
7. Ticket closed with confirmation or follow-up if issue persists

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Escalate ticket to development team when not resolvable at support level | Support agent | Jira (RAO Support) | 10 min |
| Deactivate old KMZ polygon and insert corrected/new polygon into ParkIS | Developer / support engineer (Herc) | ParkIS / AWS S3 | 60 min |
| Investigate and fix DDPK configuration (photo timing, duplicate issuance, out-of-hours issuance) | Developer (Luka) | ParkIS backend / production deployment | — |
| Request GDI export of updated street polygons for affected streets | Support agent or internal partner | GDI system | — |
| Field verification of SAC scanning accuracy after polygon update | Internal partner (field operator) | SAC vehicle / tablet | — |

## Vendor dependency

- **Vendor:** GDI (polygon export provider) / internal development team

## Evidence

Derived from 27 tickets in cluster `RAOS:internal_partner|Support|no_label:c0`. Direct quotes from 7 representative tickets:

- `RAOS-1260` _[hr]_: "dostavljam ponovno ispravljene KML poligone za radne ulice u sektorima 15 i 16. Iste su ispravljene 20.12.2024, ali se još na nekim mjestima javljaju greške."
- `RAOS-2316` _[hr]_: "imali smo upravo slučaj gdje je korisniku ispisana dnevna parkirna karta u 12:15 h od strane SAC-a, a na fotografijama u sustavu ne postoji ni jedna fotografija s vremenom ispisivanja dnevne karte"
- `RAOS-1953` _[hr]_: "primjetili smo da SAC ponekad izdaje dvije DPK u isto vrijeme za isto vozilo, na jednoj DPK nema fotografije pa je izdana druga DPK na kojoj su vidljive fotografije."
- `RAOS-3076` _[hr]_: "u zoni 3 ispisana je dnevna parkirna karta od strane SAC-a nakon 15:00 h. Radno vrijeme zone 3 je do 15:00 h, molio bih provjeru."
- `RAOS-4198` _[hr]_: "U solarisu još uvik slabo čita aute, samo 2 je zapisalo od 10"
- `RAOS-810` _[hr]_: "ScanA Car i dalje očitava poligone po ulicama po starom režimu čime brišu opažaje kontrolora ili su opažaji od Sac-a neupotrebljivi kontrolorima."
- `RAOS-4198` _[hr]_: "Vaš zahtjev nije moguće riješiti u Odjelu korisničke podrške stoga je isti otvoren prema Odjelu razvoja."

## Cluster statistics

- **Volume:** 27 tickets total (27 unique semantic events after dedup)
- **Frequency:** 1.32 tickets/month (over data window 2024-10-15 → 2026-03-30)
- **Median resolution:** 3.0 days
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~18.4 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~3.3 (range [2.4, 4.2])
- **Time reduction per ticket:** ~18% (range [13%, 23%])
- **Feasibility:** 0.55
- **Rationale:** Agent assist can accelerate the support-level escalation step (~10 min) by auto-populating city, affected streets, polygon IDs, and DDPK anomaly type from ticket text, and by surfacing the correct escalation template and developer runbook; it cannot reduce the dominant developer work time. Savings are therefore modest relative to baseline.
- **Validation:** Run a 4-week shadow-mode pilot where the assist tool pre-fills escalation fields and surfacing relevant runbook links; measure agent edit rate and time-to-escalate before and after to calibrate the 18% reduction estimate.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~8 (range [6, 10])
- **Hours eliminated per year:** ~14 (range [10.5, 18.2])
- **Root cause:** Two distinct root causes: (1) absence of an automated, validated polygon sync pipeline between GDI exports and ParkIS, requiring manual developer insertion each time a zone changes; (2) DDPK configuration defects (photo-timing race condition, duplicate-issuance logic, out-of-hours guard missing) in the SAC enforcement workflow.
- **Rationale:** A validated automated GDI-to-ParkIS polygon sync with self-service operator correction UI, combined with DDPK bug fixes, could eliminate the bulk of developer escalations; however, GDI vendor dependency and multi-city polygon complexity make full elimination uncertain. Maximum elimination is capped at the 18.4 h baseline.
- **Validation:** Engineering team should spike both workstreams separately: prototype GDI webhook/batch import in one sprint to size polygon sync effort, and instrument DDPK logs to reproduce and bound the three anomaly types before committing to a sprint estimate.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.9 (range [0.63, 1.17])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These tickets originate from internal partners (parking operators) reporting system-level polygon and DDPK configuration failures that require developer action; no self-service path can resolve a misconfigured KML polygon or a DDPK issuance bug, so deflection potential is negligible. A status page or intake form could reduce duplicate re-reports but cannot deflect the core issue.
- **Validation:** Deploy a structured intake form for Croatian operators over 8 weeks and measure whether duplicate or premature re-submissions drop; if re-submission rate falls >20%, refine the deflection estimate upward.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.5 (range [0.35, 0.65])
- **Narrow use case:** Automated acknowledgement and triage routing of new polygon/DDPK tickets to the correct developer queue with pre-filled diagnostic context
- **Safety constraints:**
  - No autonomous polygon insertion or deletion into ParkIS without developer review; incorrect polygons directly cause wrongful parking enforcement
  - No autonomous closure or resolution of DDPK anomaly tickets; duplicate or out-of-hours tickets may have legal/regulatory implications in Croatian parking enforcement
  - GDI polygon data must be validated against ParkIS schema before any automated action
  - All autonomous routing actions must be logged and reversible by a human operator
  - Operator field verification step must remain human-gated before any polygon change is considered resolved
- **Rationale:** The resolution of these tickets is fundamentally developer-gated and involves geospatial data integrity and legal parking enforcement outcomes; autonomous resolution beyond smart triage is unsafe and infeasible with current architecture. Triage automation alone yields minimal but real time savings.
- **Validation:** Pilot automated triage routing (classifier assigns city, issue type, correct developer queue) for 6 weeks on incoming tickets; accept if routing accuracy ≥90% and no mis-routed ticket causes a delayed enforcement correction.

### Risks

- **Compliance concerns:**
  - DDPK tickets issued outside working hours or as duplicates may constitute unlawful parking fines under Croatian administrative law; any automation touching ticket issuance logic must be reviewed by legal/compliance
  - Polygon boundaries define enforcement zones; incorrect automated updates could expose the operator to liability for wrongful enforcement actions
  - Data accuracy obligations to municipal authorities in Zagreb, Zadar, Šibenik, Varaždin, Rijeka, and Opatija may require human sign-off on zone changes
- **Must not automate:**
  - Insertion or modification of KML/KMZ polygon data in ParkIS without developer and operator review
  - Closure or resolution marking of DDPK anomaly tickets without confirmed developer fix and field verification
  - Cancellation or re-issuance of parking tickets (DDPK) through any automated workflow
  - Communication to internal partners that a polygon issue is resolved before field verification is complete
- **Vendor dependencies blocking automation:**
  - GDI (polygon export provider) controls the authoritative street polygon exports; any automated sync pipeline requires GDI to provide a reliable, versioned export API or webhook — currently absent and subject to negotiation
  - Typical wait time for GDI exports is unquantified (null), making SLA-based automation planning unreliable until a formal data-delivery agreement is in place

## Agent compatibility

- **Status:** `active` (extraction confidence 0.92)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Engineering backlog — not for runtime agents

