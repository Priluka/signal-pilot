---
id: wrong-parking-ticket-purchase-redirect
name: wrong_parking_ticket_purchase_redirect
title: End users requesting cancellation or refund for incorrectly purchased parking tickets
description: End users, predominantly in Croatia (HR), purchase parking tickets via the Bmove app with errors such as wrong
  vehicle registration plate, wrong parking zone, wrong vehicle type, or duplicate payments. They contact Bmove support requesting
  a storno (cancellation), refund, or correction, but Bmove has no authority to modify or cancel issued tickets and redirects
  users to the responsible local parking authority.
category: end_user/user_issues
ticket_class: end_user
issue_category: misuse
resolution_pattern: vendor_escalation
languages:
- hr
- en
- other
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|no_value|user_error:c1
project_key: BS
cluster_size: 65
cluster_size_dedup: 65
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.27
median_resolution_minutes: 1404.0
p95_resolution_minutes: 60396.399999999936
cannot_reproduce_rate: 0.0
data_window_start: '2022-02-15'
data_window_end: '2025-02-23'
annual_hours_saved: 1.0
roi:
  baseline_active_hours: 3.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 1.0
  deflection_hours_range:
  - 0.7
  - 1.3
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.0
  agent_assist_hours_range:
  - 0.7
  - 1.3
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.8
  product_fix_hours_range:
  - 0.6
  - 1.1
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.4
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-1843
- BS-2154
- BS-33916
- BS-121
- BS-788
- BS-2388
- BS-4413
- BS-7005
- BS-930
- BS-11925
- BS-21624
- BS-764
- BS-5951
- BS-664
- BS-7534
- BS-977
- BS-1576
- BS-7030
canonical_examples:
- BS-1843
- BS-7005
- BS-21624
vendor_dependency:
  vendor_name: Local parking authorities / parking concessionaires (e.g., Zagrebparking, Rijeka-plus, Opatija21, Komunalac
    Vukovar, Bratislava PAAS)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-send a templated 'Bmove cannot cancel tickets; contact your local parking authority'
    reply with pre-filled authority contact details when ticket details are confirmed in purchase history and no payment dispute
    is flagged.
  autonomous_resolve_safety_constraints:
  - Must never represent that Bmove can cancel or modify a ticket — any ambiguity must escalate to a human agent.
  - Must not handle cases involving payment disputes, double-charges, or potential fraud autonomously.
  - Must confirm ticket details exist in purchase history before sending authority redirect; unknown ticket IDs must escalate.
  - Must not send authority contact details if the relevant authority cannot be unambiguously identified from the zone/city
    data.
  - User must always be offered a human escalation path in the automated response.
related_playbooks:
- app-payment-failure-parking-ticket
- bmove-app-feedback-mixed-issues__7950cd
- croatia-parking-ticket-storno-user-error
- croatian-end-user-wrong-registration-storno-refund
- hr-open-session-after-garage-exit
- hr-parking-ticket-fine-after-paid-app
- parking-fine-received-despite-valid-payment
- parking-payment-failure-end-user
- prepaid-top-up-and-usage-issues
- slovakia-parking-payment-failure-no-ticket
- ticketless-open-session-at-exit__d8d1ba
- ticketless-open-session-at-exit__fd04ac
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# End users requesting cancellation or refund for incorrectly purchased parking tickets

## What this pattern is

End users, predominantly in Croatia (HR), purchase parking tickets via the Bmove app with errors such as wrong vehicle registration plate, wrong parking zone, wrong vehicle type, or duplicate payments. They contact Bmove support requesting a storno (cancellation), refund, or correction, but Bmove has no authority to modify or cancel issued tickets and redirects users to the responsible local parking authority.

## When this applies

- User enters wrong vehicle registration plate when purchasing a parking ticket
- User purchases ticket for wrong parking zone or wrong city
- User accidentally purchases duplicate parking tickets
- User purchases ticket for wrong vehicle type (e.g., bus instead of car)
- Payment appears charged but no ticket is confirmed in the app
- User enters wrong license plate format (e.g., vehicle description instead of plate number)

