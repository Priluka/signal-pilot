---
id: open-session-at-exit-payment-failure
name: open_session_at_exit_payment_failure
title: Parking session remains open after exit due to barrier lift by staff and subsequent payment authorization failure
description: End users report that their Bmove parking session remains active in the app after physically leaving a garage,
  because the exit barrier failed to trigger automatic session closure (often opened manually by garage staff or call center).
  When support attempts to close and charge the session, the payment authorization against the user's card fails, requiring
  the session to be closed at €0 and a debt to be created instead. The user must then manually pay the debt through the Bmove
  app.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- hr
- en
country_focus:
- hr
- at
- other
status: active
cluster_id: BS:end_user|croatia|skidata:c2
project_key: BS
cluster_size: 125
cluster_size_dedup: 125
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.97
extraction_model: claude-sonnet-4-6
frequency_per_month: 2.45
median_resolution_minutes: 1476.0
p95_resolution_minutes: 8147.8
cannot_reproduce_rate: 0.0
data_window_start: '2024-01-20'
data_window_end: '2026-01-20'
annual_hours_saved: 3.7
roi:
  baseline_active_hours: 14.7
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.7
  deflection_hours_range:
  - 0.5
  - 1.0
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 3.7
  agent_assist_hours_range:
  - 2.6
  - 4.8
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 12.5
  product_fix_hours_range:
  - 8.8
  - 14.7
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 1.5
  autonomous_resolve_hours_range:
  - 1.1
  - 1.9
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-39941
- BS-38128
- BS-25029
- BS-18282
- BS-23239
- BS-25130
- BS-28180
- BS-46737
- BS-47068
- BS-33810
- BS-34798
- BS-39466
- BS-20860
- BS-48194
- BS-36679
- BS-27849
- BS-35932
- BS-34919
canonical_examples:
- BS-25029
- BS-39941
- BS-47068
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
  autonomous_resolve_max_safe_volume_pct: 0.15
  autonomous_resolve_narrow_use_case: Automated detection of orphaned sessions after staff-triggered barrier events, with
    auto-notification to user that debt has been created — stopping short of autonomous payment charging or debt creation.
  autonomous_resolve_safety_constraints:
  - Must not autonomously charge or authorize payments on user cards without human approval
  - Must not autonomously create financial debts without operations team sign-off
  - Must not close sessions at €0 without a confirmed payment attempt failure logged by the payment gateway
  - Automated user notifications must only be sent after a human operator has confirmed the debt record exists
  - Must maintain a full audit trail of session state transitions for dispute resolution
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__7950cd
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
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__56d2b2
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- missing-parking-invoice-receipt
- open-session-at-exit-austria
- ticketless-open-session-at-exit__960f17
- ticketless-open-session-at-exit__d8d1ba
- ticketless-open-session-at-exit__fd04ac
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

# Parking session remains open after exit due to barrier lift by staff and subsequent payment authorization failure

## What this pattern is

End users report that their Bmove parking session remains active in the app after physically leaving a garage, because the exit barrier failed to trigger automatic session closure (often opened manually by garage staff or call center). When support attempts to close and charge the session, the payment authorization against the user's card fails, requiring the session to be closed at €0 and a debt to be created instead. The user must then manually pay the debt through the Bmove app.

## When this applies

- Exit barrier fails to read the vehicle plate or process the ticketless session, preventing automatic session closure
- Garage staff or call center manually lifts the barrier to let the user exit without closing the session in the system
- User notices the session is still active in the app hours, days, or weeks after leaving the garage
- User contacts support via in-app feedback to request session closure

## Typical resolution flow

1. User exits garage with barrier lifted manually by staff/call center; session remains open in Bmove app
2. User submits in-app feedback reporting the stuck/active session
3. Support agent tags the responsible internal team member and requests payment/closure of the specific session ID
4. Backend team attempts to charge the user's card for the session amount
5. Payment authorization fails; session is closed at €0
6. Support opens a debt on the user's account for the correct session amount
7. User is notified via reply that the session is closed and a debt has been created, payable through the Bmove app

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Tag internal billing/operations team and request manual payment attempt for the open session | support agent | Jira/internal ticketing system | 5 min |
| Attempt to charge user's registered payment card for the session amount | backend/operations team | payment system | 10 min |
| Close session at €0 due to authorization failure | backend/operations team | Bmove backend/admin panel | 5 min |
| Open a debt on user's account for the correct session amount | backend/operations team | Bmove backend/admin panel | 5 min |
| Notify user that session is closed and debt is available for payment in the app | support agent | Jira/email | 5 min |

## Evidence

Derived from 125 tickets in cluster `BS:end_user|croatia|skidata:c2`. Direct quotes from 6 representative tickets:

- `BS-25029` _[hr]_: "na izlazi iz garaže nije se htjela rampa dignuti, tako da mi je čovjek ručno digao rampu i zapisao da sam izašao iz garaže ali mi na aplikaciji nije registriralo da sam izašao"
- `BS-39941` _[hr]_: "sesija zatvorena na 0,00 zbog greške u autorizaciji. Potrebno otvaranje duga na 10,00 €"
- `BS-47068` _[hr]_: "Rampu je digao netko iz call centra ručno jer po tko zna koji put tablica na izlazu nije očitana"
- `BS-39941` _[hr]_: "sesija 202507081131262700214188 nije mogla biti naplaćena automatski i svi pokušaji naplate prema Vašoj kartici su bili neuspješni. Sesiju smo zatvorili i otvorili smo dug u iznosu sesije (10,00 €)."
- `BS-35932` _[hr]_: "imam aktivne 3 sesije jer se rampa na izlazu iz parkinga/garaze nije htjela otvoriti"
- `BS-39466` _[hr]_: "ticketless mi nije radio (nisam 20 min mogla izaci s parkinga, zvala sam i korisniku podrsku i sve), pa su mi samo podigli rampu da izadem, a u aplikaciji mi je i dalje aktivna sesija"

## Cluster statistics

- **Volume:** 125 tickets total (125 unique semantic events after dedup)
- **Frequency:** 2.45 tickets/month (over data window 2024-01-20 → 2026-01-20)
- **Median resolution:** 1.0 days
- **Languages:** hr, en
- **Country focus:** hr, at, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~14.7 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~3.7 (range [2.6, 4.81])
- **Time reduction per ticket:** ~25% (range [18%, 32%])
- **Feasibility:** 0.75
- **Rationale:** The resolution workflow is highly standardized (tag ops, attempt charge, close at €0, open debt, notify user), making it well-suited for an agent-assist tool that pre-populates the ops handoff request and drafts the user notification; the main time savings are in steps 1 and 5 which are agent-driven communication tasks. Backend execution steps (2–4) require human operators and cannot be accelerated by drafting alone.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool drafts the ops-tagging message and user notification for agents to review; measure time-to-send and agent acceptance/edit rate to calibrate actual savings.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~5 (range [3.5, 6.5])
- **Hours eliminated per year:** ~12.5 (range [8.8, 14.7])
- **Root cause:** Exit barrier opened by staff or call center does not trigger automatic session closure in the Bmove platform, and the subsequent payment authorization step is not retried or queued, leaving sessions orphaned and requiring manual intervention to resolve charges.
- **Rationale:** A full fix requires both reliable session-closure triggers for staff-opened barriers and a robust payment-retry or async-charge mechanism, likely involving coordination with garage hardware integrations; if successful, it could eliminate the vast majority of this ticket cluster. Engineering complexity is high due to multi-system dependencies (barrier hardware, payment gateway, app session state).
- **Validation:** Engineering team should spike on barrier-event telemetry completeness and payment-retry feasibility in a dev environment before committing sprint estimates; a staged rollout to one garage can validate closure accuracy before full deployment.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.7 (range [0.52, 0.96])
- **Form:** `in_app_help`
- **Deflection rate:** ~10% (range [7%, 13%])
- **Feasibility:** 0.30
- **Rationale:** This pattern involves a payment authorization failure and debt creation that requires backend action, so self-service cannot resolve the core issue; in-app guidance can only reduce repeat contacts or pre-inform users about the debt resolution process. Deflection potential is low because users need actual remediation, not just information.
- **Validation:** Deploy an in-app help article explaining the debt resolution process and monitor contact rate per affected session over a 4-week period; compare ticket volume per open-session-anomaly event before and after.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~1.5 (range [1.1, 1.95])
- **Narrow use case:** Automated detection of orphaned sessions after staff-triggered barrier events, with auto-notification to user that debt has been created — stopping short of autonomous payment charging or debt creation.
- **Safety constraints:**
  - Must not autonomously charge or authorize payments on user cards without human approval
  - Must not autonomously create financial debts without operations team sign-off
  - Must not close sessions at €0 without a confirmed payment attempt failure logged by the payment gateway
  - Automated user notifications must only be sent after a human operator has confirmed the debt record exists
  - Must maintain a full audit trail of session state transitions for dispute resolution
- **Rationale:** The financial and debt-creation steps in this workflow carry regulatory and trust risk that make full autonomous resolution inadvisable at this stage; a limited automation scope restricted to detection and user notification can reduce agent effort modestly while keeping humans in the loop for all financial actions. Savings potential is low given the narrow safe scope.
- **Validation:** Pilot automated orphaned-session detection alerts to the operations queue (no financial actions) for 30 days across 1–2 garages; measure reduction in time-to-ops-handoff and false-positive rate before expanding scope.

### Risks

- **Compliance concerns:**
  - Creating financial debts and closing payment sessions at €0 may be subject to consumer payment regulations (e.g., PSD2 in EU) requiring explicit user consent and dispute rights
  - Any automated payment retry must comply with card network rules on authorization attempts and stored-credential frameworks
  - Debt records on user accounts may constitute financial records subject to data retention and GDPR obligations
- **Must not automate:**
  - Autonomous charging or re-authorization of user payment methods without human review
  - Autonomous creation of debt records on user accounts without operations team approval
  - Closing sessions at €0 without a confirmed payment failure event from the payment gateway

## Agent compatibility

- **Status:** `active` (extraction confidence 0.97)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

