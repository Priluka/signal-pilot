---
id: microsoft365-quarantine-phishing-meta-impersonation
name: microsoft365_quarantine_phishing_meta_impersonation
title: Microsoft 365 Quarantine Notifications for Meta/Facebook Phishing Emails
description: End users receive automated Microsoft 365 Security Center quarantine digest emails notifying them that one or
  more inbound phishing messages have been blocked. The quarantined messages consistently impersonate Meta/Facebook (and occasionally
  other brands like Netflix), using fake verification badges, policy violation alerts, or invitations to Ads Manager Suite
  to lure recipients. These tickets appear to be auto-generated forwarded quarantine notifications rather than genuine user-reported
  support requests.
category: end_user/user_issues
ticket_class: end_user
issue_category: misuse
resolution_pattern: no_action
languages:
- en
- hr
- other
country_focus:
- other
status: active
cluster_id: BS:end_user|italy|no_label:c0
project_key: BS
cluster_size: 30
cluster_size_dedup: 30
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.92
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.59
median_resolution_minutes: 0.0
p95_resolution_minutes: 1625.5999999999972
cannot_reproduce_rate: 0.0
data_window_start: '2025-06-14'
data_window_end: '2026-04-26'
annual_hours_saved: 3.4
roi:
  baseline_active_hours: 7.6
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.4
  deflection_hours_range:
  - 0.3
  - 0.5
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 3.4
  agent_assist_hours_range:
  - 2.4
  - 4.4
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 7.1
  product_fix_hours_range:
  - 5.3
  - 7.6
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 1.1
  autonomous_resolve_hours_range:
  - 0.8
  - 1.4
  autonomous_resolve_max_safe_volume_pct: 0.3
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-48351
- BS-50374
- BS-38533
- BS-38644
- BS-41121
- BS-50388
- BS-52610
- BS-50219
- BS-41375
- BS-50716
- BS-41306
- BS-42251
- BS-41039
- BS-41485
- BS-48577
- BS-41788
- BS-50558
- BS-40063
canonical_examples:
- BS-48351
- BS-41121
- BS-38644
vendor_dependency:
  vendor_name: Microsoft 365 / Exchange Online Protection
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
  autonomous_resolve_narrow_use_case: Auto-close inbound tickets that contain a Microsoft 365 quarantine digest notification
    with no user-authored question or request body
  autonomous_resolve_safety_constraints:
  - Must confirm ticket body matches known quarantine digest email patterns (subject line, sender domain, and body structure)
    before autonomous closure — do not act on tickets that contain any additional user-authored text indicating a genuine
    concern
  - Apply only after the mailbox routing fix is in place; residual tickets should be rare and low-risk
  - Log all auto-closed tickets with reason code for human audit review at least monthly
  - Exclude any ticket where the forwarding user is flagged as a high-value or executive account until confidence in signal
    accuracy exceeds 95%
  - Maintain a human override queue for tickets auto-closed in error, with SLA to review within 1 business day
related_playbooks:
- bmove-app-negative-feedback-italy
- italian-b2b-unsolicited-procurement-marketing-emails
- italian-ticketless-setup-and-payment-issues
- italy-bmove-payment-method-issues
- microsoft365-quarantine-notification-auto-tickets
- phonzie-to-bmove-credit-refund-request
- russian-spam-suggestion-tickets
- unsolicited-spam-marketing-emails
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Microsoft 365 Quarantine Notifications for Meta/Facebook Phishing Emails

## What this pattern is

End users receive automated Microsoft 365 Security Center quarantine digest emails notifying them that one or more inbound phishing messages have been blocked. The quarantined messages consistently impersonate Meta/Facebook (and occasionally other brands like Netflix), using fake verification badges, policy violation alerts, or invitations to Ads Manager Suite to lure recipients. These tickets appear to be auto-generated forwarded quarantine notifications rather than genuine user-reported support requests.

## When this applies

- Microsoft 365 Exchange Online Protection classifies an inbound email as 'high confidence phish' and quarantines it
- The Microsoft 365 Security Center sends an automated quarantine digest notification to the mailbox owner
- The end user forwards or the system auto-submits the quarantine notification email to the Bmove support channel

## Typical resolution flow

1. Phishing email impersonating Meta/Facebook (or similar brand) is sent to a Bmove user's Microsoft 365 mailbox
2. Microsoft 365 Exchange Online Protection quarantines the message as high-confidence phish
3. Microsoft 365 Security Center sends an automated quarantine summary notification to the user
4. The quarantine notification email arrives in the Bmove support ticket queue (likely via an auto-forward or shared mailbox configuration)
5. A support ticket is created with subject 'Microsoft 365 security: You have messages in quarantine'

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Identify ticket as an auto-generated Microsoft 365 quarantine notification, not a genuine end-user support request | support_agent | Bmove Support ticketing system | 2 min |
| Close ticket without action or with a brief note explaining the quarantine notification is automated and no support action is needed | support_agent | Bmove Support ticketing system | 2 min |
| Investigate and fix the mailbox or routing configuration that causes quarantine digest emails to land in the support queue | it_admin | Microsoft 365 Admin Center / Exchange Online | 60 min |

## Vendor dependency

- **Vendor:** Microsoft 365 / Exchange Online Protection

## Evidence

Derived from 30 tickets in cluster `BS:end_user|italy|no_label:c0`. Direct quotes from 6 representative tickets:

- `BS-48351` _[hr]_: "Prevented high confidence phish messages    Sender:  t****@s.ksmg.org   🚨 [HITNO] Aktivirajte besplatnu biometrijsku zaštitu za Bmove - Primite Meta plavu kvačicu"
- `BS-41121` _[en]_: "Prevented high confidence phish messages    Sender:  a****@gmail.com   Meta lnc has invited you to test Ads Manager Suite"
- `BS-38644` _[en]_: "Prevented high confidence phish messages    Sender:  i****@s.lb.edu.vn   -Action Required: Meta Policy Violation Identified"
- `BS-50374` _[hr]_: "🎉 Meta Business: Vaša je stranica odabrana za besplatnu plavu značku"
- `BS-41788` _[en]_: "Prevented high confidence phish messages    Sender:  p****@casasanti.it  Subject: NETFLIX :Oops! There's an Issue with Your Account Billing #V****"
- `BS-40063` _[en]_: "Review them within  15 days of the received date by going to the Quarantine pagein the Security Center."

## Cluster statistics

- **Volume:** 30 tickets total (30 unique semantic events after dedup)
- **Frequency:** 0.59 tickets/month (over data window 2025-06-14 → 2026-04-26)
- **Median resolution:** 0 min
- **Languages:** en, hr, other
- **Country focus:** other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~7.6 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~3.4 (range [2.4, 4.4])
- **Time reduction per ticket:** ~45% (range [32%, 58%])
- **Feasibility:** 0.85
- **Rationale:** The resolution pattern is fully deterministic (identify quarantine notification → close with standard note), making it an ideal candidate for an agent-assist macro or auto-classification rule that pre-fills ticket disposition and a templated closure note, cutting active work from ~4 minutes down to ~2 minutes per ticket. The 60-minute IT admin investigation action is a one-time fix and should not recur once routing is corrected.
- **Validation:** Run auto-classification in shadow mode for 2 weeks, comparing suggested disposition to agent decisions; require ≥90% agreement before enabling one-click acceptance; measure handle-time delta via ticketing system timestamps.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~0.2 (range [0.2, 0.3])
- **Hours eliminated per year:** ~7.1 (range [5.3, 7.6])
- **Root cause:** A mailbox or mail-flow routing rule causes Microsoft 365 Security Center quarantine digest emails to be delivered into the support queue rather than being discarded or routed to IT administrators only. This is an internal configuration defect, not a Microsoft platform bug.
- **Rationale:** Correcting the mail-flow or forwarding rule that routes quarantine digests to the support mailbox is a single Exchange Online configuration change estimated at under half a sprint; if implemented correctly it eliminates the entire ticket class. The upper bound is capped at the 7.6-hour baseline.
- **Validation:** IT admin applies the routing fix in a staging tenant, confirms quarantine digests no longer reach the support queue over a 2-week observation window, then promotes to production; ticket volume for this cluster is monitored for 4 weeks post-deployment.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.4 (range [0.28, 0.5])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.15
- **Rationale:** These tickets are auto-generated forwards of Microsoft 365 quarantine digest emails, not deliberate user-initiated support requests — there is no end-user decision point where self-service content would intercept the ticket creation. A help-center article explaining quarantine notifications would not stop the mailbox routing that generates these tickets.
- **Validation:** Publish a help-center article on M365 quarantine digests and measure ticket volume over a 6-week period; if volume does not drop, routing fix (product_fix) is the correct lever.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 30% of tickets
- **Hours saved per year:** ~1.1 (range [0.8, 1.43])
- **Narrow use case:** Auto-close inbound tickets that contain a Microsoft 365 quarantine digest notification with no user-authored question or request body
- **Safety constraints:**
  - Must confirm ticket body matches known quarantine digest email patterns (subject line, sender domain, and body structure) before autonomous closure — do not act on tickets that contain any additional user-authored text indicating a genuine concern
  - Apply only after the mailbox routing fix is in place; residual tickets should be rare and low-risk
  - Log all auto-closed tickets with reason code for human audit review at least monthly
  - Exclude any ticket where the forwarding user is flagged as a high-value or executive account until confidence in signal accuracy exceeds 95%
  - Maintain a human override queue for tickets auto-closed in error, with SLA to review within 1 business day
- **Rationale:** Given the low annual frequency (7.1 tickets/year) and deterministic resolution pattern, autonomous closure is technically feasible with high confidence; however, absolute hours savings are modest and the primary ROI lever is the product fix. Autonomous resolve is most valuable as a safety net for any tickets that slip through after the routing fix.
- **Validation:** Pilot autonomous closure on 30% of matching tickets for 6 weeks; acceptance criteria: zero false-positive closures on genuine user issues, confirmed by weekly human audit of the auto-closed log; expand only if false-positive rate remains at 0% across ≥20 auto-closed tickets.

### Risks

- **Compliance concerns:**
  - Auto-closing tickets without human review could inadvertently suppress a genuine phishing report or security incident if pattern matching is imprecise
  - Audit trails must be preserved for all auto-closed tickets to satisfy any information-security or compliance review requirements
- **Must not automate:**
  - Any ticket where the end user has authored a question, expressed confusion, or reported a suspected active compromise — these require human triage
  - The one-time IT admin investigation and routing fix (Action 3) — this is a human configuration task requiring judgment and access controls
- **Vendor dependencies blocking automation:**
  - The mailbox routing fix requires access to Microsoft 365 Exchange Admin Center or Exchange Online PowerShell; no Microsoft vendor approval or wait time is required, but internal IT admin access and change-management approval may be needed before the configuration change can be applied

## Agent compatibility

- **Status:** `active` (extraction confidence 0.92)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** Informational — safe for agent self-service