## Typical resolution flow

1. User purchases a parking ticket via Bmove app or web
2. User realizes an error (wrong plate, wrong zone, duplicate, wrong vehicle)
3. User contacts Bmove support via email or app feedback requesting storno/refund/correction
4. Bmove support verifies the ticket details in their system
5. Bmove support explains they have no authority to cancel or modify issued tickets per their disclaimer/terms
6. Bmove support redirects user to the responsible local parking authority (parking concessionaire) with contact details
7. Ticket is closed with no action taken by Bmove

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Review purchase history to confirm ticket details and payment status | support_agent | Bmove back-office system | 5 min |
| Inform user that Bmove cannot cancel or modify issued parking tickets per terms of service | support_agent | email / Jira | 5 min |
| Provide user with contact details of the relevant local parking authority | support_agent | email / Jira | 3 min |

## Vendor dependency

- **Vendor:** Local parking authorities / parking concessionaires (e.g., Zagrebparking, Rijeka-plus, Opatija21, Komunalac Vukovar, Bratislava PAAS)

## Evidence

Derived from 65 tickets in cluster `BS:end_user|no_value|user_error:c1`. Direct quotes from 6 representative tickets:

- `BS-1843` _[hr]_: "kako piše u našem disclaimeru - mi ne možemo poništavati i mijenjati već kupljene parkirne karte. Za navedeni upit molimo Vas da se obratite parking službi u Opatiju"
- `BS-7005` _[hr]_: "mi ne možemo stornirati krivo kupljene karte. Za to se morate obratiti parking koncesionaru jer su kupljene karte u njihovoj nadležnosti."
- `BS-21624` _[other]_: "Po zakúpení lístka, žiaľ nie je možné meniť údaje (dĺžku parkovania, poznávaciu značku, parkovaciu zónu, … ). Nie je možné ani vráťiť úhradu za vystavené parkovanie."
- `BS-664` _[hr]_: "storniranje karata isključivo može napraviti parking služba grada za koji ste platili parking. Molimo Vas da se javite u Zagrebparking"
- `BS-7030` _[hr]_: "Greškom sam uplatila mjesečnu kartu za krivu registraciju. Može li se sredstvo prebaciti na registraciju ispravnog automobila?"
- `BS-11925` _[en]_: "you have input the wrong license plate number in the app. In the license plate number field you input VWTOURAN, and in the vehicle description you input your license plate."

## Cluster statistics

