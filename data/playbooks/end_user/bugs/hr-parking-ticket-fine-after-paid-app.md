---
id: hr-parking-ticket-fine-after-paid-app
name: hr_parking_ticket_fine_after_paid_app
title: User receives parking fine despite paying via Bmove app
description: 'End users in Croatia (and occasionally neighbouring countries) pay for parking via the Bmove app, receive a
  payment confirmation, but still get a physical parking fine issued by the local parking authority. Root causes vary: technical
  transaction confirmation failures on the Bmove side, app geolocation assigning the wrong parking zone, licence plate mismatches
  (digit 0 vs. letter O), or app blocking repeat purchases due to an existing active fine. Resolution typically requires Bmove
  support to verify the transaction, contact the local parking operator to cancel the fine, and/or manually confirm the parking
  ticket.'
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
resolution_pattern: vendor_escalation
languages:
- hr
- en
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|no_value|dpk:c1
project_key: BS
cluster_size: 22
cluster_size_dedup: 22
sample_size_used: 18
extraction_schema: v1.0
extraction_confidence: 0.93
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.43
median_resolution_minutes: 4186.5
p95_resolution_minutes: 80910.49999999999
cannot_reproduce_rate: 0.0
data_window_start: '2022-03-04'
data_window_end: '2023-02-24'
annual_hours_saved: 0.9
roi:
  baseline_active_hours: 4.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.4
  deflection_hours_range:
  - 0.3
  - 0.5
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.9
  agent_assist_hours_range:
  - 0.6
  - 1.1
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 3.2
  product_fix_hours_range:
  - 2.2
  - 4.2
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: high
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.1
  autonomous_resolve_max_safe_volume_pct: 0.1
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-686
- BS-153
- BS-5088
- BS-228
- BS-821
- BS-1290
- BS-4269
- BS-6240
- BS-147
- BS-316
- BS-1273
- BS-671
- BS-155
- BS-3603
- BS-919
- BS-6084
- BS-5120
- BS-161
canonical_examples:
- BS-228
- BS-5088
- BS-153
vendor_dependency:
  vendor_name: Local parking operators (Zagrebparking, Splitparking, Parking Pula, Makarska parking, Elektromodul Osijek,
    etc.)
  involves_vendor: true
  typical_wait_days: 3
agent_compatibility:
  rag_consumable: true
  brainbox_skill: ready
  claude_skill: ready
  agent_assist: true
  autonomous_resolve: true
  note: Vendor coordination — needs human verification
  autonomous_resolve_max_safe_volume_pct: 0.1
  autonomous_resolve_narrow_use_case: Auto-detect and inform user of licence-plate mismatch (0 vs O), directing them to the
    parking authority — no financial or operator action taken
  autonomous_resolve_safety_constraints:
  - No automated contact with or commitments to parking operators; all vendor escalation must remain human-initiated
  - No automated fine cancellation or any action affecting the user's legal liability
  - Autonomous path limited to information-only responses where no transaction verification or backend change is required
  - All autonomous actions must be logged and reviewed weekly during any pilot
  - Explicit human handoff triggered if user disputes the mismatch diagnosis or indicates financial harm
related_playbooks:
- app-payment-failure-parking-ticket
- bmove-app-feedback-mixed-issues__7950cd
- hr-open-session-after-garage-exit
- missing-parking-receipt-email
- parking-fine-received-despite-valid-payment
- parking-payment-failure-end-user
- prepaid-top-up-and-usage-issues
- slovakia-parking-payment-failure-no-ticket
- ticketless-open-session-at-exit__d8d1ba
- ticketless-open-session-at-exit__fd04ac
- wrong-parking-ticket-purchase-redirect
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

# User receives parking fine despite paying via Bmove app

## What this pattern is

End users in Croatia (and occasionally neighbouring countries) pay for parking via the Bmove app, receive a payment confirmation, but still get a physical parking fine issued by the local parking authority. Root causes vary: technical transaction confirmation failures on the Bmove side, app geolocation assigning the wrong parking zone, licence plate mismatches (digit 0 vs. letter O), or app blocking repeat purchases due to an existing active fine. Resolution typically requires Bmove support to verify the transaction, contact the local parking operator to cancel the fine, and/or manually confirm the parking ticket.

