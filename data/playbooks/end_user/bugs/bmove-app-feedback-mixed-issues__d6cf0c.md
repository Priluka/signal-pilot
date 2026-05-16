---
id: bmove-app-feedback-mixed-issues__d6cf0c
name: bmove_app_feedback_mixed_issues
title: Bmove App In-App Feedback Submissions Covering Mixed Issues
description: Users submit feedback through the Bmove App covering a wide range of issues including unclosed parking sessions,
  payment failures, license plate recognition problems, wrong ticket purchases, refund requests, and general app problems.
  The tickets are auto-generated from an in-app feedback form and routed to support, resulting in a heterogeneous cluster
  with no single dominant root cause. Support typically acknowledges the ticket with a standard response and investigates
  the specific sub-issue on a case-by-case basis.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- de
- en
- other
country_focus:
- at
- hr
- other
status: draft
cluster_id: BS:unknown|no_value|no_label:c3
project_key: BS
cluster_size: 33
cluster_size_dedup: 30
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.62
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.59
median_resolution_minutes: 3622.0
p95_resolution_minutes: 443216.39999999973
cannot_reproduce_rate: 0.0303
data_window_start: '2023-04-04'
data_window_end: '2025-06-27'
annual_hours_saved: 2.2
roi:
  baseline_active_hours: 10.9
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.3
  deflection_hours_range:
  - 0.2
  - 0.3
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 2.2
  agent_assist_hours_range:
  - 1.5
  - 2.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 4.4
  product_fix_hours_range:
  - 3.1
  - 5.7
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.0
  autonomous_resolve_hours_range:
  - 0.0
  - 0.0
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-16141
- BS-24990
- BS-30994
- BS-7212
- BS-13745
- BS-14262
- BS-17574
- BS-17479
- BS-22338
- BS-20674
- BS-21138
- BS-30993
- BS-21394
- BS-7244
- BS-27585
- BS-21625
- BS-37660
- BS-16119
canonical_examples:
- BS-13745
- BS-24990
- BS-30994
vendor_dependency:
  vendor_name: CorvusPay / SKIDATA / parkdots.com
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: draft
  claude_skill: draft
  agent_assist: false
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-close confirmed test/spam feedback tickets with zero customer impact
  autonomous_resolve_safety_constraints:
  - Autonomous action limited strictly to tickets confirmed as test or spam with no payment or session state involved
  - No autonomous processing of refunds, payment disputes, or session closures
  - All vendor-dependent sub-issues (CorvusPay, SKIDATA, parkdots.com) must remain human-reviewed
  - Any ticket mentioning a financial amount or account action must be escalated to a human agent
  - Confidence threshold for spam/test classification must exceed 0.95 before auto-close
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__7950cd
- bmove-app-operational-issues-austria
- croatia-parking-payment-failure__e3b934
- croatia-ticketless-open-session-at-exit__a7c97e
- croatia-ticketless-open-session-at-exit__f25b63
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- hr-parking-transaction-reconciliation-discrepancy
- missing-parking-invoice-receipt
- open-session-at-exit-austria
- open-session-at-exit-payment-failure
- russian-spam-suggestion-tickets
- test-and-junk-tickets
- ticketless-open-session-at-exit__960f17
- ticketless-open-session-not-closed-at-exit
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Bmove App In-App Feedback Submissions Covering Mixed Issues

## What this pattern is

Users submit feedback through the Bmove App covering a wide range of issues including unclosed parking sessions, payment failures, license plate recognition problems, wrong ticket purchases, refund requests, and general app problems. The tickets are auto-generated from an in-app feedback form and routed to support, resulting in a heterogeneous cluster with no single dominant root cause. Support typically acknowledges the ticket with a standard response and investigates the specific sub-issue on a case-by-case basis.

## When this applies

