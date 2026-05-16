---
id: internal-it-misc-tasks-hr
name: internal_it_misc_tasks_hr
title: RAO Internal IT & Miscellaneous Support Tasks (Croatia)
description: These tickets represent a recurring pattern of bundled internal IT support and administrative tasks performed
  by RAO support staff for internal colleagues and partner locations. Tasks typically include hardware setup (laptops, monitors,
  printers, peripherals), user account management (password resets, domain users, email creation), SAC system testing and
  communication with telecom operators, and miscellaneous errands. Each ticket groups multiple small unrelated tasks completed
  in a single work session.
category: internal_partner/configuration
ticket_class: internal_partner
issue_category: configuration
resolution_pattern: manual_close
languages:
- hr
country_focus:
- hr
- other
status: active
cluster_id: RAOS:internal_partner|Support interni zadaci|duplikat:c2
project_key: RAOS
cluster_size: 22
cluster_size_dedup: 22
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.88
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.07
median_resolution_minutes: 1.5
p95_resolution_minutes: 54.69999999999998
cannot_reproduce_rate: 0.0
data_window_start: '2025-12-03'
data_window_end: '2026-04-16'
annual_hours_saved: 5.8
roi:
  baseline_active_hours: 38.7
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 4.6
  deflection_hours_range:
  - 3.2
  - 6.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 5.8
  agent_assist_hours_range:
  - 4.1
  - 7.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.0
  product_fix_hours_range: null
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: not_applicable
  autonomous_resolve_hours_midpoint: 0.6
  autonomous_resolve_hours_range:
  - 0.4
  - 0.8
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-5587
- RAOS-6594
- RAOS-6225
- RAOS-5331
- RAOS-6044
- RAOS-6881
- RAOS-6418
- RAOS-5881
- RAOS-6756
- RAOS-6275
- RAOS-6491
- RAOS-5928
- RAOS-6898
- RAOS-5954
- RAOS-6643
- RAOS-6856
- RAOS-6820
- RAOS-6732
canonical_examples:
- RAOS-6594
- RAOS-5587
- RAOS-5331
vendor_dependency:
  vendor_name: HT / A1 / COMBIS / Instar / Info Kod
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Automated Office365/AD password reset via self-service portal triggered by internal
    user request
  autonomous_resolve_safety_constraints:
  - Password reset automation must enforce MFA verification before execution
  - Account changes must be limited to internal non-privileged users only; admin accounts excluded
  - All automated account actions must produce an immutable audit log entry
  - Hardware setup, domain join, and vendor coordination tasks must remain fully human-handled
  - Automation must halt and escalate if the requesting identity cannot be verified
related_playbooks:
- hr-b2b-monthly-invoice-generation-and-fiscalization
- hr-bmove-tools-request-verification__1f253d
- hr-bmove-tools-request-verification__e581c1
- hr-concessionaire-request-verification-bmove
- hr-internal-weekly-report-coordination
- hr-rao-recurring-support-requests
- internal-coordination-and-reporting
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

# RAO Internal IT & Miscellaneous Support Tasks (Croatia)

## What this pattern is

These tickets represent a recurring pattern of bundled internal IT support and administrative tasks performed by RAO support staff for internal colleagues and partner locations. Tasks typically include hardware setup (laptops, monitors, printers, peripherals), user account management (password resets, domain users, email creation), SAC system testing and communication with telecom operators, and miscellaneous errands. Each ticket groups multiple small unrelated tasks completed in a single work session.

## When this applies

- Internal colleague requests IT help (hardware, software, connectivity)
- SAC system card or device needs testing, setup, or operator communication
- New employee or equipment onboarding requires configuration
- Password or account reset needed for Office365, AD, or other systems
- Periodic batching of small internal tasks into a single ticket

## Typical resolution flow

1. IT support person identifies or receives multiple internal requests
2. Tasks are aggregated into a single ticket for the work session
3. Hardware issues are diagnosed and resolved on-site or remotely
4. User accounts, emails, and domain memberships are created or reset
5. SAC system cards and devices are tested or coordinated with telecom operators
6. Communication with external vendors (HT, A1, COMBIS, Instar) is performed as needed
7. Ticket is closed after all listed sub-tasks are completed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Laptop setup including domain join, AV install, email creation, and Slack onboarding | Internal IT support | Active Directory, Office365, Slack | 90 min |
| Password reset for Office365 or AD user | Internal IT support | Active Directory / Office365 | 10 min |
| SAC system card or device testing and communication with telecom operator | Internal IT support | SAC system, phone/email | 30 min |
| Hardware troubleshooting (monitors, printers, peripherals, network) | Internal IT support | — | 30 min |
| Communication with external vendors (COMBIS, HT, A1, Instar) | Internal IT support | email / phone | 20 min |

## Vendor dependency

- **Vendor:** HT / A1 / COMBIS / Instar / Info Kod

## Evidence

Derived from 22 tickets in cluster `RAOS:internal_partner|Support interni zadaci|duplikat:c2`. Direct quotes from 7 representative tickets:

- `RAOS-6594` _[hr]_: "Kreiranje domenskog usera i računala - Instalacija AV-a - Kreiranje maila - Ubacivanje u Slack"
- `RAOS-5587` _[hr]_: "Romani treba pomoći nešto oko laptopa (ima problema s wordom, printerom…) - Saši treba provjeriti periferiju koja ne radi."
- `RAOS-5331` _[hr]_: "resetirati Borku lozinku za Office365"
- `RAOS-6898` _[hr]_: "Komunikacija s A1 vezano za PULA SAC karticu Testiranje SAC sustava za Karlovac"
- `RAOS-6225` _[hr]_: "Mariniću treba osposobiti da mu rade monitori na dockingu. Leku treba pomoći oko osposobljavanja testnog kioska za Plitvice."
- `RAOS-6594` _[hr]_: "Komunikacija s COMBIS-om vezano za PAX uređaje"
- `RAOS-5881` _[hr]_: "Prebacivanje tehnološkog otpada i suvišnog namještaja na tavan."

## Cluster statistics

- **Volume:** 22 tickets total (22 unique semantic events after dedup)
- **Frequency:** 1.07 tickets/month (over data window 2025-12-03 → 2026-04-16)
- **Median resolution:** 2 min
- **Languages:** hr
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~38.7 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~5.8 (range [4.06, 7.54])
- **Time reduction per ticket:** ~15% (range [10%, 20%])
- **Feasibility:** 0.55
- **Rationale:** AI-assisted tooling can provide value on the documentation and communication sub-tasks — pre-filling vendor communication templates, suggesting standard onboarding checklists, and auto-populating ticket summaries — but the dominant time cost is physical hands-on work (hardware setup, cabling, troubleshooting) that no agent-assist tool can accelerate. Time savings are therefore modest and concentrated in a minority of each ticket's active minutes.
- **Validation:** Run shadow-mode agent-assist for 3 weeks on new tickets in this cluster, measuring time-on-ticket for the documentation and vendor-communication steps versus a control group; accept if average active minutes drop by ≥10%.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~4.6 (range [3.22, 5.98])
- **Form:** `help_center`
- **Deflection rate:** ~12% (range [8%, 16%])
- **Feasibility:** 0.35
- **Rationale:** These tickets bundle multiple hands-on physical tasks (hardware setup, domain join, peripheral troubleshooting) that inherently require human action and cannot be deflected by self-service documentation; only the simplest sub-tasks like password reset guidance or basic onboarding checklists have any deflection potential. The bundled, multi-task nature and physical hardware involvement keep feasibility and deflection rates very low.
- **Validation:** Deploy a help-center article covering Office365/AD password self-reset and a laptop onboarding checklist for 6 weeks; measure whether ticket inflow for those specific sub-tasks drops before attributing savings.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.6 (range [0.42, 0.78])
- **Narrow use case:** Automated Office365/AD password reset via self-service portal triggered by internal user request
- **Safety constraints:**
  - Password reset automation must enforce MFA verification before execution
  - Account changes must be limited to internal non-privileged users only; admin accounts excluded
  - All automated account actions must produce an immutable audit log entry
  - Hardware setup, domain join, and vendor coordination tasks must remain fully human-handled
  - Automation must halt and escalate if the requesting identity cannot be verified
- **Rationale:** Only password reset — a narrow, well-defined sub-task — is a realistic autonomous candidate; it represents a small fraction of each ticket's total active time (approximately 10 of 180 minutes) and appears in only a subset of tickets. All physical hardware tasks, SAC system testing, and vendor coordination require human presence and judgment, making full ticket automation unsafe and infeasible.
- **Validation:** Pilot a self-service password reset portal for internal Croatian staff for 8 weeks; measure how many password-reset sub-tasks are resolved without IT staff involvement and confirm zero unauthorized account changes before scaling.

### Risks

- **Compliance concerns:**
  - Account creation and domain join must comply with Croatian data protection regulations (GDPR/AZOP); automated provisioning must ensure proper data handling and logging
  - Audit trails for all user account actions (creation, password reset, email setup) are required under standard IT security policy
- **Must not automate:**
  - Laptop domain join and full user onboarding — requires physical presence and verified identity confirmation
  - SAC system card/device testing — involves telecom operator coordination and physical device handling
  - Hardware troubleshooting (monitors, printers, peripherals, network) — requires on-site diagnosis
  - Privileged or admin account management of any kind
  - External vendor communication with HT, A1, COMBIS, Instar, or Info Kod — requires human relationship context and contractual accountability
- **Vendor dependencies blocking automation:**
  - SAC system testing requires direct coordination with HT, A1, or other telecom operators — no API or automated handoff exists, blocking any automation of that sub-task
  - Hardware procurement and configuration tasks involving COMBIS or Instar require vendor-side scheduling and human sign-off, preventing end-to-end automation

## Agent compatibility

- **Status:** `active` (extraction confidence 0.88)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

