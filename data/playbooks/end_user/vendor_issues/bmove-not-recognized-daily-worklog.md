---
id: bmove-not-recognized-daily-worklog
name: bmove_not_recognized_daily_worklog
title: Daily BMove 'nicht erkannt' worklog reports requiring manual gate/checkout interventions
description: An automated daily report is submitted as a support ticket each morning listing all parking garage events where
  the BMove system failed to recognize a vehicle (error code '12 - Bmove nicht erkannt'), requiring manual agent interventions
  such as gate opening (Handöffnung) or customer information (Kundeninfo). The tickets cover multiple parking garages primarily
  in Austria, with agents manually processing payments and checking out customers in the SKIDATA system. Some days include
  spike/anomaly detection notes when a specific garage shows significantly higher-than-average failure counts.
category: end_user/vendor_issues
ticket_class: end_user
issue_category: vendor_failure
resolution_pattern: manual_close
languages:
- de
- en
country_focus:
- at
- de
- other
status: active
cluster_id: BS:end_user|austria|no_label:c1
project_key: BS
cluster_size: 96
cluster_size_dedup: 94
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.84
median_resolution_minutes: 417.5
p95_resolution_minutes: 7763.55
cannot_reproduce_rate: 0.0
data_window_start: '2026-01-14'
data_window_end: '2026-05-08'
annual_hours_saved: 3.0
roi:
  baseline_active_hours: 11.8
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.3
  deflection_hours_range:
  - 0.2
  - 0.4
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 3.0
  agent_assist_hours_range:
  - 2.1
  - 3.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 9.4
  product_fix_hours_range:
  - 7.1
  - 11.8
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.6
  autonomous_resolve_hours_range:
  - 0.4
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-49515
- BS-52763
- BS-51585
- BS-47847
- BS-51417
- BS-48065
- BS-50951
- BS-49082
- BS-50723
- BS-51456
- BS-49554
- BS-48138
- BS-48605
- BS-49926
- BS-49984
- BS-52943
- BS-49871
- BS-50679
canonical_examples:
- BS-52763
- BS-49515
- BS-51585
vendor_dependency:
  vendor_name: SKIDATA
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-generate and route the structured SKIDATA session-close request (InstallError cleanup)
    when the daily report contains only standard error-12 entries with no anomaly/spike flag
  autonomous_resolve_safety_constraints:
  - Must not autonomously open physical gates or process payments without human confirmation
  - Must exclude any ticket containing a spike/anomaly detection flag requiring investigation
  - Must not initiate customer-facing communications on behalf of agents without review
  - Requires SKIDATA API write access with full audit logging; session changes must be reversible
  - Must be limited to session-close requests only, not full checkout or payment finalization
  - Autonomous actions must pause if error-12 volume exceeds 2× the rolling 30-day average for a garage
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-incorrect-charge-refund
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- email-address-change-not-possible
- email-address-change-not-supported
- expired-card-deletion-ticketless-link
- microsoft365-quarantine-notification-auto-tickets
- missing-parking-invoice-receipt
- missing-parking-receipt-email
- missing-parking-receipt-request
- open-session-at-exit-austria
- outstanding-payment-credit-card-failure
- pkc-vehicle-registration-automated-tickets
- ticketless-open-session-at-exit__960f17
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Daily BMove 'nicht erkannt' worklog reports requiring manual gate/checkout interventions

## What this pattern is

An automated daily report is submitted as a support ticket each morning listing all parking garage events where the BMove system failed to recognize a vehicle (error code '12 - Bmove nicht erkannt'), requiring manual agent interventions such as gate opening (Handöffnung) or customer information (Kundeninfo). The tickets cover multiple parking garages primarily in Austria, with agents manually processing payments and checking out customers in the SKIDATA system. Some days include spike/anomaly detection notes when a specific garage shows significantly higher-than-average failure counts.

## When this applies

