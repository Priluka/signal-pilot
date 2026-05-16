---
id: croatia-ticketless-rental-car-ghost-charge
name: croatia_ticketless_rental_car_ghost_charge
title: Tourists charged via Ticketless for rental cars they no longer hold
description: End users who visited Croatia and registered a rental car in their Bmove account continue to be charged via the
  automated Ticketless garage system after returning home, because the vehicle plate remains linked to their account. A subsequent
  renter of the same car triggers the automated charge against the original account holder. Customers contact support believing
  their account or card has been compromised, request refunds, and are advised to remove the vehicle and contact their bank.
category: end_user/knowledge_gaps
ticket_class: end_user
issue_category: knowledge_gap
resolution_pattern: user_education
languages:
- en
- hr
- other
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|croatia|ticketless:c0
project_key: BS
cluster_size: 148
cluster_size_dedup: 147
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.88
median_resolution_minutes: 1289.0
p95_resolution_minutes: 20153.600000000006
cannot_reproduce_rate: 0.0
data_window_start: '2023-05-04'
data_window_end: '2025-08-30'
annual_hours_saved: 3.2
roi:
  baseline_active_hours: 12.7
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 3.2
  deflection_hours_range:
  - 2.3
  - 4.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 3.2
  agent_assist_hours_range:
  - 2.3
  - 4.1
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 11.4
  product_fix_hours_range:
  - 8.9
  - 12.7
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 1.1
  autonomous_resolve_hours_range:
  - 0.8
  - 1.4
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-26666
- BS-29857
- BS-14596
- BS-7914
- BS-11684
- BS-19394
- BS-31468
- BS-20650
- BS-27837
- BS-24647
- BS-41359
- BS-27444
- BS-25294
- BS-24707
- BS-20194
- BS-21989
- BS-25412
- BS-25223
canonical_examples:
- BS-25223
- BS-25223
- BS-31468
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
  note: User education — safe for self-service deflection
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-send educational message + plate-removal instructions when an unexpected Ticketless
    charge is detected for a vehicle not actively rented by the account holder.
  autonomous_resolve_safety_constraints:
  - Never autonomously process or initiate a financial refund without agent review
  - Never close a ticket flagged as potential fraud or card compromise without human confirmation
  - Autonomous action limited to sending informational message and plate-removal deep-link only
  - Require human agent to confirm plate removal was completed before case closure
  - Do not autonomously advise bank dispute specifics due to potential financial and legal liability
related_playbooks:
- croatia-bmove-app-feedback-miscellaneous
- croatia-parking-fine-dispute
- croatia-parking-fine-dispute-and-payment
- croatia-parking-fine-payment-failure
- croatia-parking-payment-failure__ffdf4e
- croatia-parking-ticket-storno-user-error
- croatia-ticketless-best-in-parking-knowledge-gap
- croatia-ticketless-open-session-at-exit__f25b63
- croatian-end-user-wrong-registration-storno-refund
- croatian-invoice-download-request
- croatian-parking-debt-payment-failure
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__56d2b2
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- expired-card-deletion-ticketless-link
- hr-b2b-r1-invoice-request
- igeus-portal-access-credential-management
- italian-ticketless-setup-and-payment-issues
- open-session-at-exit-payment-failure
- phonzie-to-bmove-credit-refund-request
- prepaid-top-up-and-usage-issues
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Tourists charged via Ticketless for rental cars they no longer hold

## What this pattern is

End users who visited Croatia and registered a rental car in their Bmove account continue to be charged via the automated Ticketless garage system after returning home, because the vehicle plate remains linked to their account. A subsequent renter of the same car triggers the automated charge against the original account holder. Customers contact support believing their account or card has been compromised, request refunds, and are advised to remove the vehicle and contact their bank.

## When this applies

- User registered a rental car vehicle plate in their Bmove Ticketless account during a holiday in Croatia
- User returned the rental car and left Croatia without removing the vehicle from their Bmove account
- A subsequent renter of the same vehicle uses a Ticketless-enabled garage in Croatia
- The automated Ticketless system charges the original account holder whose plate is still registered

## Typical resolution flow

1. Customer receives unexpected parking receipt by email or bank notification while outside Croatia
2. Customer contacts Bmove support reporting unauthorized or fraudulent charge
3. Support identifies that the vehicle plate is still registered under the customer's Bmove Ticketless account
4. Support deactivates or confirms deletion of the Ticketless entry for that vehicle
5. Support explains the Ticketless mechanism and that they cannot identify or charge the actual user
6. Support advises customer to dispute the charge with their bank as Bmove cannot issue a refund

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Deactivate or confirm deletion of Ticketless registration for the implicated vehicle plate | support_agent | Bmove back-office | 5 min |
| Explain the Ticketless auto-charge mechanism to the customer | support_agent | — | 5 min |
| Advise customer to contact their bank to dispute/cancel the transaction | support_agent | — | 2 min |
| Occasionally issue direct refund (minority of cases) | support_agent | Bmove payment system | 10 min |

## Evidence

Derived from 148 tickets in cluster `BS:end_user|croatia|ticketless:c0`. Direct quotes from 7 representative tickets:

- `BS-25223` _[en]_: "someone used the automated Ticketless garage with the vehicle ZG****. Since you were still the holder of that vehicle in your Bmove account, the automated service was automatically charged to you."
- `BS-25223` _[en]_: "I returned my car to the rental on the 5th of August. I returned to my country, but today 07/08/2024 I received a notification from my card account that there was a 3 euro payment for a ticketless par"
- `BS-31468` _[en]_: "I am I the uk so please explain how my card has been charged for this and refund me the money. I have never ever been to Zagreb."
- `BS-19394` _[en]_: "A payment was made with my account and my credit card for parking in croatia but i'm not even in this country."
- `BS-14596` _[en]_: "Since we don't know who used the vehicle, we cannot grant a refund for a service that was used. If you did not used that car, you can explain the situation to your bank and ask them to cancel those ch"
- `BS-27444` _[en]_: "I used this rental car last May and then used your app. Now you send me a receipt from a parking I did not use with the Bmove app."
- `BS-27837` _[en]_: "The Ticketless activation is an option that is screened to you on the first login in the app. There you must manually add a payment method and a vehicle. There is also a skip button."

## Cluster statistics

- **Volume:** 148 tickets total (147 unique semantic events after dedup)
- **Frequency:** 2.88 tickets/month (over data window 2023-05-04 → 2025-08-30)
- **Median resolution:** 21.5 hours
- **Languages:** en, hr, other
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~12.7 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~3.2 (range [2.3, 4.1])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.80
- **Rationale:** The resolution steps are highly scripted and consistent (explain mechanism, confirm plate removal, advise bank contact), making this pattern well-suited for a pre-drafted macro or AI-suggested response that covers all three standard actions. Time savings are moderate because active handle time is already short at 22 minutes.
- **Validation:** Run a 3-week shadow-mode pilot: surface the suggested macro to agents on matching tickets and measure accept rate, edit rate, and actual handle time vs. historical median to validate the 25% reduction assumption.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~11.4 (range [8.9, 12.7])
- **Root cause:** The Ticketless plate-linking system has no automatic expiry or rental-period boundary; it is a UX/design gap rather than a code defect. The system behaves as designed but lacks a safeguard (e.g., rental end-date, inactivity expiry, or post-trip prompt to unlink) that would prevent continued charges after the rental concludes.
- **Rationale:** Adding a rental-end-date field or an inactivity-triggered prompt to remove the vehicle would eliminate the majority of these tickets; however, the fix requires integration with rental timing data or a heuristic (e.g., auto-unlink after N days of inactivity) which carries moderate engineering complexity. Hours eliminated are capped at the 12.7-hour baseline.
- **Validation:** Engineering team should spike on how rental end-date data could be sourced (user-entered vs. rental-company API); estimate refined after a 1-sprint technical discovery before committing to full build.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~3.2 (range [2.3, 4.1])
- **Form:** `help_center`
- **Deflection rate:** ~25% (range [18%, 32%])
- **Feasibility:** 0.65
- **Rationale:** The root cause is a knowledge gap — customers are unaware they must remove rental plates after returning home. A targeted help-center article or in-app prompt at vehicle-removal could deflect a meaningful share of contacts, but many customers will still reach out due to fraud anxiety and the urgency of an unexpected charge.
- **Validation:** Deploy a help-center article and in-app 'remove vehicle' reminder; track ticket volume for this cluster over a 6-week period pre/post and compare deflection rate against control baseline.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~1.1 (range [0.77, 1.43])
- **Narrow use case:** Auto-send educational message + plate-removal instructions when an unexpected Ticketless charge is detected for a vehicle not actively rented by the account holder.
- **Safety constraints:**
  - Never autonomously process or initiate a financial refund without agent review
  - Never close a ticket flagged as potential fraud or card compromise without human confirmation
  - Autonomous action limited to sending informational message and plate-removal deep-link only
  - Require human agent to confirm plate removal was completed before case closure
  - Do not autonomously advise bank dispute specifics due to potential financial and legal liability
- **Rationale:** Customers frequently contact support believing their account is compromised, which requires empathetic, human-verified handling; autonomous resolution is therefore constrained to the narrow scope of sending an explanatory message and removal link. Financial dispute guidance and refund actions must remain with agents, limiting autonomous volume to a small fraction.
- **Validation:** Pilot with 15% of incoming tickets matching this pattern: auto-send the educational message + removal link, then route to agent for verification; measure customer satisfaction, re-contact rate, and whether fraud escalation was required within 30 days.

### Risks

- **Compliance concerns:**
  - Unauthorized card charges may trigger consumer protection obligations (e.g., EU PSD2 chargeback rights) requiring timely human response and documentation
  - Storing and acting on payment card dispute advice could create regulatory exposure if not handled by qualified personnel
  - GDPR implications of retaining vehicle plate data beyond the rental period without a defined retention policy
- **Must not automate:**
  - Issuing or approving financial refunds without agent authorization
  - Advising customers on bank dispute or chargeback procedures autonomously
  - Closing tickets where the customer has explicitly alleged fraud or account compromise without human review

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

