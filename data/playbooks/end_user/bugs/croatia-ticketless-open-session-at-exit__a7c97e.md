---
id: croatia-ticketless-open-session-at-exit__a7c97e
name: croatia_ticketless_open_session_at_exit
title: Ticketless parking session remains active after vehicle has left the garage
description: Users report that their parking session in the Bmove app remains active (and continues accruing charges) even
  after they have physically exited the garage. This often occurs when the exit barrier fails to open automatically, requiring
  manual intervention by garage staff, and the system never registers the exit. Some users report the stuck session persisting
  for days, weeks, or even a month, and have contacted support multiple times without resolution.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: manual_close
languages:
- hr
- en
country_focus:
- hr
- other
- at
status: active
cluster_id: BS:unknown|croatia|no_label:c2
project_key: BS
cluster_size: 30
cluster_size_dedup: 30
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.92
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.59
median_resolution_minutes: 11804.5
p95_resolution_minutes: 36781.79999999999
cannot_reproduce_rate: 0.0
data_window_start: '2023-08-23'
data_window_end: '2025-10-31'
annual_hours_saved: 0.7
roi:
  baseline_active_hours: 3.5
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.3
  deflection_hours_range:
  - 0.2
  - 0.3
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.7
  agent_assist_hours_range:
  - 0.5
  - 0.9
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 3.5
  product_fix_hours_range:
  - 2.8
  - 3.5
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.0
  autonomous_resolve_hours_range: null
  autonomous_resolve_max_safe_volume_pct: 0.0
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-44179
- BS-13400
- BS-14354
- BS-13126
- BS-16060
- BS-17144
- BS-21107
- BS-16807
- BS-16437
- BS-16559
- BS-41980
- BS-16390
- BS-17055
- BS-16150
- BS-12564
- BS-22020
- BS-16588
- BS-16539
canonical_examples:
- BS-16060
- BS-17144
- BS-22020
vendor_dependency:
  vendor_name: Garage/parking facility operator (e.g., Zagrad, Stari grad, Cambieri, Centar Kaptol)
  involves_vendor: true
  typical_wait_days: 7
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: false
  note: Backend action — agent drafts, human verifies
  autonomous_resolve_max_safe_volume_pct: 0.0
  autonomous_resolve_narrow_use_case: Auto-flag sessions exceeding 24 hours for agent review, with no autonomous financial
    close without human approval
  autonomous_resolve_safety_constraints:
  - Do not autonomously close or modify billing records without agent sign-off — financial impact requires human accountability
  - Cannot verify exit independently without reliable garage operator event feed; false positives could close legitimate active
    sessions
  - Vendor dependency on garage operators means system-of-record data is not trustworthy enough for unsupervised action
  - 'User dispute risk: autonomous session closure without log verification could create chargeback or fraud liability'
  - 'Regulatory concern: automated modification of payment/billing records may require audit trail with human authorisation'
related_playbooks:
- austrian-open-session-at-exit
- austrian-ticketless-open-session-at-exit__06e3d4
- austrian-ticketless-open-session-at-exit__deee93
- b2b-partner-austria-ticketless-open-session-at-exit
- bmove-app-feedback-mixed-issues__7950cd
- bmove-app-feedback-mixed-issues__d6cf0c
- bmove-app-operational-issues-austria
- croatia-parking-payment-failure__e3b934
- croatia-ticketless-open-session-at-exit__f25b63
- croatian-ticketless-open-session-at-exit__275624
- croatian-ticketless-open-session-at-exit__56d2b2
- croatian-ticketless-open-session-at-exit__ab83b0
- croatian-ticketless-open-session-at-exit__dc548a
- croatian-ticketless-open-session-at-exit__e3afed
- missing-parking-invoice-receipt
- open-session-at-exit-austria
- open-session-at-exit-payment-failure
- ticketless-open-session-at-exit__960f17
- ticketless-open-session-at-exit__d8d1ba
- ticketless-open-session-not-closed-at-exit
known_product_bugs: []
escalates_to: null
maintainers: []
generated_by: praxis-v0.1
created: '2026-05-15'
updated: '2026-05-15'
correction_count: 0
---

# Ticketless parking session remains active after vehicle has left the garage

## What this pattern is

Users report that their parking session in the Bmove app remains active (and continues accruing charges) even after they have physically exited the garage. This often occurs when the exit barrier fails to open automatically, requiring manual intervention by garage staff, and the system never registers the exit. Some users report the stuck session persisting for days, weeks, or even a month, and have contacted support multiple times without resolution.

## When this applies

- User exits the garage but the exit barrier does not open automatically via the Bmove ticketless system
- Garage staff manually opens the barrier, bypassing the normal session-close flow
- App fails to detect or register the vehicle exit, leaving the session open
- Session continues billing after physical departure

## Typical resolution flow

1. User parks using the Bmove ticketless feature and exits (or attempts to exit) the garage
2. Exit barrier does not open automatically; garage staff may intervene manually
3. User notices the session is still shown as active in the Bmove app
4. User submits feedback or contacts support requesting the session be terminated
5. Support agent manually closes/deletes the active session in the backend
6. User may follow up multiple times if no response or action is taken

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Manually terminate (close/delete) the stuck active parking session in the backend | support_agent | Bmove admin backend | 10 min |
| Verify exit timestamp and garage logs to confirm user did leave the garage | support_agent | Bmove admin backend / garage system logs | 15 min |
| Communicate resolution status back to the user via email | support_agent | email | 5 min |

## Vendor dependency

- **Vendor:** Garage/parking facility operator (e.g., Zagrad, Stari grad, Cambieri, Centar Kaptol)
- **Typical wait:** 7 day(s)

## Evidence

