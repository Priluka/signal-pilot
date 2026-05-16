---
id: email-address-change-not-possible
name: email_address_change_not_possible
title: Users requesting email address change on Bmove account — not supported in-product
description: End users (predominantly Austrian) contact support requesting to change the email address registered on their
  Bmove account, after discovering no self-service option exists in the app or website. A recurring sub-case involves Apple's
  private relay anonymised email addresses being used at registration. The standard resolution is to instruct users to delete
  their current account and create a new one with the desired email address.
category: end_user/feature_requests
ticket_class: end_user
issue_category: feature_request
resolution_pattern: user_education
languages:
- de
country_focus:
- at
- de
- other
status: active
cluster_id: BS:end_user|austria|ticketless:c1
project_key: BS
cluster_size: 35
cluster_size_dedup: 35
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.69
median_resolution_minutes: 993.0
p95_resolution_minutes: 6316.7
cannot_reproduce_rate: 0.0
data_window_start: '2023-06-02'
data_window_end: '2025-11-30'
annual_hours_saved: 0.7
roi:
  baseline_active_hours: 2.0
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.8
  deflection_hours_range:
  - 0.6
  - 1.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.7
  agent_assist_hours_range:
  - 0.5
  - 0.9
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 2.0
  product_fix_hours_range:
  - 1.6
  - 2.0
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.4
  - 0.7
  autonomous_resolve_max_safe_volume_pct: 0.25
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-38132
- BS-41155
- BS-35055
- BS-8731
- BS-11802
- BS-17738
- BS-21535
- BS-28049
- BS-39708
- BS-41133
- BS-43882
- BS-31162
- BS-25083
- BS-37097
- BS-35406
- BS-40538
- BS-40058
- BS-18986
canonical_examples:
- BS-38132
- BS-35055
- BS-17738
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
  autonomous_resolve_narrow_use_case: Auto-reply with standardised delete-and-recreate instructions for tickets that contain
    no active Ticketless subscription signals and match the email-change intent classifier.
  autonomous_resolve_safety_constraints:
  - Must not auto-close tickets where user mentions an active Ticketless subscription or licence plates, as incorrect deletion
    order causes data loss.
  - Must not process tickets where account has pending charges or unresolved parking sessions.
  - Requires human review if user's message indicates frustration, data-loss concern, or accessibility needs.
  - Austrian consumer-protection norms require clear escalation path; automated reply must offer agent follow-up option.
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-incorrect-charge-refund
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- bmove-not-recognized-daily-worklog
- email-address-change-not-supported
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

# Users requesting email address change on Bmove account — not supported in-product

## What this pattern is

End users (predominantly Austrian) contact support requesting to change the email address registered on their Bmove account, after discovering no self-service option exists in the app or website. A recurring sub-case involves Apple's private relay anonymised email addresses being used at registration. The standard resolution is to instruct users to delete their current account and create a new one with the desired email address.

## When this applies

- User has a new email address and wants to update their Bmove registration email
- User registered with an Apple private relay anonymised email and wants to switch to their real email
- User cannot find an option to change the primary email address in the Bmove app or website
- User's old email address is no longer active and they need invoices/communications sent to a new address

## Typical resolution flow

1. User searches for email change option in app/website and fails to find one
2. User contacts Bmove support via ticket or app feedback
3. Support agent responds informing user that changing the predefined email address is not possible in Bmove
4. Support agent instructs user to deactivate Ticketless and delete licence plates on the old account (if applicable)
5. Support agent provides step-by-step instructions to delete the current account via App Menu → Konto → Konto löschen
6. Support agent advises user to create a new account with the desired email address

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Send standard response explaining email change is not possible and provide account deletion instructions | support_agent | Bmove Support ticketing system | 5 min |
| If user has Ticketless active, instruct user to deactivate Ticketless and delete licence plates before deleting old account | support_agent | Bmove Support ticketing system | 5 min |
| User deletes old account via App Menu → Konto → Konto löschen | end_user | Bmove app | 5 min |

## Evidence

Derived from 35 tickets in cluster `BS:end_user|austria|ticketless:c1`. Direct quotes from 5 representative tickets:

- `BS-38132` _[de]_: "In Bmove ist es nicht möglich die vordefinierte Email Adresse nachträglich zu ändern. Die einzige Möglichkeit Ihre neuen Daten zu hinterlegen ist das aktuelle Konto zu löschen und ein neues, aktualisi"
- `BS-35055` _[de]_: "Apple hat meine Email Adresse anonymisiert und so bin ich unter f****@privaterelay.appleid.com bei Ihnen angemeldet. Bitte ändern Sie diese auf meine richtige Emailadresse p****@gmail.com"
- `BS-17738` _[de]_: "ich hatte bereits ein Bmove Konto, ich wollte meine Mailadresse ändern, dies sei aber nur mit Stornio und Neueröffnung möglich. Das habe ich jetzt gemacht, es hat mir aber angeschrieben, das es schon "
- `BS-18986` _[de]_: "Ich kann weder in der App noch im Browser meine E-Mail Adresse ändern. Ein hinzufügen einer zusätzlichen E-Mail Adresse hat funktioniert."
- `BS-39708` _[de]_: "Und ich wurde nur ungern deswegen ein neues Konto anlegen müssen. Oder können Sie das für mich wechseln?"

