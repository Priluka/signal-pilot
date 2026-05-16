---
id: pkc-license-plate-purchase-logging
name: pkc_license_plate_purchase_logging
title: PKC Parking Purchase Records Linked to License Plates
description: These tickets are automatically or manually created to log PKC (parking purchase/Kupovina) events tied to specific
  license plates and dates. Each ticket typically contains a license plate number, a date, and in some cases system log entries
  showing the creation of a 'Kupovina' (purchase) object with associated user, serial number, and parking unit (pbu_id) data.
  The tickets appear to serve as audit or tracking records for parking session purchases processed through the Bmove/SKIDATA/Arivo
  ecosystem.
category: internal_partner/integrations
ticket_class: internal_partner
issue_category: integration_issue
resolution_pattern: manual_close
languages:
- de
- en
- other
country_focus:
- at
- de
- other
status: draft
cluster_id: BS:unknown|austria|no_label:c3
project_key: BS
cluster_size: 56
cluster_size_dedup: 56
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.62
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.1
median_resolution_minutes: 2.0
p95_resolution_minutes: 154.75
cannot_reproduce_rate: 0.0357
data_window_start: '2025-02-12'
data_window_end: '2026-05-08'
annual_hours_saved: 0.8
roi:
  baseline_active_hours: 2.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.1
  deflection_hours_range:
  - 0.1
  - 0.2
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.8
  agent_assist_hours_range:
  - 0.6
  - 1.0
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.3
  product_fix_hours_range:
  - 0.9
  - 1.7
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.3
  - 0.6
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-48070
- BS-51937
- BS-46758
- BS-33498
- BS-47108
- BS-49191
- BS-51934
- BS-48149
- BS-49813
- BS-51939
- BS-48282
- BS-46555
- BS-52701
- BS-47916
- BS-53034
- BS-49879
- BS-49726
- BS-49824
canonical_examples:
- BS-33498
- BS-46758
- BS-48149
vendor_dependency:
  vendor_name: SKIDATA / Arivo
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: draft
  claude_skill: draft
  agent_assist: false
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-close tickets where system logs confirm a complete, error-free Kupovina object
    (all required fields present) with no anomalies in entry/exit timestamps
  autonomous_resolve_safety_constraints:
  - Must not auto-close if Kupovina log entry is absent or incomplete
  - Must not auto-close if entry/exit timestamp data is missing or inconsistent
  - Must not auto-close if the ticket contains any free-text complaint or dispute from a customer
  - Requires read-only API access to SKIDATA/Arivo — no write operations may be performed autonomously
  - All auto-closed tickets must be flagged for daily human spot-check audit
related_playbooks:
- bmove-app-operational-issues-austria
- bmove-skidata-not-recognized-manual-open
- hr-parking-transaction-reconciliation-discrepancy
- manual-debt-cancellation-request
- scs-westfield-open-session-daily-check__a69ff7
- scs-westfield-open-session-daily-check__c72ee4
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# PKC Parking Purchase Records Linked to License Plates

## What this pattern is

These tickets are automatically or manually created to log PKC (parking purchase/Kupovina) events tied to specific license plates and dates. Each ticket typically contains a license plate number, a date, and in some cases system log entries showing the creation of a 'Kupovina' (purchase) object with associated user, serial number, and parking unit (pbu_id) data. The tickets appear to serve as audit or tracking records for parking session purchases processed through the Bmove/SKIDATA/Arivo ecosystem.

## When this applies

- A parking purchase (Kupovina) event is registered for a specific license plate on a given date
- A license plate cannot be found in SKIDATA system
- Entry/exit data needs to be verified in Arivo for a specific date and time
- System log captures creation of a new Kupovina object with lpn, serial_number, valid_from, user, and pbu_id

## Typical resolution flow

1. Ticket is created with summary containing 'PKC', a date, and a license plate number
2. System log (if present) records Kupovina object creation with license plate, serial number, timestamp, user email, and pbu_id
3. Support agent checks SKIDATA or Arivo system for matching entry/exit records
4. Ticket is resolved or noted based on whether the record is found in the parking management system

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Search for license plate in SKIDATA system | support agent | SKIDATA | 5 min |
| Verify entry and exit data by date and time in Arivo | support agent | Arivo | 5 min |
| Log or review Kupovina object creation from system logs | system / support agent | Bmove backend / logging system | 2 min |

## Vendor dependency

- **Vendor:** SKIDATA / Arivo

## Evidence

Derived from 56 tickets in cluster `BS:unknown|austria|no_label:c3`. Direct quotes from 4 representative tickets:

- `BS-33498` _[en]_: "W**** not in skidata"
- `BS-46758` _[en]_: "In Arivo we have entry and exit data by searching 20.12.2025. jump to time 16:30h."
- `BS-48149` _[en]_: "Creating new Kupovina object with data: lpn: IL****, serial_number: 202601191128168600212808, valid_from: 2026-01-19 10:28:16.860000+00:00, user: k****@gmx.at, pbu_id: 734003"
- `BS-49813` _[en]_: "Creating new Kupovina object with data: lpn: W****, serial_number: 202602210857165100211808, valid_from: 2026-02-21 07:57:16.510000+00:00, user: f****@email.de, pbu_id: 1043130"

