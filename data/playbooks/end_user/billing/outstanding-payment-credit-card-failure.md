---
id: outstanding-payment-credit-card-failure
name: outstanding_payment_credit_card_failure
title: End-user receives 'Outstanding Payment' email after failed automatic credit card charge for Ticketless parking
description: Users of the Bmove Ticketless parking service receive an automated 'Outstanding payment' email when the system
  could not charge their credit card after a parking session. Customers reply to support because they believe their card is
  valid, want an alternative payment method, or are confused about why the charge failed despite having a card on file. Common
  root causes include expired/replaced cards, cards not properly linked to the Ticketless service, or deleted cards that cannot
  be removed via the app.
category: end_user/billing
ticket_class: end_user
issue_category: billing
resolution_pattern: user_education
languages:
- de
- en
country_focus:
- at
- de
- other
status: active
cluster_id: BS:end_user|austria|no_label:c6
project_key: BS
cluster_size: 40
cluster_size_dedup: 35
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.93
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.69
median_resolution_minutes: 0.0
p95_resolution_minutes: 12856.799999999948
cannot_reproduce_rate: 0.025
data_window_start: '2023-04-19'
data_window_end: '2026-01-15'
annual_hours_saved: 0.7
roi:
  baseline_active_hours: 2.9
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.9
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
  - 1.4
  - 2.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.5
  autonomous_resolve_hours_range:
  - 0.3
  - 0.6
  autonomous_resolve_max_safe_volume_pct: 0.2
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-28697
- BS-29695
- BS-31419
- BS-7539
- BS-14141
- BS-30276
- BS-32111
- BS-33136
- BS-47861
- BS-31954
- BS-31676
- BS-33817
- BS-33090
- BS-31220
- BS-30472
- BS-33127
- BS-32780
- BS-32684
canonical_examples:
- BS-28697
- BS-47861
- BS-31954
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: 2
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: User education — safe for self-service deflection
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Fully automated re-send of step-by-step card re-link instructions when account lookup
    confirms the sole root cause is 'card not activated in Ticketless settings' and no payment dispute flag is present.
  autonomous_resolve_safety_constraints:
  - Must not trigger autonomous reply if any open payment dispute or chargeback flag exists on the account.
  - Must not autonomously initiate a payment charge on behalf of the user.
  - Must hand off to a human agent if account lookup returns ambiguous or multiple card-state issues.
  - Must include a clear human-escalation path in every automated response.
  - Audit log required for every autonomous action for billing compliance.
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-incorrect-charge-refund
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-ticketless-outstanding-payment-failure
- bmove-not-recognized-daily-worklog
- email-address-change-not-possible
- email-address-change-not-supported
- expired-card-deletion-ticketless-link
- italian-b2b-invoice-billing-question
- microsoft365-quarantine-notification-auto-tickets
- missing-parking-invoice-receipt
- missing-parking-receipt-email
- missing-parking-receipt-request
- open-session-at-exit-austria
- pkc-vehicle-registration-automated-tickets
- slovakia-parking-payment-failure-no-ticket
- ticketless-open-session-at-exit__960f17
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# End-user receives 'Outstanding Payment' email after failed automatic credit card charge for Ticketless parking

## What this pattern is

Users of the Bmove Ticketless parking service receive an automated 'Outstanding payment' email when the system could not charge their credit card after a parking session. Customers reply to support because they believe their card is valid, want an alternative payment method, or are confused about why the charge failed despite having a card on file. Common root causes include expired/replaced cards, cards not properly linked to the Ticketless service, or deleted cards that cannot be removed via the app.

## When this applies

- Bmove system fails to charge the user's stored credit card after a Ticketless parking session
- Automated 'Outstanding payment' email is sent to the user
- User's credit card was replaced, expired, blocked, or not properly linked to the Ticketless service
- Old/invalid credit card cannot be deleted via the app

## Typical resolution flow

1. User receives automated 'Outstanding payment' email from Bmove
2. User forwards or replies to the email to s****@bmove.com expressing confusion or frustration
3. User explains their card is valid, has been replaced, or asks for an alternative payment method (bank transfer, invoice)
4. Support sends automated acknowledgement with 2-5 business day response time
5. Support agent reviews account and identifies why payment failed (e.g., new card not linked to Ticketless settings)
6. Support instructs user to update or correctly link payment method in the app, or processes the outstanding amount manually

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Send automated acknowledgement asking user to provide plate, garage, entry/exit time, ticket photo | system | Bmove support email system | 1 min |
| Review user account to identify reason for payment failure (wrong card linked, card not activated in Ticketless settings, old card not removed) | support_agent | Bmove back-office system | 10 min |
| Instruct user to correctly link new credit card to Ticketless/vehicle settings in the app, or manually trigger payment | support_agent | Bmove back-office system / email | 10 min |

## Evidence

Derived from 40 tickets in cluster `BS:end_user|austria|no_label:c6`. Direct quotes from 6 representative tickets:

