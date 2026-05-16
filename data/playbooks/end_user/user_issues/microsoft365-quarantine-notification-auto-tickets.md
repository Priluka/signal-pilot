---
id: microsoft365-quarantine-notification-auto-tickets
name: microsoft365_quarantine_notification_auto_tickets
title: Automated Microsoft 365 Quarantine Notification Emails Creating Support Tickets
description: End users are forwarding or triggering support tickets from automated Microsoft 365 Security Center quarantine
  notification emails, which inform them that phishing or high-confidence phish messages have been blocked and held for review.
  These are not genuine support requests but rather automated system notifications from Microsoft 365 that have been routed
  into the Bmove support queue. The quarantined emails themselves are phishing attempts in multiple languages (Japanese, Croatian,
  German, Spanish, English) targeting a variety of services.
category: end_user/user_issues
ticket_class: end_user
issue_category: misuse
resolution_pattern: no_action
languages:
- en
- de
- hr
- other
country_focus:
- at
- hr
- other
status: active
cluster_id: BS:end_user|austria|no_label:c0
project_key: BS
cluster_size: 37
cluster_size_dedup: 37
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.73
median_resolution_minutes: 0.0
p95_resolution_minutes: 1979.199999999997
cannot_reproduce_rate: 0.0
data_window_start: '2025-04-20'
data_window_end: '2026-04-07'
annual_hours_saved: 0.1
roi:
  baseline_active_hours: 0.4
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.1
  deflection_hours_range:
  - 0.1
  - 0.1
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.1
  agent_assist_hours_range:
  - 0.1
  - 0.2
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.3
  product_fix_hours_range:
  - 0.2
  - 0.4
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.2
  autonomous_resolve_max_safe_volume_pct: 0.3
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-36505
- BS-37079
- BS-39647
- BS-36863
- BS-42009
- BS-46374
- BS-47974
- BS-51640
- BS-47339
- BS-38157
- BS-47366
- BS-37754
- BS-41870
- BS-36673
- BS-50645
- BS-50180
- BS-36812
- BS-36576
canonical_examples:
- BS-36505
- BS-37079
- BS-51640
vendor_dependency:
  vendor_name: Microsoft (Microsoft 365 / Office 365)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Informational — safe for agent self-service
  autonomous_resolve_max_safe_volume_pct: 0.3
  autonomous_resolve_narrow_use_case: Auto-close tickets that exactly match Microsoft 365 quarantine notification email patterns
    (sender domain, subject template) with a standardized no-action closure note sent to the submitter.
  autonomous_resolve_safety_constraints:
  - Only apply to tickets whose sender/subject unambiguously match Microsoft 365 Security Center quarantine notification templates;
    require high-confidence pattern match (≥0.95 precision in validation).
  - Never auto-close if the ticket body contains any additional user-reported issue beyond the forwarded notification.
  - Retain all auto-closed tickets in a daily digest for human spot-check review during the first 90 days.
  - Do not auto-close tickets from VIP or executive accounts without human review.
  - Log all autonomous closures for audit trail; maintain ability to reopen within 7 days.
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-incorrect-charge-refund
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- bmove-not-recognized-daily-worklog
- email-address-change-not-possible
- email-address-change-not-supported
- expired-card-deletion-ticketless-link
- italian-b2b-unsolicited-procurement-marketing-emails
- microsoft365-quarantine-phishing-meta-impersonation
- missing-parking-invoice-receipt
- missing-parking-receipt-email
- missing-parking-receipt-request
- open-session-at-exit-austria
- outstanding-payment-credit-card-failure
- pkc-vehicle-registration-automated-tickets
- russian-spam-suggestion-tickets
- ticketless-open-session-at-exit__960f17
- unsolicited-spam-marketing-emails
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Automated Microsoft 365 Quarantine Notification Emails Creating Support Tickets

## What this pattern is

End users are forwarding or triggering support tickets from automated Microsoft 365 Security Center quarantine notification emails, which inform them that phishing or high-confidence phish messages have been blocked and held for review. These are not genuine support requests but rather automated system notifications from Microsoft 365 that have been routed into the Bmove support queue. The quarantined emails themselves are phishing attempts in multiple languages (Japanese, Croatian, German, Spanish, English) targeting a variety of services.

## When this applies

- Microsoft 365 Security Center sends an automated quarantine notification email to end users
- End user forwards or the system auto-routes the Microsoft 365 quarantine notification into the Bmove support ticket system
- Phishing or high-confidence phish email is detected and held by Microsoft 365 for up to 15 days

## Typical resolution flow

1. Microsoft 365 detects a phishing email sent to an end user
2. Microsoft 365 quarantines the email and sends an automated notification to the recipient
3. The automated notification email is forwarded or ingested as a new support ticket in Bmove
4. Ticket is created with summary 'Microsoft 365 security: You have messages in quarantine'
5. Ticket contains the full Microsoft 365 quarantine notification body including sender, subject, and action links

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Identify ticket as an auto-forwarded Microsoft 365 quarantine notification, not a genuine support request | support_agent | Bmove Support ticketing system | 2 min |
| Close ticket without action or with a brief note that no support action is required | support_agent | Bmove Support ticketing system | 1 min |

## Vendor dependency

- **Vendor:** Microsoft (Microsoft 365 / Office 365)

## Evidence

Derived from 37 tickets in cluster `BS:end_user|austria|no_label:c0`. Direct quotes from 6 representative tickets:

