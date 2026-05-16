---
id: du-pass-system-outage-hr
name: du_pass_system_outage_hr
title: Du Pass ticket scanning system outage or slowdown reported by Croatian end users
description: End users at Croatian venues report that the Du Pass digital pass system is not working or is extremely slow,
  typically manifesting as a '5% loading' stuck screen during QR/barcode scanning, requiring users to cancel and retry. The
  issue recurs frequently, often starting at or around 08:00, and is resolved by a system restart/reset performed by RAO support
  staff. A minority of tickets also concern incorrect Du Pass sales reports or a physical scanner hardware issue.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: configuration_change
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:end_user|Support|duplikat:c2
project_key: RAOS
cluster_size: 21
cluster_size_dedup: 21
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.91
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.02
median_resolution_minutes: 344.0
p95_resolution_minutes: 11436.0
cannot_reproduce_rate: 0.0
data_window_start: '2025-03-27'
data_window_end: '2025-12-28'
annual_hours_saved: 0.4
roi:
  baseline_active_hours: 12.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.2
  deflection_hours_range:
  - 0.1
  - 0.3
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.4
  agent_assist_hours_range:
  - 0.3
  - 0.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 10.5
  product_fix_hours_range:
  - 7.4
  - 12.3
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.2
  autonomous_resolve_hours_range:
  - 0.2
  - 0.3
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-3092
- RAOS-2624
- RAOS-3176
- RAOS-2206
- RAOS-3118
- RAOS-4172
- RAOS-5621
- RAOS-3010
- RAOS-2527
- RAOS-2938
- RAOS-3148
- RAOS-2848
- RAOS-5618
- RAOS-2899
- RAOS-2896
- RAOS-3335
- RAOS-3126
- RAOS-2628
canonical_examples:
- RAOS-2527
- RAOS-5621
- RAOS-3335
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
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: 'Automated acknowledgement and triage routing: detect the stuck-screen keyword pattern,
    confirm venue and time-of-day, and auto-route to the RAO support queue with a pre-filled restart checklist — stopping
    short of executing any system action.'
  autonomous_resolve_safety_constraints:
  - No automated system restart may be triggered without a human RAO agent confirming the action, as unattended restarts at
    an active venue could disrupt live ticket scanning.
  - Sales-report correction tickets must always route to a human agent due to financial data integrity risk.
  - Zebra scanner hardware reconfiguration must not be automated without physical-presence confirmation.
  - Autonomous actions must be limited to read-only triage and notification; no write operations on the Du Pass system.
related_playbooks: []
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Du Pass ticket scanning system outage or slowdown reported by Croatian end users

## What this pattern is

End users at Croatian venues report that the Du Pass digital pass system is not working or is extremely slow, typically manifesting as a '5% loading' stuck screen during QR/barcode scanning, requiring users to cancel and retry. The issue recurs frequently, often starting at or around 08:00, and is resolved by a system restart/reset performed by RAO support staff. A minority of tickets also concern incorrect Du Pass sales reports or a physical scanner hardware issue.

## When this applies

- Du Pass QR/barcode scan hangs at '5% loading' or times out
- Every second or alternate Du Pass scan fails and requires cancellation and retry
- Du Pass completely non-functional for an extended period (e.g. 15–30 minutes or longer)
- Physical scanner (Zebra device) stops reading after factory reset
- Du Pass sales reports do not match expected totals for a given month

## Typical resolution flow

1. End user notices Du Pass is not processing or is extremely slow during venue entry
2. End user contacts RAO support (phone or portal) to report the issue
3. RAO support restarts/resets the Du Pass system
4. RAO support confirms to end user that the system is working again
5. Ticket is closed; end user occasionally confirms resolution

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Restart or reset the Du Pass system | RAO support agent | Du Pass backend/admin system | 10 min |
| Verify and correct Du Pass sales report | RAO support agent | Du Pass reporting module (e-izvještaji) | 30 min |
| Restore application configuration on Zebra scanner after factory reset | RAO support agent | Zebra device / DateWedge application | 20 min |

## Evidence

Derived from 21 tickets in cluster `RAOS:end_user|Support|duplikat:c2`. Direct quotes from 6 representative tickets:

- `RAOS-2527` _[hr]_: "Du Pass pojavljuje se greška. Kada skeniramo Du Pass moramo ići na odustani pa ponovno skenirati. Svako drugi ne prolazi."
- `RAOS-5621` _[hr]_: "Du Pass neće da prolazi, pojavi se očitanje 5% (dugo čekanje), moramo na odustani i dođe na 45%, čekanje 5 sekundi i onda ga prihvati."
- `RAOS-3335` _[hr]_: "Du Pass ponovno ne radi od 08:00 sati. Pojavljuje se čekanje 5% i neće da prođe."
- `RAOS-2848` _[hr]_: "Napravili smo nekoliko restarta, molimo Vas povratne informacije."
- `RAOS-3176` _[hr]_: "telefonski smo Vam prijavili da nam ne štimaju izvješća za Du Pass za 5 mjesec, a pošto oba dva izvješća šaljemo gradu molimo Vas da nam ispravite izvješće koje ne štima."
- `RAOS-3010` _[hr]_: "Du Pass danas uopće nije radio pola sata. Nakon pola sata što se resetirao sustav je proradilo."

## Cluster statistics

- **Volume:** 21 tickets total (21 unique semantic events after dedup)
- **Frequency:** 1.02 tickets/month (over data window 2025-03-27 → 2025-12-28)
- **Median resolution:** 5.7 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~12.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.4 (range [0.29, 0.533])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.75
- **Rationale:** The resolution pattern is highly repetitive (restart → verify → optionally reconfigure scanner), making it well-suited for a pre-filled diagnostic checklist and a single-click restart-instruction template; agent assist would primarily save documentation and triage time rather than active resolution time, limiting overall savings on a small cluster.
- **Validation:** Deploy the restart-instruction template and diagnostic checklist in shadow mode for 2 weeks, measuring agent acceptance rate and time-to-first-response; accept if ≥70% of drafts are used without material edits.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~10.5 (range [7.4, 12.3])
- **Root cause:** The Du Pass scanning system enters a degraded state (manifesting as a stuck '5% loading' screen) that appears to trigger on a predictable schedule (around 08:00 daily) and is resolved by a manual restart, suggesting a resource leak, hung process, or misconfigured startup/scheduling task in the Du Pass application or its backend integration layer.
- **Rationale:** If the root cause (likely a startup-time resource contention or scheduled-task misconfiguration) is fixed, the majority of restart-related tickets (~85% of cluster) would be eliminated; the remaining ~15% covering sales-report corrections and hardware scanner issues are separate sub-problems. Hours eliminated are capped at baseline (12.3 h/yr).
- **Validation:** Engineering should instrument Du Pass process health around 08:00 startup, capture memory/thread dumps on degraded instances, and reproduce in staging; a spike of 2–3 days should clarify whether it is a software bug or a deployment configuration issue before committing sprint estimates.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.2 (range [0.147, 0.27])
- **Form:** `help_center`
- **Deflection rate:** ~10% (range [7%, 13%])
- **Feasibility:** 0.35
- **Rationale:** The '5% loading / stuck screen' symptom is recognizable, but the fix (system restart by RAO support) requires privileged access that end users cannot perform themselves, severely limiting self-service deflection. A help-center article could reduce repeat contact from the same user within a session but cannot resolve the underlying outage.
- **Validation:** Publish a help-center article describing the stuck-screen symptom and advising users to contact their venue's RAO support; measure ticket-creation rate per affected venue over a 4-week period before and after publication.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.2 (range [0.175, 0.32])
- **Narrow use case:** Automated acknowledgement and triage routing: detect the stuck-screen keyword pattern, confirm venue and time-of-day, and auto-route to the RAO support queue with a pre-filled restart checklist — stopping short of executing any system action.
- **Safety constraints:**
  - No automated system restart may be triggered without a human RAO agent confirming the action, as unattended restarts at an active venue could disrupt live ticket scanning.
  - Sales-report correction tickets must always route to a human agent due to financial data integrity risk.
  - Zebra scanner hardware reconfiguration must not be automated without physical-presence confirmation.
  - Autonomous actions must be limited to read-only triage and notification; no write operations on the Du Pass system.
- **Rationale:** The restart action itself cannot safely be automated end-to-end due to venue-operations risk, so autonomous value is confined to triage acceleration and queue routing. Given the low annual frequency (12.3 tickets/yr) the absolute hour savings are modest even at the safety cap.
- **Validation:** Run auto-triage routing in parallel (human still acts) for 30 days on 20% of incoming tickets matching the stuck-screen keyword pattern; accept if routing accuracy ≥90% and no false-positive restarts occur.

### Risks

- **Compliance concerns:**
  - Du Pass sales report corrections involve financial transaction data; any automated handling must comply with applicable Croatian fiscal/e-invoice regulations and internal audit requirements.
  - Access logs for system restarts should be preserved for operational audit trails — automation must not bypass logging.
- **Must not automate:**
  - Executing a Du Pass system restart without explicit human confirmation from an RAO agent on-site.
  - Modifying or correcting Du Pass sales report figures autonomously.
  - Performing Zebra scanner factory reset or application reconfiguration without physical-presence verification.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.91)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Admin/operator-only configuration change

