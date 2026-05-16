---
id: unsolicited-spam-marketing-emails
name: unsolicited_spam_marketing_emails
title: Unsolicited spam/marketing emails submitted as support tickets
description: External parties are sending unsolicited cold-outreach emails offering digital marketing, SEO optimization, website
  redesign, and other web services to bmove/phonzie.eu domains. These emails are being routed into the support ticket system
  rather than being filtered as spam. They contain no actual support request and require no product action.
category: b2b_operator/user_issues
ticket_class: b2b_partner
issue_category: misuse
resolution_pattern: no_action
languages:
- en
- it
country_focus:
- it
- other
status: active
cluster_id: BS:unknown|italy|no_label:c1
project_key: BS
cluster_size: 18
cluster_size_dedup: 16
sample_size_used: 16
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.31
median_resolution_minutes: 1421.0
p95_resolution_minutes: 12039.099999999984
cannot_reproduce_rate: 0.0
data_window_start: '2023-05-11'
data_window_end: '2026-02-26'
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
- BS-12253
- BS-20158
- BS-22843
- BS-24196
- BS-8075
- BS-16740
- BS-22209
- BS-26835
- BS-49681
- BS-49997
- BS-21280
- BS-36939
- BS-20569
- BS-8904
- BS-18940
- BS-21991
canonical_examples:
- BS-16740
- BS-18940
- BS-12253
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
  note: Informational — safe for agent self-service
  autonomous_resolve_max_safe_volume_pct: 0.3
  autonomous_resolve_narrow_use_case: Auto-close tickets classified as unsolicited marketing/spam with no customer account
    association and no prior thread
  autonomous_resolve_safety_constraints:
  - Only act on tickets with zero customer account or order linkage
  - Classifier confidence threshold must exceed 0.95 before autonomous close
  - All auto-closed tickets must be logged and human-reviewable for 30 days
  - Must not auto-close any ticket containing a domain-registered user's email address
  - Escalate to human if any ambiguity about sender identity exists
related_playbooks:
- bmove-app-general-feedback-and-issues
- italian-b2b-unsolicited-procurement-marketing-emails
- microsoft365-quarantine-notification-auto-tickets
- microsoft365-quarantine-phishing-meta-impersonation
- russian-spam-suggestion-tickets
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Unsolicited spam/marketing emails submitted as support tickets

## What this pattern is

External parties are sending unsolicited cold-outreach emails offering digital marketing, SEO optimization, website redesign, and other web services to bmove/phonzie.eu domains. These emails are being routed into the support ticket system rather than being filtered as spam. They contain no actual support request and require no product action.

## When this applies

- External marketers or vendors send unsolicited cold-outreach emails to support or contact email addresses of bmove.com or phonzie.eu
- Emails offering SEO, website redesign, digital marketing, or similar services are forwarded or arrive directly in the ticketing system
- Promotional newsletters or B2B service pitches reach the support inbox

## Typical resolution flow

1. Unsolicited email is sent to bmove.com or phonzie.eu contact/support address
2. Email is ingested into the support ticketing system and assigned a ticket ID
3. Ticket is classified as unknown with sub-issue 'other' due to lack of a real support request
4. Agent or automated system recognizes the ticket as spam/advertising
5. Ticket is closed with no action or noted as not a real support request

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Identify ticket as unsolicited marketing/spam email with no support need | support agent | ticket system | 2 min |
| Close or discard ticket without response | support agent | ticket system | 1 min |

## Evidence

Derived from 18 tickets in cluster `BS:unknown|italy|no_label:c1`. Direct quotes from 5 representative tickets:

- `BS-16740` _[it]_: "Non è una richiesta di supporto è solo pubblicità/spam/presentazione società"
- `BS-18940` _[it]_: "Non è un ticket ma una mail presentazione società"
- `BS-12253` _[en]_: "I am a Digital Marketing Consultant and while working on an online project I came across your website phonzie.eu"
- `BS-24196` _[en]_: "We can place your website phonzie.eu on top of the Natural Listings on Google."
- `BS-22843` _[en]_: "Do you want to Design or Redesign your website phonzie.eu? I can create a unique & beautiful website for your organization at a minimal cost."

