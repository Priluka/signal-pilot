---
id: hr-bmove-tools-request-verification__e581c1
name: hr_bmove_tools_request_verification
title: Recurring internal review of partner requests on bmove.tools interface (polygons & working hours)
description: 'Internal support tasks in Croatia involving the periodic verification of partner requests submitted through
  the bmove.tools interface. Each ticket covers the same two review areas: delivery polygons and working hours (Poligoni,
  Radno vrijeme). The identical structure and high volume (147 tickets) indicate this is a recurring, routine internal operational
  task rather than a one-off issue.'
category: internal_partner/configuration
ticket_class: internal_partner
issue_category: configuration
resolution_pattern: no_action
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:internal_partner|Support interni zadaci|no_label:c1
project_key: RAOS
cluster_size: 147
cluster_size_dedup: 147
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 7.17
median_resolution_minutes: 74.0
p95_resolution_minutes: 6762.599999999992
cannot_reproduce_rate: 0.0
data_window_start: '2025-07-23'
data_window_end: '2026-03-12'
annual_hours_saved: 8.6
roi:
  baseline_active_hours: 28.7
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.5
  deflection_hours_range:
  - 0.3
  - 0.7
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 8.6
  agent_assist_hours_range:
  - 6.0
  - 11.2
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 20.1
  product_fix_hours_range:
  - 14.1
  - 26.1
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 6.0
  autonomous_resolve_hours_range:
  - 4.2
  - 7.8
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-4458
- RAOS-4357
- RAOS-3819
- RAOS-3961
- RAOS-4676
- RAOS-6049
- RAOS-5669
- RAOS-6063
- RAOS-3899
- RAOS-6460
- RAOS-3762
- RAOS-5725
- RAOS-4419
- RAOS-3841
- RAOS-5589
- RAOS-5460
- RAOS-4325
- RAOS-4794
canonical_examples:
- RAOS-4458
- RAOS-6049
- RAOS-3762
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
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-approve partner submissions where polygon boundaries fall within pre-approved zones
    AND working hours conform to a validated schema with no flags
  autonomous_resolve_safety_constraints:
  - Only submissions that pass all automated polygon boundary checks against approved zone definitions may be auto-approved
  - Working hours must conform to a strictly defined schema (no overlaps, within permitted operating windows) before autonomous
    action
  - Any submission with a validation warning or anomaly must be routed to a human agent
  - Full audit log of every autonomous decision must be retained and reviewable
  - Human override must be possible within a defined grace period after auto-approval
related_playbooks:
- hr-bmove-tools-request-verification__1f253d
- hr-concessionaire-request-verification-bmove
- hr-internal-weekly-report-coordination
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

# Recurring internal review of partner requests on bmove.tools interface (polygons & working hours)

## What this pattern is

Internal support tasks in Croatia involving the periodic verification of partner requests submitted through the bmove.tools interface. Each ticket covers the same two review areas: delivery polygons and working hours (Poligoni, Radno vrijeme). The identical structure and high volume (147 tickets) indicate this is a recurring, routine internal operational task rather than a one-off issue.

## When this applies

- A partner submits or updates a request on the bmove.tools interface
- Scheduled or routine internal review cycle is triggered
- Changes to delivery polygons or working hours require verification

## Typical resolution flow

1. Ticket is created as an internal task to review pending requests on bmove.tools
2. Internal team member opens bmove.tools interface
3. Reviewer checks partner-submitted polygon configurations
4. Reviewer checks partner-submitted working hours configurations
5. Verification is completed and ticket is closed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Log into bmove.tools interface and locate pending partner requests | internal support agent | Bmove.tools | 5 min |
| Review and verify polygon configurations submitted by partner | internal support agent | Bmove.tools | 10 min |
| Review and verify working hours submitted by partner | internal support agent | Bmove.tools | 5 min |

## Evidence

Derived from 147 tickets in cluster `RAOS:internal_partner|Support interni zadaci|no_label:c1`. Direct quotes from 4 representative tickets:

- `RAOS-4458` _[hr]_: "Provjera zahtjeva na bmove.tools sučelju -Poligoni -Radno vrijeme"
- `RAOS-6049` _[hr]_: "Provjera zahtjeva na bmove.tools sučelju -Poligoni -Radno vrijeme"
- `RAOS-3762` _[hr]_: "Provjera zahtjeva na bmove.tools sučelju -Poligoni -Radno vrijeme"
- `RAOS-6460` _[hr]_: "Provjera zahtjeva na bmove.tools sučelju -Poligoni -Radno vrijeme"

## Cluster statistics

- **Volume:** 147 tickets total (147 unique semantic events after dedup)
- **Frequency:** 7.17 tickets/month (over data window 2025-07-23 → 2026-03-12)
- **Median resolution:** 1.2 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~28.7 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~8.6 (range [6.02, 11.18])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.75
- **Rationale:** The task is highly structured and repetitive — two fixed review areas per ticket — making it well-suited for an assist tool that pre-fetches the partner's pending polygon and working-hours submission and surfaces a pre-filled checklist, reducing the login-and-locate step and guiding faster verification. A 30% active-time reduction is conservative given the structured nature but accounts for edge cases requiring human judgment.
- **Validation:** Deploy a shadow-mode assist tool for 2–3 weeks that auto-populates submission data alongside the existing workflow; measure average active minutes per ticket before and after to calibrate actual time reduction.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~20.1 (range [14.1, 26.1])
- **Root cause:** The root cause is a manual, human-in-the-loop review process baked into operations: partner submissions on bmove.tools are not automatically validated, so an agent must log in, locate requests, and inspect polygon and working-hours data on every cycle. This is a process/product design gap rather than a software defect.
- **Rationale:** Building automated validation rules in bmove.tools (e.g., polygon boundary checks and working-hours schema validation at submission time) could eliminate a large share of manual review steps; estimated 70% of active hours could be eliminated if the product flags compliant submissions automatically, capped at the 28.7-hour baseline. Engineering effort is directional because bmove.tools architecture and API surface are not fully characterised here.
- **Validation:** Engineering team should spike on bmove.tools API/data model for 1–2 days to confirm whether validation hooks can be injected at submission; a prototype covering polygon-bounds checking alone would validate the effort estimate before committing to full build.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.5 (range [0.35, 0.65])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** This is an internal operational review task performed by support agents, not a partner-facing inquiry; self-service or FAQ deflection is not applicable because there is no inbound end-user question to deflect. The cluster is driven by the volume of partner submissions requiring mandatory internal verification, so deflection would not reduce the core workload.
- **Validation:** Track whether any portion of tickets represents partners asking about review status; a 4-week tagging exercise on incoming tickets could confirm whether a status-update FAQ or portal could eliminate even a small slice of follow-up contacts.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~6 (range [4.2, 7.8])
- **Narrow use case:** Auto-approve partner submissions where polygon boundaries fall within pre-approved zones AND working hours conform to a validated schema with no flags
- **Safety constraints:**
  - Only submissions that pass all automated polygon boundary checks against approved zone definitions may be auto-approved
  - Working hours must conform to a strictly defined schema (no overlaps, within permitted operating windows) before autonomous action
  - Any submission with a validation warning or anomaly must be routed to a human agent
  - Full audit log of every autonomous decision must be retained and reviewable
  - Human override must be possible within a defined grace period after auto-approval
- **Rationale:** Autonomous resolution is plausible only for the cleanest, most routine submissions; at most 25% of volume (safety cap applied) could be auto-approved with high confidence, saving roughly 25% of baseline hours. The remaining 75% requires human judgment because polygon configurations and working-hours edge cases carry operational risk for partner delivery operations.
- **Validation:** Run a 6-week pilot in read-only mode: the system proposes an auto-approve/escalate decision for each ticket, but agents still act manually; measure false-positive rate (submissions the system would have auto-approved that agents rejected) and calibrate the volume percentage and rule set before enabling autonomous action.

### Risks

- **Compliance concerns:**
  - Partner delivery polygon configurations may have regulatory or contractual implications in Croatia; incorrect auto-approvals could expose the business to operational or legal liability
  - Working-hours rules may be subject to Croatian labour or logistics regulations that require human sign-off
- **Must not automate:**
  - Any submission where polygon boundaries overlap with restricted or unverified zones
  - Working-hours submissions that deviate from expected patterns without a prior approval precedent
  - Escalations or exception cases flagged by partners for manual review

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** Informational — safe for agent self-service

