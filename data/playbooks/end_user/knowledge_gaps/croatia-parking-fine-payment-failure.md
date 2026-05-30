---
id: croatia-parking-fine-payment-failure
name: croatia_parking_fine_payment_failure
title: Users receive parking fines despite paying via app, or cannot pay fines through the app in Croatia
description: End users parking in Croatian cities (Split, Dubrovnik, Šibenik, Varaždin, Pula, etc.) either receive a penalty
  notice after successfully paying via the Bmove app (often due to license plate typos such as O vs 0 confusion, or wrong
  zone selection), or are unable to pay an existing fine through the app (due to expired payment period, unsupported fine
  type, or technical errors). In both cases, support redirects the user to the relevant local parking authority to resolve
  the dispute or find an alternative payment method.
category: end_user/knowledge_gaps
ticket_class: end_user
issue_category: knowledge_gap
resolution_pattern: vendor_escalation
languages:
- en
- other
country_focus:
- hr
- other
status: active
cluster_id: BS:end_user|croatia|dpk:c1
project_key: BS
cluster_size: 17
cluster_size_dedup: 17
sample_size_used: 17
extraction_schema: v1.0
extraction_confidence: 0.93
extraction_model: claude-sonnet-4-6
frequency_per_month: 0.33
median_resolution_minutes: 7279.0
p95_resolution_minutes: 41101.6
cannot_reproduce_rate: 0.0
data_window_start: '2023-05-19'
data_window_end: '2025-12-30'
annual_hours_saved: 0.4
roi:
  baseline_active_hours: 1.3
  baseline_active_source: sum(typical_actions.duration_estimate_minutes) from Sloj 6
  baseline_is_fallback: false
  baseline_confidence_tier: calibrated_estimate
  deflection_hours_midpoint: 0.3
  deflection_hours_range:
  - 0.2
  - 0.4
  deflection_confidence_tier: directional
  agent_assist_hours_midpoint: 0.4
  agent_assist_hours_range:
  - 0.3
  - 0.5
  agent_assist_confidence_tier: directional
  product_fix_hours_midpoint: 0.7
  product_fix_hours_range:
  - 0.5
  - 0.8
  product_fix_confidence_tier: directional
  product_fix_is_product_bug: true
  product_fix_engineering_effort_tier: medium
  autonomous_resolve_hours_midpoint: 0.1
  autonomous_resolve_hours_range:
  - 0.1
  - 0.1
  autonomous_resolve_max_safe_volume_pct: 0.15
  schema_version: v1.0
  model: claude-sonnet-4-6
  framing_note: Headline values are midpoints; ranges show ±30% uncertainty. Hours are LLM-derived from cluster samples —
    validate with pilots before commitment.
evidence_tickets:
- BS-12879
- BS-22950
- BS-27246
- BS-37855
- BS-44260
- BS-8349
- BS-21899
- BS-22745
- BS-26046
- BS-40376
- BS-47173
- BS-36245
- BS-39364
- BS-11133
- BS-35998
- BS-27443
- BS-10275
canonical_examples:
- BS-12879
- BS-22950
- BS-22745
vendor_dependency:
  vendor_name: Local Croatian parking services (e.g., Split Parking, Sanitat Dubrovnik, Gradski Parking Šibenik, Pula Parking,
    Makarska, ZIM Varaždin)
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
  autonomous_resolve_narrow_use_case: Auto-reply with city-specific parking authority contact details when user explicitly
    states inability to pay fine or requests redirect, with no contested dispute language detected.
  autonomous_resolve_safety_constraints:
  - Must not autonomously dismiss or adjudicate a fine dispute on behalf of the user
  - Must not send incorrect authority contact details — contact database must be verified and maintained
  - Must route any ticket containing dispute, wrongful fine, or legal language to a human agent
  - Must not handle tickets where payment failure involves potential financial loss without agent review
  - Low annual volume (4 tickets/year) means automation ROI is negligible and error cost is proportionally high
related_playbooks:
- croatia-bmove-app-feedback-miscellaneous
- croatia-parking-fine-dispute
- croatia-parking-fine-dispute-and-payment
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

# Users receive parking fines despite paying via app, or cannot pay fines through the app in Croatia

## What this pattern is