- `BS-28697` _[de]_: "Meine Kreditkarte ist OK ! Sonst schicken Sie mir bitte eine andere Einzahlungsmöglichkeit."
- `BS-47861` _[de]_: "Sie haben zwar Ihre neue Kreditkarte im Profil hinterlegt, diese wurde jedoch noch nicht aktiv in den Ticketless-Einstellungen mit Ihren Fahrzeugen verknüpft."
- `BS-31954` _[de]_: "Die Abbuchung funktioniert leider nicht automatisch, da die Kreditkarte mit der Endnummer 9414 gelöscht werden muss, was aber über die App leider nicht geht!"
- `BS-33817` _[en]_: "My credit card is currently blocked due to previous fraud attempts and I'm still waiting for my new one to arrive. I can pay immediately if you send me an invoice with your bank account."
- `BS-32111` _[de]_: "ich habe Ihnen schon mind 3x geantwortet, sie haben meine Kreditkartendaten hinterlegt, wenn sie das nicht abbuchen können, dann schicken sie mir eine Kontonummer!"
- `BS-32684` _[de]_: "warum ziehen sie es nicht ab? Ich habe schon nach einem Bankkonto gefragt, dass ich es überweise, angeblich gibt es kein Bankkonto wo man überweisen kann."

## Cluster statistics

- **Volume:** 40 tickets total (35 unique semantic events after dedup)
- **Frequency:** 0.69 tickets/month (over data window 2023-04-19 → 2026-01-15)
- **Median resolution:** 0 min
- **Cannot Reproduce rate:** 2.5%
- **Languages:** de, en
- **Country focus:** at, de, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~2.9 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.7 (range [0.52, 0.949])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.80
- **Rationale:** The resolution pattern is highly templated (account lookup → diagnose card state → instruct re-link or trigger manual charge), making it well-suited for an assist tool that auto-surfaces the relevant account card-state and pre-populates the instructional reply. Time savings are moderate because the account-review step still requires human judgment.
- **Validation:** Run agent-assist in shadow mode for 3 weeks: present agents with a pre-populated card-state summary and a draft reply; measure actual handle-time versus the 21-minute baseline and score draft acceptance rate against the 0.80 target.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~2 (range [1.45, 2.61])
- **Root cause:** The app allows cards to enter an invalid state (expired, not activated for Ticketless, or 'deleted but not removable') without proactively alerting the user before a parking session, and there is no retry or alternative-payment prompt at charge-failure time — forcing the user to discover the problem only via an alarming 'Outstanding Payment' email.
- **Rationale:** Proactive card-validity checks before session start, in-app card-state warnings, and a self-service retry/re-link flow triggered at charge failure would eliminate the majority of contacts; residual contacts would be edge cases (e.g., bank-side declines outside the app's knowledge). Hours eliminated are capped at baseline 2.9 h/yr and assume ~70% reduction in ticket volume.
- **Validation:** Engineering team spikes on card-validation API coverage and app settings UX; prototype the charge-failure re-link flow in a staging environment and validate end-to-end with 5 internal testers before estimating final sprint count.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.9 (range [0.602, 1.118])
- **Form:** `in_app_help`
- **Deflection rate:** ~30% (range [21%, 39%])
- **Feasibility:** 0.65
- **Rationale:** The root causes (expired card, mis-linked card, deleted card) are procedural and app-navigable, making in-app guidance at the point of the 'Outstanding Payment' email a plausible deflection. However, some users will still need agent confirmation that their payment was actually received, limiting total deflection.
- **Validation:** Deploy a contextual in-app help article and a deep-link to card-settings within the 'Outstanding Payment' email for 6 weeks; measure the ratio of users who complete card re-linking without opening a support ticket versus the prior-period baseline.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.5 (range [0.322, 0.598])
- **Narrow use case:** Fully automated re-send of step-by-step card re-link instructions when account lookup confirms the sole root cause is 'card not activated in Ticketless settings' and no payment dispute flag is present.
- **Safety constraints:**
  - Must not trigger autonomous reply if any open payment dispute or chargeback flag exists on the account.
  - Must not autonomously initiate a payment charge on behalf of the user.
  - Must hand off to a human agent if account lookup returns ambiguous or multiple card-state issues.
  - Must include a clear human-escalation path in every automated response.
  - Audit log required for every autonomous action for billing compliance.
- **Rationale:** Autonomous resolution is feasible only for the narrow, unambiguous sub-case where the account clearly shows a deactivated Ticketless card setting; billing sensitivity and the variety of root causes make broader autonomous handling risky and trust-eroding. Volume cap is set conservatively at 20% given the billing context.
- **Validation:** Pilot for 8 weeks on the specific 'card not activated in Ticketless settings' case only; acceptance criteria: zero autonomous mis-classifications into dispute/chargeback cases, user satisfaction score ≥ prior agent-handled benchmark, and manual audit of 100% of autonomous resolutions in weeks 1–2.

### Risks

- **Compliance concerns:**
  - Automated handling of billing failures must comply with applicable consumer payment regulations and data-protection rules (e.g., GDPR for EU users).
  - Any autonomous payment retry must not be initiated without explicit user consent to avoid unauthorized charge disputes.
  - Audit trails for all automated billing-related communications must be retained per financial record-keeping requirements.
- **Must not automate:**
  - Triggering or re-attempting a credit card charge on behalf of the user without explicit user-initiated confirmation.
  - Closing a ticket as resolved when the user has expressed they believe their card is valid and the charge is in dispute.
  - Handling cases where a chargeback, fraud flag, or payment dispute is indicated on the account.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.93)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** User education — safe for self-service deflection

