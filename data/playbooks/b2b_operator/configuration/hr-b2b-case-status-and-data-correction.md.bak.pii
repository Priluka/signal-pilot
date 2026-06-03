---
id: hr-b2b-case-status-and-data-correction
name: hr_b2b_case_status_and_data_correction
title: B2B Partner Requests for Manual Case Status Changes and Data Corrections in RAO System
description: Croatian B2B partners (enforcement agents, municipalities, courts) frequently request manual corrections to case
  statuses (e.g. reverting erroneous 'za obustavu', 'za obavijest', or other workflow statuses) and personal data updates
  (name/address changes based on notary decisions) in the RAO enforcement system. Errors are typically caused by operator
  mistakes or system automation glitches. Support staff perform the corrections directly in the backend system, usually resolving
  the issue promptly.
category: b2b_operator/configuration
ticket_class: b2b_partner
issue_category: configuration
resolution_pattern: configuration_change
languages:
- hr
country_focus:
- hr
status: active
cluster_id: RAOS:b2b_partner|Support|no_label:c3
project_key: RAOS
cluster_size: 55
cluster_size_dedup: 55
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.91
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.68
median_resolution_minutes: 243.5
p95_resolution_minutes: 27165.149999999885
cannot_reproduce_rate: 0.0
data_window_start: '2024-09-26'
data_window_end: '2026-04-24'
annual_hours_saved: 13.4
roi:
  baseline_active_hours: 67.1
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 2.7
  deflection_hours_range:
  - 1.9
  - 3.5
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 13.4
  agent_assist_hours_range:
  - 9.4
  - 17.4
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 20.1
  product_fix_hours_range:
  - 14.1
  - 26.1
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 3.2
  autonomous_resolve_hours_range:
  - 2.2
  - 4.2
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- RAOS-6372
- RAOS-968
- RAOS-5129
- RAOS-217
- RAOS-929
- RAOS-1553
- RAOS-2640
- RAOS-5739
- RAOS-5052
- RAOS-1000
- RAOS-6108
- RAOS-5781
- RAOS-1049
- RAOS-1027
- RAOS-6058
- RAOS-4957
- RAOS-5804
- RAOS-1979
canonical_examples:
- RAOS-2640
- RAOS-968
- RAOS-5129
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
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-revert a case status to the immediately prior state when the triggering event is
    a confirmed system automation glitch (not a human operator action), scoped to a whitelist of reversible statuses.
  autonomous_resolve_safety_constraints:
  - Only applicable to system-glitch-triggered transitions, never to operator-initiated changes, to avoid masking deliberate
    workflow decisions
  - Status reversion must be limited to a pre-approved whitelist of reversible statuses verified with legal/compliance team
  - All autonomous reversions must generate a full audit trail entry attributed to the automation, not a human agent
  - 'A human agent must review and approve each autonomous reversion within 24 hours (two-phase: auto-flag + human confirm)'
  - Personal data changes (name, address) must never be autonomously applied; notary decision documents require human verification
  - Partner must receive a notification and have a dispute window before the autonomous change is finalized
related_playbooks:
- android-ppc-device-setup-and-app-installation
- dubrovnik-pass-website-hours-notice-posting
- dubrovnik-pass-website-notice-management
- hr-b2b-monthly-invoice-generation-and-fiscalization
- hr-b2b-parking-operations-support
- hr-b2b-parking-price-change-request
- hr-b2b-photo-download-enablement
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

# B2B Partner Requests for Manual Case Status Changes and Data Corrections in RAO System

## What this pattern is

Croatian B2B partners (enforcement agents, municipalities, courts) frequently request manual corrections to case statuses (e.g. reverting erroneous 'za obustavu', 'za obavijest', or other workflow statuses) and personal data updates (name/address changes based on notary decisions) in the RAO enforcement system. Errors are typically caused by operator mistakes or system automation glitches. Support staff perform the corrections directly in the backend system, usually resolving the issue promptly.

## When this applies

- Operator accidentally sets wrong case status (e.g. 'za obustavu' instead of 'za obavijest')
- System automation places case in incorrect status
- Personal data (name, address) needs updating based on notary decision or court document
- Authorized signatory or contact person on official documents needs to be changed
- Email address for a partner becomes outdated or undeliverable
- Case history or process sequence appears incorrect

## Typical resolution flow

1. B2B partner identifies incorrect case status or outdated data in the system
2. Partner opens support ticket specifying case/subject number and desired status or data change
3. Support agent reviews the request and verifies the case
4. Support agent manually corrects the status or data in the backend RAO system
5. Support agent confirms the change to the partner via ticket comment
6. Ticket is closed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Manually change case status to the requested value in the RAO system | support_agent | RAO backend system | 10 min |
| Update personal data (name, address) of enforcement subject based on notary decision | support_agent | RAO backend system | 15 min |
| Update authorized signatory or official contact name on documents/invoices | development_team | RAO backend system | 30 min |
| Update partner email address in the system | support_agent | RAO backend system | 10 min |
| Investigate and escalate systemic automation issue causing incorrect status transitions | development_team | RAO backend system | 60 min |

## Evidence

Derived from 55 tickets in cluster `RAOS:b2b_partner|Support|no_label:c3`. Direct quotes from 6 representative tickets:

