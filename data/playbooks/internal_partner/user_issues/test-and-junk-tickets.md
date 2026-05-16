---
id: test-and-junk-tickets
name: test_and_junk_tickets
title: Test, junk, and empty tickets with no real support content
description: This cluster consists entirely of test tickets, empty submissions, and junk entries created by internal staff
  or automated email-to-ticket integrations. These tickets contain no real customer issue and are typically closed manually
  without any support action. Many originate from Outlook email-to-Jira routing tests or internal connectivity checks.
category: internal_partner/user_issues
ticket_class: internal_partner
issue_category: misuse
resolution_pattern: manual_close
languages:
- de
- en
- hr
- other
country_focus:
- other
status: active
cluster_id: BS:unknown|no_value|no_label:c1
project_key: BS
cluster_size: 24
cluster_size_dedup: 22
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.95
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.43
median_resolution_minutes: 917.0
p95_resolution_minutes: 295371.85
cannot_reproduce_rate: 0.0
data_window_start: '2022-09-19'
data_window_end: '2026-02-06'
annual_hours_saved: 0.1
roi:
  baseline_active_hours: 0.2
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.0
  deflection_hours_range:
  - 0.0
  - 0.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.1
  agent_assist_hours_range:
  - 0.1
  - 0.1
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.2
  product_fix_hours_range:
  - 0.1
  - 0.2
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: false
  product_fix_engineering_effort_tier: low
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.1
  autonomous_resolve_max_safe_volume_pct: 0.3
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-32703
- BS-36136
- BS-37233
- BS-2178
- BS-7056
- BS-16456
- BS-22894
- BS-36131
- BS-36145
- BS-48817
- BS-2179
- BS-36139
- BS-36135
- BS-36127
- BS-39249
- BS-36129
- BS-49115
- BS-36148
canonical_examples:
- BS-36136
- BS-22894
- BS-2178
vendor_dependency:
  vendor_name: null
  involves_vendor: false
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.3
  autonomous_resolve_narrow_use_case: Auto-close tickets where subject or body matches known test-email patterns (e.g., 'test',
    'junk', empty body) and sender is an internal domain
  autonomous_resolve_safety_constraints:
  - Restrict to tickets where sender domain is confirmed internal (not a customer domain)
  - Require both subject-line pattern match AND empty or near-empty body to reduce false-positive risk
  - Auto-close comment must be logged for audit trail
  - Any ticket with an attachment or body length above a minimal threshold must be routed to an agent
  - Maintain a human-reviewable daily digest of all auto-closed tickets
related_playbooks:
- bmove-app-feedback-mixed-issues__d6cf0c
- croatian-b2b-parking-ticket-storno-request
- hr-parking-transaction-reconciliation-discrepancy
- pkc-vehicle-registration-automated-tickets
- russian-spam-suggestion-tickets
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Test, junk, and empty tickets with no real support content

## What this pattern is

This cluster consists entirely of test tickets, empty submissions, and junk entries created by internal staff or automated email-to-ticket integrations. These tickets contain no real customer issue and are typically closed manually without any support action. Many originate from Outlook email-to-Jira routing tests or internal connectivity checks.

## When this applies

- Internal staff sends a test email to the support inbox to verify email-to-Jira integration
- Someone manually creates a blank or placeholder ticket to test the system
- Automated or accidental ticket creation via Outlook connector with no real content
- Staff checking whether support email address is reachable

## Typical resolution flow

1. Test ticket is created via email or manually in Jira with minimal or no content
2. Support team recognizes ticket as a test or junk entry
3. Ticket is manually closed with a brief comment indicating it is a test

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Identify ticket as test/junk with no real support issue | support agent | Jira | 1 min |
| Close the ticket with a comment noting it is a test | support agent | Jira | 1 min |

## Evidence

Derived from 24 tickets in cluster `BS:unknown|no_value|no_label:c1`. Direct quotes from 6 representative tickets:

- `BS-36136` _[en]_: "testing tickets => closing"
- `BS-22894` _[en]_: "delivery test to podrska email address for Croatian support podrška = support"
- `BS-2178` _[en]_: "@@Michael Gasparik can we close these two test tickets? @@Hrvoje Sirovina Yes please"
- `BS-2179` _[en]_: "Does someone receive this?"
- `BS-36136` _[other]_: "s****@bmove.com outlook 1924"
- `BS-32703` _[de]_: "aklan mustafa Handy fragen"

## Cluster statistics

- **Volume:** 24 tickets total (22 unique semantic events after dedup)
- **Frequency:** 0.43 tickets/month (over data window 2022-09-19 → 2026-02-06)
- **Median resolution:** 15.3 hours
- **Languages:** de, en, hr, other
- **Country focus:** other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~0.2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.1 (range [0.042, 0.078])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.50
- **Rationale:** An assist tool that auto-classifies tickets as test/junk and pre-populates the close comment would shave roughly 30% off the 2-minute handling time, but absolute savings are trivial given the low annual volume. The primary value is agent cognitive offload, not hours recovered.
- **Validation:** Run classifier in shadow mode for 2 weeks, flagging tickets it predicts as test/junk; measure precision/recall against agent decisions before enabling pre-population of close comments.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~0.5 (range [0.3, 0.7])
- **Hours eliminated per year:** ~0.2 (range [0.14, 0.2])
- **Root cause:** Tickets arise from Outlook-to-Jira email routing tests and internal connectivity checks — a process/configuration issue rather than a product defect. Configuring a dedicated test queue or suppression rule in the email-to-ticket integration could eliminate most inflow.
- **Rationale:** Routing test emails to a dedicated no-action mailbox or adding a subject-line filter rule could suppress the majority of these tickets before they enter the support queue. Elimination rate is estimated at ~85% of baseline given some residual manual tests may still reach the queue.
- **Validation:** Engineering team can scope effort by reviewing the current email-to-Jira integration config; a spike ticket of ≤1 day should confirm whether a filter rule or dedicated test address is feasible before committing sprint capacity.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0.01, 0.01])
- **Form:** `none`
- **Deflection rate:** ~5% (range [4%, 6%])
- **Feasibility:** 0.10
- **Rationale:** Test and junk tickets originate from internal staff or automated integrations, not end-users seeking help; self-service content cannot meaningfully intercept these submissions. Deflection potential is near-zero because the submitters are not attempting to resolve a support issue.
- **Validation:** Monitor ticket source metadata for 4 weeks to confirm what fraction, if any, originates from users who could have been redirected by a help-center prompt before submission.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 30% of tickets
- **Hours saved per year:** ~0.1 (range [0.04, 0.065])
- **Narrow use case:** Auto-close tickets where subject or body matches known test-email patterns (e.g., 'test', 'junk', empty body) and sender is an internal domain
- **Safety constraints:**
  - Restrict to tickets where sender domain is confirmed internal (not a customer domain)
  - Require both subject-line pattern match AND empty or near-empty body to reduce false-positive risk
  - Auto-close comment must be logged for audit trail
  - Any ticket with an attachment or body length above a minimal threshold must be routed to an agent
  - Maintain a human-reviewable daily digest of all auto-closed tickets
- **Rationale:** The pattern is highly stereotyped (empty body, internal sender, no customer impact) making autonomous closure technically sound, but annual volume is so low (5.2 tickets/year) that total hours saved are negligible. Implementation is still worth considering if it bundles into a broader junk-filtering workflow.
- **Validation:** Pilot for 8 weeks with auto-close gated behind a 24-hour hold; review all auto-closed tickets weekly to confirm zero false positives before removing the hold period.

### Risks

- **Compliance concerns:**
  - Auto-closing tickets without human review risks discarding a legitimate issue miscategorised as junk; audit log of all auto-closed tickets is required.
  - If any test ticket inadvertently contains PII or security-relevant content, automated disposal without review could create a compliance gap.
- **Must not automate:**
  - Tickets from external or customer domains must never be auto-closed under this pattern, even if they superficially resemble test submissions.
  - Tickets with non-empty bodies or attachments should not be autonomously resolved without agent review.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.95)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

