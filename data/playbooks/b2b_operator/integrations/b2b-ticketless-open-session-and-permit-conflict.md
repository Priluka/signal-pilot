---
id: b2b-ticketless-open-session-and-permit-conflict
name: b2b_ticketless_open_session_and_permit_conflict
title: B2B partners with stuck open parking sessions or permit/ticketless billing conflicts
description: B2B partner users experience parking sessions that remain open after exiting a garage (ticketless system fails
  to close), or their license plate is charged via Bmove despite having an active Dauerparker (permanent parking) contract
  with the garage. Both cases result in incorrect charges or inability to re-enter the garage. Resolution typically requires
  manual session closure by support and/or linking the license plate to the permanent parking card in the backend.
category: b2b_operator/integrations
ticket_class: b2b_partner
issue_category: integration_issue
resolution_pattern: configuration_change
languages:
- de
- en
country_focus:
- at
- de
- other
status: active
cluster_id: BS:b2b_partner|no_value|no_label:c3
project_key: BS
cluster_size: 20
cluster_size_dedup: 19
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.91
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.37
median_resolution_minutes: 5247.0
p95_resolution_minutes: 109651.15000000002
cannot_reproduce_rate: 0.0
data_window_start: '2022-10-27'
data_window_end: '2026-01-16'
annual_hours_saved: 0.7
roi:
  baseline_active_hours: 2.6
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
  - 0.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.2
  product_fix_hours_range:
  - 1.6
  - 2.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.2
  autonomous_resolve_hours_range:
  - 0.1
  - 0.2
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-6321
- BS-6474
- BS-5561
- BS-4226
- BS-6992
- BS-44433
- BS-47925
- BS-5396
- BS-4227
- BS-43695
- BS-5104
- BS-2835
- BS-5984
- BS-6398
- BS-6647
- BS-6051
- BS-6197
- BS-6637
canonical_examples:
- BS-6992
- BS-4227
- BS-43695
vendor_dependency:
  vendor_name: BIP (Best in Parking) / garage operators
  involves_vendor: true
  typical_wait_days: 1
agent_compatibility:
  rag_consumable: true
  brainbox_skill: reference_only
  claude_skill: reference_only
  agent_assist: false
  autonomous_resolve: false
  note: Admin/operator-only configuration change
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: 'Automated data-collection step only: bot gathers Dauerparker card number and license
    plate from the customer before routing to a human agent.'
  autonomous_resolve_safety_constraints:
  - No autonomous financial adjustments or session closures without human agent review and approval
  - License plate and contract data must never be written to production backend systems without human confirmation
  - All cases involving an incorrect charge must be reviewed by a human before any refund or billing correction is issued
  - Vendor (BIP/garage operator) interactions must remain human-initiated until a validated API contract is in place
  - B2B partner SLA obligations require a named human contact point for resolution communication
related_playbooks:
- b2b-parking-invoice-payment-issues
- b2b-partner-parking-card-storno-refund
- hr-b2b-partner-billing-payment-storno
- hr-b2b-sms-parking-payment-failure
- skidata-hosted-services-maintenance-notification
- zagreb-parking-cancelled-ticket-refund
- zagrebparking-b2b-storno-refund-request
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# B2B partners with stuck open parking sessions or permit/ticketless billing conflicts

## What this pattern is

B2B partner users experience parking sessions that remain open after exiting a garage (ticketless system fails to close), or their license plate is charged via Bmove despite having an active Dauerparker (permanent parking) contract with the garage. Both cases result in incorrect charges or inability to re-enter the garage. Resolution typically requires manual session closure by support and/or linking the license plate to the permanent parking card in the backend.

## When this applies

- Exit barrier does not register the vehicle leaving, leaving a parking session open in the app
- Customer exits after hours or during a technical failure of the ticketless system
- Customer with a Dauerparker (permanent parking) contract enters a garage where Bmove also operates, causing double billing
- License plate not yet linked to the permanent parking card in the Bmove backend
- Manual barrier opening by garage staff bypasses the Bmove session closure

## Typical resolution flow

1. Customer contacts support reporting a session still shown as active or an unexpected charge
2. Support identifies the open session in the backend system (e.g., Graylog or internal dashboard)
3. Support internally coordinates (e.g., tags a colleague) to verify session timestamps
4. Support manually closes the session with the correct amount or €0 depending on circumstances
5. If permit conflict: support requests license plate number and Dauerparker card number from customer
6. Support colleague links the license plate to the permanent parking card so Bmove does not trigger a new session
7. Customer is informed of resolution and advised to restart the app or temporarily disable Ticketless if needed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Manually close the open parking session with the correct charge amount | support agent | internal backend / Graylog | 15 min |
| Request Dauerparker card number and license plate from customer | support agent | email | 5 min |
| Link license plate to permanent parking card in backend to prevent future Bmove charges | support agent (or colleague) | internal backend system | 10 min |
| Advise customer to temporarily disable Ticketless feature while fix is in progress | support agent | email | 5 min |

## Vendor dependency

- **Vendor:** BIP (Best in Parking) / garage operators
- **Typical wait:** 1 day(s)

## Evidence

Derived from 20 tickets in cluster `BS:b2b_partner|no_value|no_label:c3`. Direct quotes from 7 representative tickets:

- `BS-6992` _[de]_: "Ich bin mir nicht sicher, wer von Ihnen für folgendes Problem zuständig ist... Unser GF wollte gestern in die Garage Mahü77 fahren und bekam am Eingang die Meldung, das Fahrzeug befinde sich bereits d"
- `BS-4227` _[de]_: "ICH BIN NICHT 9 TAGE IN DER GARAGE. BEENDEN SIE BITTE ENDLICH DIE SITZUNG."
- `BS-43695` _[de]_: "das Ausfahren / Abschließen hat in Bratislava nicht funktioniert. Somit hat der Mitarbeiter vor Ort, mich manuell abgeschlossen und ich habe mit einer anderen Karte bezahlt…direkt am Schranken. Jedoch"
- `BS-5104` _[de]_: "bucht die App aber automatisch Gebühren ab, obwohl wir ja einen Vertrag mit dem Betreiber haben, somit zahlen wir doppelt."
- `BS-6051` _[de]_: "Mein Kollege hat Ihr Kennzeichen zu der Karte hinzufügt. Jetzt werden Sie nicht in der Garage nicht mit Bmove abgebucht."
- `BS-47925` _[en]_: "I have a problem with the session that lasts 13 days. I was in SCS and they advised to contact your support. Please cancel this session because it is a mistake."
- `BS-6474` _[de]_: "beende es mit 14€ AF 05.03.2023 23:10 war 4. und 5.3.2023 (4+6€) drinnen, und hat noch die andere offene Sitzung die nicht abgebucht wurde (4€), diese beende ich mit 0€"

## Cluster statistics

- **Volume:** 20 tickets total (19 unique semantic events after dedup)
- **Frequency:** 0.37 tickets/month (over data window 2022-10-27 → 2026-01-16)
- **Median resolution:** 3.6 days
- **Languages:** de, en
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.7 (range [0.47, 0.845])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** The resolution workflow is highly procedural and consistent across tickets — session closure, data collection, backend linking — making it well-suited for an agent-assist playbook or guided script that reduces decision overhead and copy-paste steps. Time savings are moderate rather than large because active work per ticket is already low (35 min) and the main steps still require backend tool access.
- **Validation:** Run a 3-week shadow-mode pilot where agent-assist drafts the data-request message and pre-populates the backend linking form; measure average handle time before vs. after for this cluster.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~2.2 (range [1.6, 2.6])
- **Root cause:** Two distinct integration gaps: (1) the ticketless garage exit event is not reliably transmitted to or processed by the platform, leaving sessions open; (2) the Bmove billing flow does not check for an active Dauerparker contract against the vehicle license plate before applying charges, resulting in double-billing.
- **Rationale:** A reliable fix requires both a robust exit-event reconciliation mechanism with BIP/garage operators and a pre-billing contract lookup; vendor coordination makes timeline uncertain and may require protocol changes outside the platform's direct control. If fully delivered, most manual resolution steps are eliminated, saving up to the full baseline.
- **Validation:** Engineering should spike with BIP to confirm available exit-event API reliability and Dauerparker contract lookup endpoints before committing sprint estimates; a technical discovery spike of 1 sprint is recommended first.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.084, 0.15])
- **Form:** `help_center`
- **Deflection rate:** ~8% (range [6%, 10%])
- **Feasibility:** 0.25
- **Rationale:** These issues require backend intervention (session closure, license plate linking) that no end-user can perform themselves; a help-center article may reduce duplicate follow-up tickets but cannot deflect the initial support need. Deflection potential is therefore very low for this technically-gated B2B integration issue.
- **Validation:** Deploy a targeted help-center article explaining the Dauerparker/Bmove conflict and the stuck-session symptom; monitor ticket volume and article contact rate over 8 weeks to measure any deflection signal.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.2 (range [0.133, 0.247])
- **Narrow use case:** Automated data-collection step only: bot gathers Dauerparker card number and license plate from the customer before routing to a human agent.
- **Safety constraints:**
  - No autonomous financial adjustments or session closures without human agent review and approval
  - License plate and contract data must never be written to production backend systems without human confirmation
  - All cases involving an incorrect charge must be reviewed by a human before any refund or billing correction is issued
  - Vendor (BIP/garage operator) interactions must remain human-initiated until a validated API contract is in place
  - B2B partner SLA obligations require a named human contact point for resolution communication
- **Rationale:** Full autonomous resolution is blocked by the need for backend session closure and billing corrections that carry financial and contractual risk; only the structured data-collection sub-step (gathering card number and plate) is low-risk enough to partially automate. Even this narrow scope saves only the ~5-minute collection action on a capped fraction of volume.
- **Validation:** Pilot a chatbot data-collection flow on 10% of incoming tickets of this type for 6 weeks; measure data completeness rate on handoff to agent and customer satisfaction scores versus the all-human baseline before expanding scope.

### Risks

- **Compliance concerns:**
  - Incorrect billing corrections may violate B2B contract terms if not properly documented and approved
  - License plate data is personal data under GDPR; automated collection, storage, and linking must comply with applicable data-protection requirements
  - Any automated session closure that affects a financial charge constitutes a billing action and may require audit logging under local payment regulations
- **Must not automate:**
  - Closing an open parking session with a charge amount determination — requires human judgment on correct amount
  - Writing license plate-to-Dauerparker-card links in the production backend without human review
  - Issuing refunds or billing corrections to B2B partner accounts
  - Communicating resolution status to B2B partners without human sign-off given SLA and contractual sensitivity
- **Vendor dependencies blocking automation:**
  - BIP / garage operators must provide reliable, real-time exit-event API signals for ticketless session auto-closure to be feasible
  - Dauerparker contract data must be queryable via a stable BIP API for pre-billing contract lookup; currently this requires manual backend intervention
  - Typical vendor response time of ~1 day per issue means automation cannot bypass the vendor coordination step for live incidents

## Agent compatibility

- **Status:** `active` (extraction confidence 0.91)
- **Brainbox skill:** `reference_only`
- **Claude skill:** `reference_only`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Admin/operator-only configuration change