- `RAOS-2640` _[hr]_: "greškom djelatnika su predmeti stavljeni u status 'za obustavu'. Molim povrat u prethodni status"
- `RAOS-968` _[hr]_: "molim za promjenu podataka u sustavu za KATARINU PAVIČIĆ, OIB: 51100732206. Potrebno je promijeniti prezime ovršenice iz PAVIČIĆ u PETROVIĆ"
- `RAOS-5129` _[hr]_: "molimo Vas da nam izmijenite potpis na svim službenim aktima tj. da stavite brojeve službenih iskaznica umjesto imena i prezimena redara"
- `RAOS-6108` _[hr]_: "molimo da što prije izmjenite email adresu za našeg partnera Zračnu luku Dubrovnik, jer nam već dulje vrijeme dolazi ova obavijest"
- `RAOS-929` _[hr]_: "status predmeta je promijenjen prema Vašem zahtjevu"
- `RAOS-4957` _[hr]_: "problem je nastao zbog automatike koja prebacuje predmete sa obavijesti vozaču na ZA_OPN, a trenutno se gleda datum kreiranja akta"

## Cluster statistics

- **Volume:** 55 tickets total (55 unique semantic events after dedup)
- **Frequency:** 2.68 tickets/month (over data window 2024-09-26 → 2026-04-24)
- **Median resolution:** 4.1 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~67.1 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~13.4 (range [9.4, 17.42])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.75
- **Rationale:** Agent-assist tooling (pre-populated correction forms, case lookup shortcuts, and templated audit notes) could reduce the lookup and documentation overhead within each ticket action, particularly for the 10-15 min routine tasks (actions #1, #2, #4). The 30-60 min development tasks are less amenable to assist-layer acceleration.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-fills the RAO case ID, current status, and suggested target status from the inbound ticket text; measure active-minutes-per-ticket before and after go-live for a matched cohort of correction requests.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~5 (range [3.5, 6.5])
- **Hours eliminated per year:** ~20.1 (range [14.1, 26.13])
- **Root cause:** Two distinct root causes: (1) automation glitches in RAO workflow engine trigger incorrect status transitions (e.g. erroneous 'za obustavu' / 'za obavijest') without agent error, and (2) there is no automated integration path to ingest notary decisions for personal data updates, forcing manual corrections. Addressing (1) would eliminate action #1 and #5 tickets; addressing (2) would reduce action #2 burden.
- **Rationale:** Fixing the automation glitch (action #5 investigates these) could eliminate the subset of tickets caused by system errors (~30% of volume estimated); a notary-decision integration feed would reduce manual data entry. Both are medium-to-high engineering efforts given the specialized RAO enforcement domain and Croatian legal data formats.
- **Validation:** Engineering team should instrument RAO status-transition events to count glitch-triggered corrections versus operator-error corrections over 8 weeks; this separates fixable automation bugs from human error, tightening the elimination estimate before committing sprint capacity.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~2.7 (range [1.89, 3.51])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These tickets require backend system access to perform status reversions and data corrections; self-service is not viable because partners cannot correct the RAO system themselves. A help-center article explaining how to submit a well-structured correction request could marginally reduce back-and-forth, but cannot deflect the underlying work.
- **Validation:** Deploy a structured intake form (ticket template) for 4 weeks and measure whether average active minutes per ticket drops due to cleaner initial submissions; deflection cannot be validated directly as the work is inherently agent-performed.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~3.2 (range [2.24, 4.16])
- **Narrow use case:** Auto-revert a case status to the immediately prior state when the triggering event is a confirmed system automation glitch (not a human operator action), scoped to a whitelist of reversible statuses.
- **Safety constraints:**
  - Only applicable to system-glitch-triggered transitions, never to operator-initiated changes, to avoid masking deliberate workflow decisions
  - Status reversion must be limited to a pre-approved whitelist of reversible statuses verified with legal/compliance team
  - All autonomous reversions must generate a full audit trail entry attributed to the automation, not a human agent
  - A human agent must review and approve each autonomous reversion within 24 hours (two-phase: auto-flag + human confirm)
  - Personal data changes (name, address) must never be autonomously applied; notary decision documents require human verification
  - Partner must receive a notification and have a dispute window before the autonomous change is finalized
- **Rationale:** Fully autonomous correction of enforcement case statuses in a Croatian legal context carries significant compliance and liability risk; the narrow scope of auto-reverting confirmed system glitches at low volume (≤10%) is the only defensible starting point. Savings are modest because the autonomous path still requires human review before finalization.
- **Validation:** Pilot by having the system auto-flag suspected glitch-reversions (but not execute them) for 4 weeks; measure what fraction of flagged cases agents confirm vs. reject to calibrate true safe automation rate and refine the 10% volume cap before enabling auto-execution.

### Risks

- **Compliance concerns:**
  - RAO enforcement system changes affect legally binding case records under Croatian enforcement law; incorrect automated corrections could create liability for enforcement agents, municipalities, and courts
  - Personal data updates based on notary decisions must follow Croatian GDPR implementation requirements and notary document authentication standards
  - Audit trails for all case status changes are likely required under Croatian administrative procedure law; automation must preserve traceable, attributable records
  - Autonomous or semi-automated changes to enforcement statuses could affect creditor/debtor rights if applied incorrectly
- **Must not automate:**
  - Personal data (name, address) corrections — these require verified notary documents and human judgment on document authenticity
  - Authorized signatory or contact name updates on legal documents/invoices (action #3) — legal document integrity requires human sign-off
  - Any status change that affects whether enforcement proceeds or is suspended ('za obustavu') without human confirmation, given the legal consequences for parties involved
  - Systemic automation issue investigation and escalation (action #5) — root-cause analysis of glitches must remain human-led to avoid automated systems masking their own bugs

## Agent compatibility

- **Status:** `active` (extraction confidence 0.91)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Admin/operator-only configuration change