End users parking in Croatian cities (Split, Dubrovnik, Šibenik, Varaždin, Pula, etc.) either receive a penalty notice after successfully paying via the Bmove app (often due to license plate typos such as O vs 0 confusion, or wrong zone selection), or are unable to pay an existing fine through the app (due to expired payment period, unsupported fine type, or technical errors). In both cases, support redirects the user to the relevant local parking authority to resolve the dispute or find an alternative payment method.

## When this applies

- User paid for parking via Bmove app but still received a parking fine
- License plate entered incorrectly (e.g., letter O vs digit 0) causing mismatch with fine
- User selected wrong parking zone or city in the app
- User is unable to pay a parking fine through the app (technical error, expired period, unsupported fine)
- User scanned a QR code but payment was not recognised by parking inspector

## Typical resolution flow

1. User contacts support reporting a fine received despite paying, or inability to pay a fine
2. Support agent reviews payment receipt and/or fine details submitted by the user
3. Agent identifies root cause: license plate mismatch, wrong zone, expired fine, or system error
4. Agent informs user that fine jurisdiction lies with the local parking service
5. Agent provides contact details of the relevant local parking authority (email, phone, website)
6. User is advised to contact the parking service directly to dispute or pay the fine

## Typical actions

| What | Who | Tool | Duration |
|---|---|---|---|
| Review payment receipt and fine details provided by the user to identify discrepancy | support_agent | Bmove back-office / email | 10 min |
| Inform user of the specific mismatch or reason for failure | support_agent | email | 5 min |
| Redirect user to the relevant local parking authority with contact details | support_agent | email | 5 min |

## Vendor dependency

- **Vendor:** Local Croatian parking services (e.g., Split Parking, Sanitat Dubrovnik, Gradski Parking Šibenik, Pula Parking, Makarska, ZIM Varaždin)

## Evidence

Derived from 17 tickets in cluster `BS:end_user|croatia|dpk:c1`. Direct quotes from 7 representative tickets:

- `BS-12879` _[en]_: "you have paid for the license plate number RI4420, but that is an incorrect format of the Croatian license plate. The last character of the license plate is probably the letter O."
- `BS-22950` _[en]_: "the fine is issued for the vehicle FY****, and you paid for the vehicle BY****. Please contact the Splitparking service at r****@splitparking.hr since this is in their jurisdiction."
- `BS-22745` _[en]_: "the parking controller issued a fine to ZG****, but you have paid for the license plate ZG4915I0 (the difference is the letter O and number zero)"
- `BS-47173` _[en]_: "since the payment period expired, you cannot pay for it in the Bmove app. Please contact the Šibenik parking service and check with them other payment methods."
- `BS-27246` _[en]_: "it seems that the service provider of city of Ston does not support this kind of fine for a reason that is unknown to us. Please contact them and check with them how can you pay for the fine in other "
- `BS-39364` _[en]_: "I paid for parking in the app, but still received a receipt for parking for the day even though I didn't plan to."
- `BS-36245` _[en]_: "the fine is issued for DA****, and you paid for DA****."

## Cluster statistics

- **Volume:** 17 tickets total (17 unique semantic events after dedup)
- **Frequency:** 0.33 tickets/month (over data window 2023-05-19 → 2025-12-30)
- **Median resolution:** 5.1 days
- **Languages:** en, other
- **Country focus:** hr, other

## Automation opportunity

These are LLM-derived estimates from cluster sample analysis (Sloj 7). Headline values are midpoints; ranges show ±30% uncertainty. **Validate with pilots before committing engineering resources.**

### Baseline (`calibrated_estimate`)

- **Annual active work:** ~1.3 hours/year
- _Source:_ sum(typical_actions.duration_estimate_minutes) from Sloj 6

### Agent-assist (`directional`)

- **Hours saved per year:** ~0.4 (range [0.273, 0.507])
- **Time reduction per ticket:** ~30% (range [21%, 39%])
- **Feasibility:** 0.75
- **Rationale:** The resolution workflow is highly templated — identify mismatch, explain reason, provide city-specific authority contact — making it well suited for an assist tool that auto-populates the relevant authority details and drafts the redirect message based on user-stated city, reducing lookup and writing time per ticket.
- **Validation:** Run a 2-week shadow-mode pilot where the assist tool surfaces a pre-drafted response for agent review; measure draft acceptance rate and average handle time versus the prior 2-week baseline.