- **Volume:** 65 tickets total (65 unique semantic events after dedup)
- **Frequency:** 1.27 tickets/month (over data window 2022-02-15 → 2025-02-23)
- **Median resolution:** 23.4 hours
- **Languages:** hr, en, other
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~3.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1 (range [0.693, 1.287])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.85
- **Rationale:** This pattern is highly templated: the agent always reviews purchase history, delivers a standard 'cannot cancel' explanation, and provides authority contact details. An assist tool that auto-surfaces the user's recent ticket data and pre-populates a response template with the relevant parking authority's contact info could cut active handling time by ~30%.
- **Validation:** Run agent-assist in shadow mode for 3 weeks (tool suggests response but agent sends manually); measure time-to-send and template acceptance rate; target ≥80% template acceptance and ≥20% time reduction to confirm value.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~2 (range [1.5, 2.5])
- **Hours eliminated per year:** ~0.8 (range [0.581, 1.07])
- **Root cause:** The root cause is user input error at purchase time combined with no post-purchase correction capability. Bmove lacks authority to modify or cancel issued tickets — this is a policy and vendor constraint, not a software defect. Engineering could add confirmation screens (plate/zone review step) or real-time plate format validation to reduce error rates upstream.
- **Rationale:** Adding a mandatory purchase-confirmation step (display plate, zone, vehicle type with explicit user confirmation) and basic plate-format validation could plausibly reduce purchase errors by 25%, eliminating a proportional share of support contacts. This is an estimate; actual error reduction depends on how many errors are typos vs. intentional misuse.
- **Validation:** A/B test the confirmation-step UI with 50% of users for 6 weeks; compare parking-error support ticket rate between cohorts to validate the 25% error-reduction assumption before full rollout.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1 (range [0.693, 1.287])
- **Form:** `in_app_help`
- **Deflection rate:** ~30% (range [21%, 39%])
- **Feasibility:** 0.65
- **Rationale:** A prominent in-app message at purchase confirmation — warning users to verify plate, zone, and vehicle type before paying — plus a clear post-purchase FAQ explaining that Bmove cannot cancel tickets and directing users to the relevant parking authority, could prevent a meaningful share of contacts. However, many users have already made the error by the time they contact support, limiting deflection ceiling.
- **Validation:** Deploy an in-app help banner and a FAQ article for 8 weeks; measure the ratio of parking-error contacts to parking transactions before and after; target ≥20% reduction in contact rate to confirm viability.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.5 (range [0.36, 0.66])
- **Narrow use case:** Auto-send a templated 'Bmove cannot cancel tickets; contact your local parking authority' reply with pre-filled authority contact details when ticket details are confirmed in purchase history and no payment dispute is flagged.
- **Safety constraints:**
  - Must never represent that Bmove can cancel or modify a ticket — any ambiguity must escalate to a human agent.
  - Must not handle cases involving payment disputes, double-charges, or potential fraud autonomously.
  - Must confirm ticket details exist in purchase history before sending authority redirect; unknown ticket IDs must escalate.
  - Must not send authority contact details if the relevant authority cannot be unambiguously identified from the zone/city data.
  - User must always be offered a human escalation path in the automated response.
- **Rationale:** Autonomous resolution is feasible only for the narrow, unambiguous subset where the ticket details are confirmed and the response is a pure redirect. The pattern involves vendor dependency and no Bmove-side action, making a simple scripted auto-reply low-risk, but the low annual volume (15.3 tickets/year) means absolute savings are minimal.
- **Validation:** Pilot with 20% of incoming tickets of this category for 6 weeks using a rule-based bot; measure false-positive rate (cases where auto-reply was wrong or incomplete) and user satisfaction; accept only if false-positive rate is below 5%.

### Risks

- **Compliance concerns:**
  - GDPR: Purchase history lookups involve personal data (vehicle registration plates, payment records); any automated processing must comply with applicable Croatian and EU data protection rules.
  - Consumer protection: Automated refusal responses must not misrepresent user rights under Croatian or EU consumer law; users may have statutory remedies Bmove's ToS cannot override.
  - Parking regulation: Different local authorities (Zagrebparking, Rijeka-plus, etc.) have different cancellation policies; a one-size-fits-all automated response may provide incorrect guidance if authority rules change.
- **Must not automate:**
  - Any case involving a potential double-charge or payment processing error — these require human review and possible financial remediation.
  - Cases where the user disputes the charge with their bank or payment provider (chargeback risk).
  - Cases where the parking authority is ambiguous or the ticket cannot be located in purchase history.
  - Any response that could be construed as legal or regulatory advice about the user's rights with the parking authority.
- **Vendor dependencies blocking automation:**
  - All actual ticket cancellation or correction authority rests with local parking concessionaires (Zagrebparking, Rijeka-plus, Opatija21, Komunalac Vukovar, Bratislava PAAS); Bmove has no API or direct integration to modify tickets, so no automation can resolve the underlying user problem.
  - Contact details and cancellation procedures for each authority must be kept current; stale information in automated responses could actively harm users.
  - Any future self-service cancellation feature would require formal agreements and technical integrations with each individual parking authority — a multi-vendor, multi-jurisdiction effort.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