## Cluster statistics

- **Volume:** 18 tickets total (16 unique semantic events after dedup)
- **Frequency:** 0.31 tickets/month (over data window 2023-05-11 → 2026-02-26)
- **Median resolution:** 23.7 hours
- **Languages:** en, it
- **Country focus:** it, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~0.2 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.1 (range [0.035, 0.065])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.50
- **Rationale:** An agent-assist classifier that auto-labels incoming tickets as 'spam/no-action' and pre-populates a one-click close action could shave roughly 25% off the already-minimal 3-minute handle time, though absolute savings are negligible given the low annual frequency. The marginal ROI is very low at this volume.
- **Validation:** Run a 4-week shadow-mode pilot where the classifier tags suspected spam tickets; measure precision/recall and compare agent close-time with and without the assist label to validate the 25% reduction assumption.

### Product fix (`directional`)

- **Is product bug:** `False`
- **Engineering effort tier:** `low`
  - Sprints estimate: ~0.5 (range [0.3, 0.7])
- **Hours eliminated per year:** ~0.2 (range [0.14, 0.2])
- **Root cause:** Spam/marketing emails sent to bmove/phonzie.eu domain addresses are being routed into the support ticketing system without adequate spam filtering. This is an infrastructure/configuration gap (missing or misconfigured spam filter upstream of the ticketing ingest), not a product bug.
- **Rationale:** Configuring or tightening email spam filtering rules (e.g., SPF/DKIM/DMARC enforcement, keyword/sender-pattern blocklists, or a dedicated spam gateway) upstream of ticketing ingest could eliminate virtually all of this cluster at low engineering cost. Hours eliminated are capped at the 0.2-hour baseline.
- **Validation:** Engineering team should audit current email ingest pipeline and spam-filter configuration; a 2-week trial with a spam-filter rule targeting common solicitation keywords and unknown sender domains can quantify false-positive rate before full rollout.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0 (range [0, 0])
- **Form:** `none`
- **Deflection rate:** ~0% (range [0%, 0%])
- **Feasibility:** 0.05
- **Rationale:** These tickets originate from external spammers, not from customers seeking help; no FAQ or self-service form can intercept or redirect unsolicited cold-outreach before it enters the ticketing system. Deflection via user-facing content is structurally inapplicable to this pattern.
- **Validation:** No pilot needed; structural analysis confirms zero deflection potential via self-service content.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 30% of tickets
- **Hours saved per year:** ~0.1 (range [0.042, 0.078])
- **Narrow use case:** Auto-close tickets classified as unsolicited marketing/spam with no customer account association and no prior thread
- **Safety constraints:**
  - Only act on tickets with zero customer account or order linkage
  - Classifier confidence threshold must exceed 0.95 before autonomous close
  - All auto-closed tickets must be logged and human-reviewable for 30 days
  - Must not auto-close any ticket containing a domain-registered user's email address
  - Escalate to human if any ambiguity about sender identity exists
- **Rationale:** Autonomous close is technically feasible for clearly identified spam with no customer relationship, and the safety risk is low since no product action or customer response is involved; however, absolute hours saved are negligible (≈0.06 hrs/year) at this volume, making the implementation cost likely to exceed the benefit without the product-fix path. The 30% volume cap is applied conservatively.
- **Validation:** Pilot with a high-confidence spam classifier in shadow mode for 6 weeks, reviewing all candidate auto-closes manually; accept autonomous action only when false-positive rate is confirmed below 1% across at least 20 candidate tickets.

### Risks

- **Compliance concerns:**
  - Auto-closing tickets without human review risks misclassifying legitimate vendor or partner communications as spam
  - Audit trail must be maintained for all autonomously closed tickets to satisfy any future dispute or compliance review
- **Must not automate:**
  - Any ticket where the sender email matches a registered customer or known partner domain
  - Any ticket that contains an attached document that has not been scanned for content (potential misrouted contract or legal notice)

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `True`
- **RAG-consumable:** `True`
- **Note:** Informational — safe for agent self-service