Derived from 30 tickets in cluster `BS:unknown|croatia|no_label:c2`. Direct quotes from 6 representative tickets:

- `BS-16060` _[hr]_: "Sesija na vozilo još traje iako je vozilo izašlo iz garaže."
- `BS-17144` _[hr]_: "Molim da iskljucite aktivnu sesiju koja traje mjesec dana, ja sam izasla iz garaze nakon sat vremena! Ovo je valjda peti put da vas kontaktiram."
- `BS-22020` _[hr]_: "U aplikaciji mi I dalje Stoji da je aktivna sesija iako Sam izasao iz garaze U subotu! molim Vas da prekinete sesiju jer ispada da Sam ja U garazi vec 3 Dana te nezelim da mi dodje racun za uslugu Koj"
- `BS-16539` _[hr]_: "molim da mi iskljucite aktivnu sesiju koja traje 4 tjedna a izasla sam dva sata nakon dolaska iz garaze a niste mi ponistili sesiju!"
- `BS-44179` _[hr]_: "Pise mi da imam aktivne sesije u cak 4 garaze, medutim nemam ni u jednoj. Molim Vas da mi iste sesije obrisete."
- `BS-16390` _[hr]_: "sada mi se poslje tjedan dana još računa da sam parkiran"

## Cluster statistics

- **Volume:** 30 tickets total (30 unique semantic events after dedup)
- **Frequency:** 0.59 tickets/month (over data window 2023-08-23 → 2025-10-31)
- **Median resolution:** 8.2 days
- **Languages:** hr, en
- **Country focus:** hr, other, at

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~3.5 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.7 (range [0.49, 0.91])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.75
- **Rationale:** The resolution workflow is highly repetitive (verify logs, close session, draft email), making it well-suited for agent-assist tooling that pre-populates the garage log lookup, surfaces the stuck session directly, and drafts the resolution email — reducing the communication step from ~5 min to ~1-2 min and the verification step modestly. The backend close action still requires human confirmation due to billing impact.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool pre-drafts the resolution email and pre-fetches the suspected stuck session; compare actual handle time vs. the 30-minute baseline using time-tracked tickets.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~5 (range [3.5, 6.5])
- **Hours eliminated per year:** ~3.5 (range [2.8, 3.5])
- **Root cause:** Exit events from garage barrier systems are not reliably transmitted to or processed by the Bmove backend, leaving parking sessions open indefinitely when manual barrier overrides occur without a corresponding system exit signal.
- **Rationale:** A reliable fix requires integration changes with multiple third-party garage operators (Zagrad, Stari grad, Cambieri, Centar Kaptol) to ensure exit events are always transmitted, plus a safeguard timeout rule in the Bmove backend that auto-closes sessions exceeding a plausible parking duration. Vendor dependency makes the effort estimate wide and the timeline uncertain.
- **Validation:** Engineering team should scope vendor API audit for all listed operators and prototype a session auto-close safety rule in a staging environment; run a 2-sprint spike to validate feasibility before full estimate is committed.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.3 (range [0.21, 0.35])
- **Form:** `in_app_help`
- **Deflection rate:** ~8% (range [6%, 10%])
- **Feasibility:** 0.25
- **Rationale:** This bug requires a manual backend action to close the stuck session — users cannot self-serve the fix, so FAQ or in-app help can only set expectations and reduce repeat contacts, not deflect the ticket itself. Deflection potential is very low and limited to reducing duplicate follow-up tickets from the same user.
- **Validation:** Deploy an in-app help article for 4 weeks explaining the known issue and expected resolution SLA; measure whether repeat-contact rate per affected user drops vs. prior 4-week baseline.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 0% of tickets
- **Narrow use case:** Auto-flag sessions exceeding 24 hours for agent review, with no autonomous financial close without human approval
- **Safety constraints:**
  - Do not autonomously close or modify billing records without agent sign-off — financial impact requires human accountability
  - Cannot verify exit independently without reliable garage operator event feed; false positives could close legitimate active sessions
  - Vendor dependency on garage operators means system-of-record data is not trustworthy enough for unsupervised action
  - User dispute risk: autonomous session closure without log verification could create chargeback or fraud liability
  - Regulatory concern: automated modification of payment/billing records may require audit trail with human authorisation
- **Rationale:** Fully autonomous resolution is not safe at any meaningful volume because the root cause is an unreliable vendor event feed — the system cannot independently confirm the user has left, making autonomous session closure a billing error risk. Until a trusted exit-event integration is in place, this opportunity yields zero safe automation.
- **Validation:** Revisit autonomous feasibility only after a product fix establishes a reliable, auditable exit event feed from all garage operators; acceptance criterion is <0.5% false-positive rate on auto-detected exit events over 90 days.

### Risks

- **Compliance concerns:**
  - Modifying or closing billing records must maintain a complete audit trail for consumer protection and payment dispute purposes
  - Automated financial adjustments (refunds, session closures) may require documented human authorisation under applicable e-payment regulations
  - Extended erroneous charges (days to weeks) may trigger consumer-rights obligations depending on jurisdiction
- **Must not automate:**
  - Autonomous closure of active parking sessions with billing implications without agent confirmation
  - Issuing refunds or billing adjustments without verifying garage exit logs
  - Any action that modifies payment state when the underlying vendor event feed is known to be unreliable
- **Vendor dependencies blocking automation:**
  - Garage/parking facility operators (Zagrad, Stari grad, Cambieri, Centar Kaptol) must provide reliable, real-time exit event feeds before any backend automation is safe
  - Typical vendor response SLA of 7 days means log verification cannot be automated end-to-end today
  - No standardised API or event format across multiple operators increases integration complexity and delays a product fix

## Agent compatibility

- **Status:** `active` (extraction confidence 0.92)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Backend action — agent drafts, human verifies