## When this applies

- User pays for parking via Bmove app and receives confirmation email but app does not record the order properly
- Transaction confirmation fails on Bmove/payment processor side while charge goes through
- App GPS assigns wrong parking zone, leading to fine for correct zone
- Licence plate entered or read with 0/O mismatch between app and parking inspector
- App blocks new purchase because an existing DPK (daily parking fine) is active on the plate
- App shows no active billing for a location that is actually being enforced

## Typical resolution flow

1. User pays parking via Bmove app and receives or expects confirmation
2. Parking inspector issues a fine (DPK) to the vehicle
3. User contacts Bmove support with photo of fine and payment confirmation
4. Support verifies transaction status in backend systems (Igeus BO, CorvusPay, toolsi)
5. Support determines root cause (failed confirmation, wrong zone, plate mismatch, etc.)
6. Support contacts local parking operator (e.g. Zagrebparking, Splitparking, Parking Pula, Elektromodul) to cancel the fine
7. Support manually confirms parking ticket if not auto-confirmed
8. Support notifies user of outcome

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Check transaction status and confirm/manually activate parking ticket | Bmove support agent | IGeus BO / internal toolsi | 15 min |
| Send cancellation request for the issued fine to local parking operator | Bmove support agent | email / Jira (PYD project) | 10 min |
| Fix incorrect zone/billing data in the app backend | Bmove support agent or developer | Internal toolsi | 20 min |
| Inform user of licence plate mismatch and advise contacting parking authority directly | Bmove support agent | Jira comment / email | 5 min |

## Vendor dependency

- **Vendor:** Local parking operators (Zagrebparking, Splitparking, Parking Pula, Makarska parking, Elektromodul Osijek, etc.)
- **Typical wait:** 3 day(s)

## Evidence

Derived from 22 tickets in cluster `BS:end_user|no_value|dpk:c1`. Direct quotes from 7 representative tickets:

- `BS-228` _[hr]_: "Greška je s naše strane, tako da će Vam dobivena kazna biti poništena."
- `BS-5088` _[hr]_: "Ovo je naša greška, ne znam imamo li igdje u termsima da je ovo samo informativno i da ne mora biti točno."
- `BS-153` _[hr]_: "Transakcija nije confirmana 3k5cr-4cuhd-q2x"
- `BS-6240` _[hr]_: "aplikacija mi je locirala da se nalazim u 4. zoni i ja sam uredno platila onoliko koliko je pisalo. nažalost, dobila sam kaznu za 3. zonu."
- `BS-1290` _[hr]_: "vidimo u sustavu da ste dobili DPK i zato ne možete kupit novu kartu. Tek nakon isteka kazne ćete moći kupiti kartu."
- `BS-6084` _[hr]_: "kartica Vam je bila odbijena za 5 pokušaja plaćanja. Razlog odbijanja kartice ne znamo jer je to komunikacija između CorvusPay naplatnog servisa i Vaše banke"
- `BS-686` _[hr]_: "kazna je ispisana za reg. oznaku O52M255 (Vaš prvi znak je nula, dok je kontrolor ispisao kaznu sa prvim slovom O)"

## Cluster statistics

- **Volume:** 22 tickets total (22 unique semantic events after dedup)
- **Frequency:** 0.43 tickets/month (over data window 2022-03-04 → 2023-02-24)
- **Median resolution:** 2.9 days
- **Languages:** hr, en
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~4.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.9 (range [0.602, 1.118])
- **Time reduction per ticket:** ~20% (range [14%, 26%])
- **Feasibility:** 0.65
- **Rationale:** Agent assist can pre-fetch the transaction status from Bmove's backend and surface a templated cancellation-request draft for the relevant operator, reducing lookup and drafting time on actions 1 and 2; actions 3 and 4 still require judgment. The modest 20% reduction reflects the vendor-escalation overhead that no assist tool can compress.
- **Validation:** Run a 4-week shadow-mode pilot where the assist tool fetches transaction status and pre-fills operator email drafts; compare agent active-minutes before and after on matched ticket samples, requiring ≥10% reduction to proceed.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `high`
  - Sprints estimate: ~6 (range [4.2, 7.8])
