---
id: hr-b2b-parking-card-storno-refund
name: hr_b2b_parking_card_storno_refund
title: 'Croatian B2B Partner: Parking Card Cancellation and Refund Requests'
description: B2B partners (primarily Zagrebački holding / ZGParking) contact Bmove Support to cancel (storno) incorrectly
  purchased or invalid parking cards and request refunds to end users' bank accounts or Aircash wallets. The tickets are initiated
  when an end user purchased a parking card for the wrong vehicle, wrong zone, wrong time period, or a duplicate charge, and
  the parking operator has already voided the card on their side. Bmove then processes the transaction reversal and confirms
  fund return.
category: b2b_operator/billing
ticket_class: b2b_partner
issue_category: billing
resolution_pattern: refund_issued
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:b2b_partner|croatia|no_label:c3
project_key: BS
cluster_size: 74
cluster_size_dedup: 74
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.93
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.45
median_resolution_minutes: 1877.0
p95_resolution_minutes: 11649.1
cannot_reproduce_rate: 0.0
data_window_start: '2023-05-15'
data_window_end: '2026-05-05'
annual_hours_saved: 3.5
roi:
  baseline_active_hours: 11.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.0
  deflection_hours_range:
  - 0.0
  - 0.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 3.5
  agent_assist_hours_range:
  - 2.5
  - 4.4
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 4.1
  product_fix_hours_range:
  - 2.9
  - 5.3
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.3
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-22059
- BS-53031
- BS-51678
- BS-8159
- BS-11370
- BS-15074
- BS-23624
- BS-52376
- BS-51813
- BS-15411
- BS-52698
- BS-32802
- BS-50692
- BS-51898
- BS-23111
- BS-49895
- BS-51376
- BS-8459
canonical_examples:
- BS-53031
- BS-51678
- BS-22059
vendor_dependency:
  vendor_name: Aircash / Erste Bank
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Financial action — agent drafts, human approves
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-acknowledgement and data-completeness check on inbound storno requests from ZGParking,
    flagging missing IBAN or cardholder fields before routing to agent
  autonomous_resolve_safety_constraints:
  - No autonomous execution of financial transactions (refunds to IBAN or Aircash wallet) without a human finance approver
  - Vendor API access to Aircash and Erste Bank required for any deeper automation; currently no confirmed programmatic refund
    endpoint
  - All storno decisions require validation against operator-side void confirmation — cannot be asserted by automation alone
  - 'GDPR compliance: IBAN and cardholder data must not be stored or processed outside approved systems during automated handling'
  - B2B partner relationship (ZGParking) demands human accountability for financial reversals
related_playbooks:
- austrian-ticketless-incorrect-charge-refund
- b2b-partner-parking-card-storno-refund
- croatia-b2b-parking-card-refund-request
- croatia-sms-parking-payment-failure
- croatian-b2b-parking-ticket-storno-refund
- croatian-b2b-parking-ticket-storno-request
- hr-b2b-parking-card-cancellation-refund
- hr-b2b-parking-ticket-storno-refund
- hr-b2b-r1-invoice-request
- igeus-portal-access-credential-management
- zagreb-parking-cancelled-ticket-refund
- zagrebparking-b2b-storno-refund-request
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

# Croatian B2B Partner: Parking Card Cancellation and Refund Requests

## What this pattern is

B2B partners (primarily Zagrebački holding / ZGParking) contact Bmove Support to cancel (storno) incorrectly purchased or invalid parking cards and request refunds to end users' bank accounts or Aircash wallets. The tickets are initiated when an end user purchased a parking card for the wrong vehicle, wrong zone, wrong time period, or a duplicate charge, and the parking operator has already voided the card on their side. Bmove then processes the transaction reversal and confirms fund return.

## When this applies

- End user purchased a parking card for the wrong vehicle registration
- End user purchased a parking card for the wrong zone
- End user purchased a duplicate parking card
- Parking card was issued for the wrong validity period due to a system error
- Parking operator (ZGParking/Zagrebački holding) has already cancelled/voided the card on their side
- End user received a parking fine due to an incorrectly issued card

## Typical resolution flow

