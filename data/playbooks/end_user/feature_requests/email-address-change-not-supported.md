---
id: email-address-change-not-supported
name: email_address_change_not_supported
title: Users requesting email address change on Bmove account — feature not supported
description: End users (predominantly Austrian) contact Bmove support asking how to change the email address associated with
  their account, often because the old address is being deactivated or they want to switch to a personal address. Bmove does
  not support in-place email address changes; the only resolution offered is to delete the existing account and create a new
  one with the desired email address. This is a recurring, high-volume pattern driven by a product limitation.
category: end_user/feature_requests
ticket_class: end_user
issue_category: feature_request
resolution_pattern: user_education
languages:
- de
country_focus:
- at
- de
status: active
cluster_id: BS:end_user|austria|no_label:c5
project_key: BS
cluster_size: 44
cluster_size_dedup: 44
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.86
median_resolution_minutes: 786.0
p95_resolution_minutes: 28177.200000000023
cannot_reproduce_rate: 0.0
data_window_start: '2023-07-13'
data_window_end: '2026-05-07'
annual_hours_saved: 0.9
roi:
  baseline_active_hours: 2.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 1.2
  deflection_hours_range:
  - 0.8
  - 1.5
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.9
  agent_assist_hours_range:
  - 0.7
  - 1.2
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.6
  product_fix_hours_range:
  - 2.0
  - 2.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.7
  autonomous_resolve_hours_range:
  - 0.5
  - 0.8
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-51185
- BS-51364
- BS-45202
- BS-10306
- BS-19732
- BS-20049
- BS-27307
- BS-19901
- BS-50418
- BS-39810
- BS-53154
- BS-39919
- BS-35398
- BS-45775
- BS-50252
- BS-50018
- BS-50901
- BS-49493
canonical_examples:
- BS-51185
- BS-49493
- BS-50901
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
  autonomous_resolve_narrow_use_case: Auto-reply with templated explanation (email change unsupported + delete/re-register
    steps) when ticket is classified with high confidence as this exact pattern and no additional sub-issues are present.
  autonomous_resolve_safety_constraints:
  - Must not autonomously take any action on the user's account (no deletion, no data changes)
  - Confidence classifier threshold must exceed 0.90 before triggering auto-reply
  - Auto-reply must include clear escalation path to human agent
  - Any ticket mentioning data export, billing, or account security must be routed to human agent
  - Austrian GDPR considerations require that automated responses do not collect or confirm personal data beyond what was
    submitted
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-incorrect-charge-refund
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- bmove-not-recognized-daily-worklog
- email-address-change-not-possible
- expired-card-deletion-ticketless-link
- microsoft365-quarantine-notification-auto-tickets
- missing-parking-invoice-receipt
- missing-parking-receipt-email
- missing-parking-receipt-request
- open-session-at-exit-austria
- outstanding-payment-credit-card-failure
- pkc-vehicle-registration-automated-tickets
- ticketless-open-session-at-exit__960f17
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Users requesting email address change on Bmove account — feature not supported

## What this pattern is

End users (predominantly Austrian) contact Bmove support asking how to change the email address associated with their account, often because the old address is being deactivated or they want to switch to a personal address. Bmove does not support in-place email address changes; the only resolution offered is to delete the existing account and create a new one with the desired email address. This is a recurring, high-volume pattern driven by a product limitation.

## When this applies

- User's registered email address is being deactivated or discontinued
- User wants to switch from a work/corporate email to a personal email
- User discovers no self-service option exists in the app or website to change their email
- User receives monthly report to old email and wants to update to new address

## Typical resolution flow

1. User contacts support via email or in-app feedback requesting email address change
2. Support agent sends canned response explaining that email address change is not possible in Bmove
3. Agent instructs user to delete their current account via App Menu → Konto → Konto löschen
4. Agent instructs user to create a new account with the desired email address
5. Ticket is closed

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Send canned response explaining email change is not supported and advising account deletion + re-registration | support_agent | Jira Service Management / email | 5 min |
| User deletes existing account via app (Menu → Konto → Konto löschen) and creates new account | end_user | Bmove App | 10 min |

## Evidence

Derived from 44 tickets in cluster `BS:end_user|austria|no_label:c5`. Direct quotes from 5 representative tickets:

- `BS-51185` _[de]_: "In Bmove ist es nicht möglich die vordefinierte Email Adresse nachträglich zu ändern. Die einzige Möglichkeit Ihre neuen Daten zu hinterlegen ist das aktuelle Konto zu löschen und ein neues, aktualisi"
- `BS-49493` _[de]_: "Ich habe gerade versucht, im Online Account meine Mailadresse zu ändern. Dies ist leider nicht möglich."
- `BS-50901` _[de]_: "Die E-Mail-Adresse, unter welcher ich mein Konto bei Bmove ursprünglich angemeldet habe, wird in den nächsten Monaten deaktiviert."
- `BS-50418` _[de]_: "Ich würde gerne die bei meinem Account hinterlegte Mailadresse ändern, damit ich mir die Abrechnungen nicht dauernd auf meine Firmenmail weiterleiten muss."
- `BS-45775` _[de]_: "Meine e-mail Adresse wird sich demnächst ändern. Bitte verwenden sie in Hinkunft nur mehr e****@icloud.com"

## Cluster statistics

- **Volume:** 44 tickets total (44 unique semantic events after dedup)
- **Frequency:** 0.86 tickets/month (over data window 2023-07-13 → 2026-05-07)
- **Median resolution:** 13.1 hours
- **Languages:** de
- **Country focus:** at, de

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.9 (range [0.65, 1.17])
- **Time reduction per ticket:** ~35% (range [25%, 45%])
- **Feasibility:** 0.90
- **Rationale:** Because the resolution is a single canned response, an LLM-assisted draft can be auto-populated the moment the ticket is classified, reducing agent active time from ~5 min to ~3 min per ticket; the remaining time is agent review and send. The 35% reduction reflects the already-low active effort leaving little further room.
- **Validation:** Run shadow-mode auto-draft for 2 weeks across all tickets in this cluster; measure agent edit rate and time-to-send versus the prior 2-week baseline to validate the 35% time-reduction assumption.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~2.6 (range [2, 2.6])
- **Root cause:** Bmove does not support in-place email address changes as a product feature; there is no bug — this is a deliberate or unimplemented capability gap requiring account identity re-design.
- **Rationale:** Implementing native email-address change requires touching account-identity, authentication, and potentially data-migration flows — a high-effort undertaking. If shipped, it would eliminate virtually all tickets in this cluster, capped at the 2.6 h baseline.
- **Validation:** Engineering team should scope a discovery spike (1–2 days) to map all identity and auth touchpoints affected by an email-change flow, then refine sprint estimate before committing.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1.2 (range [0.82, 1.51])
- **Form:** `help_center`
- **Deflection rate:** ~45% (range [32%, 58%])
- **Feasibility:** 0.85
- **Rationale:** This pattern is highly FAQ-deflectable because the resolution is a single, deterministic answer (email change not supported; delete + re-register) with no agent judgment required. However, users motivated by urgency (deactivating email) may still prefer human confirmation, limiting deflection to roughly half.
- **Validation:** Deploy a dedicated help-center article and/or in-app tooltip at the account-settings screen for 4 weeks; measure ticket volume reduction against the prior 4-week baseline to validate the deflection rate assumption.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~0.7 (range [0.46, 0.84])
- **Narrow use case:** Auto-reply with templated explanation (email change unsupported + delete/re-register steps) when ticket is classified with high confidence as this exact pattern and no additional sub-issues are present.
- **Safety constraints:**
  - Must not autonomously take any action on the user's account (no deletion, no data changes)
  - Confidence classifier threshold must exceed 0.90 before triggering auto-reply
  - Auto-reply must include clear escalation path to human agent
  - Any ticket mentioning data export, billing, or account security must be routed to human agent
  - Austrian GDPR considerations require that automated responses do not collect or confirm personal data beyond what was submitted
- **Rationale:** The resolution is fully deterministic and requires no account-side action by the bot, making autonomous reply feasible; however, the low absolute volume (10.3 tickets/year) means savings are modest, and a 25% safe-volume cap is applied to preserve human oversight during initial rollout.
- **Validation:** Pilot autonomous reply on 25% of tickets classified at ≥0.90 confidence for 8 weeks; acceptance criteria are <5% escalation rate post-auto-reply and zero incidents involving incorrect account-action instructions.

### Risks

- **Compliance concerns:**
  - GDPR (Austria/EU): automated responses must not inadvertently confirm, store, or expose personal email addresses beyond the original ticket submission
  - Right-to-erasure workflows may be entangled if account deletion is part of the advised resolution; agents or automation must not initiate deletion on behalf of the user
- **Must not automate:**
  - Actual account deletion — this must always be performed by the end user, never by an automated system or agent
  - Any confirmation that a specific email address belongs to a specific user (PII validation)

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