- `BS-36505` _[en]_: "1 messages are being held for you to review as of 4/26/2025 1:20:45 AM (UTC). Review them within 15 days of the received date by going to the Quarantine page in the Security Center."
- `BS-37079` _[en]_: "Prevented high confidence phish messages    Sender:  n****@appsheet.com   We are about to enforce forbidden usage on your account (Decision No. 9587632495)"
- `BS-51640` _[de]_: "Sender:  i****@a1business.at   World4you - Bestätigung der Rückerstattung doppelter Rechnung"
- `BS-47339` _[hr]_: "Sender:  n****@steinermolanoigens.org   Upozorenje prije blokiranja: Utvrđeno kršenje pravila o žigovima"
- `BS-47366` _[de]_: "Sender:  a****@accesx-d39b4.firebaseapp.com   Zahlung storniert / Rückerstattung von 192,10 EUR"
- `BS-50180` _[other]_: "Sender:  n****@fiableindustries.com   Su cuenta corre el riesgo de ser prohibida y sus archivos pueden eliminarse."

## Cluster statistics

- **Volume:** 37 tickets total (37 unique semantic events after dedup)
- **Frequency:** 0.73 tickets/month (over data window 2025-04-20 → 2026-04-07)
- **Median resolution:** 0 min
- **Languages:** en, de, hr, other
- **Country focus:** at, hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~0.4 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.1 (range [0.1, 0.18])
- **Time reduction per ticket:** ~35% (range [25%, 45%])
- **Feasibility:** 0.80
- **Rationale:** The resolution is entirely formulaic (identify pattern, close with standard note), making it an ideal candidate for an agent-assist macro or auto-suggested canned response; agent time would shrink to near-verification-only. Savings are small in absolute terms given low annual frequency.
- **Validation:** Deploy a shadow-mode classifier that auto-suggests a 'no-action quarantine notification' macro when ticket subject/body matches known patterns; measure agent acceptance rate over 2 weeks before enabling one-click close.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~0.5 (range [0.3, 0.7])
- **Hours eliminated per year:** ~0.3 (range [0.21, 0.39])
- **Root cause:** Root cause is organizational: Microsoft 365 quarantine notification emails are being forwarded or manually submitted into the Bmove support queue by confused end users. There is no Bmove product defect; the issue is a routing/user-education gap and, optionally, a Microsoft 365 notification configuration gap (e.g., end-user quarantine release settings or notification wording).
- **Rationale:** A lightweight intake-filter rule (e.g., email subject/sender pattern matching on Microsoft 365 quarantine notification formats) could auto-tag or auto-close these tickets before they reach an agent, effectively eliminating most of the active work. This is a configuration/workflow fix rather than deep engineering.
- **Validation:** Define subject-line and sender-domain regex patterns for Microsoft 365 quarantine notifications; shadow-test the filter against 30 days of historical tickets to measure precision and recall before enabling auto-close.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.1 (range [0.063, 0.11])
- **Form:** `help_center`
- **Deflection rate:** ~20% (range [14%, 26%])
- **Feasibility:** 0.45
- **Rationale:** Users submitting these tickets are confused by automated Microsoft 365 quarantine emails; a help-center article explaining what these notifications mean and that no action is required could preempt a subset of submissions, but many users will still ticket first without searching. Annual volume is low (8.7/yr), so absolute savings are minimal.
- **Validation:** Publish a dedicated help-center article and add a link in the support portal intake form; measure ticket deflection rate over a 4-week pilot by tracking article views vs. tickets filed for this pattern.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 30% of tickets
- **Hours saved per year:** ~0.1 (range [0.084, 0.156])
- **Narrow use case:** Auto-close tickets that exactly match Microsoft 365 quarantine notification email patterns (sender domain, subject template) with a standardized no-action closure note sent to the submitter.
- **Safety constraints:**
  - Only apply to tickets whose sender/subject unambiguously match Microsoft 365 Security Center quarantine notification templates; require high-confidence pattern match (≥0.95 precision in validation).
  - Never auto-close if the ticket body contains any additional user-reported issue beyond the forwarded notification.
  - Retain all auto-closed tickets in a daily digest for human spot-check review during the first 90 days.
  - Do not auto-close tickets from VIP or executive accounts without human review.
  - Log all autonomous closures for audit trail; maintain ability to reopen within 7 days.
- **Rationale:** Given the fully formulaic, no-action resolution and unambiguous signal (Microsoft 365 quarantine notification sender/subject), autonomous closure is highly feasible at capped volume; however, low annual frequency (8.7 tickets/yr) means absolute hour savings are very small, so ROI depends on bundling with broader automation infrastructure.
- **Validation:** Run pattern-match filter in shadow mode for 4 weeks, validating precision ≥0.95 and recall ≥0.80 against human-labeled tickets before enabling autonomous close on ≤30% of matched volume; review daily digest for false positives.

### Risks

- **Compliance concerns:**
  - Auto-closing tickets without human review carries a small risk of suppressing legitimate security incidents if a genuine phishing-related user report is misclassified as a routine quarantine notification.
  - Audit trail of auto-closed tickets must be retained per applicable data retention policies.
- **Must not automate:**
  - Any ticket where the user describes a specific security concern, account compromise, or suspicious activity beyond simply forwarding the quarantine notification.
  - Tickets from accounts flagged as VIP, executive, or under active security investigation.
- **Vendor dependencies blocking automation:**
  - Configuring Microsoft 365 quarantine notification settings (e.g., disabling end-user notifications or customizing notification wording to reduce confusion) requires access to the Microsoft 365 Security Center admin panel and is subject to Microsoft's feature roadmap and tenant configuration permissions.
  - Modifying the quarantine release workflow to prevent user-initiated ticket creation would require Microsoft 365 tenant-level policy changes outside Bmove's direct control.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** Informational — safe for agent self-service