1. End user contacts parking operator (ZGParking/Zagrebački holding) to report incorrect purchase
2. Parking operator voids/cancels the card in their system
3. Parking operator's representative (e.g. Tomislav Hac, Zagrebački holding) forwards refund request to Bmove Support via email, including IBAN and cardholder name
4. Bmove Support agent (internally) retrieves transaction code, amount, parking article, and registration details
5. Bmove agent tags internal colleague (e.g. Lidija Petricević) with storno details for Erste processing
6. Refund is executed to the user's IBAN or Aircash wallet
7. Bmove Support confirms to the parking operator that the refund has been completed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Receive forwarded refund/storno request with IBAN and cardholder data from parking operator | Bmove Support agent | email / ticketing system | 5 min |
| Look up transaction details (transaction code, amount, parking article, registration) | Bmove Support agent | Internal Bmove system | 10 min |
| Tag internal responsible colleague (e.g. Lidija Petricević) with storno and Erste payment details | Bmove Support agent | Ticketing system / internal comment | 5 min |
| Execute refund to end user's IBAN or Aircash wallet | Bmove Finance / Operations (Lidija Petricević or equivalent) | Erste Bank portal / Aircash back-end | 15 min |
| Confirm refund completion to the parking operator via ticket/email | Bmove Support agent | email / ticketing system | 5 min |

## Vendor dependency

- **Vendor:** Aircash / Erste Bank

## Evidence

Derived from 74 tickets in cluster `BS:b2b_partner|croatia|no_label:c3`. Direct quotes from 7 representative tickets:

- `BS-53031` _[hr]_: "Molim da izvršite povrat sredstava za pogrešno kupljenu kartu. Karta je kod nas poništena."
- `BS-51678` _[hr]_: "Erste storno i podatci Transaction code: zrcy1-98gdx-q95 Iznos: 11,90 EUR Parking artikl: TJEDNA KPK 2. ZONA Registracija: ZG**** IBAN: HR47**********, Marinko Mamić"
- `BS-22059` _[hr]_: "predmetna transakcija je stornirana te su sredstva vraćena na Aircash novčanik korisnika."
- `BS-52376` _[hr]_: "Novac vraćen korisnici"
- `BS-8459` _[hr]_: "korisnik je putem Aircash aplikacije 15.05.2023. u 09:57:18h kupio tjednu kartu za 1. zonu u Zagrebu, no dobio je kartu koja vrijedi za period 10.-17.07.2023."
- `BS-32802` _[hr]_: "povrat i dalje nije izvršen jer je karta iz 10. mjeseca, a nismo dobili suglasnost između BIP-a i Zagrebparkinga što činiti u ovim situacijama jer taj novac nije kod Bmovea"
- `BS-50692` _[hr]_: "sve kupljene karte su u nadležnosti parking službi, pa Vas za ovaj problem molimo da im se javite direktno na: k****@rovinj.hr"

## Cluster statistics

