---
id: hr-bmove-tools-request-verification__1f253d
name: hr_bmove_tools_request_verification
title: Periodic verification of partner requests on bmove.tools interface (Polygons & Working Hours)
description: This pattern represents a recurring internal support task in Croatia where agents perform routine checks of partner-submitted
  requests on the bmove.tools interface, specifically verifying polygon configurations and working hours settings. All tickets
  are identical in content, suggesting this is a templated, repetitive operational task rather than an ad-hoc issue. The high
  volume and uniformity indicate a scheduled or triggered internal review process.
category: internal_partner/configuration
ticket_class: internal_partner
issue_category: configuration
resolution_pattern: manual_close
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:internal_partner|Support interni zadaci|no_label:c2
project_key: RAOS
cluster_size: 18
cluster_size_dedup: 18
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.91
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.88
median_resolution_minutes: 94.0
p95_resolution_minutes: 8587.59999999998
cannot_reproduce_rate: 0.0
data_window_start: '2025-07-24'
data_window_end: '2026-03-09'
annual_hours_saved: 1.2
roi:
  baseline_active_hours: 4.7
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.0
  deflection_hours_range:
  - 0.0
  - 0.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.2
  agent_assist_hours_range:
  - 0.8
  - 1.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 3.8
  product_fix_hours_range:
  - 2.8
  - 4.7
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 1.1
  autonomous_resolve_hours_range:
  - 0.8
  - 1.4
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-3807
- RAOS-4475
- RAOS-4112
- RAOS-4293
- RAOS-4821
- RAOS-4216
- RAOS-5649
- RAOS-6401
- RAOS-3948
- RAOS-6306
- RAOS-4509
- RAOS-4436
- RAOS-5622
- RAOS-4966
- RAOS-5806
- RAOS-3714
- RAOS-4182
- RAOS-5076
canonical_examples:
- RAOS-3807
- RAOS-6401
- RAOS-5649
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
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Automated pass/fail validation of polygon geometry and working-hours format against
    predefined rules, with auto-close only when all checks pass and no anomaly is detected
  autonomous_resolve_safety_constraints:
  - Auto-close only when all validation rules pass with zero exceptions; any rule failure must route to human agent
  - Human audit of a random 20% sample of auto-closed tickets each quarter
  - Scope limited to format and completeness checks; semantic/business-logic review remains human
  - Full audit log of every automated decision retained for ≥90 days
  - Partner-facing configuration changes must never be auto-approved; only the internal review ticket may be auto-closed
related_playbooks:
- hr-b2b-monthly-invoice-generation-and-fiscalization
- hr-bmove-tools-request-verification__e581c1
- hr-concessionaire-request-verification-bmove
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

# Periodic verification of partner requests on bmove.tools interface (Polygons & Working Hours)

## What this pattern is

This pattern represents a recurring internal support task in Croatia where agents perform routine checks of partner-submitted requests on the bmove.tools interface, specifically verifying polygon configurations and working hours settings. All tickets are identical in content, suggesting this is a templated, repetitive operational task rather than an ad-hoc issue. The high volume and uniformity indicate a scheduled or triggered internal review process.

## When this applies

- A partner submits a request that requires internal verification on the bmove.tools interface
- Routine scheduled review of polygon configurations and working hours for partners in Croatia
- Internal workflow triggers creation of a verification task ticket

## Typical resolution flow

1. Ticket is created (manually or automatically) to track a verification task on bmove.tools
2. Internal agent accesses the bmove.tools interface
3. Agent reviews submitted polygon configurations
4. Agent reviews submitted working hours settings
5. Agent confirms or flags the request and closes the ticket

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Access bmove.tools interface and review polygon configurations | internal support agent | Bmove.tools | 15 min |
| Review working hours settings submitted by partner | internal support agent | Bmove.tools | 10 min |
| Close the verification ticket after review is complete | internal support agent | — | 2 min |

## Evidence

Derived from 18 tickets in cluster `RAOS:internal_partner|Support interni zadaci|no_label:c2`. Direct quotes from 3 representative tickets:

- `RAOS-3807` _[hr]_: "Provjera zahtjeva na bmove.tools sučelju -Poligoni -Radno vrijeme"
- `RAOS-6401` _[hr]_: "Provjera zahtjeva na bmove.tools sučelju -Poligoni -Radno vrijeme"
- `RAOS-5649` _[hr]_: "Provjera zahtjeva na bmove.tools sučelju -Poligoni -Radno vrijeme"

## Cluster statistics

- **Volume:** 18 tickets total (18 unique semantic events after dedup)
- **Frequency:** 0.88 tickets/month (over data window 2025-07-24 → 2026-03-09)
- **Median resolution:** 1.6 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~4.7 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.2 (range [0.84, 1.5])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** Because all tickets are near-identical, a checklist-driven assist tool that pre-populates the review steps and auto-fills the close action could reduce the 2-minute close step to near-zero and trim review time by surfacing direct deep-links into the bmove.tools polygon and hours views. Savings are modest given the already low annual volume.
- **Validation:** Deploy a shadow-mode assist panel for 3 weeks on all new verification tickets; measure average active minutes with vs. without assist and compare to the 27-minute baseline to validate the 25% reduction assumption.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~3.8 (range [2.8, 4.7])
- **Root cause:** The recurrence is a designed operational process: agents must manually verify partner-submitted polygon and working-hours configurations on bmove.tools because the interface lacks automated validation, change-detection, or approval-workflow capabilities. This is a process gap, not a software defect.
- **Rationale:** Building automated validation rules and a diff-alert mechanism in bmove.tools could eliminate the manual review step for straightforward polygon and hours changes, reducing or removing the need for agent-created verification tickets. Hours-eliminated is capped at the 4.7-hour baseline; midpoint assumes ~80% of tickets are fully eliminable, with ~20% still requiring human judgment.
- **Validation:** Engineering should scope a spike (≤2 days) to assess whether bmove.tools supports webhook or rule-based validation hooks; spike outcome determines if effort estimate is accurate before committing sprint capacity.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0.028, 0.05])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** This is an internally-triggered operational review task, not a partner-initiated support request; there is no external user seeking help, so self-service deflection is not applicable. The tickets appear to originate from a scheduled or triggered process, meaning FAQ or chatbot tooling would not intercept their creation.
- **Validation:** Confirm ticket origin in a 4-week pilot: log whether tickets are agent-created on schedule versus partner-submitted; if >90% are internally created, deflection potential is effectively zero.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~1.1 (range [0.8, 1.4])
- **Narrow use case:** Automated pass/fail validation of polygon geometry and working-hours format against predefined rules, with auto-close only when all checks pass and no anomaly is detected
- **Safety constraints:**
  - Auto-close only when all validation rules pass with zero exceptions; any rule failure must route to human agent
  - Human audit of a random 20% sample of auto-closed tickets each quarter
  - Scope limited to format and completeness checks; semantic/business-logic review remains human
  - Full audit log of every automated decision retained for ≥90 days
  - Partner-facing configuration changes must never be auto-approved; only the internal review ticket may be auto-closed
- **Rationale:** At 25% safe volume, roughly 2–3 tickets per year could be auto-resolved when polygon geometry and working-hours fields pass all schema-level checks automatically, saving the full 27 active minutes each. Feasibility is limited because the verification task involves judgment on business-logic correctness, not just format validation.
- **Validation:** Run a 6-week shadow pilot where the automation engine logs a pass/fail verdict without acting; compare its verdicts to agent outcomes on the same tickets — accept autonomous resolution only if precision ≥95% on the shadow set.

### Risks

- **Compliance concerns:**
  - Partner configuration errors (e.g., incorrect polygon boundaries or wrong working hours) could cause operational or contractual harm if missed; any automation must not reduce oversight below current levels
  - Audit trail requirements: Croatia-based operations may be subject to local data-handling or operational-record retention obligations; automated close actions must preserve equivalent records
- **Must not automate:**
  - Approval or acceptance of partner-submitted configuration changes that have business-logic implications (e.g., polygon expansion into new zones, hours changes affecting SLAs)
  - Any ticket where the verification surfaces a discrepancy or anomaly — these must always route to a human agent

## Agent compatibility

- **Status:** `active` (extraction confidence 0.91)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