### Product fix (`directional`)

- **Is product bug:** `True`
- **Engineering effort tier:** `medium`
  - Sprints estimate: ~3 (range [2.1, 3.9])
- **Hours eliminated per year:** ~0.7 (range [0.455, 0.845])
- **Root cause:** Two distinct product gaps: (1) lack of real-time license plate validation with a visual warning for O/0 ambiguity at entry, and (2) absence of in-app guidance or error messaging when a fine payment attempt fails due to expired period, unsupported fine type, or technical error — leaving users without actionable next steps.
- **Rationale:** Better plate-entry validation and in-app error messaging with city-specific authority contacts could prevent or self-resolve the majority of tickets in this cluster; however, resolution of actual fines still requires vendor action, so elimination is partial rather than total.
- **Validation:** Instrument the app to log plate-entry correction events and fine payment error codes pre- and post-fix; compare ticket volumes for this cluster over two equivalent 90-day windows.

### Self-service deflection (`directional`)

- **Hours saved per year:** ~0.3 (range [0.24, 0.42])
- **Form:** `help_center`
- **Deflection rate:** ~25% (range [18%, 32%])
- **Feasibility:** 0.55
- **Rationale:** A clearly written help-center article explaining common causes (O vs 0 plate typos, wrong zone, expired payment period) and directing users to the appropriate local authority per city could deflect a portion of tickets where users just need contact details. However, users with active disputes or genuine payment failures often need agent confirmation of their specific case, limiting deflection ceiling.
- **Validation:** Deploy a help-center article and in-app FAQ covering Croatian parking fine scenarios for 4 weeks; measure the ratio of users who view the article and do not open a ticket versus the pre-deployment baseline rate.

### Autonomous resolve (`directional`, ≤30% safety cap)

- **Max safe volume:** 15% of tickets
- **Hours saved per year:** ~0.1 (range [0.05, 0.09])
- **Narrow use case:** Auto-reply with city-specific parking authority contact details when user explicitly states inability to pay fine or requests redirect, with no contested dispute language detected.
- **Safety constraints:**
  - Must not autonomously dismiss or adjudicate a fine dispute on behalf of the user
  - Must not send incorrect authority contact details — contact database must be verified and maintained
  - Must route any ticket containing dispute, wrongful fine, or legal language to a human agent
  - Must not handle tickets where payment failure involves potential financial loss without agent review
  - Low annual volume (4 tickets/year) means automation ROI is negligible and error cost is proportionally high
- **Rationale:** The strictly informational redirect sub-case (user needs authority contact only) is theoretically automatable, but the low annual volume, vendor dependency, and risk of routing users to incorrect authorities in a legal/fine context make autonomous resolve low value and moderate risk.
- **Validation:** Define a pilot scope of 4 weeks limited to tickets where intent classifier confidence for 'redirect only' exceeds 0.90; require a human review queue for all auto-sent replies and measure error rate against a 0% incorrect-contact-details acceptance criterion.

### Risks

- **Compliance concerns:**
  - Parking fines are legal instruments under Croatian municipal law; incorrect or misleading information provided to users could expose the company to liability
  - GDPR: ticket content may include vehicle registration data and personal fine details requiring careful handling in any automated pipeline
  - Each Croatian municipality operates independently — contact details and procedures vary and can change, requiring active maintenance of any automated contact database
- **Must not automate:**
  - Adjudicating or expressing opinion on whether a fine is valid or invalid
  - Promising refunds or outcomes related to fine disputes
  - Any response where the user has indicated legal action or escalation intent
- **Vendor dependencies blocking automation:**
  - Resolution of wrongful fines requires direct action by the relevant local Croatian parking authority (e.g., Split Parking, Sanitat Dubrovnik, ZIM Varaždin) — Bmove has no API or data integration with these authorities to verify or reverse fines programmatically
  - Fine payment failures caused by vendor-side technical errors or unsupported fine types cannot be resolved without vendor cooperation, blocking any end-to-end automation

## Agent compatibility

- **Status:** `active` (extraction confidence 0.93)
- **Brainbox skill:** `ready`
- **Claude skill:** `ready`
- **Agent-assist:** `True`
- **Autonomous resolve:** `False`
- **RAG-consumable:** `True`
- **Note:** Vendor coordination — needs human verification

