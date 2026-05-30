---
id: croatian-ticketless-open-session-at-exit__275624
name: croatian_ticketless_open_session_at_exit
title: Bmove Ticketless session remains open after user has exited parking garage
description: End users in Croatia (primarily) report that their Bmove Ticketless parking session remains active in the app
  after they have physically exited a parking garage. The failure to auto-close the session is typically triggered by a barrier/ramp
  malfunction at exit, an invalid payment card, or a system error, after which a garage employee manually raises the barrier
  but the session is not automatically closed in the Bmove system. Support resolves tickets by manually billing the session
  via Bmove tools and then closing the session, after which users are advised to restart the app.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- hr
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|croatia|skidata:c0
project_key: BS
cluster_size: 58
cluster_size_dedup: 58
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 1.14
median_resolution_minutes: 1171.0
p95_resolution_minutes: 5817.649999999995
cannot_reproduce_rate: 0.0
data_window_start: '2024-01-23'
data_window_end: '2026-01-18'
annual_hours_saved: 1.0
roi:
  baseline_active_hours: 3.9
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.3
  deflection_hours_range:
  - 0.2
  - 0.4
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 1.0
  agent_assist_hours_range:
  - 0.7
  - 1.2
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 3.5
  product_fix_hours_range:
  - 2.7
  - 3.9
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
- BS-28574
- BS-43833
- BS-33502
- BS-17820
- BS-20877
- BS-26227
- BS-28789
- BS-47358
- BS-30075
- BS-23921
- BS-47342
- BS-45923
- BS-33066
- BS-23879
- BS-29562
- BS-46959
- BS-22132
- BS-20128
canonical_examples:
- BS-28574
- BS-43833
- BS-26227
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
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.2
  autonomous_resolve_narrow_use_case: Auto-close sessions where payment has already succeeded and the only remaining action
    is closing the session record and sending the user notification, with no billing dispute or ambiguity.
  autonomous_resolve_safety_constraints:
  - Autonomous action must not process or initiate any payment; billing must already be confirmed complete before automation
    triggers.
  - Session must have a clear and unambiguous exit timestamp from barrier logs to avoid closing an active paying session.
  - A human billing agent must remain in the approval loop for any case where payment status is uncertain or disputed.
  - All autonomous closes must be logged with full audit trail and reversible within 24 hours.
  - Pilot must be limited to a single garage location before broader rollout.
related_playbooks:
- austrian-ticketless-open-session-at-exit__06e3d4
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__d6cf0c
- bmove-app-operational-issues-austria
- croatia-bmove-app-feedback-miscellaneous
- croatia-parking-fine-dispute
- croatia-parking-fine-dispute-and-payment
- croatia-parking-fine-payment-failure
- croatia-parking-payment-failure__e3b934
- croatia-parking-payment-failure__ffdf4e
- croatia-parking-ticket-storno-user-error
- croatia-ticketless-best-in-parking-knowledge-gap
- croatia-ticketless-open-session-at-exit__a7c97e
- croatia-ticketless-open-session-at-exit__f25b63
- croatia-ticketless-rental-car-ghost-charge
- croatian-end-user-wrong-registration-storno-refund
- croatian-invoice-download-request
- croatian-parking-debt-payment-failure
- croatian-ticketless-open-session-at-exit__56d2b2
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- open-session-at-exit-austria
- open-session-at-exit-payment-failure
- ticketless-open-session-at-exit__960f17
- ticketless-open-session-not-closed-at-exit
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

# Bmove Ticketless session remains open after user has exited parking garage

## What this pattern is

End users in Croatia (primarily) report that their Bmove Ticketless parking session remains active in the app after they have physically exited a parking garage. The failure to auto-close the session is typically triggered by a barrier/ramp malfunction at exit, an invalid payment card, or a system error, after which a garage employee manually raises the barrier but the session is not automatically closed in the Bmove system. Support resolves tickets by manually billing the session via Bmove tools and then closing the session, after which users are advised to restart the app.

## When this applies

- Exit barrier/ramp does not open automatically at parking exit
- Garage employee manually raises the barrier without the system closing the session
- Invalid or expired payment card prevents automatic session closure
- System processes payment but fails to close the ticketless session
- Session remains active after user has already physically left the garage

## Typical resolution flow

1. User parks using Bmove Ticketless (license plate recognition)
2. At exit, the barrier fails to lift automatically (due to system error, payment failure, or unknown reason)
3. Garage employee or support manually raises the barrier
4. User leaves the garage but the Bmove app still shows an active parking session
5. User contacts Bmove support requesting session closure
6. Support agent identifies the session ID and requests billing
7. Billing agent processes payment for the session
8. Session is manually closed in Bmove tools
9. User is notified that the session is closed and asked to restart the app

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Identify open session ID from ticket description or account lookup | support_agent | Bmove tools | 5 min |
| Request billing of the open session | support_agent (e.g. Zelimir Mateskovic) | Bmove tools | 5 min |
| Process payment and close the session | billing_agent (e.g. Hrvoje Sirovina, Paulina Mrnarević) | Bmove tools | 5 min |
| Notify user that session is closed and advise app restart | support_agent | ticketing system / email | 2 min |

## Evidence

Derived from 58 tickets in cluster `BS:end_user|croatia|skidata:c0`. Direct quotes from 7 representative tickets:

- `BS-28574` _[hr]_: "Zaposlenik na kasi mi je onda otvorio rampu te je rekao da će moj broj tablica unijeti ručno da sam izašao sa parkinga međutim u aplikaciji još uvijek piše da sam parkiran u garaži (već 3. dan), a nis"
- `BS-43833` _[hr]_: "Ostao mi je otvoren Ticketless zbog nevažeće kartice, promijenila sam karticu u aplikaciji pa molim da zatvorite taj ticketless."
- `BS-26227` _[hr]_: "Rampu nam je naposlijetku podignuo djelatnik garaže i rekao da će on zatvoriti parkirni nalog te da će nam se za isti skinuti sa računa. Izašli smo nakon 1sat i 45 minuta. Međutim nalog je još aktiva "
- `BS-30075` _[hr]_: "u aplikaciji mi stoji jedan otvorena sesija , ja sam normalno izašao iz garaže i sada kada želim ući ne prepoznaje me aplikacija."
- `BS-29562` _[hr]_: "u aplikaciji mi je još uvijek aktivna sesija na parkingu (već 4 dana) sa kojeg sam izašao isti dan"
- `BS-28574` _[hr]_: "Poštovani, Vaša Bmove Ticketless sesija je zatvorena. Ako je i dalje vidite kao aktivnu, molimo Vas da ponovno pokrenete Bmove aplikaciju."
- `BS-23921` _[hr]_: "prema Bmove tools naplata je prošla odmah, ali sesija je aktivna. Zatvorim na 0,00."

## Cluster statistics

- **Volume:** 58 tickets total (58 unique semantic events after dedup)
- **Frequency:** 1.14 tickets/month (over data window 2024-01-23 → 2026-01-18)
- **Median resolution:** 19.5 hours
- **Languages:** hr
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~3.9 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~1 (range [0.7, 1.25])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** The workflow is highly structured (lookup session ID → request billing → close → notify user), making it a strong candidate for an agent-assist tool that pre-populates session IDs from the ticket, generates the billing request, and drafts the user-notification message, reducing active minutes from ~17 to roughly ~13 per ticket.
- **Validation:** Run a 3-week shadow-mode pilot where the assist tool pre-fetches session IDs and drafts the closing notification; compare agent time-on-ticket before and after using ticket timestamps.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~3.5 (range [2.7, 3.9])
- **Root cause:** When a garage employee manually raises the barrier (bypassing the normal automated exit flow due to ramp malfunction, invalid card, or system error), the Bmove Ticketless system receives no exit signal and therefore never auto-closes the parking session. The fix requires implementing a fallback session-closure mechanism triggered by manual barrier override events or a configurable session-timeout with alert-and-auto-close logic.
- **Rationale:** A product fix that auto-closes sessions on manual barrier override or after a configurable timeout would eliminate nearly all tickets in this cluster; a small residual is retained for edge cases where billing disputes or unusual errors still require human review. Effort estimate assumes integration work with barrier hardware/event APIs is non-trivial but well-scoped.
- **Validation:** Engineering team should spike on the barrier event API contract and parking system webhook availability to validate the integration effort estimate; a prototype in a single garage in Croatia could confirm end-to-end session closure within one sprint.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.3 (range [0.23, 0.39])
- **Form:** `in_app_help`
- **Deflection rate:** ~8% (range [6%, 10%])
- **Feasibility:** 0.25
- **Rationale:** The session cannot be closed by the user themselves — it requires backend access by a support or billing agent — so self-service content cannot resolve the issue, only set expectations. A small deflection rate is credited purely for users who might stop re-contacting after reading that manual resolution is underway.
- **Validation:** Deploy an in-app FAQ article explaining the manual-close process for 6 weeks; measure whether repeat contacts per incident drop, and whether any tickets cite the article as reducing follow-up messages.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 20% of tickets
- **Hours saved per year:** ~0.5 (range [0.35, 0.57])
- **Narrow use case:** Auto-close sessions where payment has already succeeded and the only remaining action is closing the session record and sending the user notification, with no billing dispute or ambiguity.
- **Safety constraints:**
  - Autonomous action must not process or initiate any payment; billing must already be confirmed complete before automation triggers.
  - Session must have a clear and unambiguous exit timestamp from barrier logs to avoid closing an active paying session.
  - A human billing agent must remain in the approval loop for any case where payment status is uncertain or disputed.
  - All autonomous closes must be logged with full audit trail and reversible within 24 hours.
  - Pilot must be limited to a single garage location before broader rollout.
- **Rationale:** Full autonomous resolution carries payment and billing risk; a narrow use case covering only already-billed sessions with confirmed exit events is feasible at low volume, but the small annual frequency (13.6 tickets/year) means absolute savings are modest. The product fix opportunity is a higher-ROI path.
- **Validation:** Pilot autonomous close on 20% of tickets over 8 weeks where billing is pre-confirmed; acceptance criteria are zero incorrect closes, zero erroneous charges, and 100% audit log completeness before expanding scope.

### Risks

- **Compliance concerns:**
  - Automated session closure combined with payment processing must comply with Croatian and EU payment regulations (PSD2); any autonomous billing action requires explicit audit trails.
  - GDPR requires that automated decisions affecting users (e.g. billing closure) are logged and contestable.
  - If the user's card was invalid at exit, automated re-billing attempts must respect retry limits and card-scheme rules.
- **Must not automate:**
  - Initiating or re-attempting payment on a card that previously failed — this requires human judgment and may involve fraud or dispute risk.
  - Closing a session where exit time is ambiguous or where the user has raised a billing dispute.
  - Any action that could result in double-billing a user for the same parking session.

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