- BMove system fails to recognize a vehicle at a parking garage exit device
- Automated daily worklog report is generated and submitted as a support ticket each morning
- Spike detection threshold exceeded for a specific garage (e.g., today's count significantly above recent average)

## Typical resolution flow

1. Automated system generates and submits daily BMove worklog report ticket each morning
2. Report lists each 'Bmove nicht erkannt' event with date, garage, device, agent comment, license plate, and action taken
3. Agents at garages manually open gates (Handöffnung) or provide customer info (Kundeninfo) for affected vehicles
4. Agents manually process outstanding parking fees in SKIDATA where possible
5. If SKIDATA session cannot be closed automatically, support team is asked to close the session manually
6. Ticket is reviewed and closed by support

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Manual gate opening for vehicle not recognized by BMove | Parking garage agent | SKIDATA terminal (e.g., AF41, TÜR51, EF21) | 5 min |
| Manual checkout and payment processing in SKIDATA | Parking garage agent | SKIDATA | 10 min |
| Request to close open SKIDATA session with InstallError | Support agent | SKIDATA | 5 min |
| Customer informed to contact BMove directly | Parking garage agent | — | 2 min |
| Review anomaly/spike detection flag and investigate high-frequency garage | Support agent | — | 10 min |

## Vendor dependency

- **Vendor:** SKIDATA

## Evidence

Derived from 96 tickets in cluster `BS:end_user|austria|no_label:c1`. Direct quotes from 7 representative tickets:

- `BS-52763` _[de]_: "12 - Bmove nicht erkannt"
- `BS-49515` _[en]_: "Good morning , here are the BMove worklogs from 15.02.2026. No BMove worklogs for this day."
- `BS-51585` _[en]_: "078 - WST: today 14 vs. avg 3.2 over the last 4 days"
- `BS-50723` _[en]_: "Please close the session in Skidati for this user. I am getting an 'InstallError' message. User needs to be charged €3. LPN: W****"
- `BS-49926` _[de]_: "gestern gab es einen Stromausfall in der Garage, Ma vor Ort hat sich laut Kundin nicht ausgekannt und konnte Kundin nicht ausbuchen, 4€abgebucht"
- `BS-50951` _[de]_: "AF Ausbuchen eider nicht Möglich"
- `BS-52943` _[de]_: "Kunde wurde gebeten sich an BMove zu wenden"

## Cluster statistics

- **Volume:** 96 tickets total (94 unique semantic events after dedup)
- **Frequency:** 1.84 tickets/month (over data window 2026-01-14 → 2026-05-08)
- **Median resolution:** 7.0 hours
- **Languages:** de, en
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~11.8 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~3 (range [2.12, 3.835])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.70
- **Rationale:** Each daily report ticket follows a highly structured, repetitive workflow (gate open → SKIDATA checkout → session close → customer note), making it a strong candidate for a guided macro or pre-filled action checklist; anomaly-detection summaries could be auto-drafted from the structured report data, reducing investigation time. Savings are moderate because the actions themselves are physical or system-level and cannot be fully eliminated by assist tools alone.
- **Validation:** Run a 3-week shadow-mode pilot where an assist bot auto-populates the SKIDATA session-close request template and anomaly summary for each incoming daily report; compare active-minutes-per-ticket between assisted and unassisted cohorts via time-tracking logs.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
- **Hours eliminated per year:** ~9.4 (range [7.1, 11.8])
- **Root cause:** BMove's vehicle recognition subsystem emits error code '12 - Bmove nicht erkannt' when it fails to identify a vehicle, forcing manual gate and SKIDATA checkout interventions. The root cause lies in BMove's recognition pipeline (camera calibration, license-plate OCR, or sensor integration), which is a vendor-owned component; SKIDATA session cleanup for InstallErrors is a secondary consequence.
- **Rationale:** A vendor-side fix to BMove's recognition accuracy (e.g., improved models, better camera calibration, or fallback OCR) could eliminate the majority of these failure events; however, effort and timeline are unknown since BMove is a third-party vendor with no disclosed roadmap. Hours-eliminated ceiling is capped at the 11.8-hour baseline; midpoint assumes ~80% reduction in failure volume upon a successful fix.
- **Validation:** Escalate to BMove vendor with aggregated error-code logs and per-garage failure rates; request a root-cause analysis and a pilot firmware/model update for one high-frequency Austrian garage, measuring error-12 rate before and after over a 6-week window.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.3 (range [0.21, 0.39])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These tickets originate from an automated daily report, not from end-customers seeking self-service; deflection via FAQ or chatbot is structurally inapplicable since the inbound channel is a scheduled system report requiring agent action. Marginal deflection credit is assigned only for the small share of customer-facing 'Kundeninfo' steps that might be pre-empted by signage or BMove app guidance.
- **Validation:** Deploy in-garage BMove error signage and an app-based self-help prompt for 4 weeks; measure whether 'Customer informed to contact BMove directly' action frequency decreases as a share of total ticket actions.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.6 (range [0.39, 0.715])
- **Narrow use case:** Auto-generate and route the structured SKIDATA session-close request (InstallError cleanup) when the daily report contains only standard error-12 entries with no anomaly/spike flag
- **Safety constraints:**
  - Must not autonomously open physical gates or process payments without human confirmation
  - Must exclude any ticket containing a spike/anomaly detection flag requiring investigation
  - Must not initiate customer-facing communications on behalf of agents without review
  - Requires SKIDATA API write access with full audit logging; session changes must be reversible
  - Must be limited to session-close requests only, not full checkout or payment finalization
  - Autonomous actions must pause if error-12 volume exceeds 2× the rolling 30-day average for a garage
- **Rationale:** Autonomous resolution is severely constrained because the core work involves physical gate operations and financial payment processing, which must not be automated without human presence; the only narrow automation candidate is the SKIDATA session-close request for InstallErrors, which is formulaic and low-risk but represents only a fraction of total active time (~5 min of the 32 min per ticket). Feasibility is low overall due to vendor API access uncertainty and safety requirements.
- **Validation:** Pilot automated SKIDATA session-close request drafting and submission (with human approval step retained) for 4 weeks on a single low-volume garage; acceptance criteria: zero erroneous session closures, 100% audit trail completeness, and measurable reduction in support-agent action time for that step.

### Risks

- **Compliance concerns:**
  - Payment processing and financial checkout in SKIDATA must comply with applicable Austrian and EU payment regulations; any automation touching payment finalization requires legal review
  - Automated gate-opening actions may have liability implications if a vehicle is incorrectly identified or a security incident occurs
  - GDPR: vehicle license-plate data and parking session records processed in daily reports constitute personal data and must be handled per EU data-protection requirements
- **Must not automate:**
  - Physical gate opening (Handöffnung) — requires on-site human judgment for safety and security
  - Manual checkout and payment processing in SKIDATA — financial transaction finalization must have human authorization
  - Customer communications directing users to contact BMove — must not be sent without agent review to avoid misinformation
  - Anomaly/spike investigation — requires human judgment to assess whether a garage issue is systemic or safety-relevant
- **Vendor dependencies blocking automation:**
  - BMove recognition fix is entirely dependent on the BMove vendor's roadmap, API access, and willingness to share diagnostic data; no internal engineering team can resolve error code 12 unilaterally
  - SKIDATA session-close API access and write permissions must be granted and documented by SKIDATA before any automation of InstallError cleanup can proceed
  - Any changes to SKIDATA checkout or payment flows require SKIDATA vendor approval and may involve contractual change-order processes

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

