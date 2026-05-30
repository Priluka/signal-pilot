---
id: croatia-parking-fine-dispute-and-payment
name: croatia_parking_fine_dispute_and_payment
title: Croatian end-users disputing parking fines or unable to pay them via Bmove app
description: End users in Croatia (and occasionally other countries) contact Bmove support after receiving a parking fine
  despite having paid via the app, or being unable to pay a fine through the app. A secondary group asks general questions
  about how to pay fines via Bmove. Bmove support typically redirects users to the responsible local parking authority, as
  fine issuance and cancellation are outside Bmove's jurisdiction.
category: end_user/knowledge_gaps
ticket_class: end_user
issue_category: knowledge_gap
resolution_pattern: vendor_escalation
languages:
- hr
- en
- other
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|croatia|dpk:c2
project_key: BS
cluster_size: 50
cluster_size_dedup: 50
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.88
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.98
median_resolution_minutes: 2492.0
p95_resolution_minutes: 41742.95
cannot_reproduce_rate: 0.0
data_window_start: '2023-04-17'
data_window_end: '2025-12-17'
annual_hours_saved: 1.1
roi:
  baseline_active_hours: 4.5
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 1.4
  deflection_hours_range:
  - 0.9
  - 1.8
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.1
  agent_assist_hours_range:
  - 0.8
  - 1.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.8
  product_fix_hours_range:
  - 0.5
  - 1.0
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.3
  autonomous_resolve_hours_range:
  - 0.2
  - 0.4
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-33872
- BS-35113
- BS-10070
- BS-7804
- BS-10363
- BS-13968
- BS-19335
- BS-34306
- BS-19919
- BS-36212
- BS-39118
- BS-7707
- BS-37028
- BS-21467
- BS-20695
- BS-27875
- BS-7523
- BS-17599
canonical_examples:
- BS-33872
- BS-35113
- BS-10363
vendor_dependency:
  vendor_name: Local municipal parking authorities (e.g. Best In Parking Varaždin, Komunalac Sisak, Komunalni servis Rovinj,
    Brela parking service, Malinska parking concessionaire)
  involves_vendor: true
  typical_wait_days: null
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Auto-reply to general 'how do I pay a fine via Bmove?' informational queries with a
    help-center link and authority lookup, requiring no backend transaction review
  autonomous_resolve_safety_constraints:
  - Must not autonomously adjudicate or acknowledge liability for any disputed fine
  - Must not send authority contact details without verifying the user's municipality is in the known lookup table
  - All tickets involving a claimed payment proof or payment failure must be routed to a human agent
  - Must include a clear escalation path in every automated reply
  - No financial commitments or refund promises may be made autonomously
related_playbooks:
- croatia-bmove-app-feedback-miscellaneous
- croatia-parking-fine-dispute
- croatia-parking-fine-payment-failure
- croatia-parking-payment-failure__ffdf4e
- croatia-parking-ticket-storno-user-error
- croatia-ticketless-best-in-parking-knowledge-gap
- croatia-ticketless-open-session-at-exit__f25b63
- croatia-ticketless-rental-car-ghost-charge
- croatian-end-user-wrong-registration-storno-refund
- croatian-invoice-download-request
- croatian-parking-debt-payment-failure
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__56d2b2
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- open-session-at-exit-payment-failure
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
# Skills enabled — reads auto-execute, writes are HITL.
allowed_skills:
  - graylog_search
  - parkis_lookup
  - skidata_session_lookup
  - bmove_user_lookup
  - datatrans_transaction
  - jira_get_history
  - jira_add_internal_comment
  - jira_add_public_comment
  - jira_transition
---

# Croatian end-users disputing parking fines or unable to pay them via Bmove app

## What this pattern is

End users in Croatia (and occasionally other countries) contact Bmove support after receiving a parking fine despite having paid via the app, or being unable to pay a fine through the app. A secondary group asks general questions about how to pay fines via Bmove. Bmove support typically redirects users to the responsible local parking authority, as fine issuance and cancellation are outside Bmove's jurisdiction.

## When this applies

- User receives a parking fine after having paid via the Bmove app
- User is unable to pay a parking fine through the Bmove app (payment error or city not available)
- User asks how to pay a parking fine via the Bmove app
- User receives a fine they believe is unjust or fraudulent
- Authorization/permit status is deactivated causing recurring fines
- CorvusPay or other payment provider technical failure blocks payment, leading to a fine

## Typical resolution flow

1. User submits feedback via Bmove app or emails support describing the fine situation
2. Support agent reviews the user's parking transaction history in the backend
3. If city/service is not under Bmove jurisdiction, agent redirects user to the local parking authority
4. If payment failure caused the fine, agent explains the technical reason and advises user to re-apply for complaint/cancellation with the parking authority
5. If fine photo is needed for verification, agent requests a photo from the user
6. Ticket is closed after redirect or after confirming transaction details

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Review user's transaction and parking card history in Bmove backend | support_agent | Bmove backend/admin system | 5 min |
| Redirect user to responsible local parking authority with contact details | support_agent | Jira/email | 5 min |
| Request photo of fine from user for further investigation | support_agent | Jira/email | 3 min |
| Explain technical payment failure (e.g. CorvusPay outage) and advise user to re-file complaint | support_agent | Jira/email | 10 min |

## Vendor dependency

- **Vendor:** Local municipal parking authorities (e.g. Best In Parking Varaždin, Komunalac Sisak, Komunalni servis Rovinj, Brela parking service, Malinska parking concessionaire)

## Evidence

Derived from 50 tickets in cluster `BS:end_user|croatia|dpk:c2`. Direct quotes from 7 representative tickets:

- `BS-33872` _[hr]_: "kaznu su izdali djelatnici parking službe grada Varaždina, pa Vas ovim putem molimo da se za navedeno obratite njima"
- `BS-35113` _[hr]_: "za navedeno Vas molimo da se javite parking službi grada Varaždina jer je to u njihovoj nadležnosti"
- `BS-10363` _[en]_: "city of Brela is not available on Bmove app. For this, please contact Brela parking service"
- `BS-13968` _[hr]_: "29.9.2023. CorvusPay je imao tehničkih poteškoća u jutarnjim satima. Zbog toga niste bili u mogućnosti platiti parking."
- `BS-7523` _[hr]_: "mi ne možemo poništavati kazne jer one nisu u našoj nadležnosti, već u nadležnosti onoga tko ih izdaje"
- `BS-20695` _[hr]_: "platila sam parking preko ove aplikacije no unatoč tome sam dobila uplatnicu za plaćanje kazne za parkiranje"
- `BS-36212` _[hr]_: "Vaša autorizacija je u statusu 'deaktivirana', a zadnja povlaštena karta koju ste kupili putem Bmove usluge istekla je 12.4.2025."

## Cluster statistics

- **Volume:** 50 tickets total (50 unique semantic events after dedup)
- **Frequency:** 0.98 tickets/month (over data window 2023-04-17 → 2025-12-17)
- **Median resolution:** 1.7 days
- **Languages:** hr, en, other
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~4.5 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1.1 (range [0.791, 1.46])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.80
- **Rationale:** The resolution pattern is highly templated — transaction lookup, authority contact details by municipality, and a standard redirect message — making agent-assist macros and a contextual authority-lookup tool highly applicable; the main variable is matching the correct local authority to the user's location, which a lookup widget can automate.
- **Validation:** Run a 3-week shadow-mode pilot where the assist tool pre-populates the municipal authority contact and a draft redirect message; measure whether agents accept the draft ≥80% of the time and whether average handle time drops by ≥15%.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~0.8 (range [0.53, 0.975])
- **Root cause:** A subset of tickets stems from a technical payment failure (e.g. CorvusPay gateway outage) that silently leaves a transaction in a failed or ambiguous state, causing users to receive fines for sessions they believed were paid. Better real-time payment status feedback and retry/failure notifications in the app would reduce this sub-cluster.
- **Rationale:** Improved in-app payment failure alerting and a visible transaction status screen would pre-empt tickets from users unaware their payment failed, but fine disputes arising from parking authority errors are outside Bmove's technical control and cannot be eliminated by a product fix. Hours eliminated are capped to the estimated payment-failure sub-cluster (~17% of volume).
- **Validation:** Engineering team should instrument CorvusPay callback failures to quantify how many active sessions end without a confirmed payment event; a spike-test in a staging environment against a mock gateway outage confirms the retry/notification logic before release.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~1.4 (range [0.95, 1.755])
- **Form:** `help_center`
- **Deflection rate:** ~30% (range [21%, 39%])
- **Feasibility:** 0.65
- **Rationale:** A significant share of tickets are informational — users asking how to pay fines via Bmove or what to do next — which are strong candidates for a structured help-center article listing responsible parking authorities and step-by-step dispute instructions. Tickets involving disputed transactions or payment failures require human review and cannot be deflected by self-service alone.
- **Validation:** Deploy a help-center article covering the 'how to dispute a fine' and 'which authority to contact' flows, then measure ticket volume for this cluster over 8 weeks; deflection is validated if tagged inbound tickets drop by ≥20% without a rise in repeat contacts.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.3 (range [0.203, 0.37])
- **Narrow use case:** Auto-reply to general 'how do I pay a fine via Bmove?' informational queries with a help-center link and authority lookup, requiring no backend transaction review
- **Safety constraints:**
  - Must not autonomously adjudicate or acknowledge liability for any disputed fine
  - Must not send authority contact details without verifying the user's municipality is in the known lookup table
  - All tickets involving a claimed payment proof or payment failure must be routed to a human agent
  - Must include a clear escalation path in every automated reply
  - No financial commitments or refund promises may be made autonomously
- **Rationale:** Only the purely informational sub-cluster (users asking how the fine payment process works) is safe to resolve autonomously; any ticket involving a transaction dispute, fine cancellation request, or payment failure carries regulatory and reputational risk that requires human judgment. Volume and savings potential are low given the small annual frequency.
- **Validation:** Pilot over 6 weeks by automatically tagging inbound tickets as 'informational-only' using keyword classification, manually reviewing 100% of auto-tagged tickets to confirm false-positive rate is <5% before enabling any automated reply.

### Risks

- **Compliance concerns:**
  - Parking fine issuance and cancellation fall under Croatian municipal law; any statement implying Bmove accepts responsibility could create legal liability
  - GDPR: transaction history and fine photos constitute personal data — automated processing must have a documented legal basis and data minimisation controls
  - Consumer protection regulations may require human-reviewable escalation paths for financial disputes
- **Must not automate:**
  - Adjudicating whether a fine should be cancelled or upheld
  - Communicating directly with parking authorities on behalf of the user
  - Confirming or denying whether a specific payment was legally valid
  - Issuing any form of compensation or credit without human approval
- **Vendor dependencies blocking automation:**
  - Fine cancellation decisions are entirely at the discretion of the relevant municipal parking authority (e.g. Best In Parking Varaždin, Komunalac Sisak, Komunalni servis Rovinj, Brela, Malinska) — Bmove has no API or SLA with these authorities
  - CorvusPay payment gateway outages are an external dependency; resolution of tickets caused by gateway failures depends on CorvusPay's own incident response timeline
  - No structured data exchange exists between Bmove and municipal authorities, so transaction verification must remain manual

## Agent compatibility

- **Status:** `active` (extraction confidence 0.88)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