- User submits feedback via the Bmove App in-app feedback form
- Parking session not closed after vehicle exit
- Payment card authentication fails when adding a card
- License plate not recognized at garage barrier
- User purchases ticket for wrong license plate
- User requests refund for accidental payment
- User reports incorrect parking duration displayed
- User cannot find or use bonus card
- Ghost parking session appears in app for a location the user never visited
- Ticket purchase fails with 'payment not made in time' error

## Typical resolution flow

1. User encounters problem with app or parking and submits feedback via in-app form
2. Auto-generated ticket is created in support system with user ID, email, feedback type, and message
3. Support agent sends standard acknowledgement response
4. Agent investigates the specific sub-issue (e.g., checks open sessions, verifies license plate setup, contacts technical team)
5. Agent resolves or escalates depending on issue type
6. Ticket is closed manually once resolved or if no action is required (e.g., test submissions)

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Send standard acknowledgement message to customer | support_agent | Jira / email | 5 min |
| Check and close unclosed parking session in backend | support_agent | Bmove backend / admin panel | 15 min |
| Verify license plate ticketless setup and check garage compatibility | support_agent | Bmove admin panel | 20 min |
| Escalate payment card authentication failure to technical/vendor team | support_agent | Internal escalation / CorvusPay portal | 30 min |
| Close test/spam feedback tickets without action | support_agent | Jira | 2 min |
| Process refund for accidental payment | support_agent | Bmove admin / payment backend | 20 min |

## Vendor dependency

- **Vendor:** CorvusPay / SKIDATA / parkdots.com

## Evidence

Derived from 33 tickets in cluster `BS:unknown|no_value|no_label:c3`. Direct quotes from 8 representative tickets:

- `BS-13745` _[de]_: "Mein Auto wurde bereits ausgefahren, aber der Timer läuft weiter."
- `BS-24990` _[en]_: "Dear customer, your entry should now work again. There was an unclosed parking session from earlier on."
- `BS-30994` _[other]_: "vedeli by ste prosím preveriť, prečo nefunguje čítanie nových slovenských EČV v garáži Erdberg vo Viedni?"
- `BS-37660` _[other]_: "Prečo keď pridavam platbu kartou, tak mi to napriek potvrdeniu testovacej plarby povie authentication failed?"
- `BS-17574` _[other]_: "omylom som zaklikla zlú ŠPZ keď som si kupovala parkovací lístok v starom meste"
- `BS-22338` _[other]_: "hlasi mi to ze parkujem v taliansku v Termi.. som pritom doma aj s autom. prosim okamžite zrušiť."
- `BS-21625` _[other]_: "Omylom uhradené parkovné 7.5.2024 za Kiu sportag červenú BT****. Prosím spatne vrátiť sumu 12,98€"
- `BS-7212` _[hr]_: "Na CorvusPay portalu se sada može vidjeti kako je kupovina moguća putem Visa, MC i Diners kartica."

## Cluster statistics

