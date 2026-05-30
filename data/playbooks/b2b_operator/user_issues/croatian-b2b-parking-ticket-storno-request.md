---
id: croatian-b2b-parking-ticket-storno-request
name: croatian_b2b_parking_ticket_storno_request
title: Croatian B2B Partner Parking Ticket Cancellation (Storno) Requests
description: B2B partner staff (primarily from Tisak network) submit requests to cancel (storno) parking tickets that were
  issued incorrectly or not sold/charged. Common reasons include frozen cash registers that printed no ticket, wrong vehicle
  registration plates entered by customers or cashiers, customer abandonment of purchase, wrong parking zone selected, and
  system errors causing duplicate ticket issuance. The partner's accounting department (typically Grgo Medić or colleagues)
  escalates these to Bmove support for manual cancellation on the backend.
category: b2b_operator/user_issues
ticket_class: b2b_partner
issue_category: misuse
resolution_pattern: manual_close
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:b2b_partner|croatia|no_label:c2
project_key: BS
cluster_size: 17
cluster_size_dedup: 16
sample_size_used: 16
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.31
median_resolution_minutes: 73.0
p95_resolution_minutes: 6303.5999999999985
cannot_reproduce_rate: 0.0
data_window_start: '2023-07-25'
data_window_end: '2026-03-12'
annual_hours_saved: 0.4
roi:
  baseline_active_hours: 1.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.0
  deflection_hours_range:
  - 0.0
  - 0.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.4
  agent_assist_hours_range:
  - 0.3
  - 0.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 1.1
  product_fix_hours_range:
  - 0.8
  - 1.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.2
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-10776
- BS-11063
- BS-11226
- BS-11917
- BS-17657
- BS-24349
- BS-24402
- BS-28416
- BS-19774
- BS-17158
- BS-11398
- BS-15960
- BS-49911
- BS-40613
- BS-32244
- BS-50595
canonical_examples:
- BS-10776
- BS-11063
- BS-24349
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
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-cancel tickets where backend system logs confirm a duplicate issuance event within
    the same session for the same vehicle plate
  autonomous_resolve_safety_constraints:
  - Only apply to system-generated duplicates with unambiguous backend audit trail; never act on human-entry-error cases
  - Require an automated confirmation email to the B2B partner contact before the cancellation is committed, with a 30-minute
    hold window
  - Maintain a full audit log of every autonomous cancellation for financial reconciliation
  - Do not process cancellations that would affect already-settled accounting periods without human sign-off
  - Limit autonomous scope to ≤15% of annual storno volume until a 90-day pilot with zero error rate is confirmed
related_playbooks:
- croatia-b2b-parking-card-refund-request
- croatia-sms-parking-payment-failure
- croatian-b2b-parking-ticket-storno-refund
- hr-b2b-parking-card-cancellation-refund
- hr-b2b-parking-card-storno-refund
- hr-b2b-parking-ticket-storno-refund
- hr-b2b-r1-invoice-request
- igeus-portal-access-credential-management
- pkc-vehicle-registration-automated-tickets
- test-and-junk-tickets
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
# Skills enabled — reads auto-execute, writes are HITL.
allowed_skills:
  - graylog_search
  - parkis_lookup
  - skidata_session_lookup
  - bmove_user_lookup
  - datatrans_transaction
  - jira_get_history
  - jira_add_internal_comment
  - jira_add_public_comment
  - jira_transition
---

# Croatian B2B Partner Parking Ticket Cancellation (Storno) Requests

## What this pattern is

B2B partner staff (primarily from Tisak network) submit requests to cancel (storno) parking tickets that were issued incorrectly or not sold/charged. Common reasons include frozen cash registers that printed no ticket, wrong vehicle registration plates entered by customers or cashiers, customer abandonment of purchase, wrong parking zone selected, and system errors causing duplicate ticket issuance. The partner's accounting department (typically Grgo Medić or colleagues) escalates these to Bmove support for manual cancellation on the backend.

## When this applies

- Cash register froze and ticket was not printed or charged but may be recorded in the system
- Customer provided incorrect vehicle registration plate
- Customer abandoned purchase after ticket was issued
- Wrong parking zone was sold to the customer
- System error caused multiple duplicate tickets to be issued
- Ticket issued with incorrect amount (e.g., 65€ instead of 5€)
- Ticket recorded in system but not sold or charged at point of sale

## Typical resolution flow

1. Point-of-sale staff notices error and reports to Tisak accounting/helpdesk
2. Tisak accounting representative (e.g., Grgo Medić) compiles ticket serial number(s) and reason
3. Tisak representative emails Bmove support with storno request including ticket serial number and reason
4. Bmove support processes the cancellation on the backend system
5. Bmove support confirms cancellation to Tisak representative

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Submit storno request email with ticket serial number and reason | Tisak accounting representative | email | 5 min |
| Verify ticket status in backend system and process cancellation | Bmove support agent | Bmove backend system | 15 min |
| Confirm cancellation to requesting partner | Bmove support agent | email / ticket comment | 5 min |

## Evidence

Derived from 17 tickets in cluster `BS:b2b_partner|croatia|no_label:c2`. Direct quotes from 7 representative tickets:

- `BS-10776` _[hr]_: "Blagajna se zaledila te karta nije ispisana niti naplaćena . Molim vas ukoliko je karta zabilježena kod vas da ju stornirate te nas ne teretite za istu."
- `BS-11063` _[hr]_: "Molim vas storno karte zq4e3-vrskf-9t1 kupac odustao."
- `BS-24349` _[hr]_: "Molim storno niže satne karte -2 zona reg -HF-**** iznos 3 €-kupac je kupio krivu zonu"
- `BS-24402` _[hr]_: "Molim vas storno karte 6twhg-5eh5m-q18 reg. Oznaka OS****, Osijek 1. zona 1 sat. Kupac dao krivu reg. oznaku"
- `BS-49911` _[hr]_: "Prodavačica greškom izdala na 65,00 € umjesto na 5,00 €. Karta se nalazi na PM, te je izdana nova na 5,00 €."
- `BS-40613` _[hr]_: "Prilikom prodaje karte u 9:17 h izašla su 4 računa. Kupac je uzeo i platio samo jednu kartu... Ostala 3 računa bi trebalo stornirati"
- `BS-11917` _[hr]_: "Kod nas nije prodana ni naplaćena . Nema računa."

## Cluster statistics

- **Volume:** 17 tickets total (16 unique semantic events after dedup)
- **Frequency:** 0.31 tickets/month (over data window 2023-07-25 → 2026-03-12)
- **Median resolution:** 1.2 hours
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~1.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.4 (range [0.29, 0.51])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** An assist tool that auto-fetches ticket status from the backend when a storno email arrives and pre-populates the cancellation form could shorten the 15-min verification step by roughly 25%; the agent still exercises judgment on legitimacy and executes the cancellation, preserving human oversight. Volume is low enough that even modest time-per-ticket savings accumulate slowly.
- **Validation:** Run shadow-mode for 4 weeks: on receipt of storno emails, automatically query ticket status and surface results in the agent UI without taking action; measure reduction in time-to-verification compared to manual baseline.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~1.1 (range [0.8, 1.4])
- **Root cause:** Multiple distinct root causes drive storno requests: frozen cash registers that print no ticket yet charge the customer, no real-time duplicate-ticket detection, and absent input validation for vehicle registration plates and parking zones at point of sale. Eliminating these at the POS/system layer would prevent the majority of erroneous tickets from ever being issued.
- **Rationale:** Hardening POS terminal resilience (frozen register handling), adding duplicate-ticket guards, and enforcing plate/zone validation could eliminate an estimated 65–75% of storno triggers; customer abandonment cases would remain since those are behavioural. Engineering scope is high because changes likely span the Tisak POS integration, the Bmove backend, and potentially partner hardware.
- **Validation:** Engineering team should instrument storno reason codes over 3 months to confirm the frequency split between system errors vs. human errors, then spike a duplicate-detection prototype to validate backend feasibility before committing full sprint budget.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0.021, 0.039])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.15
- **Rationale:** Storno requests require backend cancellation by Bmove support staff; partners cannot self-serve the actual cancellation, so a FAQ or form can only marginally reduce back-and-forth clarification emails, not the core manual step. B2B accounting contacts are already procedurally competent, leaving almost no deflection upside.
- **Validation:** Deploy a structured intake web form for storno submissions pre-addressed to Bmove support over 8 weeks; measure whether clarification round-trips per ticket drop below current baseline.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.1 (range [0.1, 0.18])
- **Narrow use case:** Auto-cancel tickets where backend system logs confirm a duplicate issuance event within the same session for the same vehicle plate
- **Safety constraints:**
  - Only apply to system-generated duplicates with unambiguous backend audit trail; never act on human-entry-error cases
  - Require an automated confirmation email to the B2B partner contact before the cancellation is committed, with a 30-minute hold window
  - Maintain a full audit log of every autonomous cancellation for financial reconciliation
  - Do not process cancellations that would affect already-settled accounting periods without human sign-off
  - Limit autonomous scope to ≤15% of annual storno volume until a 90-day pilot with zero error rate is confirmed
- **Rationale:** Fully autonomous cancellation carries financial and accounting risk in a B2B context; the only safe narrow case is a system-confirmed duplicate where the evidence is unambiguous. Even under this constraint, the eligible volume is a small fraction of an already low annual frequency, making ROI minimal.
- **Validation:** Pilot over 90 days on duplicate-confirmed cases only; acceptance criteria are zero erroneous cancellations, 100% audit trail completeness, and partner confirmation of correct accounting reconciliation before expanding scope.

### Risks

- **Compliance concerns:**
  - Parking ticket cancellations affect financial records; incorrect stornos may create VAT or invoicing discrepancies under Croatian fiscal regulations
  - B2B partner accounting workflows may have audit requirements that mandate human sign-off on every cancellation
  - Data retention rules may require cancelled ticket records to be preserved for a minimum statutory period
- **Must not automate:**
  - Cancellations where the reason is ambiguous or disputed between the partner and end customer
  - Cancellations affecting already-closed accounting periods without explicit finance team approval
  - Any case where the ticket has already been used or validated in a parking enforcement system

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

