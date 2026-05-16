---
id: hr-concessionaire-request-verification-bmove
name: hr_concessionaire_request_verification_bmove
title: Recurring verification of concessionaire requests on Bmove tools interface (HR)
description: Internal partner tickets representing a recurring task to verify concessionaire (operator/licensee) requests
  via the Bmove tools interface. Each ticket covers verification of polygons, working hours, and zones. All tickets are identical
  in content and appear to be a repeating periodic internal workflow rather than a one-time issue.
category: internal_partner/configuration
ticket_class: internal_partner
issue_category: configuration
resolution_pattern: manual_close
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:internal_partner|Support interni zadaci|no_label:c0
project_key: RAOS
cluster_size: 41
cluster_size_dedup: 41
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.0
median_resolution_minutes: 533.0
p95_resolution_minutes: 7595.000000000004
cannot_reproduce_rate: 0.0
data_window_start: '2026-03-13'
data_window_end: '2026-05-08'
annual_hours_saved: 6.4
roi:
  baseline_active_hours: 21.3
  baseline_active_source: 'fallback: 10% of wall-clock median (533 min)'
  baseline_is_fallback: true
  baseline_confidence_tier: directional
  deflection_hours_midpoint: 1.1
  deflection_hours_range:
  - 0.8
  - 1.4
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 6.4
  agent_assist_hours_range:
  - 4.5
  - 8.3
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 17.0
  product_fix_hours_range:
  - 12.0
  - 21.3
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 3.5
  autonomous_resolve_hours_range:
  - 2.5
  - 4.5
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-7115
- RAOS-6928
- RAOS-6671
- RAOS-6527
- RAOS-7030
- RAOS-6784
- RAOS-6972
- RAOS-6703
- RAOS-6627
- RAOS-6582
- RAOS-6735
- RAOS-6991
- RAOS-6842
- RAOS-6757
- RAOS-6858
- RAOS-6803
- RAOS-6899
- RAOS-6472
canonical_examples:
- RAOS-7115
- RAOS-6472
- RAOS-6527
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Automated Bmove API polling to verify polygon, hours, and zone fields against defined
    rules, closing the ticket automatically only when all checks pass with no exceptions
  autonomous_resolve_safety_constraints:
  - Autonomous closure only permitted when all three verification checks (polygons, working hours, zones) return a clean pass
    with no anomalies
  - Any exception or mismatch must route to a human agent for review before ticket closure
  - Bmove tools must expose a reliable, auditable API or data interface for automated reads — manual-only interfaces block
    this path
  - Audit log of every automated verification result must be retained for compliance and dispute resolution
  - Pilot must be supervised for a minimum of 4 weeks before expanding volume
related_playbooks:
- hr-b2b-monthly-invoice-generation-and-fiscalization
- hr-bmove-tools-request-verification__1f253d
- hr-bmove-tools-request-verification__e581c1
- hr-internal-weekly-report-coordination
- hr-rao-recurring-support-requests
- internal-coordination-and-reporting
- internal-it-misc-tasks-hr
- internal-roland-meeting-ticket-review
- internal-ticket-analysis-and-documentation
- periodic-table-update-lpr-a1-ht
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Recurring verification of concessionaire requests on Bmove tools interface (HR)

## What this pattern is

Internal partner tickets representing a recurring task to verify concessionaire (operator/licensee) requests via the Bmove tools interface. Each ticket covers verification of polygons, working hours, and zones. All tickets are identical in content and appear to be a repeating periodic internal workflow rather than a one-time issue.

## When this applies

- A concessionaire submits a request that requires internal review on the Bmove tools interface
- Recurring periodic internal task is created to check concessionaire configurations

## Typical resolution flow

1. Open Bmove tools interface
2. Review concessionaire request for polygon correctness
3. Review concessionaire working hours settings
4. Review concessionaire zone configuration
5. Mark ticket as resolved after verification

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Verify concessionaire polygons on Bmove tools interface | internal support agent | Bmove tools | — |
| Verify concessionaire working hours on Bmove tools interface | internal support agent | Bmove tools | — |
| Verify concessionaire zones on Bmove tools interface | internal support agent | Bmove tools | — |

## Evidence

Derived from 41 tickets in cluster `RAOS:internal_partner|Support interni zadaci|no_label:c0`. Direct quotes from 3 representative tickets:

- `RAOS-7115` _[hr]_: "Provjera zahtjeva koncesionara na Bmove tools sučelju -Poligoni -Radno vrijeme -Zone"
- `RAOS-6472` _[hr]_: "Provjera zahtjeva koncesionara na Bmove tools sučelju -Poligoni -Radno vrijeme -Zone"
- `RAOS-6527` _[hr]_: "Provjera zahtjeva koncesionara na Bmove tools sučelju -Poligoni -Radno vrijeme -Zone"

## Cluster statistics

- **Volume:** 41 tickets total (41 unique semantic events after dedup)
- **Frequency:** 2.0 tickets/month (over data window 2026-03-13 → 2026-05-08)
- **Median resolution:** 8.9 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`directional`) ⚠️ fallback heuristic

- **Annual active work:** ~21.3 hours/year
- _Source:_ fallback: 10% of wall-clock median (533 min)
- _Note:_ Sloj 6 did not produce action durations for this cluster, so the baseline is a coarse approximation. Treat the ROI block below as **directional only**.

### Agent-assist (`directional`)

- **Hours saved per year:** ~6.4 (range [4.5, 8.3])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.70
- **Rationale:** A structured checklist or guided workflow tool (e.g., pre-populated verification template with direct deep-links into Bmove tools for each check) could reduce per-ticket active time by roughly 30% by eliminating navigation and recall overhead. The task is repetitive and well-scoped, making it a good candidate for agent assist tooling.
- **Validation:** Run a 2-week shadow-mode pilot where agents use a structured verification checklist alongside their normal process; compare active time per ticket before and after to validate the 30% reduction assumption.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~17 (range [12, 21.3])
- **Root cause:** This is a recurring internal verification workflow (not a bug) — agents must manually confirm concessionaire polygons, working hours, and zones via the Bmove tools interface on a periodic basis. The ticket volume reflects a designed but manual process, not a system defect.
- **Rationale:** Building an automated verification check within Bmove tools (e.g., scheduled script or dashboard alert that runs polygon/hours/zone validation and surfaces exceptions only) could eliminate most manual ticket handling. Hours eliminated are capped at the 21.3-hour baseline; high end assumes near-full automation, low end retains exception review overhead.
- **Validation:** Engineering team should spike on Bmove API capability for automated polygon/zone/hours checks; estimate effort in a discovery sprint before committing to full build.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1.1 (range [0.77, 1.43])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These are internal periodic workflow tickets initiated by staff who already know the process; self-service or FAQ deflection is not applicable since the work itself (verification on Bmove tools) must still occur. No meaningful deflection is achievable without eliminating the underlying workflow.
- **Validation:** Over a 4-week pilot, document whether any submitter could have self-verified without agent involvement; if rate is <5%, deflection should not be pursued further.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~3.5 (range [2.5, 4.5])
- **Narrow use case:** Automated Bmove API polling to verify polygon, hours, and zone fields against defined rules, closing the ticket automatically only when all checks pass with no exceptions
- **Safety constraints:**
  - Autonomous closure only permitted when all three verification checks (polygons, working hours, zones) return a clean pass with no anomalies
  - Any exception or mismatch must route to a human agent for review before ticket closure
  - Bmove tools must expose a reliable, auditable API or data interface for automated reads — manual-only interfaces block this path
  - Audit log of every automated verification result must be retained for compliance and dispute resolution
  - Pilot must be supervised for a minimum of 4 weeks before expanding volume
- **Rationale:** Autonomous resolution is technically plausible for the subset of tickets where all checks pass cleanly, but feasibility is gated on Bmove tools having a queryable API; without it, this path is blocked. A conservative 20% safe volume cap accounts for the novelty of automated verification in an HR/operations context.
- **Validation:** Pilot scope: select 4–5 upcoming tickets (representing ~20% of quarterly volume), run automated checks in parallel with manual agent work, and compare outcomes; accept if false-pass rate is 0% over 4 weeks.

### Risks

- **Compliance concerns:**
  - Concessionaire polygon and zone configurations may have contractual or regulatory implications; incorrect verification could expose the organization to legal or operational liability
  - HR-adjacent internal workflows may be subject to audit requirements — automated closures must produce a verifiable audit trail
  - Any change to verification logic must be reviewed against applicable licensing or franchise agreements
- **Must not automate:**
  - Tickets where polygon, zone, or working-hours data contains discrepancies or anomalies — these require human judgment before resolution
  - Cases involving new or modified concessionaire agreements not yet reflected in Bmove tools
  - Any ticket flagged with escalation indicators or exceptions from the requester

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