## Cluster statistics

- **Volume:** 56 tickets total (56 unique semantic events after dedup)
- **Frequency:** 1.1 tickets/month (over data window 2025-02-12 → 2026-05-08)
- **Median resolution:** 2 min
- **Cannot Reproduce rate:** 3.6%
- **Languages:** de, en, other
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.8 (range [0.55, 1.01])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.75
- **Rationale:** The resolution steps are highly structured and repetitive — license plate lookup, date/time cross-check, log review — making them strong candidates for an assist tool that pre-fetches SKIDATA and Arivo records and surfaces the Kupovina log excerpt automatically. This could compress the 10-minute lookup and verification steps significantly while still requiring agent sign-off.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-populates SKIDATA lookup results and log excerpts for each incoming ticket; measure actual agent time-to-close versus the 12-minute baseline to calibrate the reduction rate.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~1.3 (range [0.91, 1.69])
- **Root cause:** Tickets are intentional audit records of Kupovina (parking purchase) events in the Bmove/SKIDATA/Arivo ecosystem, not symptoms of a bug. The manual-close resolution pattern and low annual frequency suggest the process is working as designed but lacks full automation for ticket lifecycle management.
- **Rationale:** If the system could auto-validate Kupovina object creation success and auto-close tickets when all required fields (license plate, date, user, serial, pbu_id) are confirmed present in logs, roughly half the active work (verification steps) could be eliminated. Full elimination is unlikely due to vendor data dependency and edge-case investigation needs.
- **Validation:** Engineering should instrument a spike to determine whether SKIDATA/Arivo webhook payloads reliably carry all required Kupovina fields; if ≥90% of tickets in a 60-day sample would auto-pass validation, the effort estimate is sound.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.091, 0.169])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** These tickets appear to be system-generated audit or tracking records tied to backend integration events, not customer-initiated requests seeking self-service answers; there is no meaningful FAQ or chatbot path that would prevent their creation. End-user deflection is structurally inapplicable for internally-triggered logging tickets.
- **Validation:** Over a 4-week period, tag any tickets with an identifiable human submitter and assess whether an in-app parking receipt or status page could have substituted; if fewer than 10% are human-initiated, abandon deflection investment.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~0.5 (range [0.343, 0.637])
- **Narrow use case:** Auto-close tickets where system logs confirm a complete, error-free Kupovina object (all required fields present) with no anomalies in entry/exit timestamps
- **Safety constraints:**
  - Must not auto-close if Kupovina log entry is absent or incomplete
  - Must not auto-close if entry/exit timestamp data is missing or inconsistent
  - Must not auto-close if the ticket contains any free-text complaint or dispute from a customer
  - Requires read-only API access to SKIDATA/Arivo — no write operations may be performed autonomously
  - All auto-closed tickets must be flagged for daily human spot-check audit
- **Rationale:** A narrow subset of these tickets — those where the integration log is clean and all fields are verifiably populated — could be auto-closed without agent review. Given vendor dependency on SKIDATA/Arivo data availability and the audit nature of the records, autonomous resolution is limited to unambiguous success cases only.
- **Validation:** Pilot with a 30-day read-only simulation: apply the auto-close decision logic to incoming tickets without actually closing them, then have an agent verify whether the bot's decision would have been correct; target ≥95% accuracy before enabling live auto-close on up to 25% of volume.

### Risks

- **Compliance concerns:**
  - Parking purchase records may constitute financial transaction audit trails subject to data retention and auditability requirements under local or EU regulations (e.g., GDPR for license plate PII, fiscal record-keeping laws).
  - License plate data is personal data under GDPR; automated processing or storage must be justified under an appropriate legal basis and minimised.
- **Must not automate:**
  - Any ticket containing a customer dispute, billing discrepancy, or complaint about a parking charge must always route to a human agent.
  - Tickets flagged with anomalous or mismatched entry/exit records must not be auto-closed.
  - Deletion or modification of Kupovina audit records must never be performed autonomously.
- **Vendor dependencies blocking automation:**
  - SKIDATA / Arivo API access is required for agent-assist pre-fetching and any autonomous validation; availability and latency of this API are not confirmed and must be assessed before implementation.
  - Webhook or log payload completeness from the Bmove/SKIDATA/Arivo ecosystem is unverified; if vendor payloads are inconsistent, both agent-assist and autonomous-resolve implementations will require fallback handling.
  - No typical_wait_days data is available for the vendor, making it impossible to estimate SLA risk for tickets requiring vendor escalation.

## Agent compatibility

- **Status:** `draft` (extraction confidence 0.62)
- **Brainbox skill:** `draft`
- **Claude skill:** `draft`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