- **Volume:** 74 tickets total (74 unique semantic events after dedup)
- **Frequency:** 1.45 tickets/month (over data window 2023-05-15 → 2026-05-05)
- **Median resolution:** 1.3 days
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~11.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~3.5 (range [2.5, 4.4])
- **Time reduction per ticket:** ~30% (range [22%, 38%])
- **Feasibility:** 0.80
- **Rationale:** The workflow is highly structured — lookup transaction details, tag finance colleague with standard storno fields, confirm completion — making it a strong candidate for AI-assisted pre-fill: auto-surfacing transaction records, pre-drafting the internal tag message for Lidija/equivalent, and generating the operator confirmation email. Steps 2, 3, and 5 (20 of 40 active minutes) are the primary targets, with a realistic 30% time reduction on the total ticket.
- **Validation:** Deploy shadow-mode agent assist for 3 weeks on new storno tickets: measure time-to-complete steps 2, 3, and 5 with vs. without pre-filled drafts; accept if ≥80% of drafts require no substantive agent edits and median active time drops by ≥20%.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~4.1 (range [2.9, 5.33])
- **Root cause:** Tickets arise from genuine end-user errors (wrong vehicle, zone, time period, or duplicate purchase) and operator-side voiding, not from a Bmove platform defect. The root cause is a UX gap — the card-purchase flow lacks sufficient confirmation guards (e.g., registration plate confirmation, zone map preview, duplicate-purchase warning) that would reduce mis-purchases before they occur.
- **Rationale:** Strengthening purchase confirmation UX (plate verification, zone preview, duplicate detection) could reduce mis-purchases by an estimated 30–50%, yielding a proportional drop in storno requests, but uptake depends on end-user behaviour and operator cooperation. Total annual hours eliminated is capped below the 11.6-hour baseline.
- **Validation:** A/B test enhanced confirmation flow for ZGParking cards over one quarter; compare storno ticket rate in test vs. control cohort to validate the 30–50% reduction assumption before broader rollout.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0, 0])
- **Form:** `none`
- **Deflection rate:** ~4% (range [3%, 5%])
- **Feasibility:** 0.05
- **Rationale:** These tickets originate from a vetted B2B partner (Zagrebački holding / ZGParking), not end users navigating a self-service portal; the operator has already voided the card on their side and must forward IBAN/cardholder data to Bmove, so there is no realistic FAQ or chatbot path that would deflect the contact. Deflection potential is effectively zero for this B2B-initiated flow.
- **Validation:** Add a structured web form for ZGParking to submit storno requests with all required fields pre-populated; measure whether form submissions replace email contacts over 8 weeks — expected deflection gain is near-zero but would validate the channel assumption.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.5 (range [0.35, 0.65])
- **Narrow use case:** Auto-acknowledgement and data-completeness check on inbound storno requests from ZGParking, flagging missing IBAN or cardholder fields before routing to agent
- **Safety constraints:**
  - No autonomous execution of financial transactions (refunds to IBAN or Aircash wallet) without a human finance approver
  - Vendor API access to Aircash and Erste Bank required for any deeper automation; currently no confirmed programmatic refund endpoint
  - All storno decisions require validation against operator-side void confirmation — cannot be asserted by automation alone
  - GDPR compliance: IBAN and cardholder data must not be stored or processed outside approved systems during automated handling
  - B2B partner relationship (ZGParking) demands human accountability for financial reversals
- **Rationale:** Full autonomous resolution is blocked by the mandatory human finance approver for payment execution and the absence of a confirmed programmatic refund API with Aircash/Erste Bank; the only safe autonomous slice is triage — auto-acknowledging receipt and checking data completeness — which saves only a fraction of Step 1's 5 minutes. Attempting broader automation would create unacceptable financial and compliance risk.
- **Validation:** Pilot automated intake bot for 6 weeks: bot acknowledges receipt and checks for mandatory fields (IBAN, cardholder name, transaction code, reason); measure reduction in back-and-forth emails due to missing data and agent time savings on Step 1; accept if ≥70% of requests pass completeness check without agent intervention.

### Risks

- **Compliance concerns:**
  - GDPR / Croatian data protection law: IBAN and personal cardholder data included in storno requests must be handled under a valid legal basis and must not persist in automation logs beyond necessary retention periods
  - PSD2 / payment regulation: Refund execution is a regulated payment operation requiring human authorisation; autonomous triggering of bank transfers is not permissible without explicit compliance sign-off
  - AML / fraud risk: Automated refund flows could be exploited via spoofed storno requests if sender authentication is not enforced
- **Must not automate:**
  - Execution of refunds to end-user IBANs or Aircash wallets without a human finance approver in the loop
  - Validation of whether the parking operator has genuinely voided the card — this requires human cross-check with operator-side system or confirmation
  - Any decision to approve or deny a refund request
- **Vendor dependencies blocking automation:**
  - Aircash: no confirmed programmatic refund API available for autonomous execution; all Aircash wallet reversals currently require manual finance action
  - Erste Bank: bank transfer execution requires internal finance team access and cannot be triggered via support tooling without a dedicated integration not currently in scope
  - ZGParking / Zagrebački holding: storno request format and data completeness vary; structured API or webhook from operator side would be prerequisite for deeper automation

## Agent compatibility

- **Status:** `active` (extraction confidence 0.93)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Financial action — agent drafts, human approves