## Cluster statistics

- **Volume:** 35 tickets total (35 unique semantic events after dedup)
- **Frequency:** 0.69 tickets/month (over data window 2023-06-02 → 2025-11-30)
- **Median resolution:** 16.6 hours
- **Languages:** de
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.7 (range [0.5, 0.9])
- **Time reduction per ticket:** ~35% (range [25%, 45%])
- **Feasibility:** 0.85
- **Rationale:** The resolution is highly templated — a macro or AI-drafted reply covering the delete-and-recreate flow (plus Ticketless conditional) can be inserted in one click, reducing active work from ~15 min to roughly 8–11 min per ticket. Draft quality can be high because branching logic is simple.
- **Validation:** Run a 3-week shadow-mode pilot where the assist tool pre-populates a draft response when the cluster is detected; measure agent edit rate and handle-time delta versus control tickets to confirm the ~35% time reduction assumption.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~2 (range [1.6, 2])
- **Root cause:** Email change is a missing self-service feature, not a bug. The in-product identity system does not expose an email-update flow, forcing users to delete and recreate accounts. The Apple private-relay sub-case is a downstream consequence of the same gap.
- **Rationale:** Adding an authenticated email-change flow (with re-verification) would eliminate virtually all tickets in this cluster; the upper bound is capped at the 2.0-hour baseline because hours_eliminated cannot exceed baseline. Engineering effort is medium due to identity system changes, email re-verification logic, and potential Ticketless/licence-plate state migration.
- **Validation:** Have the engineering team produce a spike/discovery ticket estimating backend identity-system changes; use the resulting story-point estimate to refine the sprint range before committing to roadmap prioritisation.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.8 (range [0.574, 1.066])
- **Form:** `help_center`
- **Deflection rate:** ~40% (range [28%, 52%])
- **Feasibility:** 0.75
- **Rationale:** This pattern is highly FAQ-deflectable because the resolution is a fixed instructional response with no account-level investigation required; users simply need to find the delete-and-recreate guidance before contacting support. The Apple private-relay sub-case adds a small wrinkle that benefits from explicit mention in the help article.
- **Validation:** Publish a help-center article titled 'How to change your email address on Bmove' and track ticket volume for the cluster over 8 weeks post-launch, comparing weekly ticket rate to the pre-launch baseline of ~0.16 tickets/week.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 25% of tickets
- **Hours saved per year:** ~0.5 (range [0.36, 0.65])
- **Narrow use case:** Auto-reply with standardised delete-and-recreate instructions for tickets that contain no active Ticketless subscription signals and match the email-change intent classifier.
- **Safety constraints:**
  - Must not auto-close tickets where user mentions an active Ticketless subscription or licence plates, as incorrect deletion order causes data loss.
  - Must not process tickets where account has pending charges or unresolved parking sessions.
  - Requires human review if user's message indicates frustration, data-loss concern, or accessibility needs.
  - Austrian consumer-protection norms require clear escalation path; automated reply must offer agent follow-up option.
- **Rationale:** Autonomous resolution is feasible only for the simplest sub-case (no Ticketless, straightforward email-change request) and volume is low enough that the absolute hour savings are modest; the safety cap is set at 0.25 to stay comfortably within the 0.30 project ceiling given the Ticketless complication risk.
- **Validation:** Define a 6-week pilot limited to tickets auto-classified as email-change with no Ticketless keyword signals; measure CSAT, re-open rate, and false-positive rate; set a re-open rate threshold of ≤10% as the go/no-go criterion for broader rollout.

### Risks

- **Compliance concerns:**
  - GDPR / Austrian DSG: account deletion destroys personal data permanently; any automated instruction must clearly warn users that deletion is irreversible and that data cannot be recovered.
  - GDPR right-to-portability: users should be informed whether any data (e.g. parking history) can be exported before account deletion.
  - Apple private-relay addresses: instructing users to delete accounts registered to a private-relay email requires care to avoid locking users out if they can no longer receive verification emails at that address.
- **Must not automate:**
  - Tickets where user has an active Ticketless subscription — incorrect deletion sequence can cause licence-plate or billing data loss.
  - Tickets involving pending or disputed parking charges on the account being deleted.
  - Tickets where the user expresses distress, confusion about data loss, or accessibility issues requiring human judgement.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