- **Hours eliminated per year:** ~3.2 (range [2.24, 4.16])
- **Root cause:** Multiple intersecting bugs: (1) transaction confirmation failures leaving a paid ticket unactivated in the operator system, (2) geolocation assigning the wrong parking zone, (3) '0' vs 'O' licence-plate normalisation absent at entry, (4) app blocking repeat purchase when an existing active fine is present instead of offering resolution guidance.
- **Rationale:** Fixing all four root causes (reliable transaction confirmation, zone validation, plate normalisation, and fine-state purchase unblocking) could eliminate the large majority of this cluster; however, the operator-API reliability component depends partly on third-party systems, so full elimination is uncertain and the upper bound is capped at the 4.3-hour baseline. Engineering effort is high because multiple independent subsystems are involved.
- **Validation:** Engineering team should instrument transaction confirmation success rates and zone-assignment accuracy before and after each fix in a staging environment with real operator sandboxes; measure residual ticket rate over one quarter post-deploy.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.4 (range [0.252, 0.468])
- **Form:** `help_center`
- **Deflection rate:** ~10% (range [7%, 13%])
- **Feasibility:** 0.35
- **Rationale:** Most tickets in this cluster require active Bmove-side verification or vendor escalation that users cannot self-serve; a help center article can only address the licence-plate mismatch sub-case (~10% of volume) where the user is directed straight to the parking authority without agent work. The other root causes demand system access or operator contact.
- **Validation:** Publish a targeted help-center article for licence-plate mismatch and monitor for 8 weeks: measure what fraction of new tickets reference the article or close without agent reply, targeting ≥5% deflection to validate the estimate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 10% of tickets
- **Hours saved per year:** ~0.1 (range [0.063, 0.117])
- **Narrow use case:** Auto-detect and inform user of licence-plate mismatch (0 vs O), directing them to the parking authority — no financial or operator action taken
- **Safety constraints:**
  - No automated contact with or commitments to parking operators; all vendor escalation must remain human-initiated
  - No automated fine cancellation or any action affecting the user's legal liability
  - Autonomous path limited to information-only responses where no transaction verification or backend change is required
  - All autonomous actions must be logged and reviewed weekly during any pilot
  - Explicit human handoff triggered if user disputes the mismatch diagnosis or indicates financial harm
- **Rationale:** The only genuinely safe autonomous scope is the licence-plate mismatch notification (action 4, ~5 min, ~10% of volume), where no operator interaction or financial action is involved; all other sub-cases require verification against live systems or vendor coordination that cannot be safely delegated to automation given the legal and financial stakes of parking fines.
- **Validation:** Pilot autonomous triage for licence-plate mismatch only over 6 weeks: verify the bot correctly identifies the mismatch pattern with ≥90% precision on a human-reviewed holdout set before enabling any unsupervised replies.

### Risks

- **Compliance concerns:**
  - Parking fines carry legal weight in Croatia and neighbouring jurisdictions; any automated message could be construed as legal advice or a commitment to cancel the fine
  - GDPR: transaction records and licence-plate data are personal data and must not be exposed to automation pipelines without appropriate data-processing agreements
  - Misidentifying a legitimate fine as an app error and triggering cancellation could expose Bmove to liability with parking authorities
- **Must not automate:**
  - Sending cancellation requests to parking operators on behalf of users
  - Confirming or manually activating parking tickets in any operator's backend
  - Making any representation to a user that their fine will be or has been cancelled
  - Modifying zone or billing data in the app backend
- **Vendor dependencies blocking automation:**
  - Fine cancellation is gated on each local parking operator (Zagrebparking, Splitparking, Parking Pula, Makarska parking, Elektromodul Osijek, etc.) responding within their typical 3-day window; no automation can compress this
  - Transaction confirmation reliability depends partly on operator-side API availability, which Bmove does not control
  - Any pilot touching operator communication requires prior written agreement with each operator to accept requests via the new channel or format

## Agent compatibility

- **Status:** `active` (extraction confidence 0.93)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