- **Volume:** 33 tickets total (30 unique semantic events after dedup)
- **Frequency:** 0.59 tickets/month (over data window 2023-04-04 → 2025-06-27)
- **Median resolution:** 2.5 days
- **Cannot Reproduce rate:** 3.0%
- **Languages:** de, en, other
- **Country focus:** at, hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~10.9 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~2.2 (range [1.53, 2.83])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.70
- **Rationale:** The standard acknowledgement step (5 min, every ticket) and the routing/classification decision are strong candidates for AI-drafted responses and automated sub-issue tagging, which could meaningfully reduce per-ticket active time. However, the heterogeneous nature of the cluster limits how much time can be saved on investigation steps, which remain manual and case-specific.
- **Validation:** Run shadow-mode AI draft generation for acknowledgement messages and sub-issue classification for 3 weeks; measure agent acceptance rate and time-to-first-response to validate the 20% time reduction assumption before full rollout.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~10 (range [7, 13])
- **Hours eliminated per year:** ~4.4 (range [3.1, 5.7])
- **Root cause:** Multiple distinct product defects are bundled here: unclosed session state management failures, payment card authentication errors (potentially involving CorvusPay), and license plate recognition mismatches with garage systems (SKIDATA/parkdots.com). There is no single fix; this cluster represents several independent engineering workstreams.
- **Rationale:** Addressing even a subset of the root causes (e.g., auto-closing stale sessions, improving LPR match logic) could eliminate a meaningful share of tickets, but vendor-dependent issues (CorvusPay authentication, SKIDATA compatibility) require cross-party coordination that significantly raises effort and uncertainty. The hours-eliminated estimate assumes ~40% of tickets become fully preventable via product fixes.
- **Validation:** Engineering team should triage sub-issues into independent workstreams, estimate each separately, and instrument session-close and payment-failure events to measure baseline error rates before committing to a fix scope.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.3 (range [0.189, 0.35])
- **Form:** `in_app_help`
- **Deflection rate:** ~15% (range [10%, 19%])
- **Feasibility:** 0.45
- **Rationale:** The cluster is highly heterogeneous with no single dominant root cause, limiting the effectiveness of any single FAQ or help article; only simple sub-issues like 'what happens if my session doesn't close' or 'how do I request a refund' are plausibly self-serviceable. The in-app origin of these tickets does offer a natural interception point, but most issues require backend investigation that users cannot perform themselves.
- **Validation:** Deploy targeted in-app help prompts covering the top 2-3 sub-issues (unclosed sessions, refund eligibility) for 6 weeks and measure the ratio of help-view completions to subsequent ticket submissions to validate the 15% deflection assumption.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Narrow use case:** Auto-close confirmed test/spam feedback tickets with zero customer impact
- **Safety constraints:**
  - Autonomous action limited strictly to tickets confirmed as test or spam with no payment or session state involved
  - No autonomous processing of refunds, payment disputes, or session closures
  - All vendor-dependent sub-issues (CorvusPay, SKIDATA, parkdots.com) must remain human-reviewed
  - Any ticket mentioning a financial amount or account action must be escalated to a human agent
  - Confidence threshold for spam/test classification must exceed 0.95 before auto-close
- **Rationale:** Only the test/spam ticket closure sub-type (~2 min per ticket) is safe for autonomous resolution without human review; all other sub-issues involve financial transactions, vendor systems, or account state changes that require human judgment. The very low annual frequency (7.1 tickets/year) and narrow autonomous scope result in negligible hours saved.
- **Validation:** Pilot autonomous spam/test closure on a sample of 10 tickets with 100% human audit of all auto-close decisions for 8 weeks; accept only if zero false positives (legitimate customer issues auto-closed) are observed.

### Risks

- **Compliance concerns:**
  - Refund processing must comply with applicable consumer protection and payment card regulations; automated or semi-automated refunds require audit trails
  - Payment card authentication failures may trigger PCI-DSS reporting obligations depending on root cause
  - User data accessed during backend session investigation must be handled per applicable data protection laws (e.g., GDPR if operating in EU)
- **Must not automate:**
  - Refund issuance or reversal of payments without human approval
  - Closing active parking sessions autonomously without verified session state (risk of stranding users or incorrect billing)
  - Responding definitively to license plate recognition disputes without human verification of garage system records
  - Escalation decisions to vendors (CorvusPay / SKIDATA / parkdots.com) without human review
- **Vendor dependencies blocking automation:**
  - Payment card authentication failures routed to CorvusPay require vendor cooperation for root-cause diagnosis and resolution; automation is blocked pending vendor API access or SLA agreements
  - License plate recognition issues involving SKIDATA or parkdots.com garage systems require bilateral data access and compatibility verification that cannot be resolved unilaterally
  - Any product fix addressing LPR or payment flows will require coordinated testing and sign-off with external vendor systems

## Agent compatibility

- **Status:** `draft` (extraction confidence 0.62)
- **Brainbox skill:** `draft`
- **Claude skill:** `draft`
- **Agent-assist:** `False`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

