---
id: bmove-skidata-not-recognized-manual-open
name: bmove_skidata_not_recognized_manual_open
title: Bmove license plate not recognized by Skidata – manual gate opening required
description: Parking customers with active Bmove accounts are not recognized by Skidata parking barrier devices (error code
  12 – 'Bmove nicht erkannt'), preventing automatic gate opening. Agents must manually open the gate (Handöffnung) and subsequently
  process checkout or charge in the Skidata back-office, often encountering secondary failures such as checkout errors (Ausbuchung
  fehlgeschlagen) or inability to log in to the system. The pattern is highly recurring across multiple garages in Austria,
  predominantly at WST (078), G21 (099), PREW (101), GCP (013), and GVD (112).
category: end_user/integrations
ticket_class: end_user
issue_category: integration_issue
resolution_pattern: manual_close
languages:
- de
country_focus:
- at
- de
- other
status: active
cluster_id: BS:unknown|austria|no_label:c5
project_key: BS
cluster_size: 33
cluster_size_dedup: 33
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.65
median_resolution_minutes: 228.0
p95_resolution_minutes: 8868.8
cannot_reproduce_rate: 0.0
data_window_start: '2026-02-25'
data_window_end: '2026-04-07'
annual_hours_saved: 0.7
roi:
  baseline_active_hours: 3.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.1
  deflection_hours_range:
  - 0.1
  - 0.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.7
  agent_assist_hours_range:
  - 0.5
  - 0.9
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 3.2
  product_fix_hours_range:
  - 2.5
  - 3.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.2
  autonomous_resolve_hours_range:
  - 0.1
  - 0.2
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-50293
- BS-50134
- BS-50544
- BS-50886
- BS-51664
- BS-50294
- BS-50137
- BS-50133
- BS-50783
- BS-50131
- BS-50785
- BS-50543
- BS-51662
- BS-50889
- BS-50546
- BS-50130
- BS-50136
- BS-51036
canonical_examples:
- BS-50134
- BS-50543
- BS-50544
vendor_dependency:
  vendor_name: Skidata
  involves_vendor: true
  typical_wait_days: 1
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Automated creation of the structured sub-ticket from the PKC worklog batch ticket after
    a human agent has completed gate-open and checkout actions
  autonomous_resolve_safety_constraints:
  - Physical gate opening (Handöffnung) must never be triggered autonomously without confirmed on-site agent presence
  - Financial charge and checkout actions in Skidata back-office require human authorisation due to payment liability
  - Autonomous actions must be blocked until the human-completed gate-open step is confirmed in the ticket log
  - Any autonomous sub-ticket creation must be reviewed and approved by a Bmove support agent before closure
  - Skidata vendor dependency means autonomous flows could fail silently; a dead-man's switch must alert a human within 5
    minutes of failure
related_playbooks:
- bmove-app-operational-issues-austria
- hr-parking-transaction-reconciliation-discrepancy
- manual-debt-cancellation-request
- pkc-license-plate-purchase-logging
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

# Bmove license plate not recognized by Skidata – manual gate opening required

## What this pattern is

Parking customers with active Bmove accounts are not recognized by Skidata parking barrier devices (error code 12 – 'Bmove nicht erkannt'), preventing automatic gate opening. Agents must manually open the gate (Handöffnung) and subsequently process checkout or charge in the Skidata back-office, often encountering secondary failures such as checkout errors (Ausbuchung fehlgeschlagen) or inability to log in to the system. The pattern is highly recurring across multiple garages in Austria, predominantly at WST (078), G21 (099), PREW (101), GCP (013), and GVD (112).

## When this applies

- Bmove subscriber drives to parking barrier; Skidata device does not recognize the license plate
- Skidata device returns error code 12 ('Bmove nicht erkannt')
- Customer is blocked at the exit barrier and cannot leave
- Occasional secondary failure: Skidata checkout (Ausbuchung) fails with install error or KEZ not found

## Typical resolution flow

1. Skidata device logs error code 12 – Bmove nicht erkannt for the vehicle's license plate
2. On-site agent or PKC hotline receives the incident and triggers manual gate opening (Handöffnung)
3. Agent attempts to check out (ausbuchen) the session in Skidata back-office and charge the customer
4. If checkout fails (Ausbuchung fehlgeschlagen / Installerror), agent escalates to Bmove support (BS ticket created)
5. Bmove support agent checks session status in Skidata and Bmove backend; manually closes session if still open
6. Customer is charged the applicable fee manually or session is closed at €0 if applicable
7. Ticket is resolved and closed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Manual gate opening (Handöffnung) to unblock the customer at the barrier | on-site garage agent or PKC hotline | SKIDATA device / intercom | 5 min |
| Manual checkout and fee collection in Skidata back-office | PKC agent or Bmove support agent | SKIDATA back-office | 10 min |
| Check and close open session in Skidata when automated checkout fails | Bmove support agent | SKIDATA back-office / Bmove backend | 10 min |
| Create structured sub-ticket from PKC worklog batch ticket | Bmove support agent | Jira / Bmove Support system | 3 min |

## Vendor dependency

- **Vendor:** Skidata
- **Typical wait:** 1 day(s)

## Evidence

Derived from 33 tickets in cluster `BS:unknown|austria|no_label:c5`. Direct quotes from 7 representative tickets:

- `BS-50134` _[de]_: "12 - Bmove nicht erkannt \| €6.- erfolgreich abgebucht \| W**** \| Handöffnung"
- `BS-50543` _[de]_: "Ausbuchung fehlgeschlagen - Installerror W**** Handöffnung"
- `BS-50544` _[en]_: "Hi @@Philip Siegmeth can you please close this session in Skidata. I get the same error like for LPN W****. Customer needs to be charged 3€."
- `BS-51662` _[de]_: "Ich kann mich nicht einwählen um den Kunden austztragen W**** Handöffnung"
- `BS-50889` _[de]_: "12 - Bmove nicht erkannt \| KEZ nicht gefunden \| W**** \| Handöffnung"
- `BS-50544` _[en]_: "I dont see the session open anymore in skidata , looks like its closed already"
- `BS-50546` _[de]_: "12 - Bmove nicht erkannt \| Technisches Problem PROBLEM \| Handöffnung"

## Cluster statistics

- **Volume:** 33 tickets total (33 unique semantic events after dedup)
- **Frequency:** 0.65 tickets/month (over data window 2026-02-25 → 2026-04-07)
- **Median resolution:** 3.8 hours
- **Languages:** de
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~3.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.7 (range [0.504, 0.936])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.65
- **Rationale:** Agent-assist can surface the correct manual-checkout procedure, pre-populate the Skidata back-office checklist, and auto-draft the structured sub-ticket (action 4, ~3 min), reducing cognitive load and lookup time; however, the largest time costs (physical gate open, back-office session closure) involve real-time system actions that assist tools cannot perform. Estimated 20% reduction in active minutes targets the documentation and ticket-creation steps.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool surfaces the Handöffnung checklist and pre-fills sub-ticket fields for agents at PKC hotline; measure average handle time before vs. after using call logs and ticket timestamps to validate the 20% reduction assumption.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~3.2 (range [2.5, 3.6])
- **Root cause:** Skidata barrier devices fail to recognise active Bmove accounts (error code 12 – 'Bmove nicht erkannt'), indicating a broken or degraded integration between the Bmove platform and Skidata's gate-control layer. Secondary failures (checkout errors, login problems in back-office) suggest both the real-time recognition API and the back-office reconciliation flow are affected.
- **Rationale:** A reliable fix requires diagnosing and remediating the Skidata↔Bmove integration protocol at multiple garages, coordinating with Skidata (vendor dependency, ~1-day typical wait per issue) and validating across all five sites; full elimination of manual work is feasible but depends heavily on Skidata cooperation and API stability. Upper bound of hours eliminated is capped at baseline (3.6 h/year).
- **Validation:** Engineering should instrument the Bmove↔Skidata API calls at one pilot garage (e.g. WST 078) to capture error-code-12 triggers, then run a 4-week regression with Skidata in a staging environment before live rollout; acceptance criterion is zero error-code-12 events over a 2-week soak period.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.035, 0.065])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** This pattern requires physical gate intervention and back-office system access by trained staff; a self-service FAQ or chatbot cannot unblock a barrier or perform Skidata checkout actions on behalf of the customer. Deflection potential is negligible because the root cause is a real-time hardware-software integration failure, not a customer knowledge gap.
- **Validation:** Deploy a targeted help-center article at the 5 affected garages explaining the Bmove error code 12 and advising customers to call the PKC hotline; measure call volume and ticket creation rate over 4 weeks to confirm that article awareness does not reduce inbound contacts.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.2 (range [0.126, 0.234])
- **Narrow use case:** Automated creation of the structured sub-ticket from the PKC worklog batch ticket after a human agent has completed gate-open and checkout actions
- **Safety constraints:**
  - Physical gate opening (Handöffnung) must never be triggered autonomously without confirmed on-site agent presence
  - Financial charge and checkout actions in Skidata back-office require human authorisation due to payment liability
  - Autonomous actions must be blocked until the human-completed gate-open step is confirmed in the ticket log
  - Any autonomous sub-ticket creation must be reviewed and approved by a Bmove support agent before closure
  - Skidata vendor dependency means autonomous flows could fail silently; a dead-man's switch must alert a human within 5 minutes of failure
- **Rationale:** Only the sub-ticket creation step (action 4, ~3 min) is safely automatable without physical or financial risk; gate opening and fee collection require human judgement and accountability, and the vendor integration fragility makes broader automation unreliable. Even within this narrow scope, hours saved are modest given the low annual frequency.
- **Validation:** Pilot automated sub-ticket generation for 4 weeks on tickets tagged with error-code-12 after human agent marks checkout as complete; acceptance criteria are 100% sub-ticket accuracy rate and zero instances of premature closure before human sign-off.

### Risks

- **Compliance concerns:**
  - Fee collection and parking charge processing are financial transactions subject to Austrian consumer protection and payment regulations; errors in automated checkout could create disputed charges or refund obligations
  - Audit trail requirements: any automated gate-opening or session-closure must be fully logged with timestamps and agent identifiers for liability purposes
- **Must not automate:**
  - Physical gate opening (Handöffnung) – requires confirmed on-site human presence and safety accountability
  - Skidata back-office checkout and fee charge – involves financial liability and must have human authorisation
  - Closing open parking sessions in Skidata when automated checkout has already failed – risk of double-charge or data corruption without human review
- **Vendor dependencies blocking automation:**
  - Skidata controls the barrier device firmware and back-office API; any integration fix requires Skidata cooperation and their typical 1-day response time per incident introduces delays
  - Root-cause diagnosis of error code 12 requires Skidata to share internal API documentation or provide a staging environment for joint debugging
  - Multi-garage rollout of a fix depends on Skidata performing coordinated updates across WST (078), G21 (099), PREW (101), GCP (013), and GVD (112), each potentially requiring separate change windows

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

