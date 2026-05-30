---
id: croatia-b2b-parking-card-refund-request
name: croatia_b2b_parking_card_refund_request
title: Croatian B2B Partner (ZGH) Requesting Refunds for Erroneously Purchased Parking Cards
description: Zagrebački holding d.o.o. (ZGH), acting as a B2B intermediary, forwards end-user complaints about erroneously
  purchased or duplicated parking cards to the support team. The cards have already been cancelled/stornoed on the ZGH side,
  and ZGH requests that the monetary refund be processed back to the end user's IBAN. The pattern is highly repetitive and
  standardized, with the same ZGH contact (Tomislav Hac) initiating the majority of tickets.
category: b2b_operator/billing
ticket_class: b2b_partner
issue_category: billing
resolution_pattern: refund_issued
languages:
- hr
country_focus:
- hr
status: active
cluster_id: BS:b2b_partner|croatia|koncesionar:c3
project_key: BS
cluster_size: 44
cluster_size_dedup: 44
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.96
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.86
median_resolution_minutes: 3987.5
p95_resolution_minutes: 15833.85
cannot_reproduce_rate: 0.0
data_window_start: '2024-03-19'
data_window_end: '2026-01-30'
annual_hours_saved: 2.0
roi:
  baseline_active_hours: 5.7
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.1
  deflection_hours_range:
  - 0.1
  - 0.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 2.0
  agent_assist_hours_range:
  - 1.4
  - 2.6
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 4.3
  product_fix_hours_range:
  - 3.0
  - 5.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.3
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-45949
- BS-46492
- BS-46335
- BS-19560
- BS-42154
- BS-44528
- BS-47721
- BS-42834
- BS-48281
- BS-46677
- BS-44620
- BS-42318
- BS-42465
- BS-44850
- BS-42171
- BS-45509
- BS-47871
- BS-48108
canonical_examples:
- BS-45949
- BS-42465
- BS-44528
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
  note: Financial action — agent drafts, human approves
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-acknowledge ZGH refund request and pre-validate IBAN format + cancellation confirmation
    presence before routing to human agent — no autonomous bank transfer execution.
  autonomous_resolve_safety_constraints:
  - Bank transfer execution (action 4) must always be performed by an authorised human payment colleague — no autonomous outbound
    fund movement.
  - iGeus storno action must be human-confirmed to avoid incorrect cancellation of valid cards.
  - IBAN and beneficiary data must be validated but never stored or forwarded without agent review, to comply with GDPR and
    financial data handling requirements.
  - Autonomous steps limited to intake parsing, format validation, and routing; no financial decisions.
related_playbooks:
- austrian-ticketless-incorrect-charge-refund
- b2b-partner-parking-card-storno-refund
- croatia-sms-parking-payment-failure
- croatian-b2b-parking-ticket-storno-refund
- croatian-b2b-parking-ticket-storno-request
- hr-b2b-parking-card-cancellation-refund
- hr-b2b-parking-card-storno-refund
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

# Croatian B2B Partner (ZGH) Requesting Refunds for Erroneously Purchased Parking Cards

## What this pattern is

Zagrebački holding d.o.o. (ZGH), acting as a B2B intermediary, forwards end-user complaints about erroneously purchased or duplicated parking cards to the support team. The cards have already been cancelled/stornoed on the ZGH side, and ZGH requests that the monetary refund be processed back to the end user's IBAN. The pattern is highly repetitive and standardized, with the same ZGH contact (Tomislav Hac) initiating the majority of tickets.

## When this applies

- End user purchases a parking card with incorrect registration plate
- End user accidentally purchases duplicate or multiple parking cards
- End user purchases a card for a zone where parking was not required or available
- Payment app malfunction causes duplicate charge
- ZGH cancels (stornira) the card on their side and requests monetary refund from Bmove/payment processor

## Typical resolution flow

1. End user contacts ZGH (via ZGP Povrati email) to report erroneous purchase and provides IBAN for refund
2. ZGH contact (Tomislav Hac or colleague) forwards the request to Bmove support, confirming card is cancelled on their side and providing end-user IBAN
3. Bmove support agent identifies the transaction code(s) in IGeus system
4. Agent stornos the card(s) in IGeus and tags the responsible colleague (e.g., Lidija Petricević) for payment processing
5. Payment colleague executes the bank transfer refund to end-user IBAN
6. Ticket is closed with confirmation that refund has been executed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Forward refund request with end-user IBAN and cancellation confirmation | ZGH B2B contact (Tomislav Hac) | email | 5 min |
| Look up transaction code(s) in IGeus and storno the card(s) | Bmove support agent | IGeus | 10 min |
| Tag payment colleague and provide refund details (amount, IBAN, beneficiary name) | Bmove support agent | Ticket comment / internal tagging | 5 min |
| Execute bank transfer refund to end-user IBAN | Payment colleague (Lidija Petricević or similar) | Banking system (Erste or equivalent) | 10 min |
| Confirm refund completion to ZGH | Bmove support agent | Ticket comment / email | 3 min |

## Evidence

Derived from 44 tickets in cluster `BS:b2b_partner|croatia|koncesionar:c3`. Direct quotes from 5 representative tickets:

- `BS-45949` _[hr]_: "Molim da izvršite povrat sredstava za pogrešno kupljenu kartu. Karte je kod nas poništena"
- `BS-42465` _[hr]_: "@@Lidija Petricević molim te povrat u iznosu od 11,90 € za Erste kupovinu 3d5p7-py22e-b25 (Tjedna parkirališna karta; Zona 2; Zagreb). Stornirano u IGeusu. Podaci za povrat: Božo Crnković HR2923600003"
- `BS-44528` _[hr]_: "Novac vraćen korisnici. Poštovani, povrat je izvršen."
- `BS-46335` _[hr]_: "Za ovaj IBAN mi banka vraća da se ne podudara ime primatelja. Jel da provedem povrat bez obzira ili će se to provjeriti?"
- `BS-19560` _[hr]_: "Navedena karta poništena je prije izrade računa te ista nije evidentirana na računu za 1.mjesec. Molim još jednom provjeru da li ćete izvršiti povrat?"

## Cluster statistics

- **Volume:** 44 tickets total (44 unique semantic events after dedup)
- **Frequency:** 0.86 tickets/month (over data window 2024-03-19 → 2026-01-30)
- **Median resolution:** 2.8 days
- **Languages:** hr
- **Country focus:** hr

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~5.7 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~2 (range [1.4, 2.6])
- **Time reduction per ticket:** ~35% (range [25%, 45%])
- **Feasibility:** 0.85
- **Rationale:** The workflow is highly templated: look up transaction in iGeus, storno, extract IBAN/amount, tag payment colleague, confirm. An agent-assist tool can pre-populate the iGeus lookup, draft the payment-colleague tag message, and auto-fill the confirmation reply, reducing active work per ticket from ~33 min toward ~21 min. The ~35% reduction estimate reflects that the bank-transfer execution step (action 4) remains human.
- **Validation:** Run shadow-mode assist (auto-drafts visible to agent but not sent) for 3 weeks covering at least 3 tickets; measure draft acceptance rate and actual time-on-ticket vs. 33-min baseline.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~4 (range [3, 5])
- **Hours eliminated per year:** ~4.3 (range [3.01, 5.59])
- **Root cause:** Root cause is user error or duplicate purchase by end users of ZGH's parking platform, not a software defect in Bmove's product. However, the absence of a duplicate-purchase guard or a self-service cancellation/refund flow in the ZGH-facing integration likely inflates volume. An API-level refund endpoint or an automated duplicate-detection flag at purchase time could eliminate the manual support loop.
- **Rationale:** Building a duplicate-purchase prevention guard and/or a B2B self-service refund API for ZGH could eliminate the majority of these tickets, since the workflow is highly standardised and always follows the same path. Estimated elimination rate is ~75% of baseline (4.3 h of 5.7 h), capped at baseline; residual tickets cover edge cases requiring manual review.
- **Validation:** Engineering team should audit the ZGH integration API to confirm whether a refund endpoint and duplicate-check hook are feasible within existing architecture; spike in sprint 1, then re-estimate.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.035, 0.065])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** This pattern is B2B-initiated by a single named intermediary (ZGH/Tomislav Hac) forwarding end-user refund requests; the trigger is an operational error on the purchaser side, not an information gap that self-service content could prevent. Deflection via FAQ or help-center is structurally inappropriate since the contact must transmit IBAN and cancellation confirmation to initiate the refund.
- **Validation:** Confirm over a 4-week observation window whether any ZGH-initiated tickets could have been resolved without human handoff; expect near-zero deflection rate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.5 (range [0.35, 0.65])
- **Narrow use case:** Auto-acknowledge ZGH refund request and pre-validate IBAN format + cancellation confirmation presence before routing to human agent — no autonomous bank transfer execution.
- **Safety constraints:**
  - Bank transfer execution (action 4) must always be performed by an authorised human payment colleague — no autonomous outbound fund movement.
  - iGeus storno action must be human-confirmed to avoid incorrect cancellation of valid cards.
  - IBAN and beneficiary data must be validated but never stored or forwarded without agent review, to comply with GDPR and financial data handling requirements.
  - Autonomous steps limited to intake parsing, format validation, and routing; no financial decisions.
- **Rationale:** Full autonomous resolution is blocked by the requirement to execute a bank transfer and perform an iGeus storno, both of which carry financial and data-integrity risk; partial automation of intake triage and IBAN-format pre-check can save a small portion of active time per ticket (~3–5 min on action 1 routing). Savings are modest given the low annual frequency.
- **Validation:** Pilot auto-triage routing for 8 weeks: bot parses incoming ZGH emails, validates IBAN format, and creates a pre-filled ticket — measure time saved on agent intake step vs. manual baseline, with human override logged for every ticket.

### Risks

- **Compliance concerns:**
  - IBAN and beneficiary name constitute personal financial data under GDPR; any automated parsing or storage must comply with data minimisation and purpose-limitation principles.
  - Refund execution involves outbound bank transfers; Croatian banking regulations and internal financial controls require authorised human sign-off.
  - B2B contract with ZGH may impose SLA or processing obligations that constrain automation scope.
- **Must not automate:**
  - Bank transfer execution to end-user IBAN (action 4) — must remain with authorised payment colleague.
  - iGeus storno of parking cards (action 2) — incorrect storno of a valid card would cause direct customer harm.
  - Final confirmation to ZGH without human verification that transfer was actually completed.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.96)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Financial action — agent drafts, human approves

