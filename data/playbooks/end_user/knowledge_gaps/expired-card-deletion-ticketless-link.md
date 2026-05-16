---
id: expired-card-deletion-ticketless-link
name: expired_card_deletion_ticketless_link
title: Users unable to delete expired credit card linked to Ticketless service in Bmove App
description: End users report that they cannot delete or replace an expired/old credit card in the Bmove app because it is
  still linked to the Ticketless automatic licence-plate recognition service. Users either cannot add a new card, cannot remove
  the old one, or find that automatic billing fails even after adding a new card. Resolution requires users to first add the
  new card under Payments, then explicitly re-link it to the Ticketless service before the old card can be deleted.
category: end_user/knowledge_gaps
ticket_class: end_user
issue_category: knowledge_gap
resolution_pattern: user_education
languages:
- de
country_focus:
- at
- de
- other
status: active
cluster_id: BS:end_user|austria|no_label:c8
project_key: BS
cluster_size: 48
cluster_size_dedup: 47
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.92
median_resolution_minutes: 806.0
p95_resolution_minutes: 43546.149999999994
cannot_reproduce_rate: 0.0
data_window_start: '2023-09-04'
data_window_end: '2026-04-29'
annual_hours_saved: 1.0
roi:
  baseline_active_hours: 2.8
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 1.3
  deflection_hours_range:
  - 0.9
  - 1.6
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.0
  agent_assist_hours_range:
  - 0.7
  - 1.3
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.5
  product_fix_hours_range:
  - 1.8
  - 2.8
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 0.7
  autonomous_resolve_hours_range:
  - 0.5
  - 0.9
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-18189
- BS-47187
- BS-43168
- BS-12862
- BS-37002
- BS-44973
- BS-47635
- BS-48346
- BS-52182
- BS-52072
- BS-51393
- BS-47764
- BS-44404
- BS-51162
- BS-47079
- BS-52573
- BS-49674
- BS-51313
canonical_examples:
- BS-37002
- BS-52573
- BS-47079
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
  autonomous_resolve_max_safe_volume_pct: 0.25
  autonomous_resolve_narrow_use_case: Auto-send step-by-step re-linking instructions when inbound ticket text matches expired-card
    + Ticketless keywords and no account investigation is flagged
  autonomous_resolve_safety_constraints:
  - Must not autonomously modify account payment settings or card linkages on behalf of the user
  - Must require a human review step if the user reports billing failures or financial discrepancy language
  - Must include a clear opt-out/escalation path to a human agent in every automated reply
  - Automated response must be limited to sending the standard instructions; no account lookups or data changes
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-incorrect-charge-refund
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- bmove-not-recognized-daily-worklog
- croatia-ticketless-rental-car-ghost-charge
- croatian-invoice-download-request
- email-address-change-not-possible
- email-address-change-not-supported
- hr-b2b-r1-invoice-request
- igeus-portal-access-credential-management
- italian-ticketless-setup-and-payment-issues
- microsoft365-quarantine-notification-auto-tickets
- missing-parking-invoice-receipt
- missing-parking-receipt-email
- missing-parking-receipt-request
- open-session-at-exit-austria
- outstanding-payment-credit-card-failure
- phonzie-to-bmove-credit-refund-request
- pkc-vehicle-registration-automated-tickets
- prepaid-top-up-and-usage-issues
- ticketless-open-session-at-exit__960f17
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Users unable to delete expired credit card linked to Ticketless service in Bmove App

## What this pattern is

End users report that they cannot delete or replace an expired/old credit card in the Bmove app because it is still linked to the Ticketless automatic licence-plate recognition service. Users either cannot add a new card, cannot remove the old one, or find that automatic billing fails even after adding a new card. Resolution requires users to first add the new card under Payments, then explicitly re-link it to the Ticketless service before the old card can be deleted.

## When this applies

- User's credit card has expired and they receive payment failure notifications
- User adds a new card but old expired card cannot be deleted because it is still linked to Ticketless
- Automatic billing stops working after card expiry even though a new card was added
- User explicitly tries to remove a payment method via app UI and receives an error about Ticketless linkage
- User receives repeated payment failure emails despite having already added a new card

## Typical resolution flow

1. User attempts to delete expired/old credit card in Bmove app and receives error or finds no delete option
2. User submits feedback or contacts support describing the inability to remove the card or payment failures
3. Support agent checks the user's account in the backend system to verify card and Ticketless linkage status
4. Support instructs user to add new card via Main Menu → Payments in the Bmove app
5. Support instructs user to navigate to Ticketless settings and re-link the new card to their licence plate, then save
6. Once new card is linked to Ticketless, user can delete old card (swipe left on iOS or trash icon on Android)
7. Support confirms resolution and closes ticket

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Acknowledge ticket and set user expectations for response time | support_agent | Bmove Support ticketing system | 5 min |
| Look up user account to verify card details and Ticketless linkage status | support_agent | Bmove backend/admin system | 5 min |
| Send templated instructions: add new card under Payments, re-link to Ticketless, then delete old card | support_agent | Bmove Support ticketing system | 5 min |

## Evidence

Derived from 48 tickets in cluster `BS:end_user|austria|no_label:c8`. Direct quotes from 7 representative tickets:

- `BS-37002` _[de]_: "Ich kann die alte ungültige Karte nicht löschen da Sie immer noch mit der aktuellen Zahlung verbunden ist…..das ist ein Problem"
- `BS-52573` _[de]_: "wie kann ich eine abgelaufene Kreditkarte löschen, die App sagt: löschen nicht möglich, da mit ticketless verbunden"
- `BS-47079` _[de]_: "Ich hab ja längst (seit Monaten) eine andere Karte hinterlegt. Die alte kann ich nicht löschen. Was sollte ich denn da tun???"
- `BS-52182` _[de]_: "Ich habe eine neue Kreditkarte, kann die alte nicht löschen und finde nirgends in der App wie ich das mache…"
- `BS-49674` _[de]_: "Ich hab eine neue Creditcard hinterlegt, die alte ungültige läst sich nicht löschen und die neue wird nicht belastet."
- `BS-47635` _[de]_: "Ich habe meine neue Kreditkarte vor dem neuen Jahr in der Bmove App eingegeben und diese funktioniert auch und ist freigeschalten! Leider bekomme ich trotzdem jedes Mal von euch, dass die Zahlung nich"
- `BS-48346` _[de]_: "Ihre App zeigt ständig Fehler beim hinzufügen neuer Karten. An meiner Bank liegt es nicht."

## Cluster statistics

- **Volume:** 48 tickets total (47 unique semantic events after dedup)
- **Frequency:** 0.92 tickets/month (over data window 2023-09-04 → 2026-04-29)
- **Median resolution:** 13.4 hours
- **Languages:** de
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.8 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1 (range [0.7, 1.26])
- **Time reduction per ticket:** ~35% (range [25%, 45%])
- **Feasibility:** 0.90
- **Rationale:** All three resolution actions are templated and deterministic, making this pattern an ideal candidate for an agent-assist macro: account lookup deeplink plus a pre-filled templated reply. Time savings of ~35% per ticket are achievable by eliminating copy-paste and navigation steps, though the absolute saving per ticket (~5 min) is modest.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-populates the account-lookup link and templated reply for agents, then compare actual handle time against the 15-minute baseline to confirm the 35% reduction estimate.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~1.5 (range [1.1, 1.9])
- **Hours eliminated per year:** ~2.5 (range [1.8, 2.8])
- **Root cause:** The app lacks automatic re-linking logic: when a user adds a replacement card, the Ticketless service retains the old card association, creating a dependency that blocks deletion. A UX fix (prompt to re-link at card-add time) or a backend fix (auto-transfer active service links to a newly designated default card) would eliminate the confusion entirely.
- **Rationale:** If the product surfaces a clear re-link prompt or auto-migrates service links on card replacement, most tickets in this cluster would not be raised at all; the upper bound is capped at the 2.8 h baseline. Engineering effort is estimated low because the fix is likely confined to the card-management and service-linking modules.
- **Validation:** Engineering team should spike the card-management and Ticketless-linking code paths to confirm scope; a 1-sprint proof-of-concept with QA sign-off would validate the effort range before committing to full delivery.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1.3 (range [0.9, 1.62])
- **Form:** `in_app_help`
- **Deflection rate:** ~45% (range [32%, 58%])
- **Feasibility:** 0.80
- **Rationale:** The resolution is a well-defined, repeatable three-step sequence with no account-specific complexity, making it highly suitable for an in-app help article or contextual tooltip surfaced on the Payments screen. Deflection rates for single-procedure knowledge-gap tickets typically land in the 35–55% range when the help content is placed at the point of friction.
- **Validation:** Deploy a contextual help banner on the Payments card-management screen and a linked FAQ article for 4 weeks; measure the ratio of Ticketless card-deletion tickets submitted before vs. after deployment to validate the assumed deflection rate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~0.7 (range [0.5, 0.88])
- **Narrow use case:** Auto-send step-by-step re-linking instructions when inbound ticket text matches expired-card + Ticketless keywords and no account investigation is flagged
- **Safety constraints:**
  - Must not autonomously modify account payment settings or card linkages on behalf of the user
  - Must require a human review step if the user reports billing failures or financial discrepancy language
  - Must include a clear opt-out/escalation path to a human agent in every automated reply
  - Automated response must be limited to sending the standard instructions; no account lookups or data changes
- **Rationale:** The resolution is fully scripted and requires no account-level judgment, making partial autonomous dispatch feasible; however, the low annual volume (11.1 tickets/year) means total savings are small and a conservative 25% auto-resolve cap is appropriate to protect against misclassification and user trust issues. A significant share of tickets may include billing-failure nuance requiring human verification.
- **Validation:** Pilot for 6 weeks with intent-classification confidence threshold ≥ 0.90 before auto-send; accept only if user satisfaction on auto-resolved tickets is ≥ baseline CSAT and escalation rate remains below 15% of auto-resolved cases.

### Risks

- **Compliance concerns:**
  - Any automated flow touching payment card data must comply with PCI-DSS handling requirements even if the bot only reads card status metadata
  - Automated replies referencing billing should include accurate disclaimers to avoid consumer-protection misrepresentation
- **Must not automate:**
  - Any direct modification of stored payment methods or Ticketless service linkages on a user's account
  - Resolution of tickets where the user reports actual billing charges or financial disputes — these require human review

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

